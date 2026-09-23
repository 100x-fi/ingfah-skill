# Phone tools and plugin functions

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
