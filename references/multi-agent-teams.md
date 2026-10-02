# Building a multi-agent team

A team (ทีม AI Agent, `product`) can hold several agents that hand one call
between them. This file is how to design, build, test and launch one that
holds up on real calls. The API calls for agents and teams themselves are in
`references/agents-and-teams.md`; read that too.

The rules here come from a production build: a Thai disaster-claims helpline
split from one agent into four (a main agent that answers questions and
routes, two intake agents that take a claim on the call, and one that only
redirects a claim type that cannot be taken by phone). It went live on
2026-09-30 and was tuned on its first two days of real calls. Against the
single agent it replaced, on the same test suite run three times:

| | single agent | team |
|---|---|---|
| intake calls where the ID collection tool ran | 50/60 | 62/63 |
| claims complete enough for the CRM | 41/60 | 57/63 |
| tool calls spoken as text instead of called | 10 | 1 |
| knowledge-base answers correct | 39/39 | 39/39 |

The gain came from each agent having one job, a short prompt for that job, and
only the tools that job needs.

## When to split

Split when parts of the call need **different tools, a different first move,
or different hard rules**:

- a router or FAQ agent that must never collect personal data, and an intake
  agent whose first move is a keypad tool;
- a step whose rules contradict another step's ("never ask for the ID" in the
  FAQ part, "always collect the ID first" in the intake part);
- a path that must be impossible, not just discouraged. A claim type that can
  only be filed online kept getting an in-call intake from an agent that had
  the intake tools, whatever the prompt said. A specialist with **no intake
  tools** fixed it: give an agent only the tools its job needs, and it cannot
  do the job it must not do.

Do not split for a small branch a few lines of prompt can handle. Every agent
repeats the global rules, every handoff adds latency (the receiving agent's
first reply carries the whole conversation so far, the largest prompt of the
call), and every edge is another path to test.

## How the platform runs a team

**Edges are transferabilities.** A team's `transferabilities` list holds one
entry per direction, `{from_agent_id, to_agent_id, transfer_tool_description}`.
A return path is a second entry. `PUT /client/products/{id}` replaces the
whole list, so read the team first and send every edge.

**The handoff tool is minted from the edge, not bound to the agent.** For each
edge the source agent gets a tool named `transfer_to_` plus the **target's
slug** with `-` turned into `_` (target slug `acme-claims-intake` → tool
`transfer_to_acme_claims_intake`). It takes no arguments. Its description is
"Transfer the conversation to {target's vocal_name}." followed by the edge's
`transfer_tool_description`; with no description it says "Use this when the
user asks to speak with {vocal_name}", which routes almost nothing. So:

- always write a `transfer_tool_description`: when to use it, and whether the
  handoff is silent;
- write the minted tool name into the prompts exactly. A slug change renames
  the tool and silently breaks every prompt that names it;
- do not put handoff tools in `phone_tools` or `ai_plugin_function_ids`.

**Who is in the call.** The call holds the starting agent and every agent that
is the target of an edge. Every agent on an edge must have a published
revision of the team's channel type, or the team update is refused.

**Each agent keeps its own tools.** A handoff does not carry tools across.
Bind `end_call_keyword`, the human-transfer tool, the knowledge search and any
other tool on **every agent that needs it**, and carry them into every
revision as `references/agents-and-teams.md` describes. An agent with no
`end_call_keyword` cannot hang up, however good its goodbye.

**The prompt is rendered once, at call start.** Time variables (`hour`,
`dayOfWeek`) keep the call's start time after a handoff. A business-hours gate
must be in every agent's prompt, and every agent decides on the same clock.

### Handoff modes

The team's session config decides what a handoff sounds like:

| | Default | Seamless (`handoff.seamless`) |
|---|---|---|
| Source agent | speaks one more turn (a goodbye) before handing over | says nothing |
| Receiving agent's history | **empty**: it knows nothing said so far | the whole conversation, with its own prompt in place of the source's |
| Receiving agent's first turn | its greeting message | a reply generated from the history; the greeting is not spoken |
| To the caller | a new person picks up | one continuous agent |

The session config is **not readable or writable through the client API**. Ask
the Ingfah team which mode a team runs, or to turn seamless on. To check it
yourself, make a call that hands off and read it: a goodbye from the first
agent and a greeting from the second means default mode.

Design for the mode the team actually has:

- **Seamless** (recommended for one persona): the receiving agent's
  `greeting_message` is never spoken. The API still requires one, so give it
  a short neutral line. In the receiving agent's first turn the handoff tools
  are hidden (so it cannot bounce the call straight back), but its own tools
  are available, so its first turn can be a tool call.
- **Default**: the receiving agent starts with no history. It must ask again
  for anything it needs, and its greeting is the first thing the caller hears
  from it, so write it as the next step ("ขอเลขบัตรประชาชนนะคะ ..."), not a
  re-introduction.

