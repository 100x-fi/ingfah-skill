---
name: ingfah
description: Interact with the Ingfah client platform through client API-key authenticated APIs. Use this skill when the user asks to inspect or manage Ingfah products, AI agents, chat sessions, tools, or outbound batches — including when they use the dashboard's own words in English or Thai, such as AI Agent Team / ทีม AI Agent, batch / Batch โทรออก, calls / สายทั้งหมด, chats / แชท, templates / เทมเพลตข้อมูลลูกค้า, tools / Tool, or post-call results / ผลลัพธ์หลังวางสาย. Do not use backoffice APIs or JWT-only client APIs.
---

# Ingfah client API

Use the user's Ingfah client API key to call only the client API routes listed below.

The default Ingfah API base URL is `https://api.ingfah.ai`. Use another base URL only when the user explicitly provides one.

This file holds the rules that apply to every task. The detail for each area
is in `references/`; **read the matching file before working in that area**:

| Task | Read first |
|---|---|
| Write or edit an agent's prompt | `references/prompt-authoring.md` — a prompt that bakes per-call data into its body is incorrect, not merely suboptimal |
| Create or edit an agent, a revision, or an AI Agent Team | `references/agents-and-teams.md` |
| Create, pause, resume, or cancel an outbound batch | `references/outbound-batches.md` |
| Read, write, or test-run a Tool | `references/tools.md` |
| Design disposition outcomes or an outcome metadata schema | `references/outcome-design.md` |
| Create or edit a postprocessor | `references/postprocessors.md` |
| Set up a Chat Automation (webhook, do-not-contact) | `references/automations.md` |
| Translate a field name the user reads in the dashboard | `references/dashboard-terms.md` |

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
| automation | Chat Automation | Chat Automation |
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

Field-level dashboard names — postprocessor, agent prompt, and Tool fields, and
the batch and record status words — are in `references/dashboard-terms.md`.

## Working with the user

Most users are not developers. They know the dashboard, not the API, so the
work should end where they can see it.

- **Point to where the change shows up.** After a write, name the dashboard
  page the user can open to check it — e.g. "ทีม AI Agent → เปิดทีม →
  ตั้งค่าผลลัพธ์หลังวางสาย" for a postprocessor, or the **Metadata** column on
  สายทั้งหมด for extracted results.
- **Suggest a test before going live.** After drafting or publishing an agent,
  tell the user to open the agent, pick **แบบร่าง** or **เผยแพร่**, and use the
  arrow beside **ทดลอง** → **ตั้งค่าและทดลอง**. Test calls are free and use no
  real phone line. Choosing the job type **รับสาย** there shows every variable,
  so customer context can be filled in by hand. Their transcripts are then
  readable with `GET /client/agents/{slug}/chat-session-tests`.
- **Say when something is dashboard-only.** Some tasks have no client API
  route. Give the user the path in the table below instead of trying another
  endpoint.

### Before building a new agent

Collect these first, and ask for whatever is missing rather than inventing it:

- the agent's role, **gender**, personality, and tone
- the company or brand it represents
- who it will call or answer, e.g. customers who are overdue or just ordered
- what it must say on every call, e.g. a recording consent notice, the due
  date, the amount owed
- the goal — what the customer should agree to or provide
- hard rules — things it must never do or always do
- what should be recorded after the call — the outcome, a promised date, and
  so on; this becomes the disposition outcomes and outcome metadata

### Dashboard-only tasks

| Task | Where in the dashboard |
|---|---|
| Create, rename, or delete an API key | การตั้งค่า → API Keys |
| Assign a phone number to an inbound team | เบอร์โทรศัพท์ → ⋮ → แก้ไข → ทีมรับสายเข้า |
| Upload knowledge files | คลังความรู้ → อัปโหลด; attach in the agent → แก้ไขแบบร่าง → คลังความรู้ icon → บันทึกแบบร่าง |
| Create, copy, or delete a customer template | สายออก → จัดการเทมเพลต |
| Upload a batch from a CSV file | สายออก → สร้าง Batch |
| Make a test call or chat | the agent → ทดลอง → ตั้งค่าและทดลอง |
| Add a cloned voice | a service requested from the Ingfah team |
| Data retention, billing, activity logs, guest access | การตั้งค่า — **Owner** only |

Knowledge files must be `.pdf`, `.docx`, `.txt`, or `.md`, and must reach
**พร้อมใช้งาน** before they are attached. A batch CSV must be at most 25 MB,
with column names matching its template.

A missing phone number on เบอร์โทรศัพท์ or on batch creation means no line is
connected yet: the user connects their own telephony or asks the Ingfah team
for a number, which is billed separately.

## Authentication

- Send the key only in the `X-Api-Key` request header.
- If no key is available, ask the user to provide their Ingfah client API key.
  If they have none, tell them to create one at **การตั้งค่า → API Keys →
  สร้าง API Key** on https://ingfah.ai/login. The key is shown **once** only; a
  lost key cannot be recovered, so they create a new one and delete the old.
  A new key has the full access of its account.
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
- `GET /client/products/{id}/automations`

### `client_products:write`

- `POST /client/products`
- `POST /client/products/{id}/automations`
- `PUT /client/products/{id}/automations/{automationId}`
- `DELETE /client/products/{id}/automations/{automationId}`
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

The automation routes are live but absent from the OpenAPI spec; see
`references/automations.md`. Do not call backoffice routes, API-key management routes, or client routes not listed in this file. Do not infer that a JWT-only route is available to an API-key caller.

## Rules that apply in every area

The reference files hold the detail; these are the rules not to miss even
without opening one.

- **Real-world effects need a preview and explicit confirmation immediately
  before sending.** Creating a batch places real calls. Publishing a revision
  changes a live agent. Test-running a Tool sends its real request. An
  automation sends customer data to a third party on every matching call.
- **Read before writing.** Revisions, Tool updates, postprocessor updates, and
  team `transferabilities` replace what they are given rather than patching it.
  Read the current state, change only the fields being edited, and send the
  whole body.
- **Verify after writing.** Read the object back and report what was actually
  stored, not what the write response implied. `POST /client/agents` in
  particular drops the prompt fields sent with it.
- **Report state rules as state rules.** A `403` on visibility means the key's
  admin did not create the object; a `409` or `422` on delete means something
  still uses it. Neither is an authentication failure.
- **Postprocessor and automation changes apply to new calls only.** Calls that
  already ended are not reprocessed.
- **Redact.** Never show API keys, webhook auth headers, or `hmac_secret`.
  Treat outcome metadata and transcripts as personal data.

## Response handling

Return concise, structured summaries. Preserve identifiers, statuses, timestamps, and relevant error details, but remove credentials and unrelated personal or sensitive data. For downloads, save or present the result only when the user explicitly requests it.

Recordings, transcripts, and batch data are deleted automatically once they
pass the account's data-retention period, set by an Owner under การตั้งค่า →
การเก็บรักษาข้อมูล. When an old call has no recording or transcript, mention
retention as a likely reason rather than reporting a fault.
