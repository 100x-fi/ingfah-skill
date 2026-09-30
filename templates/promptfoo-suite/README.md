# AI Agent conversation tests

Automated tests for one Ingfah AI Agent, run with [promptfoo](https://promptfoo.dev)
against the same models the platform uses. Set up by the Ingfah skill; the
full guide is the skill's `references/testing.md`.

Every run makes real model calls, billed to the key in `.env`.

| File | What it is |
|---|---|
| `agent.json` | the agent, exported with `GET /client/agents/{slug}`. Re-export after every publish |
| `tools.json` | the tools the model is offered, built by `npm run tools` from the exported tool files |
| `threads.js` | the conversations: one test per conversation |
| `asserts.js` | reusable checks (`says`, `toolFired`, `silent`, `noToolText`, ...) |
| `agent-provider.js` | plays each conversation against the model |
| `disposition/` | post-call outcome label tests (`product.json`, `cases.js`) |
| `example/` | a fictional agent for checking the setup works |

```bash
npm install
cp .env.example .env         # add your model API key
npm test                     # all conversations
npm run test:repeat          # 3 runs each: judge changes by repeats
npm run test:disposition     # outcome labels
npm run view                 # web report
```

Keep this repository private: `agent.json` contains the whole prompt. Replace
names, phone numbers, ID numbers and addresses before saving a real call as a
test.
