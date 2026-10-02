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


__version__ = "1.6.0"

DEFAULT_BASE_URL = "https://api.ingfah.ai"
API_KEY_ENV = "INGFAH_API_KEY"
BASE_URL_ENV = "INGFAH_API_BASE_URL"
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

ROUTE_PATTERNS = (
    ("GET", re.compile(r"^/client/(ai-agent-teams|disposition-outcomes|products)$")),
    ("GET", re.compile(r"^/client/ai-agent-teams/[^/]+/customer-context-variables$")),
    ("GET", re.compile(r"^/client/products/[^/]+$")),
    ("POST", re.compile(r"^/client/products$")),
    ("PUT", re.compile(r"^/client/products/[^/]+$")),
    ("PUT", re.compile(r"^/client/products/[^/]+/visibility$")),
    ("DELETE", re.compile(r"^/client/products/[^/]+$")),
    ("GET", re.compile(r"^/client/products/[^/]+/automations$")),
    ("POST", re.compile(r"^/client/products/[^/]+/automations$")),
    ("PUT", re.compile(r"^/client/products/[^/]+/automations/[^/]+$")),
    ("DELETE", re.compile(r"^/client/products/[^/]+/automations/[^/]+$")),
    ("POST", re.compile(r"^/client/products/[^/]+/postprocessors$")),
    ("PUT", re.compile(r"^/client/products/[^/]+/postprocessors/[^/]+$")),
    ("DELETE", re.compile(r"^/client/products/[^/]+/postprocessors/[^/]+$")),
    ("GET", re.compile(r"^/client/(text-channel-config-providers|text-channel-configs)$")),
    ("GET", re.compile(r"^/client/text-channel-configs/[^/]+$")),
    ("GET", re.compile(r"^/client/text-chats/channel-configs(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/(ai-agents|agent-templates|phone-tools|voices)$")),
    ("GET", re.compile(r"^/client/plugin-function-integrations$")),
    ("GET", re.compile(r"^/client/plugin-functions(?:/[^/]+)?$")),
    ("POST", re.compile(r"^/client/plugin-functions$")),
    ("PUT", re.compile(r"^/client/plugin-functions/[^/]+$")),
    ("DELETE", re.compile(r"^/client/plugin-functions/[^/]+$")),
    ("POST", re.compile(r"^/client/plugin-functions/[^/]+/(duplicate|test-run)$")),
    ("GET", re.compile(r"^/client/agents/[^/]+$")),
    ("GET", re.compile(r"^/client/agents/[^/]+/revisions(?:/[^/]+)?$")),
    ("POST", re.compile(r"^/client/agents$")),
    ("DELETE", re.compile(r"^/client/agents/[^/]+$")),
    ("PUT", re.compile(r"^/client/agents/[^/]+/(profile|description|visibility)$")),
    ("POST", re.compile(r"^/client/agents/[^/]+/revisions$")),
    ("POST", re.compile(r"^/client/agents/[^/]+/revisions/[^/]+/publish$")),
    ("POST", re.compile(r"^/client/agents/[^/]+/publish$")),
    ("DELETE", re.compile(r"^/client/agents/[^/]+/revisions/[^/]+$")),
    ("GET", re.compile(r"^/client/chat-sessions(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/chat-sessions/[^/]+/record(?:/(download|checksum))?$")),
    ("GET", re.compile(r"^/client/chat-sessions-list(?:/csv)?$")),
    ("GET", re.compile(r"^/client/agents/[^/]+/chat-session-tests(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/text-chats/chat-sessions-list(?:/csv)?$")),
    ("GET", re.compile(r"^/client/text-chats/conversations(?:/[^/]+)?$")),
    ("GET", re.compile(r"^/client/analytics/(summary|short-calls|hourly-charts|duration-histogram|heatmap|speech-ratio)$")),
    ("GET", re.compile(r"^/client/analytics/report/download$")),
    ("GET", re.compile(r"^/client/text-analytics/(summary|messages-hourly|heatmap)$")),
    ("GET", re.compile(r"^/client/outbound/options(?:/[^/]+)?$")),
    ("POST", re.compile(r"^/client/outbound/options$")),
    ("PUT", re.compile(r"^/client/outbound/options/[^/]+$")),
    ("DELETE", re.compile(r"^/client/outbound/options/[^/]+$")),
    ("GET", re.compile(r"^/client/outbound/call-data-records$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+/records$")),
    ("GET", re.compile(r"^/client/outbound/batches/[^/]+/records/download$")),
    ("POST", re.compile(r"^/client/outbound/batches$")),
    ("POST", re.compile(r"^/client/outbound/batches/[^/]+/(pause|resume|cancel)$")),
)


