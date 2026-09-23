---
name: ingfah-skill
description: Interact with the Ingfah client platform through client API-key authenticated APIs. Use this skill when the user asks to inspect or manage Ingfah products, AI agents, chat sessions, tools, or outbound batches — including when they use the dashboard's own words in English or Thai, such as AI Agent Team / ทีม AI Agent, batch / Batch โทรออก, calls / สายทั้งหมด, chats / แชท, templates / เทมเพลตข้อมูลลูกค้า, tools / Tool, or post-call results / ผลลัพธ์หลังวางสาย. Do not use backoffice APIs or JWT-only client APIs.
---

# Ingfah client API

Use the user's Ingfah client API key to call only the client API routes listed below.

The default Ingfah API base URL is `https://api.ingfah.ai`. Use another base URL only when the user explicitly provides one.

Two reference files carry the detail for authoring work:

- `references/prompt-authoring.md` — how to write an agent's identity, task,
  and conversation flow, how customer context works, and the rules every voice
  prompt needs. **Read it before writing or editing any agent prompt** — a
  prompt that bakes per-call data into its body is incorrect, not merely
  suboptimal.
- `references/outcome-design.md` — how to design disposition outcomes and an
  outcome metadata schema that agree with each other. Read it before creating
  or editing a postprocessor.

Use `scripts/ingfah_api.py` for every request. It is dependency-free and enforces the route allowlist and the mutation confirmation rule. Do not substitute `curl`, `requests`, or an ad-hoc script, even if asked to for speed: doing so bypasses both guardrails, and requests without the script's `User-Agent` header are rejected by Cloudflare with a 403 error-1010.

## Naming: what the user calls things

The API's names and the dashboard's names differ, and most users speak in
dashboard words — often Thai. Translate their words to the API entity below,
and **answer in their words**, not the API's: say "ทีม AI Agent" or "AI Agent
Team", not "product". When a term is ambiguous, name both ("the AI Agent Team
— `product` in the API") once, then stay in their language.

| API entity | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `product` | AI Agent Team | ทีม AI Agent |
| agent | AI Agent | AI Agent |
| revision (unpublished) | Draft / Has Draft | แบบร่าง / มีแบบร่าง |
| revision (published) | Published / Currently Published | เผยแพร่ / เผยแพร่อยู่ |
| publish a revision | Publish | เผยแพร่ |
| chat session (voice) | Call — All Calls | สาย — สายทั้งหมด |
| chat session (text) | Chat — Chats | แชท |
| transcript / messages | Conversation | การสนทนา |
| outbound batch | Batch — Batch Listing | Batch — รายการ Batch |
| outbound option | Template — Manage Templates | เทมเพลตข้อมูลลูกค้า — จัดการเทมเพลต |
| plugin function | Tool | Tool |
| phone tool | Tool (Calling category) | Tool (หมวดการโทร) |
| `direction: inbound` | Inbound | สายเข้า / รับสาย |
| `direction: outbound` | Outbound | สายออก / โทรออก |
| `channel_type: audio` | Voice | เสียง |
| `channel_type: text` | Text | ข้อความ |
| `visibility` | Private / Public | ส่วนตัว / สาธารณะ |
| `starting_agent_id` | Start (starting agent) | จุดเริ่มต้น |
| SIP number | Phone Numbers | เบอร์โทรศัพท์ |
| knowledge base | Knowledge | คลังความรู้ |
| API key | API Keys | จัดการ API Keys |

### Postprocessors

The dashboard does not use the word "postprocessor". All four live under
**Set post-call results / ตั้งค่าผลลัพธ์หลังวางสาย** on the team page.

