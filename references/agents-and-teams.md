# Agent handling

Agent metadata and agent behaviour are changed through two different paths.
Choose deliberately and say which one is being used.

- `PUT /client/agents/{slug}/profile`, `/description`, and `/visibility` change
  metadata and **take effect immediately, without creating a revision**.
- Behaviour changes go through the revision workflow: draft with
  `POST /client/agents/{slug}/revisions`, then
  `POST /client/agents/{slug}/revisions/{id}/publish`.

## Creating an agent

Creating a working agent is three calls, not one. `POST /client/agents` only
creates the shell: the prompt fields sent with it are **not stored**, so the
agent reads back with an empty `name`, identity, task, and flow. Always
complete all three steps and verify by reading the agent back.

Every prompt this skill writes must be **cache-safe**: the prompt body is
identical for every customer, and per-call data is referenced by name rather
than written in. Leave `prompt_engine_version` at its default on a new agent,
and keep an existing agent's version unchanged. See
`references/prompt-authoring.md` for the rules, what `{{customerContext.*}}`
renders to, and how to branch on customer data with Jinja.

1. `POST /client/agents` — creates the shell. Requires `visibility`
   (`private` or `public`); `prompt_engine_version` defaults to `v3`.
   Keep the returned `slug` and numeric `id`.
2. `POST /client/agents/{slug}/revisions` — carries the actual prompt
   (`name`, `vocal_name`, `greeting_message`, `ai_greeting_message`,
   `ai_instruction_identity`, `ai_instruction_task`, `ai_instruction_flow`,
   `voice_id`), then publish it. Nothing is live until published. A revision
   also carries `voice_speed` (a multiplier, `1` is normal — the dashboard's
   ความเร็วในการพูด) and `ai_instruction_variables`, the agent-level variables
   the dashboard edits under the `{}` icon: values reused across the prompt,
   such as a brand name, a discount code, or the politeness particle, written
   as `{{name}}`. `{{agentName}}` is always available and is the agent's
   `name`.
3. `POST /client/products` — an agent cannot take or place calls on its own. A
   product is the callable team that routes to it. Pass the agent's numeric
   `id` as `starting_agent_id`, plus `name`, `direction` (`inbound` or
   `outbound`), `channel_type` (`audio` or `text`), and `visibility`.

The product is also where disposition outcomes and outcome metadata live, so
an agent without one has no post-call labelling either. When a user asks for a
new agent, create the product as part of the same task and say so; ask first
only if an existing product should be reused instead.

Rules:

- Read `GET /client/agents/{slug}` and `GET /client/agents/{slug}/revisions`
  before editing, and show the user what is changing from what.
- After any create or publish, read the agent or revision back and confirm the
  fields actually stored. Do not report success from the write response alone.
- Publishing a revision changes how a live agent talks to real customers. Treat
  it like outbound batch creation: preview the change and get explicit
  confirmation immediately before publishing.
- Creating a draft revision is not live until published (`published_at` is
  `null`). Say so, so the user knows a draft alone changes nothing.
- A revision is a full snapshot of the agent's configuration, not a patch. Read
  the latest revision with `GET /client/agents/{slug}/revisions/{id}`, change
  the fields being edited, and post the whole body back. `name`,
  `greeting_message`, and `ai_greeting_message` are required; a revision read
  returns `greeting_message` and a nested `voice` object, so map
  `voice.id` to `voice_id` when reposting. **The tool bindings are not in the
  revision read at all** — see "Carry the tools into every revision" below.
- **Publish the revision you verified, and re-read just before publishing.**
  Several people can edit the same agent within minutes (one agent took six
  publishes in two hours on 2026-09-30). Publish by id
  (`POST .../revisions/{id}/publish`), which fails if someone drafted after
  you; if the published revision changed since you read it, start again from
  the new one rather than posting your older copy over their change.
- Deleting a revision is a soft delete: it comes back `status: deleted` with
  `deleted_at` set, and it still appears in the revisions list and is still
  readable by id. Filter on `status` before reporting a revision list, and do
  not describe the delete as permanent removal.
- `DELETE /client/agents/{slug}/revisions/{id}` and `DELETE /client/agents/{slug}`
  are destructive and need explicit confirmation.
- Visibility is creator-only: the API key acts as the admin it belongs to, so a
  key whose admin did not create the agent gets `403` even with
  `ai_agents:write`. Report that as a permission rule, not an auth failure.
- A **private / ส่วนตัว** agent is visible only to its creator and to Owners.
  Operators see public agents and their own. When a teammate says they cannot
  find an agent, check its visibility first.
- Publishing replaces the published version and the draft disappears. In the
  dashboard, a new draft is started with **ร่างใหม่จากเผยแพร่**, which copies
  the published version — the same as reading the latest revision and posting
  it back.
- The greeting cannot be interrupted: the caller hears all of it before the
  agent starts listening. Keep it short.

## Carry the tools into every revision

A revision stores exactly the tool ids it is sent, and **an omitted list means
no tools**. This is the most damaging silent mistake in the revision workflow,
because the prompt reads back perfectly and the agent still breaks on the
next call.

