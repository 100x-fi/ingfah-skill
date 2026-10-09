# Changelog

All notable changes to this skill are recorded here. Versions follow
[Semantic Versioning](https://semver.org/); the version is also sent in the
request `User-Agent` as `ingfah-skill/<version>`.

## [1.8.0] — 2026-10-09

### Added

- `GET /client/calls/inbound-admission` with `inbound_admission:read` to
  check current inbound call capacity before a SIP transfer.
- `GET /client/text-chats/tags` with `chat_sessions:read` to list and search
  customer tags and their customer counts.
- Automation discovery through `GET /client/products/{id}/automations/catalog`
  and `GET /client/automations/trigger-variables` with `client_products:read`.
- Consulting guidance for choosing a setup, explaining tradeoffs, planning
  a pilot, and measuring results from the user's business goal.

### Changed

- Refreshed the bundled Thai guide to 73 pages, including callbacks, speech
  previews, text channels, analytics, and team Automations.
- Updated Automation instructions to the current `http` and `do_not_contact`
  catalog and Jinja configuration, with guidance for legacy rows.

### Fixed

- Reporting guidance now documents API-key bot mute control rather than
  describing it as dashboard-only.

## [1.7.0] — 2026-10-05

### Added

- `GET /client/text-chat-tools` (`ai_agents:read`), the tools a text agent
  may call in a chat, starting with `handoff_to_human`.
- The `text_chat_conversations:write` scope and its two routes, which turn the
  AI on or off for one text conversation: `PUT /client/chat-conversations/{uuid}`
  and `PUT /client/text-chats/{provider_type}/channels/{channel_identifier}/conversations/{provider_conversation_id}`.
- `references/text-chat-handoff.md`: what `handoff_to_human` does, the four
  questions to settle with a client before binding it, how the bot switch
  behaves, and why dashboard test chats cannot show a handoff.
- `references/voice-handoff.md`: the cold and warm transfer tools compared,
  what only Ingfah's team can configure (numbers, ring timeout, hold and
  no-answer messages), the questions to settle with a client, and how to
  verify a transfer from the call's messages.

### Fixed

- The revision guard now checks a text agent's `text_chat_tools`. Before, a
  prompt-only revision that omitted them silently unbound `handoff_to_human`.

## [1.6.0] — 2026-10-02

### Added

- `references/multi-agent-teams.md`: building a production team of agents
  that hand one call between them, from a four-agent helpline tuned on its
  first two days of real calls. It covers when to split (and giving an
  agent only the tools its job needs), how the platform runs a team (edges,
  handoff tools named `transfer_to_<target slug>`, who joins the call, tools
  staying per agent, the prompt rendered once at call start), the default
  and seamless handoff modes, the router/specialist line and return paths,
  the "taking over a call in progress" section every receiving agent needs,
  tool-only handoff turns, post-call results and automations across agents,
  the API steps, testing each agent and edge with the promptfoo template, a
  go-live checklist, and what to watch on the first real calls.
- What an API key cannot do for a team: create phone tools, set the handoff
  mode (an API-created team starts in default mode), or choose an agent's
  slug, so prompts naming handoff tools are written after the shells exist.

### Changed

- `agents-and-teams.md`, `testing.md`, `troubleshooting.md`, and the
  `SKILL.md` task table point to the new file; the team-splitting tips moved
  there.

## [1.5.1] — 2026-10-02

### Fixed