REVISION_CREATE = re.compile(r"^/client/agents/([^/]+)/revisions$")

# A revision replaces the agent's whole configuration, tool bindings included,
# and the backend stores exactly the id lists it is sent: an omitted
# `phone_tools` or `ai_plugin_function_ids` saves a revision with NO tools.
# The revision read (GET .../revisions/{id}) does not return either list, so a
# body copied from it strips every tool. The bindings are only readable from
# GET /client/agents/{slug} (the published revision), under the names below.
# Real incident, 2026-09-30: a prompt-only edit published this way unbound an
# agent's transfer and hang-up tools; the agent then spoke
# "transfer_to_human_agent{}" aloud and repeated its goodbye without hanging up.
REVISION_TOOL_FIELDS = (
    # (revision body key, agent read key, dashboard name)
    ("phone_tools", "phone_tools", "Tools เกี่ยวกับการโทร (phone tools)"),
    ("ai_plugin_function_ids", "ai_plugin_functions", "Tools ทั่วไป (plugin functions)"),
)
FLOW_TOOL_KEYS = (("phone_tools", "phone_tools"), ("plugin_functions", "ai_plugin_function_ids"))


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


def _ids(items: Any) -> set[int]:
    out: set[int] = set()
    for item in items or []:
        value = item.get("id") if isinstance(item, dict) else item
        try:
            out.add(int(value))
        except (TypeError, ValueError):
            continue
    return out


def _unwrap(body: Any, key: str) -> Any:
    data = body.get("data", body) if isinstance(body, dict) else body
    if isinstance(data, dict) and isinstance(data.get(key), dict):
        return data[key]
    return data


def check_revision_tools(slug: str, body: Any, current_agent: Any) -> list[str]:
    """Return the reasons a revision body would unbind tools; empty when safe.

    `current_agent` is the GET /client/agents/{slug} response. A text agent's
    phone tools are dropped by the server anyway, so they are not compared.
    """
    if not isinstance(body, dict):
        return []
    agent = _unwrap(current_agent, "agent") if current_agent is not None else {}
    agent = agent if isinstance(agent, dict) else {}
    is_text = agent.get("type") == "text"
    problems: list[str] = []
    for body_key, agent_key, label in REVISION_TOOL_FIELDS:
        if body_key == "phone_tools" and is_text:
            continue
        bound = _ids(agent.get(agent_key))
        if body_key not in body:
            problems.append(
                f"`{body_key}` is missing, which saves the revision with no {label}. "
                f"The revision read does not return it: copy the ids from GET /client/agents/{slug} "
                f"`{agent_key}` (currently {sorted(bound) or '[]'})"
            )
            continue
        dropped = bound - _ids(body.get(body_key))
        if dropped:
            problems.append(
                f"`{body_key}` drops {label} {sorted(dropped)} that the published agent uses "
                f"(bound now: {sorted(bound)})"
            )
    flow = body.get("ai_instruction_flow")
    for state in flow if isinstance(flow, list) else []:
        guidelines = state.get("guidelines") if isinstance(state, dict) else None
        if not isinstance(guidelines, dict):
            continue
        for flow_key, body_key in FLOW_TOOL_KEYS:
            if body_key == "phone_tools" and is_text:
                continue
            missing = _ids(guidelines.get(flow_key)) - _ids(body.get(body_key))
            if missing:
                problems.append(
                    f"flow state {state.get('id')!r} uses {flow_key} {sorted(missing)} "
                    f"that are not in `{body_key}`, so the state cannot call them"
                )
    return problems


