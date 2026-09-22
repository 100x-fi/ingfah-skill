# Designing disposition outcomes and outcome metadata

Both run after a call ends and read the whole transcript. The disposition
picks one label; the outcome metadata extracts a structured record. They must
agree with each other and with the conversation flow.

## Disposition outcomes

A list of `{outcome, prompt, color, rank}`. `outcome` is the stored label and
`prompt` tells the model when to choose it — the `prompt` is what decides
labelling quality, so write it as a decision rule, not a description.

**Cover the whole space.** A usable set has an outcome for every way a call
can end, not just the happy ones:

- the goal achieved, and a partial or soft version of it
- customer asked to be called back
- refused, ideally split by reason when the reasons drive different follow-up
- reached the wrong person, or not the decision maker
- not a good time
- do-not-call
- answering machine
- call dropped mid-conversation, and no answer at all

**Write an explicit priority order** in the instruction, because real calls
match several outcomes at once. A workable default, highest first: answering
machine → do-not-call → wrong number → goal achieved → callback requested →
everything else. State it once and reuse the same order in the metadata
instruction.

**Guard the ambiguous pairs.** These are where labelling actually goes wrong:

- *Callback vs not-interested.* A callback requires the customer to ask for it
  or to name a time themselves. A time the agent proposed does not count, and
  a short acknowledgement while closing — ครับ, ค่ะ, โอเค — is not a callback.
- *Success vs partial.* Define the minimum that counts as success (for a sale:
  quantity, address, and payment method all confirmed). Anything short of it
  is the softer label.
- *Complaint vs dissatisfaction.* A low score or grumbling alone is not a
  complaint. Require an actual stated problem before flagging follow-up.

The instruction should end by fixing the response shape, e.g.
`{"outcome":"...","reason":"..."}` with a short reason in the call's language.

## Outcome metadata

`json_schema` is a wrapper: `{"name": ..., "description": ..., "schema": {...}}`
where `schema` is the JSON Schema. Set `additionalProperties: false` and list
every field in `required` — the model fills all of them, using `null` for
unknown.

Design rules:

- **Mirror the disposition.** Include an `outcome` field whose `enum` is
  exactly the disposition labels, and repeat the same priority rules in the
  instruction. If the two can disagree, they will.
- **Type for absence.** Use `["string", "null"]` rather than forcing a
  placeholder. Never let a display placeholder like `-` become stored data.
- **Booleans are never null.** Arrays are always arrays, empty when nothing
  applies.
- **Say what each field means in its `description`,** including when it must
  stay null. The description is the only instruction the extractor sees for
  that field.
- **Add consistency guards** in the instruction: if the outcome claims success,
  the fields that prove success must be populated, otherwise the outcome must
  be downgraded. This is the single most valuable rule in the schema.
- **Ban inference** for anything actionable — addresses, amounts, dates,
  names, competitors. Only what was actually said.
- **Distinguish "not asked" from "asked and refused."** A field is null for
  different reasons and follow-up depends on which; give the status its own
  enum field when it matters.
- Keep a short free-text `notes` field for facts only, explicitly no opinions.

## Constraints to remember

- One postprocessor per type per product; a second returns `409`.
- `type` cannot be changed on update — delete and recreate instead.
- `PUT` replaces the fields it is given, so read
  `GET /client/products/{id}` first and post the full intended state.
- Extracted metadata is customer data. Treat its values as personal data when
  displaying or exporting them.
