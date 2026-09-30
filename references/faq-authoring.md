# Writing FAQ files for the knowledge base (คลังความรู้)

Use this when the user asks for an FAQ, a knowledge file, or help turning an
existing FAQ, manual, or spreadsheet into something an AI Agent can search.
No API key is needed: the output is a local `.md` file that the user uploads
in the dashboard.

The public guide pages this is built on hold the full examples. Read them
when you need more than this summary:

- `user-guide/guides/knowledge-base/writing-faq-documents.md` — the format and every technique, with ❌ / ✅ pairs
- `user-guide/guides/knowledge-base/maintain-documents.md` — converting source documents, conflicts, updates
- `user-guide/guides/knowledge-base/test-and-improve.md` — the test loop and fixes
- `user-guide/guides/knowledge-base/prompting.md` — the prompt that makes the agent search

## How the knowledge base reads a file

Every rule below follows from this, so explain it to the user when a rule
seems odd.

1. The file is read as plain text. Blank lines are dropped, and **spaces
   between two Thai letters are removed**, so Thai phrasings separated only
   by spaces merge into one run of text. Separate phrasings with ` / ` or `, `.
2. The text is split at every line end and sentence end (`.` `?` `!`), then
   packed into chunks of about 500 tokens with **no overlap**. For Thai that
   is roughly 450 to 550 characters. Chunk boundaries ignore headings: one
   chunk often holds the end of one entry and the start of the next, and a
   question heading can land in one chunk while its answer lands in the next.
3. When the agent searches, only the few closest chunks come back. The agent
   never sees the rest of the file, so it cannot follow "see above".

Hence the one test for every line: **if this chunk were read alone, could the
agent still answer the customer?**

## Workflow

### 1. Collect before writing

Ask for whatever is missing rather than inventing it:

- the source material — an existing FAQ, product sheet, policy, price list,
  or chat and call transcripts
- whether the agent is **voice** or **text** (voice changes how numbers,
  ranges, and URLs are written)
- which agent will use it, and what it should hand to a human instead
- the words customers actually use. The best source is real conversations:
  with the user's API key, list recent calls or chats
  (`GET /client/chat-sessions`), read a few conversations
  (`GET /client/chat-sessions/{uuid}`), and lift the customers' own phrasings
  for headings and variant lines. Take the wording only — never copy names,
  numbers, or other personal details into the file.

### 2. Plan the entries

List every distinct question the source answers, one entry per question.
Merge duplicates, split entries that answer two things, and group entries
under `## หมวด` headings for human readers only — category headings do not
help search. Write facts only; wording, greetings, and hand-off behaviour
belong in the agent's prompt.

### 3. Write each entry with this template

```
### Q: <customer phrasing> / <another phrasing> / <another phrasing>

**คำถามที่เข้าข่ายหัวข้อนี้:** <phrasing>, <phrasing>, <phrasing>

<question restated in the customer's words>: <the key answer in one sentence>

<details: short lines, each saying what it is about>

---
```

The variant line is optional; add it when an entry loses to a similar one in
testing or customers use words the heading lacks. Aim for 5 to 10 phrasings.

### 4. Apply the rules

- **One question per entry, and every entry complete on its own.** Repeating
  the same fact in several entries is correct, not redundant.
- **Headings in the customer's words**, several phrasings joined with ` / `,
  one topic per heading. `### Q: สถานะสินเชื่อ` is a label; `### Q: ผลการสมัครสินเชื่อ / อยากรู้ผลสมัคร / ผลอนุมัติออกหรือยัง` is how people ask.
- **First answer line = restated question + key answer**, one sentence, using
  only facts already in the entry, in the words customers use (ไลน์ beside
  LINE, หมื่นบาท beside 10,000 บาท). This is the single most effective
  technique: whichever chunk holds this line knows what it answers. Mark a
  must-say answer with `**คำตอบหลัก (ต้องแจ้งเสมอ): ...**`.
- **Keep entries short.** An entry over about 500 tokens cannot fit one chunk,
  and one over about 700 characters usually holds two questions. For a truly
  long answer, write a short main entry ending in `[มีรายละเอียดเพิ่ม]` and
  separate `### Q: [รายละเอียด] ...` entries whose headings name the specific
  case, never the broad question.
- **Every detail line names its subject.** A lead-in such as
  `ช่องทางติดต่อ:` followed by a numbered list can end one chunk while the
  list starts the next, leaving `1. โทร 02-000-0000` with no subject. Write
  `ช่องทางติดต่อเจ้าหน้าที่ทางโทรศัพท์: โทร 02-000-0000 ...` instead.
