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
  `voice.id` to `voice_id` when reposting.
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
  knowledge. Each agent's `vocal_name` is how the others refer to it when
  transferring.
- An inbound team takes calls only once a phone number is assigned to it,
  which is done in the dashboard (see **Dashboard-only tasks** in `SKILL.md`).

Deleting a team removes the callable route to its agent and its
postprocessors. Confirm explicitly before updating, changing visibility, or
deleting, and name the team being affected.
