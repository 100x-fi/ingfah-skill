# Fixing what the user sees

Users report a symptom, not a setting: "the summary thinks we're a laundry",
"it keeps saying สรุปไม่ได้", "the AI mispronounces our brand". Knowing which
route exists is not enough. Work out **which setting produced what they see**,
then propose the change to that setting.

## How to consult

1. **Restate the problem in their words** and ask for one or two example
   calls (a time, a phone number, or a screenshot) when none were given.
2. **Look before guessing.** Read the team (`GET /client/products/{id}`, which
   includes its postprocessors), the agent's published revision, and the
   example calls (`GET /client/chat-sessions/{uuid}`: transcript, title,
   summary, outcome, metadata). Find what the setting is now, and whether a
   setting is missing.
3. **Name the cause in dashboard words.** For example: "ทีมช่วยเหลือลูกค้ามีแค่
   ผลลัพธ์แบบสถานะ ยังไม่มีสรุปบทสนทนา (อัตโนมัติ) เลยใช้ตัวสรุปตั้งต้นที่ไม่รู้ว่า
   ธุรกิจนี้คือร้านล้างรถ". If you said earlier that something could not be done
   and it can, say so plainly.
4. **Propose one concrete change** and show the exact text or JSON. Say what
   it will fix, what it will not (settings apply to **new calls only**), and
   where they will see the result. Offer to adjust the wording.
5. **Ask for confirmation, then apply it, read it back, and suggest a test**
   (ทดลอง → ตั้งค่าและทดลอง, or the next real call).

When two settings could explain it, check the cheaper one first. When the
fix is dashboard-only, give the menu path instead.

## What the user sees → what produces it

| What the user sees | Produced by | Dashboard | API |
|---|---|---|---|
| หัวข้อสนทนา (call title), Conversation Summary | `summary` postprocessor; the global default when the team has none | ทีม AI Agent → แก้ไข → ตั้งค่าผลลัพธ์หลังวางสาย | `postprocessors`, `references/postprocessors.md` |
| ผลลัพธ์ (outcome label) | `disposition` postprocessor: outcome names and their criteria | same, tab ผลลัพธ์แบบสถานะ | same |
| Metadata JSON, `outcome_metadata.*` CSV columns | `outcome_metadata` postprocessor: `json_schema` key descriptions | same, tab ผลลัพธ์แบบ metadata | same |
| What the agent says, asks, skips, its tone | agent revision: greeting, identity, task, flow | AI Agent → แก้ไขแบบร่าง → เผยแพร่ | revisions, `references/prompt-authoring.md` |
| Facts the agent answers with, or invents | knowledge files attached to the agent, and the prompt | คลังความรู้ (upload is dashboard-only) | `references/faq-authoring.md` |
| The agent's voice | revision `voice_id` | AI Agent → แก้ไขแบบร่าง → เสียง | `GET /client/voices`, revisions |
| Customer name, amount, or due date wrong or missing on a call | batch record data and template columns vs the prompt's variables | สายออก → จัดการเทมเพลต | outbound options, `customer-context-variables` |
| Handoff to another agent, or none; the next agent greets again, re-asks, or says it is transferring | team transferabilities, the handoff mode, and each receiving agent's "taking over a call" section | ทีม AI Agent → แก้ไข | `references/multi-agent-teams.md` |
| The agent says a tool's name aloud (`transfer_to_human_agent{}`), says it will transfer and does not, or repeats its goodbye without hanging up | first the agent's **tool bindings**, then the prompt around the tool | AI Agent → แก้ไขแบบร่าง → Tools | `GET /client/agents/{slug}` `phone_tools` / `ai_plugin_functions`; `references/agents-and-teams.md` |
| A Tool not called, or failing | Tool description and parameters | Tool | `references/tools.md` |
| Data not reaching their CRM, sheet, or webhook | Chat Automation | — | `references/automations.md` |
| Missed or unanswered outbound calls | batch schedule and SIP result | สายออก → รายการ Batch → รายละเอียด Batch | `GET /client/outbound/call-data-records`, `references/outbound-batches.md` |

## Common complaints