| Revision body key (write) | Where the current ids are (read) | Dashboard |
|---|---|---|
| `phone_tools` — ids | `GET /client/agents/{slug}` → `phone_tools[].id` | Tools เกี่ยวกับการโทร |
| `ai_plugin_function_ids` — ids | `GET /client/agents/{slug}` → `ai_plugin_functions[].id` | Tools ทั่วไป |

`GET /client/agents/{slug}/revisions/{id}` returns **neither** list. A body
built only from the revision read — the obvious "read, edit the prompt, post
it back" — unbinds every tool.

**What it looked like in production (2026-09-30).** A prompt-only edit was
published this way. The agent lost its transfer tool and `end_call_keyword`.
For the next two hours it told callers "เดี๋ยวผมโอนสายให้เจ้าหน้าที่นะครับ
transfer_to_human_agent{}" — reading the tool's name aloud — and never
transferred. It also repeated its goodbye because nothing could hang up the call.
7 of the next 11 calls were affected. The revision read back looked correct.

Rules:

1. **Before drafting**, read `GET /client/agents/{slug}` and copy
   `phone_tools[].id` and `ai_plugin_functions[].id` into the body as
   `phone_tools` and `ai_plugin_function_ids`. Send them even when unchanged,
   and even when empty on purpose.
2. **Every tool a flow state names must be bound.** A state's
   `guidelines.plugin_functions[].id` must be in `ai_plugin_function_ids`, and
   its `guidelines.phone_tools[].id` in `phone_tools`, or that state cannot
   call it.
3. **`scripts/ingfah_api.py` enforces 1 and 2.** On
   `POST /client/agents/{slug}/revisions` it reads the agent first and refuses
   a body that omits either list, drops an id the published agent uses, or
   names a state tool that is not bound. Pass `--allow-tool-drop` **only**
   when removing a tool is the change the user asked for, and name the tool
   being removed in the preview.
4. **Show the tool lists in the preview** next to the prompt diff: "Tools
   stay: transfer_to_human_agent, end_call_keyword, …". A user can catch a
   missing tool there; they cannot catch it in a prompt diff.
5. **After publishing**, read `GET /client/agents/{slug}` again and compare
   `phone_tools` and `ai_plugin_functions` with what you sent. The create
   response also echoes the revision's `phone_tools`. Report a mismatch
   instead of success.
6. **After the next real call**, open it (`GET /client/chat-sessions/{uuid}`):
   a transfer shows as a message with `role: tool` and
   `tool_name: transfer_to_human_agent`. The agent announcing a transfer with
   no such message means the tool did not run.

A voice agent that should hang up needs `end_call_keyword` bound as well as
the `end_call_keyword` flag on its terminal state (see
`references/prompt-authoring.md` → Ending the call). A new agent does not get
it automatically. Text agents take no phone tools; the server drops them.

# AI team (product) handling

A `product` is what the dashboard calls an **AI Agent Team / ทีม AI Agent**.
Beyond creation it can be read, updated, made public or private, and deleted.

- `PUT /client/products/{id}` takes `name`, `description`,
  `starting_agent_id`, `channel_type`, and `transferabilities`. `channel_type`
  is accepted only when it equals the current value — changing it returns
  `400`. `starting_agent_id` must name an agent with a published revision that
  matches the team's channel type. `transferabilities`, when present, replaces
  the whole list rather than appending to it.
- `PUT /client/products/{id}/visibility` takes `{"visibility": "private"|"public"}`.
  Like agent visibility, only the admin who created the team may change it: a
  key belonging to another admin gets `403` even with `client_products:write`.
- `DELETE /client/products/{id}` is refused with `422` while a phone number is
  assigned to the team or one of its outbound batches is still active. Take the
  number off and cancel the batch first; report the `422` as a state rule, not
  a permission problem.

- `direction` is fixed at creation: `PUT` does not take it, and the dashboard
  warns that a team type cannot be changed later. Confirm inbound vs outbound
  before creating.
- Every agent in a voice team must be a published voice agent. One agent can
  belong to several teams, and an agent that takes over a transferred call
  keeps the conversation so far.
- Split work across agents rather than overloading one: a first agent that
  asks the language or the topic, then transfers to a specialist with its own
  knowledge. When splitting an existing agent into a team:
  - **copy the global rules into every agent.** One split dropped the
    anti-repetition rule and the mishearing ladder from the specialists, and
    that caused half of the next reported defects;
  - **give each receiving agent a "taking over a call in progress" section**,
    or it reads the handoff as its own transfer and apologises or defers;
  - an agent that should act before speaking works best when its first turn is
    tool-only;
  - put "skip what the customer already gave" inside the collection steps
    themselves, not in a separate rules section;
  - **give each agent every transfer destination its callers may need.** With
    one transfer tool and a rule "transfer when asked for a human", every such
    caller goes to that one destination. The order tools are listed in also
    steers the choice: listing the right default first fixed a routing case a
    ❌/✅ pair did not. Each agent's `vocal_name` is how the others refer to it when
  transferring.
- An inbound team takes calls only once a phone number is assigned to it,
  which is done in the dashboard (see **Dashboard-only tasks** in `SKILL.md`).

Deleting a team removes the callable route to its agent and its
postprocessors. Confirm explicitly before updating, changing visibility, or
deleting, and name the team being affected.
