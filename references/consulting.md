# Advise on an Ingfah setup

Use this guide when the user needs a recommendation, a rollout plan, or help
improving results. Start with the business outcome. Read the relevant bundled
guide and technical reference before claiming that Ingfah supports a feature.

## Establish the decision

Use facts the user already supplied. For a broad request, ask at most three
focused questions in the first turn. Choose the questions that change the setup:

- What should a successful conversation achieve, and which channel is needed?
- What information must the agent know, collect, or look up in another system?
- When must a person take over, and who can receive the transfer?
- What volume, calling window, languages, and budget constraints matter?
- Which team, published agent, or example conversations already exist?

If a required fact is missing, name it and wait before preparing a configuration
that depends on it. You can still explain the supported choices. Do not turn a
general advice question into a request for an API key.

## Choose the smallest supported setup

The following are recommendations, not requirements or guaranteed results.

| User's goal | Recommended starting point | Read before advising |
|---|---|---|
| Answer questions from approved business documents | One agent with a focused FAQ knowledge base, retrieval instructions, and a fallback when information is missing | `faq-authoring.md`, `user-guide/guides/knowledge-base/prompting.md` |
| Check an order, balance, or appointment during a conversation | A Tool connected to the source system, with failure handling and confirmation before consequential actions | `tools.md`, `prompt-authoring.md` |
| Make outbound reminders, surveys, or follow-ups | A team, customer template, per-customer variables, calling schedule, and explicit outcomes | `outbound-batches.md`, `outcome-design.md` |
| Handle inbound calls and escalate to staff | An inbound team, connected phone channel, and a tested human transfer path | `voice-handoff.md`, `user-guide/guides/inbound-outbound/inbound-set-up.md` |
| Answer LINE messages with staff taking over when needed | A text agent and connected channel, with an inbox handover procedure | `text-chat-handoff.md`, `user-guide/guides/contact-channels/connect-line-oa.md` |
| Send conversation results to a CRM | Structured outcome metadata and an Automation after the conversation | `postprocessors.md`, `automations.md` |
| Separate specialist tasks or departments | A multi-agent team only when responsibilities and transfer conditions are distinct | `multi-agent-teams.md` |
| Reduce poor answers or early hang-ups | Inspect representative conversations and the relevant settings before changing the prompt | `troubleshooting.md`, `reporting.md` |

Keep changing business facts in the knowledge base. Keep per-customer values in
customer context variables. Use Tools for live external data and actions. Use
the prompt for conversation rules. See `prompt-authoring.md` before drafting.

Start with one agent when one flow covers the task. Recommend several agents
when ownership or instructions differ enough to justify handoff testing.
Explain the extra transfer paths and receiving-agent context that must be tested.

Distinguish an agent's mid-conversation Tool from an event-driven Automation.
For "send the result after every matching call", recommend Automation. For
"look up this customer's order now", recommend a Tool.

## Apply current operational guidance

- For customers who request another call, read
  `user-guide/guides/inbound-outbound/follow-up-calls.md`. The Batch must enable
  callbacks, and the customer must request or accept a future time. A vague
  "call later" does not schedule one. The guide documents a seven-day limit,
  separate callback retries, and possible queue delay. Do not promise an exact
  dial time or treat an unanswered-call retry as a customer appointment.
- Before an outbound launch, recommend the dashboard's speech preview for
  representative customer names, dates, amounts, and codes. Read
  `user-guide/guides/inbound-outbound/speech-preview.md`. Previewing data is
  one check; it does not prove the full conversation or Tool flow works.
- When a customer asks to stop future contact, read
  `user-guide/guides/inbound-outbound/team-automations.md` and `automations.md`.
  Confirm the intended outcome condition and exclusion period before proposing
  a do-not-contact Automation. A declined offer alone is not an explicit
  request to stop all contact.
- Verify the account's license before promising disposition or metadata
  processing. Release notes document that settings can exist without the
  license needed to process them. Read `user-guide/guides/settings/billing.md`
  and `user-guide/release-notes.md`. Ask for the current account details when
  estimating cost; do not supply invented tariffs or concurrency allowances.
- Dashboard support does not establish API-key support. Use the routes in
  `SKILL.md` and the helper's allowlist. Give the dashboard path when a needed
  operation is not supported by the helper.

## Propose a pilot the user can evaluate

Prepare a concrete plan before proposing a platform write:

1. Name the use case and what counts as success. Agree the acceptance threshold
   with the user rather than presenting an arbitrary target as an Ingfah norm.
2. Identify approved documents, required customer fields, external systems,
   escalation rules, and any channel or license prerequisite.
3. Draft the prompt, outcome criteria, metadata fields, or integration payload
   needed for the task. Use the matching references instead of duplicating their
   schemas here.
4. Test representative successful conversations and failure cases. Include
   missing data, unclear answers, unavailable Tools, refusal, and escalation
   where relevant. Use `testing.md` for automated conversation tests.
5. Start with an agreed small set of test contacts or conversations. Creating a
   Batch places real calls. Follow the preview and confirmation rules in
   `SKILL.md` before creating, publishing, or enabling anything.
6. Compare the results with the baseline and inspect example transcripts.
   Recommend the next change from observed failures, then test it again.

For voice, consider task completion, correct answers, successful transfers,
early hang-ups, and wrong or missing extracted fields. For outbound, separate
dial attempts, answered calls, completed tasks, and customer outcomes. For
text, consider answer quality, delivery failures, and staff takeover.

State the date range, teams, channel, and denominator for every rate. Do not
call an answer rate a conversion rate. Use `reporting.md` for available
analytics, and identify measures that require reviewing transcripts or joining
external business data. Do not imply every proposed metric is a dashboard field.

## Give a useful recommendation

Lead with the recommended setup and why it fits the user's stated goal.
Explain the material tradeoff, prerequisites, and next test. Include the relevant
public guide links from their `Source:` lines. Use the user's language and the
dashboard's terms. Keep an API payload out of a general advice answer unless
the user needs it to review an implementation.

Separate documented behavior, observations from the user's account, and your
recommendation. Do not claim that backend source proves a feature is enabled on
the user's deployment. For a reported problem, follow `troubleshooting.md` and
label an unverified cause as a hypothesis.

### Example: outbound appointment reminders

User: "อยากให้ AI โทรเตือนนัด แล้วส่งผลเข้า CRM ควรเริ่มยังไง"

Recommend one outbound agent and one team. Ask which customer fields and CRM
payload are required. Propose a template with the confirmed fields, a short
reminder flow, distinct confirmed, reschedule, and unreachable outcomes, and
metadata for the details the CRM needs. Recommend a post-call Webhook and test
its payload before enabling it. Offer callbacks only after checking whether
they fit the process and the Batch configuration. Measure answered calls and
confirmed appointments separately.

### Example: improve a knowledge agent

User: "AI ตอบเรื่องราคาไม่ตรง ทำยังไงดี"

Ask for a wrong answer and its approved source price. Check the attached
documents, conflicting versions, retrieval result, and published prompt.
Recommend the change supported by that evidence. Do not invent a price or
promise that adding "do not hallucinate" fixes retrieval. Propose tests for
the affected question and nearby variants before publishing.

## Source baseline

This guidance was reviewed against public-docs commit `7f54224` and backend
commit `d21f203` on 2026-10-09. The user guide index records its own sync commit.
Treat this as a source snapshot, not verification of a live customer's account.
