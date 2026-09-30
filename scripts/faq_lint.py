#!/usr/bin/env python3
"""Check an FAQ file for the Ingfah knowledge base (คลังความรู้) before upload.

    python3 scripts/faq_lint.py faq.md                 # rule check
    python3 scripts/faq_lint.py faq.md --chunks        # also show the chunk split
    python3 scripts/faq_lint.py faq.md --compare old.md

The rules are the ones in references/faq-authoring.md. The chunk split is a
simulation of how the knowledge base cuts an uploaded .md or .txt file: blank
lines dropped, spaces between Thai letters removed, text split at line and
sentence ends, then packed into chunks of about 500 tokens with no overlap.
Token counts are estimated, so boundaries are approximate (usually within a
line or two).

Exit status is 1 when an error is found, else 0. Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CHUNK_TOKENS = 500
LONG_ENTRY_CHARS = 700  # the user guide's rule of thumb for "split this entry"

# Knowledge-base ingest (mirrors the server's text clean-up and splitter).
THAI_GAP = re.compile(r"(?<=[฀-๿])[ \t]+(?=[฀-๿])")
SENTENCE_END = re.compile(r"[.?!。？！]+\s*")

HEADING_Q = re.compile(r"^###\s+Q\s*[:：]\s*(.*)$")
HEADING_ANY = re.compile(r"^(#{1,6})\s+(.*)$")
SEPARATOR = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
VARIANTS_LINE = re.compile(r"^\**\s*คำถามที่เข้าข่ายหัวข้อนี้")
KEY_ANSWER = re.compile(r"^\**\s*คำตอบหลัก")
TABLE_ROW = re.compile(r"^\s*\|.*\|")
HYPHEN_RANGE = re.compile(r"(?<![\d\-/.:])(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?[-–]\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)(?![\d\-/])")
TIME_RANGE = re.compile(r"(\d{1,2}[:.]\d{2})\s?[-–]\s?(\d{1,2}[:.]\d{2})")
AUTHOR_NOTE = re.compile(r"<!--|\bTODO\b|\bFIXME\b|\bTBD\b|หมายเหตุ(?:ถึง)?ผู้เขียน|X{3,}", re.IGNORECASE)
PLACEHOLDER = re.compile(r"<(?!/?say-as\b)[^<>\n]{1,60}>")
CROSS_REF = re.compile(r"ด้านบน|ข้างบน|ด้านล่าง|ข้างล่าง|ข้างต้น|ดังกล่าวแล้ว|หัวข้อก่อนหน้า|หัวข้อถัดไป|ดูในเอกสาร|ตามที่กล่าว")
CHAT_FILLER = re.compile(r"สอบถาม(?:เพิ่มเติม)?ได้(?:เลย|ตลอด)|มีอะไรให้ช่วย|ยินดีให้บริการ|หากมีข้อสงสัย|หากต้องการ(?:ข้อมูล|รายละเอียด)เพิ่มเติม")
FIXED_TAG = re.compile(r"\[[^\]\n]*คงที่\]")
DETAIL_ENTRY = re.compile(r"^\s*\[รายละเอียด\]")
MORE_DETAIL = "[มีรายละเอียดเพิ่ม]"
# "<subject>: <fact>" — the line says what it is about. A colon between digits (08:30) does not count.
SELF_DESCRIBING = re.compile(r"^\s*(?:\d+[.)]|[-*•])?\s*[^:\n]{2,80}?(?:(?<!\d):|:(?!\d))")
URL = re.compile(r"https?://|www\.", re.IGNORECASE)


def estimate_tokens(text: str) -> float:
    """Estimate cl100k tokens; fitted on Thai guide pages (mean error ~2%)."""
    total = 0.0
    for ch in text:
        o = ord(ch)
        if 0x0E00 <= o <= 0x0E7F:
            total += 0.97
        elif ch.isspace():
            total += 0.21
        elif o < 128:
            total += 0.21 if ch.isalnum() else 0.5
        else:
            total += 2.0
    return total


def ingest_line(line: str) -> str:
    return THAI_GAP.sub("", re.sub(r"[ \t]+", " ", line).strip())


def split_sentences(line: str) -> list[str]:
    out, last = [], 0
    for m in SENTENCE_END.finditer(line):
        part = line[last:m.end()].strip()
        if part:
            out.append(part)
        last = m.end()
    tail = line[last:].strip()
    if tail:
        out.append(tail)
    return out


@dataclass
class Sentence:
    line: int  # 1-based source line
    text: str
    tokens: float


@dataclass
class Chunk:
    sentences: list[Sentence] = field(default_factory=list)

    @property
    def tokens(self) -> float:
        return sum(s.tokens for s in self.sentences)

    @property
    def lines(self) -> set[int]:
        return {s.line for s in self.sentences}


def simulate_chunks(lines: list[str]) -> list[Chunk]:
    sentences = []
    for number, raw in enumerate(lines, 1):
        clean = ingest_line(raw)
        if not clean:
            continue
        for text in split_sentences(clean):
            tokens = estimate_tokens(text)
            if tokens <= CHUNK_TOKENS:
                sentences.append(Sentence(number, text, tokens))
                continue
            pieces = int(tokens // CHUNK_TOKENS) + 1
            step = -(-len(text) // pieces)
            for i in range(0, len(text), step):
                piece = text[i:i + step]
                sentences.append(Sentence(number, piece, estimate_tokens(piece)))

    chunks: list[Chunk] = []
    current = Chunk()
    for s in sentences:
        if current.sentences and current.tokens + s.tokens > CHUNK_TOKENS:
            chunks.append(current)
            current = Chunk()
        current.sentences.append(s)
    if current.sentences:
        chunks.append(current)
    return chunks


@dataclass
class Entry:
    line: int
    question: str
    body: list[tuple[int, str]] = field(default_factory=list)
    closed: bool = False  # followed by a --- separator

    @property
    def variants(self) -> list[str]:
        return [v.strip() for v in self.question.split("/") if v.strip()]

    @property
    def restatement(self) -> tuple[int, str] | None:
        for number, text in self.body:
            if not VARIANTS_LINE.match(text):
                return number, text
        return None

    @property
    def has_variants_line(self) -> bool:
        return any(VARIANTS_LINE.match(text) for _, text in self.body)

    def text(self) -> str:
        return "\n".join([self.question] + [t for _, t in self.body])


@dataclass
class Finding:
    level: str  # error | warning | note
    line: int
    message: str


def parse(lines: list[str]) -> tuple[list[Entry], list[Finding]]:
    entries: list[Entry] = []
    findings: list[Finding] = []
    current: Entry | None = None
    for number, raw in enumerate(lines, 1):
        text = raw.rstrip()
        q = HEADING_Q.match(text)
        if q:
            current = Entry(number, q.group(1).strip())
            entries.append(current)
            continue
        heading = HEADING_ANY.match(text)
        if heading:
            if len(heading.group(1)) >= 3:
                findings.append(Finding("warning", number, "heading is not in `### Q: <question>` form, so it will not be treated as its own entry"))
            current = None
            continue
        if SEPARATOR.match(text):
            if current is not None:
                current.closed = True
            current = None
            continue
        if not text.strip():
            continue
        if current is None:
            findings.append(Finding("warning", number, "text outside any `### Q:` entry is still searched and may be read to customers; move it into an entry or delete it"))
            continue
        current.body.append((number, text.strip()))
    return entries, findings


def check(lines: list[str]) -> tuple[list[Entry], list[Chunk], list[Finding]]:
    entries, findings = parse(lines)
    if not entries:
        findings.append(Finding("error", 1, "no `### Q:` entries found; every question must start with a `### Q:` heading"))

    in_table = False
    for number, raw in enumerate(lines, 1):
        is_row = bool(TABLE_ROW.match(raw))
        if is_row and not in_table:
            findings.append(Finding("error", number, "table: tables split badly and read aloud poorly; write one self-describing line per row"))
        in_table = is_row
        if AUTHOR_NOTE.search(raw):
            findings.append(Finding("error", number, "author note, TODO, comment or XXX placeholder: everything in the file can be read to customers; keep notes in a separate file"))
        elif PLACEHOLDER.search(raw):
            findings.append(Finding("error", number, f"unfilled placeholder {PLACEHOLDER.search(raw).group(0)}"))
        for m in list(TIME_RANGE.finditer(raw)) + list(HYPHEN_RANGE.finditer(raw)):
            findings.append(Finding("warning", number, f"range `{m.group(0)}`: write `{m.group(1)} ถึง {m.group(2)}` so a voice agent does not read it as separate numbers"))
        if CROSS_REF.search(raw):
            findings.append(Finding("warning", number, f"`{CROSS_REF.search(raw).group(0)}` points elsewhere in the file, but each entry is retrieved alone; repeat the information instead"))
        if CHAT_FILLER.search(raw):
            findings.append(Finding("warning", number, f"`{CHAT_FILLER.search(raw).group(0)}` is conversation filler that will be spoken every time this entry is found; put conversation style in the prompt"))
        if URL.search(raw):
            findings.append(Finding("note", number, "URL: a voice agent reads URLs poorly; spell it out (www ดอท ...) or set pronunciation in the prompt"))

    seen: dict[str, int] = {}
    has_detail_entries = any(DETAIL_ENTRY.match(e.question) for e in entries)
    for i, entry in enumerate(entries):
        if not entry.body:
            findings.append(Finding("error", entry.line, "entry has no answer"))
            continue
        restatement = entry.restatement
        if restatement and not KEY_ANSWER.match(restatement[1]) and ":" not in restatement[1][:120]:
            findings.append(Finding("warning", restatement[0], "first answer line should restate the question, then give the key answer: `<question in the customer's words>: <key answer>`"))
        size = len(entry.text())
        tokens = estimate_tokens(entry.text())
        if tokens > CHUNK_TOKENS:
            findings.append(Finding("warning", entry.line, f"entry is ~{tokens:.0f} tokens ({size} chars), more than one chunk holds; split it into a main entry and `[รายละเอียด]` entries"))
        elif size > LONG_ENTRY_CHARS:
            findings.append(Finding("note", entry.line, f"entry is {size} chars; over ~{LONG_ENTRY_CHARS} usually means two questions in one entry"))
        if len(entry.variants) < 2 and not entry.has_variants_line:
            findings.append(Finding("note", entry.line, "only one phrasing; add the other ways customers ask, separated by ` / `"))
        if not entry.closed and i < len(entries) - 1:
            findings.append(Finding("warning", entry.line, "entry is not closed with a `---` line before the next one"))
        for variant in entry.variants:
            key = re.sub(r"\s+", "", variant.lower())
            if key in seen and seen[key] != entry.line:
                findings.append(Finding("warning", entry.line, f"phrasing `{variant}` also heads the entry at line {seen[key]}; two entries answering one question compete in search"))
            seen.setdefault(key, entry.line)
        if MORE_DETAIL in entry.text() and not has_detail_entries:
            findings.append(Finding("note", entry.line, f"`{MORE_DETAIL}` is used but there is no `### Q: [รายละเอียด] ...` entry"))

    chunks = simulate_chunks(lines)
    for entry in entries:
        anchor_lines = {entry.line}
        if entry.restatement:
            anchor_lines.add(entry.restatement[0])
        body = dict(entry.body)
        body_lines = set(body) - anchor_lines
        for index, chunk in enumerate(chunks, 1):
            touched = chunk.lines & body_lines
            if not touched or chunk.lines & anchor_lines:
                continue
            stranded = sorted(n for n in touched if not SELF_DESCRIBING.match(body[n]))
            if stranded:
                where = f"line {stranded[0]}" if len(stranded) == 1 else f"lines {', '.join(map(str, stranded))}"
                findings.append(Finding("warning", stranded[0], f"{where} likely fall in chunk {index} without this entry's question or restatement line (entry at line {entry.line}), and do not name their subject; a search for the question may not find them. Start each with its subject (`<subject>: <fact>`), or shorten or split the entry"))

    findings.sort(key=lambda f: (f.line, {"error": 0, "warning": 1, "note": 2}[f.level]))
    return entries, chunks, findings


def stats(lines: list[str]) -> dict[str, int]:
    entries, _ = parse(lines)
    text = "\n".join(lines)
    return {
        "entries": len(entries),
        "[รายละเอียด] entries": sum(1 for e in entries if DETAIL_ENTRY.match(e.question)),
        "คำถามที่เข้าข่าย lines": sum(1 for e in entries if e.has_variants_line),
        "[คงที่] tags": len(FIXED_TAG.findall(text)),
        "restatement lines": sum(1 for e in entries if e.restatement and (":" in e.restatement[1][:120] or KEY_ANSWER.match(e.restatement[1]))),
        "chunks (approx.)": len(simulate_chunks(lines)),
    }


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check an Ingfah knowledge-base FAQ file before upload.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--chunks", action="store_true", help="print the simulated chunk split")
    parser.add_argument("--compare", type=Path, metavar="OLD", help="compare tuning counts against a previous version")
    args = parser.parse_args(argv)

    if args.file.suffix.lower() not in (".md", ".txt"):
        print(f"note: {args.file.name} is not .md or .txt; FAQ files work best as .md or .txt", file=sys.stderr)
    lines = read_lines(args.file)
    entries, chunks, findings = check(lines)

    for f in findings:
        print(f"{args.file}:{f.line}: {f.level}: {f.message}")

    if args.chunks:
        entry_at = {}
        for e in entries:
            for n in [e.line] + [n for n, _ in e.body]:
                entry_at[n] = e
        print()
        for index, chunk in enumerate(chunks, 1):
            owners = []
            for s in chunk.sentences:
                e = entry_at.get(s.line)
                if e and e not in owners:
                    owners.append(e)
            first, last = chunk.sentences[0].line, chunk.sentences[-1].line
            print(f"chunk {index}: lines {first}–{last}, ~{chunk.tokens:.0f} tokens")
            for e in owners:
                print(f"    Q (line {e.line}): {e.question[:80]}")

    current = stats(lines)
    print()
    print("  ".join(f"{k}: {v}" for k, v in current.items()))
    if args.compare:
        old = stats(read_lines(args.compare))
        print(f"compared with {args.compare}:")
        for key, value in current.items():
            before = old[key]
            flag = ""
            if key != "chunks (approx.)" and before and value < before * 0.8:
                flag = "  <- dropped; tuning may have been lost in the update"
            print(f"  {key}: {before} -> {value}{flag}")

    errors = sum(1 for f in findings if f.level == "error")
    warnings = sum(1 for f in findings if f.level == "warning")
    print(f"{errors} error(s), {warnings} warning(s), {len(findings) - errors - warnings} note(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