- **No tables.** Write one self-describing line per row:
  `เบี้ยประกันตัวอย่าง ผู้กู้อายุ 20 ถึง 40 ปี: ร้อยละ 1.2 ของวงเงินต่อปี`.
- **Numbered lists** for channels and steps; **bold** for prohibitions that
  must not be dropped (`**จะไม่สามารถเปลี่ยนผู้ค้ำประกันได้**`).
- **Write numbers as spoken** for voice agents: `61 ถึง 65 ปี`, not `61-65 ปี`;
  `08:00 ถึง 20:00 น.` Phone numbers keep their hyphens. Spell out websites
  (`www ดอท example ดอท co ดอท th`) or set pronunciation in the prompt.
- **Tag fixed values** the agent must not round, recompute, or paraphrase:
  `[ตัวเลขคงที่]`, `[ระยะเวลาคงที่]`, `[เบอร์และเวลาทำการคงที่]`.
- **Separate look-alike topics in both entries**: "กรณีนี้ต่างจากกรณี ... ห้ามสับสนกัน",
  or a short note in parentheses at the end of the variant line.
- **Facts to convey** for reassurance topics: list the facts under
  `ข้อเท็จจริงที่ต้องสื่อ (เรียบเรียงคำพูดเองอย่างเป็นธรรมชาติ ห้ามท่องเป็นสคริปต์ตายตัว):`
  instead of a fixed script.
- **Say when a human must handle it**, as a fact in the entry. How to
  transfer goes in the prompt, once.

### 5. Keep out of the file

Everything in the file is searchable and may be spoken to a customer:

- author notes, TODOs, HTML comments, revision history, template instructions
- "see above", "ดูในเอกสารอีกฉบับ", or any pointer to another entry
- conversation filler such as "หากต้องการรายละเอียดเพิ่มเติม สอบถามได้เลยนะคะ",
  which the agent will repeat every time the entry is found
- placeholders such as `XXXX` or `[เบอร์]`. If a value is not confirmed, write
  `ยังไม่ประกาศ` with an alternative for the customer, and tell the user to
  make the prompt say so rather than guess
- products or offers not confirmed as live — the agent will offer them at once

**Never choose silently between conflicting values, and never include both.**
Put conflicts and unconfirmed items in a separate notes file that is not
uploaded, name who must confirm each one, and ask the user.

### 6. Check the draft

Run the checker from the skill directory and fix every error and warning:

```bash
python3 scripts/faq_lint.py faq.md
python3 scripts/faq_lint.py faq.md --chunks     # where each chunk starts and ends
```

It flags tables, author notes, placeholders, hyphenated ranges, pointers to
other entries, filler, missing restatement lines, over-long entries,
unclosed entries, duplicate phrasings, and — from a simulation of the chunk
split — answer lines likely to land in a chunk without their question or
restatement line. Fix those by shortening or splitting the entry, or by
naming the subject in the stranded lines. The split is estimated; treat a
flag as "check this" and confirm in the dashboard's search test.

### 7. Deliver

Give the user:

1. the FAQ file, saved as UTF-8 `.md` (or `.txt`) — the recommended formats;
   a multi-column `.pdf` or one full of tables can be read out of order
2. the notes file of conflicts and unconfirmed values, if any
3. a test list: for each entry, two or three customer phrasings to search with

Then point to the dashboard steps, which have no client API route:

1. **คลังความรู้ → อัปโหลด**, and wait for **พร้อมใช้งาน**.
2. **ทดสอบการค้นหา** with each phrasing in the test list. A pass means the
   **answer text**, not just the heading, is in the top result.
3. Attach it: the agent → **แก้ไขแบบร่าง** → คลังความรู้ icon → select the file
   → **บันทึกแบบร่าง**. Never leave the old and new versions attached together.
4. Make the prompt tell the agent when to search and to search again on every
   question — see "Knowledge base prompts" in `prompt-authoring.md`.
5. Test with **ทดลอง → ตั้งค่าและทดลอง**, two or three times, before publishing.

Fix 4 to 6 entries at a time and retest the whole file: any edit moves chunk
boundaries and can change results for other entries.

## Updating an existing FAQ

When a new source version arrives, re-apply the tuning — restatement lines,
variant lines, `[คงที่]` tags — rather than converting the new source
directly, which silently drops it. Compare with the version in use:

```bash
python3 scripts/faq_lint.py faq-v2.md --compare faq-v1.md
```

A count that drops sharply means tuning was lost, not that the file got
tighter.