**"The summary or title is wrong, too generic, or misunderstands our
business."** Check the team's postprocessors. With no `summary` type, add one
whose `instruction` states the business, what ambiguous words mean there
("เครื่อง" means the car-wash machine), and what the title must include
(branch, order number). With one already, sharpen its instruction using the
bad examples. Do not edit the agent's prompt for this; the summarizer does not
read it. See `references/postprocessors.md`.

**"Every call is labelled สรุปไม่ได้, or the label is wrong."** Read the
transcripts of mislabelled calls against each outcome's criteria. Usually the
criteria overlap, or none fits what customers actually say. Rewrite the
criteria, add a missing outcome, or reorder by `rank`. See
`references/outcome-design.md`.

**"A metadata field is empty or in the wrong format."** The key's
`description` in `json_schema` is what the extractor follows. Say the format
and what to put when the value is absent.

**"The new setting didn't change anything."** Postprocessor, automation, and
revision changes apply only to calls that start after them. For a revision,
also check that it was **published**, not left as a draft.

**"The AI read out `transfer_to_human_agent{}`", "it said it would transfer
me but nothing happened", "it keeps saying goodbye but doesn't hang up."**
Check in this order. Each step is one read.

1. **Is the tool bound?** `GET /client/agents/{slug}` → `phone_tools` and
   `ai_plugin_functions`. If the transfer tool or `end_call_keyword` is
   missing, the last revision probably dropped it (a revision posted without
   the tool lists stores none; see `references/agents-and-teams.md`). Compare
   the revisions' `published_at` with when the complaints started. The fix is a new
   revision that carries every id again, then publish and re-read.
2. **Did the tool actually run on the call?** `GET /client/chat-sessions/{uuid}`:
   a real transfer is a message with `role: tool`. Speech about transferring
   with no tool message means it never ran. If step 1 is fine, the cause is
   the prompt.
3. **The prompt teaches the model to write the call as text.** The usual
   causes, all seen together on one agent:
   - a rule that *quotes* the forbidden output ("ห้ามพิมพ์
     transfer_to_human_agent{}") — naming it primes it;
   - "say one sentence, then call the tool", in the prompt or in the tool's
     description;
   - scripted `examples` that speak the transfer ("เดี๋ยวผมโอนสายให้
     เจ้าหน้าที่นะครับ"), which the agent copies word for word and then follows
     with the tool name as text.

   The fix that worked (2/18 → 18/18 real transfers, measured on the production model) was a **silent
   transfer**: the transfer turn calls the tool and says nothing (the tool's
   hold message tells the caller to wait), with the quoting rule, the
   spoken-transfer examples, and the "speak first" line in the tool
   description all removed. Any instruction in that state that competes with
   transferring, such as "send details on LINE", should be removed too. See
   `references/prompt-authoring.md` → "Tools in the prompt".

**"Customers hang up straight away."** Read a few: when the call is the
greeting, one reply, and a hang-up, the model never ran again and no prompt
change reaches it. The lever is the greeting's length (a 300-character
greeting took about 26 seconds to speak) and the short-calls analytics
(`references/reporting.md`).

**"The AI stops mid-sentence where a number should be."** say-as tags are
removed before the transcript is saved, so a transcript never shows them. A
sentence cut off exactly at a number points to a malformed tag in the prompt,
such as `<say-astype=...>`; search the prompt for `say-as` and check each.

**"The AI mispronounces a word or number."** Fix it in the prompt using the
say-as guidance in `references/user-guide/guides/ai-agent/say-as-pronunciation.md`.

**"The AI makes up prices or policies."** Put the facts in a knowledge file
(`references/faq-authoring.md`) and tell the prompt to answer only from it.

**"The AI said `{{name}}`, or used the wrong customer's details."** Compare
the prompt's variables (`GET /client/ai-agent-teams/{id}/customer-context-variables`)
with the template columns and the batch record. See `references/prompt-authoring.md`.

**"Many outbound calls were never answered."** Read
`GET /client/outbound/call-data-records?batch_id=...`. `sip_disposition` and
`sip_hangup_cause` separate busy, no-answer, and invalid numbers from a
schedule problem.

**"Stop calling this customer."** A do-not-contact automation, or a new batch
without them. See `references/automations.md`.

**"How are we doing? Give me numbers."** Use the analytics routes (see
`references/reporting.md`) rather than paging through every call.

**"An old call has no recording or transcript."** Data retention, not a
fault. See Call recordings in `SKILL.md`.