| API | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `type: disposition` | Disposition Outcome / Conversation Outcome | ผลลัพธ์แบบสถานะ / ผลลัพธ์หลังจบการสนทนา |
| `disposition_outcomes[].outcome` | Outcome name | ชื่อผลลัพธ์ |
| `disposition_outcomes[].prompt` | Outcome classification criteria | เกณฑ์การจำแนกผลลัพธ์ |
| `type: outcome_metadata` | Outcome Metadata (JSON) | ผลลัพธ์แบบ metadata (JSON) |
| `json_schema.name` | Schema name / the data set | ชื่อชุดข้อมูล |
| `instruction` | Instruction | คำสั่ง |
| `is_enabled` | On / Off | เปิด / ปิด |
| `type: summary` | Conversation summary (Auto) | สรุปบทสนทนา (อัตโนมัติ) |
| `disposition_outcome` on a record | Result | ผลลัพธ์ |
| `outcome_metadata` on a record | Metadata | Metadata |

### Agent prompt fields

| API field | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `name` | AI Agent Name — what it calls itself on the call | ชื่อ AI Agent |
| `vocal_name` | Agent vocal name — what staff and other agents call it | Agent vocal name |
| `greeting_message` | Initial Greeting Message | ข้อความทักทายเริ่มต้น |
| `ai_instruction_identity` | Identity | ตัวตน |
| `ai_instruction_task` | Task | เป้าหมาย/หน้าที่ |
| `ai_instruction_flow` | Agent Flow | Agent Flow |
| `voice_id` | Voice | เสียง |

### Tool fields

| API field | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `signature` | Signature | Signature |
| `description` | Description for AI Agent | คำอธิบายสำหรับ AI Agent |
| `parameters` | Function Parameters | Function Parameters |
| `integration` | Integration Type | ประเภท Integration |
| `integration_parameters` | Integration Parameters | Integration Parameters |

### Batch and record status words

Batch tabs: In Progress / กำลังดำเนินการ, Paused / หยุดชั่วคราว,
Scheduled / รอดำเนินการ, Completed / สิ้นสุด.

Record statuses: Called / โทรแล้ว, Pending / รอโทร, Calling / กำลังสนทนา,
Missed / ไม่รับสาย, Busy / สายไม่ว่าง, Case Not Closed / ปิดเคสไม่ได้,
Error / ผิดพลาด, Do Not Contact / ไม่ติดต่อ.

## Authentication

- Send the key only in the `X-Api-Key` request header.
- If no key is available, ask the user to provide their Ingfah client API key.
- Never echo, log, save, commit, or include the key in generated files, URLs, or error messages.
- Do not ask the user to put the key in this repository.
- Treat the key as available only for the current task unless the user explicitly requests persistent configuration.
- Use HTTPS and the configured Ingfah API base URL.
- Before making a request, explain when the requested operation requires a write scope.
- Ask for explicit confirmation immediately before creating, deleting, pausing, resuming, or cancelling anything.
- Redact secrets from all displayed request and response details.

The script reads `INGFAH_API_KEY` from the process environment. When the user provides a key conversationally, pass it to the script only for the current process; never write it to a file or include it in a command shown to the user.

Examples:

```bash
python3 scripts/ingfah_api.py GET /client/products
python3 scripts/ingfah_api.py GET /client/outbound/batches/7/records --query '?per_page=20&status=called'
python3 scripts/ingfah_api.py --confirm POST /client/outbound/batches --json request.json
python3 scripts/ingfah_api.py --confirm POST /client/outbound/batches/7/pause
```

`--json` accepts either a path to a JSON file or an inline JSON document. Run the script from the skill directory, or give its absolute path.

## Client API-key scopes and routes

### `client_products:read`

- `GET /client/ai-agent-teams`
- `GET /client/disposition-outcomes`
- `GET /client/ai-agent-teams/{id}/customer-context-variables`
- `GET /client/products`
- `GET /client/products/{id}`

### `client_products:write`

- `POST /client/products`
- `PUT /client/products/{id}`
- `PUT /client/products/{id}/visibility`
- `DELETE /client/products/{id}`
- `POST /client/products/{id}/postprocessors`
- `PUT /client/products/{id}/postprocessors/{postprocessorId}`
- `DELETE /client/products/{id}/postprocessors/{postprocessorId}`

### `ai_agents:read`

- `GET /client/ai-agents`
- `GET /client/agent-templates`
- `GET /client/agents/{slug}`
- `GET /client/agents/{slug}/revisions`
- `GET /client/agents/{slug}/revisions/{id}`
- `GET /client/phone-tools`
- `GET /client/plugin-functions`
- `GET /client/plugin-functions/{id}`
- `GET /client/plugin-function-integrations`

