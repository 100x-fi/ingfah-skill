# Disposition outcomes and outcome metadata

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