In the inherited history, tool calls to tools the receiving agent does not
have are dropped, and the handoff call itself appears as a tool result. A
receiving agent without instructions reads that result as **its own**
transfer and apologises, says it is transferring, or defers. Every receiving
agent needs the section below.

## Designing the team

**Use a star.** One entry agent routes; each specialist hands back to it for
anything outside its job. Specialists do not hand to each other: every new
edge is another route a caller can be misrouted on.

**Draw the line between what the router asks and what the specialist asks.**
The router asks only the routing questions (which claim type; the owner, or
on someone's behalf) and then hands off. The specialist never re-asks them.
Write both sides down before writing prompts, and check them in tests:
production showed both failures, a router collecting intake data itself and a
specialist asking the claim type again.

**Write the routing step as ordered steps.** "Step 1: look in the history for
whether the caller is the owner or filing for someone (saying the house
flooded does not count). If not answered, this turn asks only that, and does
not call the handoff tool. Step 2: once answered, the next turn is only the
call to `transfer_to_…_household`." A one-line "ask X, then transfer" let the
router skip X when the caller came in with a direct request.

**Plan the return path for each specialist:**

- the caller changes their mind or wants a different path → hand back,
  silently;
- a question in the middle of the job → a short "I'll answer that once we
  finish", then the pending question; do not answer facts mid-job;
- a question **after** the job is done → answer it there. Give the specialist
  the knowledge-search tool for this. Without it, a specialist told callers
  "I have no information" after a completed claim;
- a new job, or something only the router does → hand back.

**Human transfer on every agent.** Bind the human-transfer tool, the
business-hours gate and the same transfer rules on every agent a caller can
be on when they ask for a person.

**Give each agent every destination its callers may need.** With one
transfer tool and a rule "transfer when asked for a human", every such caller
goes to that one destination. The order tools are listed in also steers the
choice: listing the right default first fixed a routing case a Bad/Good pair
did not.

**Name the agents for people.** Each agent's `description` (set through
`PUT /client/agents/{slug}/description`, no revision needed) should say its
team, its role, its first move and where it hands off, so the agents can be
told apart in the dashboard. `vocal_name` is how the handoff tool describes
the target to the model.

## Writing each agent's prompt

**Copy the global rules into every agent**: identity and persona, particles,
anti-repetition, the mishearing ladder, output format, content safety, AI
disclosure, the hang-up rules. One split dropped the anti-repetition rule and
the mishearing ladder from the specialists, and that caused half of the next
reported defects. Keep these sections byte-identical across agents and edit
them in all agents at once.