### `ai_agents:write`

- `POST /client/agents`
- `DELETE /client/agents/{slug}`
- `PUT /client/agents/{slug}/profile`
- `PUT /client/agents/{slug}/description`
- `PUT /client/agents/{slug}/visibility`
- `POST /client/agents/{slug}/revisions`
- `POST /client/agents/{slug}/revisions/{id}/publish`
- `DELETE /client/agents/{slug}/revisions/{id}`
- `POST /client/plugin-functions`
- `PUT /client/plugin-functions/{id}`
- `DELETE /client/plugin-functions/{id}`
- `POST /client/plugin-functions/{id}/duplicate`
- `POST /client/plugin-functions/{id}/test-run`

### `chat_sessions:read`

- `GET /client/chat-sessions`
- `GET /client/chat-sessions/{uuid}`
- `GET /client/chat-sessions/{uuid}/record`
- `GET /client/chat-sessions/{uuid}/record/download`
- `GET /client/chat-sessions/{uuid}/record/checksum`
- `GET /client/chat-sessions-list`
- `GET /client/chat-sessions-list/csv`
- `GET /client/agents/{slug}/chat-session-tests`
- `GET /client/agents/{slug}/chat-session-tests/{uuid}`

### `client_outbound_options:read`

- `GET /client/outbound/options`
- `GET /client/outbound/options/{id}`

### `client_outbound_batches:read`

- `GET /client/outbound/batches/{id}`
- `GET /client/outbound/batches/{id}/records`
- `GET /client/outbound/batches/{id}/records/download`

### `client_outbound_batches:write`

- `POST /client/outbound/batches`
- `POST /client/outbound/batches/{id}/pause`
- `POST /client/outbound/batches/{id}/resume`
- `POST /client/outbound/batches/{id}/cancel`

## Scope handling

Before calling an endpoint, identify its required scope and check the user's intended action against that scope. If the API returns an authorization or insufficient-scope error, explain the missing scope without exposing the API key.

Do not call backoffice routes, API-key management routes, or client routes not listed in this file. Do not infer that a JWT-only route is available to an API-key caller.

## Outbound batch handling

The authoritative request/response schema is the OpenAPI spec at
`https://developers.ingfah.ai/openapi.yaml`. Read it before constructing a
batch request rather than relying on this summary.

- There is no supported `GET /client/outbound/batches` list route in the documented client API. Do not invent or retry that route.
- Batch detail, records, CSV download, pause, resume, and cancel operations require a numeric batch ID in the path. That ID is the client-scoped `client_batch_id` returned as `data.id` on creation, not the internal `id` in the detail response.
- `GET /client/outbound/batches/{id}/records` supports `page`, `per_page`, `search`, `status`, `disposition_outcome`, `sort_by`, and `sort_direction` query parameters.
- `GET /client/outbound/batches/{id}/records/download` returns a CSV file. Save it only when the user explicitly requests a download or export.
- Before creating a batch, retrieve outbound options and products so the request uses a valid option ID, an outbound product ID, and every field the option marks `is_required`.
- A successful batch creation can start or schedule real outbound calls. Always show a concise preview and obtain explicit user confirmation immediately before sending it.
- Pause, resume, and cancel are state-changing actions and require explicit confirmation. Cancel is permanent and cannot be undone with resume. Batch status may lag a few seconds behind a successful cancel response.
- If batch creation returns `404 resource not found`, report that creation is unavailable on the configured deployment and do not repeatedly retry or substitute another endpoint.
- A `404` for a specific batch ID means that batch was not found; it is not evidence that API-key authentication failed.

### Creating a batch

`POST /client/outbound/batches` requires `client_outbound_option_id`, `name`,
`est_duration_minutes`, and at least one entry in `schedules`. `retry_policy`
is an optional array of retry wait times in minutes.

Each schedule requires `client_product_id`, `start_time`, `end_time`,
`day_slot`, `timezone`, `records`, and one of `time_slots` or `time_slot`.
`sip_numbers` is optional and defaults to the first configured SIP number.