def request(
    method: str,
    path: str,
    body: Any = None,
    *,
    confirm: bool = False,
    query: str = "",
    allow_tool_drop: bool = False,
) -> ApiResponse:
    method = method.upper()
    if not path.startswith("/") or "?" in path:
        raise ClientError("path must be an absolute API path without a query string")
    if not _is_allowed(method, path):
        raise ClientError(f"route is not available through this skill: {method} {path}")
    if _is_mutation(method, path) and not confirm:
        raise ClientError("mutation requires explicit confirmation (--confirm)")

    revision = REVISION_CREATE.fullmatch(path) if method == "POST" else None
    if revision and not allow_tool_drop:
        slug = revision.group(1)
        current = request("GET", f"/client/agents/{slug}").body
        problems = check_revision_tools(slug, body, current)
        if problems:
            raise ClientError(
                "refusing to create a revision that would unbind tools:\n  - "
                + "\n  - ".join(problems)
                + "\nPass --allow-tool-drop only when removing these tools is the intended change."
            )

    key = _read_key()
    url = f"{_base_url()}{path}{query}"
    data = None
    # HTTP header names are case-insensitive; the gateway accepts either
    # spelling. User-Agent is required -- Cloudflare rejects requests without
    # one with a 403 error-1010 before they reach the API.
    headers = {
        "X-Api-Key": key,
        "Accept": "application/json",
        "User-Agent": f"ingfah-skill/{__version__}",
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
    if _is_text(content_type):
        return raw.decode("utf-8", errors="replace")
    # Audio and other binary downloads stay as bytes; decoding them as text
    # would corrupt the file.
    return raw


def _is_text(content_type: str) -> bool:
    media_type = content_type.split(";")[0].strip().lower()
    return media_type.startswith("text/") or media_type in {"application/csv", "application/xml"}


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


def _save_body(body: Any, path: str) -> int:
    if isinstance(body, (dict, list)):
        data = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
    elif isinstance(body, bytes):
        data = body
    else:
        data = str(body).encode("utf-8")
    try:
        with open(path, "xb") as handle:
            handle.write(data)
    except OSError as error:
        raise ClientError(f"could not write output file: {error.strerror}") from None
    return len(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call an allowlisted Ingfah client API route")
    parser.add_argument("method", choices=("GET", "POST", "PUT", "PATCH", "DELETE"))
    parser.add_argument("path")
    parser.add_argument("--query", default="", help="URL-encoded query string, including the leading ?")
    parser.add_argument("--json", dest="json_body", help="JSON request body, inline or a path to a .json file")
    parser.add_argument("--confirm", action="store_true", help="confirm a state-changing request")
    parser.add_argument("--output", help="save the response body to this new file instead of printing it")
    parser.add_argument(
        "--allow-tool-drop",
        action="store_true",
        help="allow a new revision to unbind tools the published agent uses (only when that is the intended change)",
    )
    args = parser.parse_args(argv)

    try:
        if args.output and os.path.exists(args.output):
            raise ClientError(f"output file already exists: {args.output}")
        body = _load_json_body(args.json_body) if args.json_body else None
        response = request(
            args.method,
            args.path,
            body,
            confirm=args.confirm,
            query=args.query,
            allow_tool_drop=args.allow_tool_drop,
        )
        if args.output:
            size = _save_body(response.body, args.output)
            print(f"saved {size} bytes ({response.content_type}) to {args.output}")
        elif isinstance(response.body, (dict, list)):
            print(json.dumps(response.body, ensure_ascii=False, indent=2))
        elif isinstance(response.body, bytes):
            raise ClientError(
                f"binary response ({response.content_type}, {len(response.body)} bytes); "
                "pass --output PATH to save it"
            )
        else:
            print(response.body, end="")
        return 0
    except ClientError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
