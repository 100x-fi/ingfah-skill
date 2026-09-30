#!/usr/bin/env python3
"""Copy the Thai Ingfah user guide (คู่มือ) into references/user-guide/.

The source is the public docs site repository (Astro + Starlight). Run this
after the docs change, then commit the result:

    python3 scripts/sync_user_guide.py --source ../ingfah-public-docs

Each page is rewritten as plain Markdown: the title becomes the H1, the
description and public URL follow it, and screenshots are dropped because the
images are not copied. An INDEX.md listing every page in sidebar order is
regenerated alongside.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SITE_URL = "https://docs.ingfah.ai"
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = SKILL_ROOT / "references" / "user-guide"

# Top-level sections in the order the site's sidebar shows them.
SECTIONS = [
    ("overview", "ภาพรวม (Overview)"),
    ("services", "บริการ (Services)"),
    ("direction", "แผนงานและมาตรฐาน (Plans & Standards)"),
    ("onboarding", "สำหรับลูกค้าใหม่ (Client Onboarding)"),
    ("telephony", "การเชื่อมต่อโทรศัพท์ (Telephony Integration)"),
    ("guides", "แนะนำการใช้งาน (Guides — using the dashboard)"),
    ("release-notes", "บันทึกการอัปเดต (Release Notes)"),
]

IMAGE_LINE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
SIDEBAR_LINK = re.compile(r'link:\s*"([^"]+)"')


@dataclass
class Page:
    slug: str  # e.g. "guides/knowledge-base/overview"
    title: str
    description: str
    order: int | None
    body: str

    @property
    def url(self) -> str:
        return f"{SITE_URL}/{self.slug}/"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            value = value.strip()
            if value in (">-", ">", "|", "|-"):
                folded = []
                i += 1
                while i < len(lines) and lines[i].startswith(" "):
                    folded.append(lines[i].strip())
                    i += 1
                fields[key.strip()] = " ".join(folded)
                continue
            fields[key.strip()] = value.strip("\"'")
        elif line.strip().startswith("order:"):
            fields["order"] = line.split(":", 1)[1].strip()
        i += 1
    return fields, text[match.end():]


def clean_body(body: str) -> str:
    lines = [line for line in body.splitlines() if not IMAGE_LINE.match(line)]
    text = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", text) + "\n"


def load_pages(docs_dir: Path) -> list[Page]:
    pages = []
    for path in sorted(docs_dir.rglob("*.md")):
        rel = path.relative_to(docs_dir)
        if rel.parts[0] == "en":
            continue
        fields, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        slug = rel.with_suffix("").as_posix()
        if slug.endswith("/index"):
            slug = slug[: -len("/index")]
        order = fields.get("order")
        pages.append(
            Page(
                slug=slug,
                title=fields.get("title", slug),
                description=fields.get("description", ""),
                order=int(order) if order and order.isdigit() else None,
                body=clean_body(body),
            )
        )
    return pages


def render_page(page: Page) -> str:
    header = [f"# {page.title}", ""]
    if page.description:
        header.append(f"> {page.description}")
        header.append(">")
    header.append(f"> Source: {page.url}")
    return "\n".join(header) + "\n\n" + page.body


def sort_pages(pages: list[Page], sidebar_links: list[str]) -> list[Page]:
    position = {link.strip("/"): i for i, link in enumerate(sidebar_links)}
    section_rank = {name: i for i, (name, _) in enumerate(SECTIONS)}

    def key(page: Page):
        section = page.slug.split("/")[0]
        return (
            section_rank.get(section, len(SECTIONS)),
            position.get(page.slug, len(position)),
            page.order if page.order is not None else 999,
            page.slug,
        )

    return sorted(pages, key=key)


def source_version(source: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(source), "log", "-1", "--format=%h (%cs)"],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def render_index(pages: list[Page], version: str | None = None) -> str:
    out = [
        "# Ingfah user guide (คู่มือของอิงฟ้า) — index",
        "",
        f"A copy of the public Thai user guide at {SITE_URL}, one file per page.",
        "Do not edit these files by hand; regenerate them with",
        "`python3 scripts/sync_user_guide.py`.",
    ]
    if version:
        out.append(f"Copied from docs commit {version}.")
    out += [
        "",
        "A link inside a page such as `/guides/ai-agent/try-call` is the file",
        "`guides/ai-agent/try-call.md` in this folder, and the public page",
        f"`{SITE_URL}/guides/ai-agent/try-call/`. Screenshots are not copied.",
        "",
    ]
    current = None
    labels = dict(SECTIONS)
    for page in pages:
        section = page.slug.split("/")[0]
        if section != current:
            if current is not None:
                out.append("")
            current = section
            out += [f"## {labels.get(section, section)}", ""]
        entry = f"- `{page.slug}.md` — **{page.title}**"
        if page.description:
            entry += f": {page.description}"
        out.append(entry)
    return "\n".join(out) + "\n"


def sync(source: Path, dest: Path) -> list[Page]:
    docs_dir = source / "src" / "content" / "docs"
    if not docs_dir.is_dir():
        raise SystemExit(f"not a docs repository: {docs_dir} does not exist")
    config = source / "astro.config.mjs"
    sidebar_links = SIDEBAR_LINK.findall(config.read_text(encoding="utf-8")) if config.exists() else []

    pages = sort_pages(load_pages(docs_dir), sidebar_links)
    if dest.exists():
        shutil.rmtree(dest)
    for page in pages:
        target = dest / f"{page.slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(page), encoding="utf-8")
    (dest / "INDEX.md").write_text(render_index(pages, source_version(source)), encoding="utf-8")
    return pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source",
        type=Path,
        default=SKILL_ROOT.parent / "ingfah-public-docs",
        help="path to the ingfah-public-docs repository (default: a sibling checkout)",
    )
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    pages = sync(args.source.resolve(), args.dest.resolve())
    print(f"wrote {len(pages)} pages and INDEX.md to {args.dest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