- `start_time` and `end_time` use `YYYY-MM-DD HH:MM:SS`, interpreted in
  `timezone`. An ISO-8601 offset such as `2026-03-16T10:00:00+07:00` is
  rejected. `end_time` must be in the future.
- `day_slot` is exactly 7 characters of `0`/`1` for **Sunday through
  Saturday**; `1` allows that day. Mon-Fri is `0111110`. It is not a weekday
  name or an index list.
- `time_slots` is a list of `{"from": "HH:MM", "to": "HH:MM"}` windows in
  `timezone`. Omitting both `time_slots` and the deprecated `time_slot`
  returns `400 time_slots is required`.
- `day_slot` and `time_slots` must overlap the `start_time`/`end_time` window,
  or the request fails with `day_slot and time_slots have no overlap`.
- Each record needs `row_number`, `phone_number`, and a value for every
  required option field. Phone numbers are normalised to E.164 server-side.

```json
{
  "client_outbound_option_id": 1,
  "name": "Test Batch",
  "est_duration_minutes": 5,
  "retry_policy": [1, 2, 3],
  "schedules": [
    {
      "client_product_id": 1,
      "start_time": "2026-03-16 10:00:00",
      "end_time": "2026-03-16 18:00:00",
      "day_slot": "0111110",
      "time_slots": [{"from": "10:00", "to": "18:00"}],
      "timezone": "Asia/Bangkok",
      "records": [
        {"row_number": 1, "phone_number": "+66812345678", "customer_name": "John Doe"}
      ]
    }
  ]
}
```

To schedule an immediate call, set `start_time` to the current time in
`timezone`, set `day_slot` to today's bit, and make `time_slots` cover now.

### Creation responses

A creation request returns HTTP 200 in two different cases. Check which before
reporting success:

- **Created** — `data` contains `id`, `name`, and `uploaded_key`. `data.id` is
  the `client_batch_id` to use in later path operations.
- **Validation failed, batch not created** — `data` contains only `invalids`,
  a list of `{error, column, row_numbers}`. `error` is one of
  `DUPLICATE_PHONE_NUMBER`, `INVALID_PHONE_NUMBER`, `MISSING_REQUIRED_FIELD`,
  or `FIELD_TOO_LONG`. Report these rows to the user; do not claim the batch
  was created.

Error responses carry an `error_detail` field naming the offending field. Read
it instead of guessing at the schema, and surface it to the user.

## Agent handling

Agent metadata and agent behaviour are changed through two different paths.
Choose deliberately and say which one is being used.

- `PUT /client/agents/{slug}/profile`, `/description`, and `/visibility` change
  metadata and **take effect immediately, without creating a revision**.
- Behaviour changes go through the revision workflow: draft with
  `POST /client/agents/{slug}/revisions`, then
  `POST /client/agents/{slug}/revisions/{id}/publish`.

### Creating an agent

Creating a working agent is three calls, not one. `POST /client/agents` only
creates the shell: the prompt fields sent with it are **not stored**, so the
agent reads back with an empty `name`, identity, task, and flow. Always
complete all three steps and verify by reading the agent back.

1. `POST /client/agents` — creates the shell. Requires `visibility`
   (`private` or `public`); `prompt_engine_version` defaults to `v3`.
   Keep the returned `slug` and numeric `id`.
Every prompt this skill writes must be **cache-safe**: the prompt body is
identical for every customer, and per-call data is referenced by name rather
than written in. Leave `prompt_engine_version` at its default on a new agent,
and keep an existing agent's version unchanged. See
`references/prompt-authoring.md` for the rules, what `{{customerContext.*}}`
renders to, and how to branch on customer data with Jinja.

2. `POST /client/agents/{slug}/revisions` — carries the actual prompt
   (`name`, `vocal_name`, `greeting_message`, `ai_greeting_message`,
   `ai_instruction_identity`, `ai_instruction_task`, `ai_instruction_flow`,
   `voice_id`), then publish it. Nothing is live until published.
