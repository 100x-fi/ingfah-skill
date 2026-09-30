# Phone tools and plugin functions

These are the tools an agent may call. Read them before editing an agent whose
`phone_tools` or plugin functions are changing.

**A tool is callable only while it is bound to the published revision.** Every
new revision must re-send the ids (`phone_tools`, `ai_plugin_function_ids`),
and the revision read does not return them. See
`references/agents-and-teams.md` → "Carry the tools into every revision". A
tool that exists but is not bound gives no error anywhere. The agent just
cannot call it, and it may say the tool's name out loud instead.

- `GET /client/phone-tools` lists the on-call tools an audio agent may use —
  transfer to a human, send DTMF, hang up — the platform's global ones plus the
  client's own. Their ids go in an agent's or revision's `phone_tools`.
  Supports `page`, `per_page` (max 100), `search`, and `ids` (comma-separated).
- `GET /client/plugin-function-integrations` is the catalog a plugin function
  is built from: each integration, its methods, and the integration parameters
  it takes. Read it before creating a function so `integration` and
  `integration_parameters` use real keys.
- `GET /client/plugin-functions` supports `page`, `per_page` (max 100),
  `search`, `integrations`, `exclude_integrations`, `methods`, `id`,
  `include_global`, `sort_by`, and `sort_direction`. Repeat a parameter to pass
  several values.

## Built-in tools worth offering

Before writing a custom tool, check whether a built-in one already does it.
The dashboard shows these under **Tools ทั่วไป** and **Tools เกี่ยวกับการโทร**:

| Tool | Does |
|---|---|
| `resolve_date` | turns spoken dates — พรุ่งนี้, วันพุธหน้า, อีกสองวัน — into a calendar date |
| `validate_id_card` | checks a Thai ID number's format and check digit |
| `calculate_product_cart` | totals items × price × quantity |
| `calculate_remaining` | subtracts one value from another, e.g. amount owed minus amount paid |
| `end_call_keyword` | hangs up when a recognised closing phrase is spoken |
| `collect_id_card` | collects a 13-digit ID from the keypad instead of by voice |

Models get relative dates and weekdays wrong, confidently. Any agent that
takes a date from the customer — a payment promise, a callback, a booking —
should have `resolve_date` enabled, and its prompt should call it every time
the customer names a relative day.

### What `resolve_date` understands and returns

