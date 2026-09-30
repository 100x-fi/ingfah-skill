# Analytics, text chats, and call attempts

Read-only routes for "how are we doing" questions. Prefer them to paging
through every call. The OpenAPI spec at `https://developers.ingfah.ai/openapi.yaml`
has the full response shapes.

## Voice call analytics — `analytics:read`

All take `from` and `to` (RFC 3339, both required, at most 93 days apart),
and optionally `direction` (`inbound` / `outbound`; both when omitted),
`client_product_ids` (comma-separated team ids), and `timezone` (IANA, e.g.
`Asia/Bangkok`). Most compare the window with the window just before it.

| Route | Answers |
|---|---|
| `GET /client/analytics/summary` | call counts and durations, broken down by team, company number, outcome, and (outbound) batch row status |
| `GET /client/analytics/short-calls` | ended calls shorter than `threshold_seconds`, by team and number — hang-ups right after the greeting |
| `GET /client/analytics/hourly-charts` | calls started per hour, and peak concurrent calls |
| `GET /client/analytics/duration-histogram` | calls by length (`bucket`) |
| `GET /client/analytics/heatmap` | when calls start, weekday × hour (`mode`) |
| `GET /client/analytics/speech-ratio` | how much the agent talked vs the customer, per team |
| `GET /client/analytics/report/download` | every view above as one XLSX workbook; save with `--output report.xlsx` |

The dashboard shows these on its แดชบอร์ด page.

## Text chat — `analytics:read` / `chat_sessions:read`

- `GET /client/text-analytics/summary`, `/messages-hourly`, `/heatmap` take
  `from`, `to`, `timezone`, and optional `client_product_ids`,
  `agent_team_ids`, `channel_ids`.
- `GET /client/text-chats/conversations` is the inbox: one row per customer
  and channel, most recent writer first. It filters by `search`, `status`,
  `provider`, `client_product_id`, `text_channel_config_id`,
  `disposition_outcome`, `start_time`, `end_time`, and `is_self_assigned`.
  `GET /client/text-chats/conversations/{uuid}` returns one conversation with
  its sessions.
- `GET /client/text-chats/chat-sessions-list` (and `/csv`) lists text chat
  sessions, the text counterpart of `chat-sessions-list`.
- Channels (LINE, Facebook, and so on): `GET /client/text-channel-configs`
  and `/{id}`, and `GET /client/text-channel-config-providers` for the
  catalog, all under `client_products:read`. Credentials come back only as
  `{key, is_set}`, never as values. Adding or editing a channel is
  dashboard-only: การตั้งค่า → Channels, Owner only.

Muting the bot, replying as a human, and reassigning a conversation are
dashboard-only on purpose; an API key cannot do them.

## Outbound call attempts — `client_outbound_batches:read`

`GET /client/outbound/call-data-records` returns one row per dial attempt,
newest first: `status`, `sip_disposition` (e.g. `BUSY`), `sip_hangup_cause`,
and SIP start, answer, and end times. Filter by `batch_id` (the
`client_batch_id`), or give `from` and `to` together (at most 93 days apart).
`per_page` is at most 100. Use it to explain *why* records are Missed or Busy,
which the batch records alone do not say. Phone numbers in it are personal
data.