3. `POST /client/products` — an agent cannot take or place calls on its own. A
   product is the callable team that routes to it. Pass the agent's numeric
   `id` as `starting_agent_id`, plus `name`, `direction` (`inbound` or
   `outbound`), `channel_type` (`audio` or `text`), and `visibility`.

The product is also where disposition outcomes and outcome metadata live, so
an agent without one has no post-call labelling either. When a user asks for a
new agent, create the product as part of the same task and say so; ask first
only if an existing product should be reused instead.

Rules:

- Read `GET /client/agents/{slug}` and `GET /client/agents/{slug}/revisions`
  before editing, and show the user what is changing from what.
- After any create or publish, read the agent or revision back and confirm the
  fields actually stored. Do not report success from the write response alone.
- Publishing a revision changes how a live agent talks to real customers. Treat
  it like outbound batch creation: preview the change and get explicit
  confirmation immediately before publishing.
- Creating a draft revision is not live until published (`published_at` is
  `null`). Say so, so the user knows a draft alone changes nothing.
- A revision is a full snapshot of the agent's configuration, not a patch. Read
  the latest revision with `GET /client/agents/{slug}/revisions/{id}`, change
  the fields being edited, and post the whole body back. `name`,
  `greeting_message`, and `ai_greeting_message` are required; a revision read
  returns `greeting_message` and a nested `voice` object, so map
  `voice.id` to `voice_id` when reposting.
- Deleting a revision is a soft delete: it comes back `status: deleted` with
  `deleted_at` set, and it still appears in the revisions list and is still
  readable by id. Filter on `status` before reporting a revision list, and do
  not describe the delete as permanent removal.
- `DELETE /client/agents/{slug}/revisions/{id}` and `DELETE /client/agents/{slug}`
  are destructive and need explicit confirmation.
- Visibility is creator-only: the API key acts as the admin it belongs to, so a
  key whose admin did not create the agent gets `403` even with
  `ai_agents:write`. Report that as a permission rule, not an auth failure.

## AI team (product) handling

A `product` is what the dashboard calls an **AI Agent Team / ทีม AI Agent**.
Beyond creation it can be read, updated, made public or private, and deleted.

- `PUT /client/products/{id}` takes `name`, `description`,
  `starting_agent_id`, `channel_type`, and `transferabilities`. `channel_type`
  is accepted only when it equals the current value — changing it returns
  `400`. `starting_agent_id` must name an agent with a published revision that
  matches the team's channel type. `transferabilities`, when present, replaces
  the whole list rather than appending to it.
- `PUT /client/products/{id}/visibility` takes `{"visibility": "private"|"public"}`.
  Like agent visibility, only the admin who created the team may change it: a
  key belonging to another admin gets `403` even with `client_products:write`.
- `DELETE /client/products/{id}` is refused with `422` while a phone number is
  assigned to the team or one of its outbound batches is still active. Take the
  number off and cancel the batch first; report the `422` as a state rule, not
  a permission problem.

Deleting a team removes the callable route to its agent and its
postprocessors. Confirm explicitly before updating, changing visibility, or
deleting, and name the team being affected.

## Phone tools and plugin functions

These are the tools an agent may call. Read them before editing an agent whose
`phone_tools` or plugin functions are changing.

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

### Writing a plugin function

`POST /client/plugin-functions` requires `signature`, `description`, and
`integration`. `signature` is the function name the agent calls and must be
unique within the client — a duplicate returns `409`. `description` is what
the agent is told the tool does, at most 1000 characters.

- `parameters` are the arguments the agent supplies from the conversation; each
  needs `name` and `type`, plus `description` and `required`.
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

## Disposition outcomes and outcome metadata

Both are postprocessors: steps that run after a call to label or extract from
the transcript. A product's session config holds at most one postprocessor of
each type (`disposition`, `summary`, `assessment`, `outcome_metadata`).
Creating a second of the same type returns `409`.

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

### Writing a postprocessor

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

## Response handling

Return concise, structured summaries. Preserve identifiers, statuses, timestamps, and relevant error details, but remove credentials and unrelated personal or sensitive data. For downloads, save or present the result only when the user explicitly requests it.