It takes `date_text` (the customer's words) and an optional `calendar`
(`be` or `ce`), and works in Asia/Bangkok time. Checked against the platform
source on 2026-09-30:

- **It understands:** explicit dates in either order with any month spelling
  (`15 กรกฎาคม 2569`, `1 กุมภา 36`, `ส.ค.`, `เดือนธันวาคม วันที่ 5`); relative days
  (`วันนี้`, `พรุ่งนี้`, `มะรืน`, `เมื่อวาน`, `เมื่อวานซืน`) and chains of them
  (`มะรืนของเมื่อวาน`); weeks (`สัปดาห์หน้า`, `วันจันทร์สัปดาห์หน้า`, `อาทิตย์หน้า`);
  months (`เดือนหน้า`, `วันที่ 15 เดือนหน้า`, `สิ้นเดือน`, `ต้นเดือนกรกฎาคม`); counts
  (`อีก 3 วัน`, `อีก 2 สัปดาห์`, `อีก 3 เดือน`, `3 เดือนก่อน`); a bare `วันที่ 15`; and
  weekdays (`พุธหน้า`, `จันทร์นี้`, `วันเสาร์`). Anything else returns `invalid`,
  so the prompt still needs an "if the tool cannot read it, ask the customer
  for the date again" branch.
- **It returns** `resolved_date` (Gregorian), `resolved_date_be`,
  `thai_readback`, `days_from_today`, `is_business_day`, `needs_confirmation`,
  and `alternate_date` / `alternate_date_be` / `alternate_thai_readback`.
- **`thai_readback` is the line to speak**, and it already contains the weekday
  and พ.ศ. (`วันพุธที่ 30 กันยายน พ.ศ. 2569`). Tell the agent to say it as
  returned rather than compose its own date.
- **`needs_confirmation` means two different things:**
  - with `alternate_date` set, the phrase is genuinely ambiguous — a bare
    `วันเสาร์` is this Saturday or the next — so the agent asks the customer to
    choose between the two readbacks;
  - with `alternate_date` null, the tool filled in a month or year itself
    (`วันที่ 15`, `15 มีนาคม`), so the agent just reads the date back for the
    customer to confirm.
- **Past dates are returned as past.** `เมื่อวาน`, `3 เดือนก่อน`, and `พฤหัสนี้`
  said on a Friday all name days that have gone. A date with no year that has
  passed this year rolls forward to next year and is flagged. When a past date
  is not acceptable (a payment promise, a booking), make the prompt check
  `days_from_today` and ask again when it is negative, or beyond the allowed
  window.
- **`is_business_day` only checks for Saturday and Sunday.** It knows no
  public holidays; do not tell a customer a holiday is a working day on its
  strength.
- **It works in whole days only.** Whether a time today has already passed is
  a prompt-side comparison with `{{hour}}`.

**Write the instruction as an ordered sequence whose first step is the tool
call**, and the spoken date only its output: "1. เรียก resolve_date ด้วยคำพูดของ
ลูกค้า 2. อ่าน thai_readback ตามที่ได้ 3. ถามยืนยัน". An instruction that says "state
the date" with the tool as a side note gets the date stated without the tool.
Do not put a concrete invented date in a ❌ example either; the agent repeats
it. Describe the mistake instead.

### A tool's description is part of every prompt

The `description` of every bound tool is sent with every turn, not only when
the tool might fire. Keep it consistent with the prompt. If the prompt says
"transfer silently" while the tool description says "say one sentence first",
the model gets two contradicting instructions, and the one it follows varies
from call to call. Put *when* to call the tool in the description, and do not
restate other prompt rules there "for safety": one extra line in a transfer
tool's description has been measured nudging unrelated turns toward transferring.

When a prompt rule does not stop a behaviour, remove the capability instead:
for example, take the transfer tool off an agent that must not transfer out of
hours, rather than adding another prohibition.

## Writing a plugin function

`POST /client/plugin-functions` requires `signature`, `description`, and
`integration`. `signature` is the function name the agent calls and must be
unique within the client — a duplicate returns `409`. It may use only
`a-z`, `A-Z`, `0-9`, and `_`; name it for what it does, such as
`get_outstanding_balance`, because the agent picks tools partly by name.
`description` is what the agent is told the tool does and when to use it, at
most 1000 characters.

- `parameters` are the arguments the agent supplies from the conversation; each
  needs `name` and `type`, plus `description` and `required`. A name must start
  with a letter and use only `a-z`, `A-Z`, `0-9`, and `_`. Types are
  `string`, `number`, `boolean`, `object`, and `array`.
- `integration_parameters` are the integration's own settings as `{key, value}`
  pairs. For `http`, `method`, `base_url`, and `url` are required, and `value`
  may carry `{{name}}` placeholders filled from `parameters`. `base_url` must
  not resolve to a private, loopback, or link-local address.
- `method` comes from the integrations catalog; omit it for `http`.
- `async_enabled` lets the agent keep talking while a slow tool runs, and then
  `async_params.initial_update_message` is required.

```json
{
  "signature": "lookup_order",
  "description": "Look an order up by its number",
  "integration": "http",
  "parameters": [
    {"name": "order_id", "type": "string", "description": "The order number the customer gives", "required": true}
  ],
  "integration_parameters": [
    {"key": "method", "value": "GET"},
    {"key": "base_url", "value": "https://example.com/api"},
    {"key": "url", "value": "/orders/{{order_id}}"}
  ]
}
```

- `PUT /client/plugin-functions/{id}` **replaces the whole tool**. Read it
  first and send every parameter and integration parameter again, carrying the
  `id` of each stored parameter that stays — otherwise a rename is taken for a
  delete plus an add. A global tool cannot be updated by a client (`403`).
  An edit changes every agent using the tool at once; name those agents in the
  preview before confirming.
- `POST /client/plugin-functions/{id}/duplicate` takes a new unique
  `signature` and copies the tool, integration parameters included. The copy is
  attached to no agent.
- `POST /client/plugin-functions/{id}/test-run` takes `parameters` keyed by
  name and **really runs the tool** — an `http` tool sends its request against
  the live target. Confirm with the user before running one. A failed run is
  still `200` with status `invalid` or `error`, so read the status rather than
  the HTTP code. It is limited to 10 runs per admin per minute (`429`), shared
  with that admin's dashboard runs and other keys.
- `DELETE /client/plugin-functions/{id}` is refused with `409` while any agent
  uses the tool, in its published version or its draft; the response lists
  those agents. Report them instead of retrying.
