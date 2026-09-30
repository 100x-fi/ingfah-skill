# Disposition outcomes and outcome metadata

Both are postprocessors: steps that run after a call to label or extract from
the transcript. A product's session config holds at most one postprocessor of
each type (`disposition`, `summary`, `assessment`, `outcome_metadata`).
Creating a second of the same type returns `409`.

## What each type does, as the user sees it

| `type` | Dashboard name | What it writes | Where the user sees it |
|---|---|---|---|
| `summary` | สรุปบทสนทนา (อัตโนมัติ) | the call's **title** and its **summary**, from one model call | หัวข้อสนทนา column on สายทั้งหมด / สายเข้า / สายออก; Conversation Summary on the call detail; `title` column in CSV exports |
| `disposition` | ผลลัพธ์แบบสถานะ | one outcome label per call | ผลลัพธ์ column, dashboard charts, the batch record status |
| `outcome_metadata` | ผลลัพธ์แบบ metadata (JSON) | structured fields extracted from the call | Metadata column (JSON); `outcome_metadata.<key>` CSV columns |
| `assessment` | — | a score of the agent's performance | not shown on the main call lists |

How the instruction is used: each type has a built-in default prompt, and the
postprocessor's `instruction` is appended under it as an "Additional
Instruction". So `instruction` is where business context goes. The default
prompt knows nothing about the client's business, product names, jargon, or
branches.

**A team with no `summary` postprocessor still gets titles and summaries**,
from a global default summarizer that has no business context. This is the
usual cause of complaints like "the summary is wrong", "it thinks we are a
laundry" or "the title never says the branch". The fix is to add a `summary`
postprocessor to that team with an `instruction` that states what the business
is, what ambiguous words mean there, and what the title and summary must
include. Changing the agent's prompt does not change the summarizer.

```json
{
  "type": "summary",
  "instruction": "ธุรกิจนี้คือ <ชื่อธุรกิจ> <ประเภทธุรกิจ> ไม่ใช่ <สิ่งที่มักถูกเข้าใจผิด> เมื่อลูกค้าพูดถึง \"<คำกำกวม>\" ให้ถือว่าหมายถึง <ความหมายในธุรกิจนี้> ระบุ <ชื่อสาขา / เลขออเดอร์ / สิ่งที่ต้องเห็นในหัวข้อ> ในหัวข้อและสรุปทุกครั้งถ้ามี เขียนหัวข้อและสรุปเป็นภาษาไทย"
}
```

Before proposing one, read the team with `GET /client/products/{id}` to see
which types it already has (at most one per type), and read two or three
recent calls with `GET /client/chat-sessions/{uuid}` so the instruction
fixes what actually went wrong in them.

## Reading and results

- `GET /client/disposition-outcomes` returns the client-wide catalog of
  outcomes (`outcome`, `prompt`, `color`). It is a catalog only; it does not
  say which product uses which outcomes.
- `GET /client/products/{id}` returns that product's `postprocessors` array,
  each with `id`, `type`, `instruction`, `disposition_outcomes`, `json_schema`,
  and `is_enabled`. **This is the only read path** — there is no
  `GET /client/products/{id}/postprocessors`. Always read it before an update,
  because `PUT` replaces the fields it is given.
- Results appear on chat sessions and outbound records as
  `disposition_outcome` (a string) and `outcome_metadata` (a JSON object).
  `GET /client/chat-sessions-list/csv` flattens the latter into
  `outcome_metadata.<key>` columns.

## Writing the instruction

Keep a postprocessor's `instruction` to detection rules applied to the
transcript: the business context, what words mean, what to look for. A
sentence describing what the team lacks ("this team has no transfer, so these
fields are usually false") broke that field and unrelated ones. A ❌/✅ pair in
an instruction has side effects too; test it (`references/testing.md`).

## Writing a postprocessor

`POST /client/products/{id}/postprocessors` takes `type`, `instruction`, and
then whichever field the type requires. `PUT` takes the same body without
`type`.

- `type` must be one of `disposition`, `summary`, `assessment`,
  `outcome_metadata`. It **cannot be changed on update** — sending it to `PUT`
  returns `400 type field is not allowed to be changed`. To change a type,
  delete the postprocessor and create a new one.
- `disposition` requires `disposition_outcomes`, a list of
  `{"outcome", "prompt", "color", "rank"}`. Omitting it returns
  `400 disposition_outcomes is required when type is disposition`. The
  `prompt` tells the model when to pick that outcome, so it is the field that
  decides labelling quality.
- `outcome_metadata` requires `json_schema` shaped
  `{"name": ..., "schema": {...}, "description": ...}` — a wrapper, not a bare
  JSON Schema. A bare schema returns `400 json_schema.name is required`, and a
  wrapper without `schema` returns `400 json_schema.schema is required`.
  `is_enabled` applies to this type only.
- A disposition set needs **at least two** outcomes in the dashboard; design
  it that way.
- An outcome name can carry a value, e.g. `ยืนยัน DD-MM-YYYY` with the prompt
  saying DD-MM-YYYY is the promised date in Buddhist-era years. Calls then
  come back labelled `ยืนยัน 12-04-2569`, which the dashboard can group and
  report on. Use it only when the value itself should be a filterable label;
  otherwise put the value in outcome metadata.
- For `outcome_metadata`, `json_schema.name` allows only `a-z`, `A-Z`, `0-9`,
  and `_`, at most 64 characters. `anyOf`, `oneOf`, `$ref`, and
  `patternProperties` are not supported. With `"strict": true`, every key must
  be listed in `required`. Each key's `description` is what the extractor goes
  by, so say the format: `วันที่ลูกค้ารับปากว่าจะชำระ รูปแบบ YYYY-MM-DD`, not
  `วันที่จ่าย`.
- A postprocessor change applies to **new calls only**; calls that already
  ended are not reprocessed. Tell the user, so they do not look for new labels
  on old calls.

```json
{
  "type": "outcome_metadata",
  "instruction": "Extract the promised payment date and amount.",
  "json_schema": {
    "name": "payment_promise",
    "schema": {
      "type": "object",
      "properties": {
        "promise_date": {"type": "string"},
        "amount": {"type": "number"}
      },
      "required": ["promise_date", "amount"],
      "additionalProperties": false
    }
  }
}
```

Changing a postprocessor changes how every later call on that product is
labelled or extracted, and deleting one stops that labelling entirely. Preview
the change and confirm explicitly before sending, and name the product it
affects. `outcome_metadata` is extracted customer data: treat its values as
personal data and redact them in summaries unless the user asks for them.
