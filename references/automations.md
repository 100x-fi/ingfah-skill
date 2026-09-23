# Chat Automation

An automation makes the platform **do something when a call or chat reaches a
certain point** — most usefully, call an external system. It is how a team
posts a call result to a CRM, or triggers an SMS to the customer after the
call ends. The agent is not involved: this runs server-side after the event,
so it fires whether or not the agent remembered anything.

These routes are live but are **not in the public OpenAPI spec**. Rely on the
rules below rather than looking them up there.

An automation belongs to a product and is a pair of *when* and *what*:

| Field | Meaning |
|---|---|
| `trigger_event` | when it fires |
| `automation_type` | what it does |
| `automation_config` | the settings for that type |
| `trigger_condition` | optional filter — only fire for some sessions |
| `is_enabled` | defaults to `true` |

Each type is pinned to exactly one trigger, and a mismatched pair is refused
at creation with `400 automation_type "x" requires trigger_event "y"`:

| `automation_type` | Required `trigger_event` | What it does |
|---|---|---|
| `webhook` | `session_ended` | Sends an HTTP request when the call or chat ends |
| `mark_dnc` | `disposition_outcome_set` | Marks the number do-not-contact / ไม่ติดต่อ |

These two are the general-purpose types. Never offer or guess another type:
if a read returns an automation whose type is not in the table above, report
it by the name the API gave and leave it alone.

`session_started` and `outcome_metadata_set` are also valid trigger values,
but no general-purpose type accepts them. Some other type names exist in the
platform and are **rejected** by this API with `400 invalid automation_type`,
so a type outside the table is not worth attempting.

## The webhook type

`automation_config` for `webhook` takes `url` (required, absolute http(s)),
`method` (defaults to `POST`), `headers`, and `body`. `headers` and every
string in `body` are templates rendered against the finished session.

Placeholders are `{{path}}`:

- Session columns directly — `{{customer_phone}}`, `{{disposition_outcome}}`,
  `{{uuid}}` — or spelled `{{chat_sessions.customer_phone}}`.
- Outcome metadata by dot path — `{{outcome_metadata.promise_date}}` — so
  whatever the `outcome_metadata` postprocessor extracts can be forwarded.
- For a call dialled from a batch, the uploaded row —
  `{{outbound_batch_records.optional_data.policy_no}}`.
- Fallbacks with `||`, ending in a quoted literal:
  `{{outcome_metadata.name || customer_name || 'N/A'}}`.
- One filter, `phone`, with `--format=e164|msisdn|local`:
  `{{customer_phone | phone --format=local}}`.

An unresolved placeholder **fails the whole delivery** rather than sending a
blank, so give any optional field a quoted default. Delivery retries on 5xx and
network errors; a 4xx is terminal and is not retried.

### Example: post the call result to a CRM

```json
{
  "trigger_event": "session_ended",
  "automation_type": "webhook",
  "automation_config": {
    "url": "https://crm.example.com/api/call-results",
    "method": "POST",
    "headers": {"Authorization": "Bearer REDACTED"},
    "body": {
      "phone": "{{customer_phone | phone --format=e164}}",
      "result": "{{disposition_outcome || 'unknown'}}",
      "promise_date": "{{outcome_metadata.promise_date || ''}}",
      "session_id": "{{uuid}}"
    }
  }
}
```

### Example: send an SMS after the call, only when the customer agreed

There is no SMS automation type. Sending an SMS means pointing the webhook at
an SMS provider's own API, exactly as the CRM example points at a CRM.
`trigger_condition` keeps it to the calls that earned it:

```json
{
  "trigger_event": "session_ended",
  "automation_type": "webhook",
  "trigger_condition": {"disposition_outcome": "ลูกค้าตกลง"},
  "automation_config": {
    "url": "https://sms.example.com/send",
    "method": "POST",
    "headers": {"Authorization": "Bearer REDACTED"},
    "body": {
      "msisdn": "{{customer_phone | phone --format=msisdn}}",
      "message": "ขอบคุณค่ะ นัดชำระวันที่ {{outcome_metadata.promise_date}}",
      "sender": "Ingfah"
    }
  }
}
```

The alternative — giving the agent an SMS **Tool** — fires only if the agent
decides to call it mid-conversation. An automation fires on every matching
session. Prefer the automation for "after the call, always"; say which one is
being set up.

## Trigger conditions

`trigger_condition` is a small JSON match language over the session. Omit it,
or send `{}`, and the automation runs for every session.

- `{"disposition_outcome": "ติดต่อผิดเบอร์"}` — exact match.
- `{"outcome_metadata.duration_days": {"gte": 5}}` — operators are `eq`, `ne`,
  `gt`, `gte`, `lt`, `lte`, and all of an object's operators must hold.
- Several keys are ANDed. A path that does not resolve simply does not match,
  so the automation is skipped rather than failing.

## Rules

- Read `GET /client/products/{id}/automations` before changing anything. It
  lists everything that runs for that product's sessions.
- `automation_type` **cannot be changed on update** — sending it to `PUT`
  returns `400 automation_type field is not allowed to be changed`. Delete and
  recreate to change it.
- Creating the same trigger, condition, config, and type twice on one product
  returns `409 duplicate automation already exists`.
- An automation sends this client's customer data to a third party on every
  matching call. Show the full config, name the destination host, and get
  explicit confirmation before creating, updating, enabling, or deleting one.
  Deleting or disabling one silently stops a downstream system being fed.
- `headers` carry auth tokens and `hmac_secret` is a credential. The platform
  redacts them in its own logs; redact them in anything shown to the user too,
  and never echo a token back in a summary.
- Use `is_enabled: false` to stop an automation without losing its config —
  prefer it to deleting when the user says "pause" or "หยุดไว้ก่อน".