**One persona.** In a seamless team the caller hears one agent: same `name`,
same `voice_id`, same particles. Put the particles in variables
(`{{suffix}}`, `{{suffixQuestion}}`) with prompt defaults, so a persona change
is a variable change. The spoken lines inside tools (a keypad tool's request,
a human transfer's hold and no-answer messages) must match the persona too;
they are not in the prompt, so they are easy to miss.

**Give every receiving agent a "taking over a call in progress" section**, at
the top of the Task, marked to be read first. From the production build
(Thai, seamless mode):

```
## การเข้ารับสายต่อ (อ่านก่อนทุกส่วน)

คุณเข้าสู่สายที่ระบบส่งต่อมาแบบไร้รอยต่อ ในมุมมองของผู้โทร คุณคือ {{agentName}} คนเดิมที่คุยอยู่ด้วยตลอดสาย
- ห้ามแนะนำตัวใหม่ ห้ามทักทายใหม่ ห้ามบอกว่ามีการเปลี่ยนผู้ช่วยหรือมีการส่งต่อ
- การส่งต่อที่นำคุณเข้ามาสำเร็จเสมอ ผลของเครื่องมือ transfer_to_... ในประวัติคือการที่คุณเข้ามารับสาย ไม่ใช่การโอนสายของคุณ
- เทิร์นแรกของคุณห้ามบอกว่าทำไม่ได้ ห้ามเสนอโอนสายหาเจ้าหน้าที่ และห้ามเรียกเครื่องมือส่งต่อกลับ
- ผู้โทรตอบ <คำถามที่ผู้ช่วยหลักถามแล้ว> แล้ว ห้ามถามซ้ำ
- เทิร์นแรกหลังเข้าสายคือการเรียก <เครื่องมือแรก> อย่างเดียว ข้อความพูดว่างเปล่า
```

It says: you are the same agent the caller has been talking to; never
re-introduce yourself or mention a handoff; the handoff in the history is you
arriving, not your own transfer; on your first turn never refuse, offer a
human, or hand back; do not re-ask what the router asked; your first turn is
only the first tool call. An agent that should act before speaking works best
when that first turn is tool-only.

**A scope section per specialist**: what it does, what it hands back, what it
never does ("never invite the caller to file online again", "never answer
project facts mid-intake").

**Write handoff turns as tool-only, and describe them instead of scripting
them.** The Good line for a handoff is "เทิร์นนี้มีแค่การเรียกเครื่องมือ
transfer_to_… ข้อความพูดว่างเปล่า" (this turn is only the tool call; no
speech). A bracketed placeholder such as `[เรียก transfer_to_human_agent]` in
a Good example was spoken aloud as text in 4 test runs. In Bad examples,
describe the mistake ("transfers without knowing what the caller needs")
rather than quoting a line, or the model copies the quoted line.

**Put "skip what the caller already gave" inside each collection step**, not
in a separate rules section, and check the inherited history for it there.

**Gate data the specialist hands downstream.** Before the step that ends the
job (consent, the readback, the close), list the fields a downstream system
needs and ask for the missing one first. A claim reached the CRM with no
victim name because one branch went straight to consent; the gate at that step
fixed it where re-wording the earlier question did not.

## Post-call results and automations

The postprocessors read the whole call, every agent's part of it.

- **A call gets one disposition, however many paths it took.** The
  highest-ranked matching outcome wins. An SMS automation that triggered on
  the "send the SMS link" outcome never fired for a caller who accepted the
  SMS and then had a failed transfer attempt, because the transfer outcome
  ranked higher. **Trigger an automation on an outcome-metadata field** that
  is set whenever its event happened (`claim_channel = SMS link`), not on the
  disposition.
- **Define each metadata field for every path.** "Customer name" meant the
  caller on one path and the deceased on another; say so in the field's
  `description` (`references/outcome-design.md`).
- Several specialists feeding one CRM may need one automation per path, each
  with its own `trigger_condition` (`references/automations.md`).

## Building it through the API

Each step is a write: preview it and get confirmation before sending.

What an API key cannot do, so plan around it before promising a team:

- **Create phone tools.** `GET /client/phone-tools` lists the account's
  existing ones (end call, keypad collection, warm transfer to staff) and a
  revision can bind them, but a new one, with its own hold message or
  transfer number, is created by the Ingfah team. Plugin-function Tools can
  be created (`references/tools.md`).
- **Set the handoff mode.** A team created through the API gets the
  platform's default session config: assume default mode, and ask the Ingfah
  team to turn on seamless handoff if the team needs it.
- **Choose a slug.** `POST /client/agents` assigns the slug, so create every
  agent's shell first, read the slugs back, and only then write the prompts
  that name the `transfer_to_…` tools.

1. **Create and publish every agent** — shell, revision, publish, read back —
   per `references/agents-and-teams.md`. Bind each agent's own tools in its
   revision. Note each agent's numeric `id` and `slug`.
2. **Create the team** with the entry agent and the edges in one call. Every
   agent on an edge must already be published.
   ```json
   {
     "name": "Claims Helpline",
     "direction": "inbound",
     "channel_type": "audio",
     "visibility": "private",
     "starting_agent_id": 101,
     "transferabilities": [
       {"from_agent_id": 101, "to_agent_id": 102, "transfer_tool_description": "ส่งต่อผู้ช่วยรับแจ้งเคลมบ้านเสียหายในสาย เมื่อผู้โทรเลือกแจ้งในสายและตอบว่าบ้านเสียหาย เป็นการโอนแบบเงียบ"},
       {"from_agent_id": 102, "to_agent_id": 101, "transfer_tool_description": "ส่งผู้โทรกลับให้ผู้ช่วยหลัก เมื่อถามเรื่องอื่นหรือเปลี่ยนใจไม่แจ้งในสาย เป็นการโอนแบบเงียบ"}
     ]
   }
   ```
   To change an existing team, `PUT /client/products/{id}` with the **full**
   list.
3. **Read the team back** (`GET /client/products/{id}`). Each agent in
   `agents[]` lists its outgoing edges under `transferabilities` (target
   `agent_id`, `agent_vocal_name`, `transfer_tool_description`). Compare them
   with what you sent, and check each agent's `phone_tools` and
   `ai_plugin_functions` with `GET /client/agents/{slug}`.
4. **Confirm the handoff mode** with the Ingfah team (see "Handoff modes").
5. **Add the post-call results** (`references/postprocessors.md`) and any
   automations, triggered as above.
6. **Test** (next section), then assign the phone number in the dashboard.

## Testing a team

Test every agent alone and every edge. The template in
`templates/promptfoo-suite/` runs one agent per suite, so set up one suite per
agent (`references/testing.md`) and add the following.

**Add the handoff tools to `tools.json`.** `npm run tools` builds only bound
tools; the minted handoff tools are not bound. Append one entry per outgoing
edge, with the name and description the platform will generate:

```json
{"type": "function", "function": {"name": "transfer_to_acme_claims_intake", "description": "Transfer the conversation to <vocal_name>. <transfer_tool_description>", "parameters": {"type": "object", "properties": {}}}}
```

**Router suite:**

- each route: `toolFired` for the right `transfer_to_…` on the right turn,
  silent on that turn;
- the routing question is asked when it is missing and not when the caller
  already answered it;
- the nearest case it must **not** route: one test per neighbouring path, with
  `noTool` on the wrong handoff;
- no intake question before the handoff (`avoids` the ID or name request).

**Specialist suite (seamless):** replay the router's part as `script` turns,
ending with the handoff call and its result, then a turn with no `user`, which
is the specialist's first turn:

```js
const HANDOFF = [
  { role: 'assistant', content: '', tool_calls: [{ id: 'h1', type: 'function', function: { name: 'transfer_to_acme_claims_intake', arguments: '{}' } }] },
  { role: 'tool', tool_call_id: 'h1', content: '{"status":"success"}' },
];

thread('entry', 'first turn is the ID tool, no greeting', CALLER, [
  { user: 'บ้านน้ำท่วมค่ะ ขอแจ้งในสายเลย', script: [{ role: 'assistant', content: 'เป็นเจ้าของบ้านเองหรือแจ้งแทนผู้อื่นคะ' }] },
  { user: 'เป็นเจ้าของบ้านเองค่ะ', script: HANDOFF },
  { inject: [] },
], [
  js('toolFired', { turn: 3, tool: 'collect_id_card' }),
  js('avoids', { turn: 3, none: ['สวัสดี', 'โอนสาย', 'ส่งต่อ'] }),
]),
```

Then test each step of the job from there, the return edge (`toolFired` for
the handoff back when the caller changes their mind), a question mid-job
(deferred) and after the job (answered), and the data gate (a missing field
is asked before consent). For a default-mode team, start the specialist's
thread with no history instead, since that is what it will get.

**On the platform.** A test call (ทดลอง) is opened from one agent. Read its
transcript (`GET /client/agents/{slug}/chat-session-tests/{uuid}`) to see
whether the handoff ran; a handoff appears as a `role: tool` message named
`transfer_to_…`. Before the number goes to callers, make real calls to the
team that cross every edge.

**Replacing a single agent?** Run the same scenarios on both, interleaved and
repeated (`references/testing.md` → "Judging results"), and compare the
numbers that matter: the job's tool ran, the downstream record is complete,
no tool name spoken.

## Go-live checklist

- [ ] Every agent published; each one's `phone_tools` and
      `ai_plugin_functions` read back and complete, `end_call_keyword` on
      every agent that can end a call.
- [ ] Every edge in `GET /client/products/{id}`, in both directions where a
      return path is designed, each with a `transfer_tool_description`.
- [ ] Every `transfer_to_…` name in a prompt matches a target slug.
- [ ] Handoff mode confirmed, and the receiving agents written for it.
- [ ] Global rules identical in every agent; one persona across prompts,
      voice and tool messages.
- [ ] Business-hours gate in every agent.
- [ ] Router and specialist suites green on repeated runs; a real call has
      crossed every edge.
- [ ] Automations trigger on metadata fields, not only on the disposition.

## The first days of real calls

Read calls daily for the first days, each against these questions, then turn
each confirmed defect into a failing test before fixing it
(`references/testing.md` → "The working loop"):

- Did the handoff happen when it should, and only then? An agent that
  **says** it is transferring with no `transfer_to_…` tool message did not
  transfer.
- Did the router ask a specialist's questions, or a specialist re-ask the
  router's?
- Did any agent speak a tool name, a placeholder, or a search query aloud?
- Is the record complete enough for the system it feeds, and did the
  automation fire (check the receiving system)?
- Did the call end properly, on whichever agent the caller was with?

What the production build's first two days found, as patterns:

| Defect seen | Fix that held |
|---|---|
| Specialist called a covered event "not covered" after a garbled re-ask | skip a question the caller already answered; an unrecognisable answer is unclear, never a negative; a Bad/Good pair beside the question |
| Router said an opener, then typed its knowledge search as speech | ordered steps: search first, then speak, in one turn |
| A garbled turn made the specialist skip the name question | scope each re-ask to its own question; the next question after a readback is fixed |
| Proxy caller keyed in their own ID as the victim's | compare the two IDs and names before consent; ask once whose the first card is |
| Specialist answered "no information" after the job | give it the knowledge tool for after the job, keep the hand-back for new jobs |
| Online pitch repeated after the caller chose the phone | the pitch is said once per call, in one place, across all agents |

A fix that works on one agent can regress another: after each change run
every agent's suite, not only the one edited.
