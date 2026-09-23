# Outbound batch handling

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
- Pause and cancel stop calls that have not started, but a call already in
  progress runs to its end. Say so, so the user does not expect a live call to
  drop. A cancelled batch moves to the **สิ้นสุด** tab with status ยกเลิกแล้ว.
- If batch creation returns `404 resource not found`, report that creation is unavailable on the configured deployment and do not repeatedly retry or substitute another endpoint.
- A `404` for a specific batch ID means that batch was not found; it is not evidence that API-key authentication failed.

## Creating a batch

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

## Creation responses

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
