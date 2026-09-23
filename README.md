# Ingfah agent skill

[![test](https://github.com/100x-fi/ingfah-skill/actions/workflows/test.yml/badge.svg)](https://github.com/100x-fi/ingfah-skill/actions/workflows/test.yml)
[![skills.sh](https://img.shields.io/badge/skills.sh-ingfah-black)](https://skills.sh/100x-fi/ingfah-skill/ingfah)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An agent skill, named `ingfah`, for working with the [Ingfah](https://ingfah.ai)
client API using a client API key. It lets a coding agent such as Claude Code
inspect and manage AI Agent Teams, AI agents and their revisions, Tools, calls
and chats, outbound batches, post-call results, and Chat Automation — in
English or Thai, using the dashboard's own words.

The skill restricts the agent to a documented allowlist of client API routes,
requires explicit confirmation before anything is created, changed, or deleted,
and keeps the API key out of files, logs, and command output.

## What it looks like

An illustrative exchange:

> **You:** หยุด Batch 7 ไว้ก่อน
>
> **Agent:** Batch 7 "ลูกค้าค้างชำระ ก.ย." is **กำลังดำเนินการ** — 412 of 1,000
> records called. Pausing stops calls that have not started; a call already in
> progress runs to its end. Pause it?
>
> **You:** ok
>
> **Agent:** Paused. It is now under the **หยุดชั่วคราว** tab on สายออก →
> รายการ Batch. Say "resume batch 7" to continue.

Every write goes through the same pattern: read the current state, show what
will change, wait for a yes, send it, then read it back.

## What's in here

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill itself: routes, scopes, naming, and the rules that apply to every task |
| `scripts/ingfah_api.py` | Dependency-free request script; enforces the allowlist and the confirmation gate |
| `references/agents-and-teams.md` | Creating and editing agents, revisions, and AI Agent Teams |
| `references/prompt-authoring.md` | How to write an agent's identity, task, and conversation flow |
| `references/outbound-batches.md` | Creating and controlling outbound batches |
| `references/tools.md` | Phone tools and plugin functions |
| `references/postprocessors.md` | The disposition and outcome metadata API |
| `references/outcome-design.md` | How to design disposition outcomes and an outcome metadata schema |
| `references/automations.md` | Chat Automation: webhooks and do-not-contact |
| `references/dashboard-terms.md` | Field-level English and Thai dashboard names |
| `tests/` | Unit tests for the script |

The agent reads `SKILL.md` every time the skill is used, and opens a reference
file only when the task needs it.

## Requirements

- Python 3.9+ (standard library only — no packages to install)
- An Ingfah client API key, with the scopes for what you intend to do

## Install

Install with the [`skills`](https://skills.sh) CLI, which pulls straight from
this repository's `main` branch:

```bash
npx skills add 100x-fi/ingfah-skill -g            # personal, every project
npx skills add 100x-fi/ingfah-skill               # this project only
```

Start a new session afterwards — skills are discovered at startup. Confirm it
loaded by asking the agent to list your Ingfah products.

The CLI detects Claude Code and other `SKILL.md`-style agents and links the
skill into each one's skills directory. The skill has no tool-specific
dependencies — the agent only needs to be able to run
`python3 scripts/ingfah_api.py`.

### From a git clone

To work on the skill itself, clone it and link it in instead. Linking rather
than copying means `git pull` updates the installed skill.

```bash
git clone git@github.com:100x-fi/ingfah-skill.git ~/src/ingfah-skill
mkdir -p ~/.claude/skills
ln -s ~/src/ingfah-skill ~/.claude/skills/ingfah
```

## Providing the API key

The script reads `INGFAH_API_KEY` from the environment. Give it to the agent
for the session only:

```bash
INGFAH_API_KEY='sk-ing-...' claude
```

The skill instructs the agent never to write the key to a file, commit it,
include it in a command it shows you, or echo it in output. Do not put it in
this repository or in a `.env` file inside it.

The base URL defaults to `https://api.ingfah.ai`. Override it with
`INGFAH_API_BASE_URL` when working against another deployment; it must be
HTTPS.

## Verify the install

```bash
cd ~/src/ingfah-skill
python3 -m unittest tests.test_ingfah_api          # 17 tests, no network
INGFAH_API_KEY='sk-ing-...' python3 scripts/ingfah_api.py GET /client/products
```

The first command needs no key and no network. The second makes one real
read-only request.

## Safety model

- **Route allowlist.** Only the routes listed in `SKILL.md` are callable.
  Anything else — backoffice routes, API-key management, JWT-only routes —
  is refused by the script before a request is made.
- **Confirmation gate.** Every `POST`, `PUT`, and `DELETE` requires
  `--confirm`, and the skill requires the agent to preview the change and get
  your explicit go-ahead first.
- **Real-world effects.** Creating an outbound batch places real calls to real
  people. Publishing an agent revision changes how a live agent speaks to
  customers. Both are gated, but the gate is only as good as the preview you
  read — read it.

## Updating

Update by hand:

```bash
npx skills update ingfah
```

Or keep it current automatically with a Claude Code `SessionStart` hook in
`~/.claude/settings.json`. The hook runs before each session starts, outside
the agent's context, so it costs no tokens:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "npx -y skills update -g -y >/dev/null 2>&1 || true" }
        ]
      }
    ]
  }
}
```

This updates every globally installed skill, not just this one. If an update
lands after the session has loaded its skills, it takes effect in the next
session.

For a git clone, use `git -C ~/src/ingfah-skill pull --ff-only -q || true` as
the hook command instead.

## Contributing

Issues and pull requests are welcome. Run the tests before opening a pull
request; CI runs them on Python 3.9 and 3.13. Report security problems
privately — see [SECURITY.md](SECURITY.md). Changes are recorded in
[CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE) © 100X
