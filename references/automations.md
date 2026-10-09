# Team Automations

Use Automation for work that must happen on a conversation event, such as
sending results to a CRM. Use a Tool for an action the agent chooses during
the conversation. Read `user-guide/guides/inbound-outbound/team-automations.md`
for dashboard instructions.

## Discover what the team supports

Read through `scripts/ingfah_api.py` before proposing a change:

- `GET /client/products/{id}/automations` lists the current Automations.
- `GET /client/products/{id}/automations/catalog` lists supported event/type
  pairs, configuration fields, and variables for that team's channel.
- `GET /client/automations/trigger-variables` lists variables more broadly.
  It does not expand the event/type pairs the team catalog permits.

Reads require `client_products:read`. Mutations require `client_products:write`.
If catalog discovery fails, report the response and use the dashboard or ask
the Ingfah team. Source code does not establish support on a live deployment.

The source snapshot reviewed on 2026-10-09 offers these pairs:

| Team channel | `automation_type` | `trigger_event` |
|---|---|---|
| Voice | `http`, `do_not_contact` | `session_started`, `session_ended` |
| Text | `http` | `session_started`, `handoff_to_human`, `session_ended` |

Use `session_ended` for completed postprocessing results. Disposition and
metadata can remain null when their postprocessor is absent.

## Create a current Automation

`POST /client/products/{id}/automations` takes `trigger_event`,
`automation_type`, `trigger_condition_jinja`, `automation_config_jinja`, and
`is_enabled`. The condition is optional and enabled defaults to true.
Prepare an integration disabled when its destination contract is untested.
Creating a disabled configuration still requires write confirmation.

The current client API rejects `trigger_condition` and `automation_config`,
including null values. Do not copy them from a legacy row. New types are
`http` and `do_not_contact`; do not create legacy `webhook` or `mark_dnc` types.

### Send results to a CRM

The whole `automation_config_jinja` string must render to a JSON object.
An `http` object takes required `url`, optional `method`, `headers`, and `body`.
Method defaults to POST; supported methods are GET, POST, PUT, PATCH, and DELETE.
Headers and body are JSON values. There is no second placeholder rendering pass.

Use `session.*` variables from the catalog. Insert dynamic JSON values with
`tojson` without quoting the interpolation. Escape quotes for the outer JSON.

```json
{
  "trigger_event": "session_ended",
  "automation_type": "http",
  "trigger_condition_jinja": "{{ session.disposition_outcome == 'ลูกค้าตกลง' }}",
  "automation_config_jinja": "{\"url\":\"https://crm.example.com/calls\",\"method\":\"POST\",\"body\":{\"session_id\":{{ session.id | tojson }},\"phone\":{{ session.customer_phone | tojson }},\"outcome\":{{ session.disposition_outcome | tojson }}}}",
  "is_enabled": false
}
```

Replace this voice-team example's destination and outcome with the confirmed
contract. For text teams, use text variables instead of voice phone fields.

A condition runs only when its rendered output is `true`, ignoring case and
surrounding whitespace. Other outputs skip; rendering errors fail. Guard
optional objects before accessing nested fields. Use only fields available
for the selected event, even inside conditional branches.

HTTP 2xx succeeds; 4xx is terminal. Network errors and HTTP 3xx or 5xx retry.
Design the destination to tolerate repeated deliveries, using the session id
when appropriate. Private, loopback, and link-local destinations are blocked.

### Honor a request to stop contact

For a voice team, use `do_not_contact` with a condition matching the confirmed
opt-out outcome. Configuration accepts only `duration_days`, an integer of
at least 1. Omit it for an indefinite exclusion. The phone comes from the
session; do not add a `phone` field.

For 30 days, the config string is `"{\"duration_days\":30}"`. Confirm the
period and outcome criteria. The dashboard guide explains that excluded
numbers also skip pending callbacks.

## Update or migrate safely

- Read current Automations and avoid duplicates yourself. Do not assume the
  server deduplicates identical creates.
- PUT cannot contain `automation_type` or `trigger_event`. Create a replacement
  to change either.
- Omitted Jinja fields preserve their values. An empty string clears them,
  but HTTP configuration still requires a URL. Clearing a legacy row's Jinja
  condition can fall back to its stored legacy condition. It does not
  necessarily mean "run for every conversation".
- Prefer `is_enabled: false` to pause. Read it back after updating.
- Legacy rows remain manageable. A legacy `webhook` cannot become `http` by
  updating its type or adding config Jinja. Prepare a replacement and agree
  the disable/enable order to avoid gaps or duplicate effects. Read back both.
- Show the destination host, event, condition, payload, and expected effects
  before confirmation. Redact header credentials. Disabling or deleting stops
  downstream delivery.
- Observe a new test conversation and verify receipt at the destination before
  claiming the integration works.

## Source baseline

Reviewed against backend commit `d21f203` on 2026-10-09. Maintainer pointers
are `ingfah/internal/modules/client/router.go`, `create_automation.go`,
`update_automation.go`, `ingfah/internal/model/automation_catalog.go`, and
`ingfah/internal/model/chat_session_automation.go` in the backend checkout.