- `SKILL.md` frontmatter failed to parse as YAML, so the skill could not be
  installed. The unquoted `description` contained `: ` (in "Thai words: AI
  Agent Team"), which YAML reads as a new key. The value is now quoted.

## [1.5.0] — 2026-09-30

### Added

- Lessons from tuning live agents, written without client specifics:
  - `prompt-authoring.md`: branches and fallbacks (clear-but-unexpected answers,
    accept branches, a general no-information line, per-question mismatch
    branches, routing fixes, absolute-reading prohibitions, scoping
    contradictions), content that must be said despite interruptions,
    mishearing (letter/digit codes, no echo, saying the limit aloud, separate
    ladders), persuasion ladders, knowledge-base search (query wording, facts
    that suppress search, the two-search rule, a search check at the end of the
    task), one-line flow examples, the greeting's own rendering, concrete values
    in examples, asking for silence, no in-call summaries, computed numbers in
    say-as, price tables, scoped pronunciation rules, business-hours gates that
    fail closed, and where to place new text
  - `tools.md`: tools that ask the customer something, lookup keys, failed
    transfers, returning decisions instead of raw values, exception lists in
    descriptions, sending the day and time together to `resolve_date`, and a
    caveat on model-side `days_from_today` comparisons
  - `agents-and-teams.md`: splitting one agent into a team
  - `outcome-design.md`: the labels that go wrong most, and schema pitfalls
    (integer enums, stored field order, tool results visible to post-call
    steps but not webhooks)
  - `postprocessors.md`, `faq-authoring.md`, `troubleshooting.md`: instruction
    wording, fixing a repeatedly wrong entry, greeting hang-ups, and cut-off
    numbers from malformed say-as tags

### Changed

- The knowledge-base query guidance no longer suggests adding a brand name to
  queries; the company's own name measurably lowers retrieval.

- `references/testing.md` and `templates/promptfoo-suite/`: how to set up an
  automated conversation test suite for an agent with promptfoo. The template
  exports the agent and its tools through the client API, composes the prompt
  in the platform's order, plays whole conversations on the production model
  (`google/gemma-4-26b-a4b-it`, temperature 0.5, 768 output tokens), and tests
  the disposition outcomes on `google/gemini-3.1-flash-lite`. It includes
  reusable assertions (tool fired, silence after a transfer, no tool name
  spoken, spoken-Thai digit matching), a fictional example agent to check the
  setup, token and cost reporting, and guidance on keys, cost, what to test,
  and how to write assertions that survive run-to-run variation. Verified end
  to end: 8 conversations × 3 repeats and 4 disposition cases passing, with
  assertions confirmed to fail when their behaviour breaks.

## [1.4.0] — 2026-09-30

### Added

- `references/prompt-authoring.md`:
  - where the template engine (gonja v2.9.0) differs from Python Jinja, as a
    table of traps that fail silently, probed on the production version
  - how to parse `{{now}}` safely (its current shape, the non-breaking-space
    history, a validity check with a fallback), and a preference for `{{hour}}`
    and the other dedicated variables
  - computing derived values onto `customerContext` so the body stays
    cacheable
  - the 1024-character limit on `ai_instruction_identity`
  - silence after a successful transfer
  - "Scripted lines are copied, so scope them" and "How scripted to make it"
    (controlled variety as the default, with the measured cost of going fully
    free-form)
  - "Testing a change": re-test beyond the edited state, treat greeting edits
    as affecting every call, repeat a scenario before concluding, and a go-live
    checklist of guardrail and complaint cases
- `references/tools.md`: what `resolve_date` understands and returns, checked
  against the platform source: the phrase coverage, `thai_readback`, the two
  meanings of `needs_confirmation`, past dates, weekend-only `is_business_day`,
  and how to order the instruction.

## [1.3.0] — 2026-09-30

### Fixed

- Publishing a prompt edit could strip every tool from a live agent. A
  revision stores only the tool ids it is sent, and
  `GET /client/agents/{slug}/revisions/{id}` returns none, so a body rebuilt
  from the revision read unbound the transfer and hang-up tools. The agent
  then read `transfer_to_human_agent{}` aloud instead of transferring and
  could not hang up. `scripts/ingfah_api.py` now reads the agent before
  `POST /client/agents/{slug}/revisions` and refuses a body that omits
  `phone_tools` or `ai_plugin_function_ids`, drops an id the published agent
  uses, or has a flow state naming a tool that is not bound.
  `--allow-tool-drop` overrides it when removing a tool is the intended
  change.

### Added

- `references/agents-and-teams.md`: "Carry the tools into every revision",
  covering where the ids are read from, the preview and post-publish checks, and
  publishing by id when others edit the same agent.
- `references/troubleshooting.md`: the "reads a tool name aloud / promises a
  transfer that never happens / repeats its goodbye" complaint, in check order
  (bindings, the call's tool messages, then the prompt).
- `references/prompt-authoring.md`: "Tools in the prompt" (silent transfers,
  never quote a forbidden output, keep the tool description and prompt
  consistent), the `end_call_keyword` tool as a third requirement for
  hanging up, and two pre-publish checks.
- `references/tools.md`: a tool is callable only while bound, and a tool's
  description is part of every turn.

## [1.2.0] — 2026-09-30

### Added

- `references/troubleshooting.md` and a "When the user reports a problem"
  section in `SKILL.md`: they map what a user sees in the dashboard (a call
  title or summary, an outcome label, metadata, what the agent says, missed
  calls) to the setting that produces it, and describe how to consult before
  proposing a fix.
- `references/postprocessors.md` now explains what each post-call result type
  writes and where it shows up. It also notes that a `summary` postprocessor
  sets both the call title and the summary, and that a team without one falls
  back to a global default with no business context.
- Newly allowlisted API-key routes, confirmed against the backend router:
  - analytics (`analytics:read`): `/client/analytics/*` and
    `/client/text-analytics/*`, including the XLSX report download
  - text chats (`chat_sessions:read`): `/client/text-chats/conversations`
    and `/client/text-chats/chat-sessions-list` (plus CSV)
  - text channels (`client_products:read`): `/client/text-channel-configs`
    and the provider catalog, read only
  - customer templates (`client_outbound_options:write`): create, update,
    and delete `/client/outbound/options`
  - `GET /client/outbound/call-data-records`, for per-attempt SIP results
  - `GET /client/voices` and `POST /client/agents/{slug}/publish`
- `references/reporting.md` documents the analytics, text chat, and
  call-attempt routes.

### Changed

- Creating, editing, and deleting a customer template is no longer listed as
  dashboard-only. Only copying a template still is.

## [1.1.0] — 2026-09-30

### Added

- The skill now answers questions about Ingfah from a bundled copy of the
  public Thai user guide (คู่มือ, https://docs.ingfah.ai) in
  `references/user-guide/`, with an `INDEX.md` of every page. No API key is
  needed for questions.
- `scripts/sync_user_guide.py` regenerates that copy from the docs repository.
- `references/faq-authoring.md`: a workflow for writing, converting, and
  updating FAQ files for the knowledge base (คลังความรู้), grounded in how the
  knowledge base reads and chunks a file.
- `scripts/faq_lint.py` checks an FAQ file before upload and simulates where
  its chunks split, flagging answer lines that would be retrieved without
  their question. `--compare` catches tuning lost in an update.

## [1.0.2] — 2026-09-23

### Changed

- The Chat Automation reference no longer mentions client-specific webhook
  types, and the SMS example uses a placeholder provider URL.

## [1.0.1] — 2026-09-23

### Fixed

- The script now allows the three call recording routes `SKILL.md` already
  listed: `GET /client/chat-sessions/{uuid}/record`, `/record/download`, and
  `/record/checksum`. They were refused as outside the allowlist.
- Binary responses such as the Ogg recording are no longer decoded as text,
  which corrupted them. The script refuses to print one and saves it with the
  new `--output PATH` option, which never overwrites an existing file.

## [1.0.0] — 2026-09-23

First versioned release.

- Client API-key access to AI Agent Teams, agents and revisions, Tools, chat
  sessions, outbound templates and batches, postprocessors, and Chat
  Automation, restricted to an allowlist of routes.
- A `--confirm` gate on every `POST`, `PUT`, and `DELETE`.
- Guidance for writing agent prompts and designing disposition outcomes and
  outcome metadata.
- English and Thai dashboard names for every entity.
- The skill is named `ingfah` (previously `ingfah-skill`). Per-area detail
  moved from `SKILL.md` into `references/`, so less loads on every use.
- Install and update through the `skills` CLI; MIT license.

[1.7.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.7.0
[1.6.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.6.0
[1.5.1]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.5.1
[1.2.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.2.0
[1.1.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.1.0
[1.0.2]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.2
[1.0.1]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.1
[1.0.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.0
