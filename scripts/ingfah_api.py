#!/usr/bin/env python3
"""Small, dependency-free client for the supported Ingfah client API routes."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://api.ingfah.ai"
API_KEY_ENV = "INGFAH_API_KEY"
BASE_URL_ENV = "INGFAH_API_BASE_URL"
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

ROUTE_PATTERNS = (
    ("GET", re.compile(r"^/client/(ai-agent-teams|disposition-outcomes|products)$")),
    ("GET", re.compile(r"^/client/ai-agent-teams/[^/]+/customer-context-variables$")),
    ("GET", re.compile(r"^/client/(ai-agents|agent-templates)$")),
    ("GET", re.compile(r"^/client/agents/[^/]+$")),
    ("GET", re.compile(r"^/client/agents/[^/]+/revisions(?:/[^/]+)?$")),
    ("POST", re.compile(r"^/client/agents$")),
    ("DELETE", re.compile(r"^/client/agents/[^/]+$")),
    ("GET", re.compile(r"^/client/chat-sessions(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/chat-sessions-list(?:/csv)?$")),
    ("GET", re.compile(r"^/client/agents/[^/]+/chat-session-tests(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/outbound/options(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+/records$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+/records/download$")),
    ("POST", re.compile(r"^/client/outbound/batches$")),
    ("POST", re.compile(r"^/client/outbound/batches/[^/]+/(pause|resume|cancel)$")),
)


class ClientError(Exception):
    """User-safe client or API error."""


@dataclass
class ApiResponse:
    status: int
    body: Any
    content_type: str = "application/json"


def _is_allowed(method: str, path: str) -> bool:
    return any(allowed_method == method and pattern.fullmatch(path) for allowed_method, pattern in ROUTE_PATTERNS)


def _is_mutation(method: str, path: str) -> bool:
    return method in MUTATING_METHODS and _is_allowed(method, path)


def _base_url() -> str:
    value = os.environ.get(BASE_URL_ENV, DEFAULT_BASE_URL).strip().rstrip("/")
    if not value.startswith("https://"):
        raise ClientError(f"{BASE_URL_ENV} must use an HTTPS URL")
    return value


def _read_key() -> str:
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        raise ClientError(f"Set {API_KEY_ENV} before calling Ingfah")
    return key


def request(method: str, path: str, body: Any = None, *, confirm: bool = False, query: str = "") -> ApiResponse:
    method = method.upper()
    if not path.startswith("/") or "?" in path:
        raise ClientError("path must be an absolute API path without a query string")
    if not _is_allowed(method, path):
        raise ClientError(f"route is not available through this skill: {method} {path}")
    if _is_mutation(method, path) and not confirm:
        raise ClientError("mutation requires explicit confirmation (--confirm)")

    key = _read_key()
    url = f"{_base_url()}{path}{query}"
    data = None
    # HTTP header names are case-insensitive; the gateway accepts either
    # spelling. User-Agent is required -- Cloudflare rejects requests without
    # one with a 403 error-1010 before they reach the API.
    headers = {
        "X-Api-Key": key,
        "Accept": "application/json",
        "User-Agent": "ingfah-skill/1.0",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    http_request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(http_request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "application/json")
            raw = response.read()
            return ApiResponse(response.getcode(), _decode_body(raw, content_type), content_type)
    except urllib.error.HTTPError as error:
        raw = error.read()
        content_type = error.headers.get("Content-Type", "application/json")
        body_value = _decode_body(raw, content_type)
        raise ClientError(_format_api_error(error.code, body_value)) from None
    except urllib.error.URLError as error:
        raise ClientError(f"could not reach Ingfah API: {error.reason}") from None


def _decode_body(raw: bytes, content_type: str) -> Any:
    if "json" in content_type.lower():
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"raw_bytes": len(raw)}
    return raw.decode("utf-8", errors="replace")


def _format_api_error(status: int, body: Any) -> str:
    if isinstance(body, dict):
        error = body.get("error") or body.get("message") or "request failed"
        # error_detail carries the field-level reason (e.g. "time_slots is
        # required"). Without it every validation failure reads "bad request".
        detail = body.get("error_detail")
        if isinstance(detail, str) and detail.startswith(f"{error}: "):
            detail = detail[len(error) + 2 :]
        if detail and detail != error:
            return f"Ingfah API returned HTTP {status}: {error}: {detail}"
        return f"Ingfah API returned HTTP {status}: {error}"
    return f"Ingfah API returned HTTP {status}"


def _load_json_body(value: str) -> Any:
    """Accept either an inline JSON document or a path to a JSON file."""
    text = value
    if not value.lstrip().startswith(("{", "[")):
        try:
            with open(value, encoding="utf-8") as handle:
                text = handle.read()
        except OSError as error:
            raise ClientError(f"could not read JSON body file: {error.strerror}") from None
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ClientError(f"invalid JSON body: {error.msg}") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call an allowlisted Ingfah client API route")
    parser.add_argument("method", choices=("GET", "POST", "PUT", "PATCH", "DELETE"))
    parser.add_argument("path")
    parser.add_argument("--query", default="", help="URL-encoded query string, including the leading ?")
    parser.add_argument("--json", dest="json_body", help="JSON request body, inline or a path to a .json file")
    parser.add_argument("--confirm", action="store_true", help="confirm a state-changing request")
    args = parser.parse_args(argv)

    try:
        body = _load_json_body(args.json_body) if args.json_body else None
        response = request(args.method, args.path, body, confirm=args.confirm, query=args.query)
        if isinstance(response.body, (dict, list)):
            print(json.dumps(response.body, ensure_ascii=False, indent=2))
        elif isinstance(response.body, bytes):
            sys.stdout.buffer.write(response.body)
        else:
            print(response.body, end="")
        return 0
    except ClientError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
