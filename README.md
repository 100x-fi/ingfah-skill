# ingfah-skill

An agent skill for working with the [Ingfah](https://ingfah.ai) client API using
a client API key. It lets a coding agent inspect and manage Ingfah products, AI
agents and their revisions, chat sessions, outbound batches, and post-call
disposition outcomes and outcome metadata.

The skill restricts the agent to a documented allowlist of client API routes,
requires explicit confirmation before anything is created, changed, or deleted,
and keeps the API key out of files, logs, and command output.

## What's in here

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill itself: routes, scopes, and the rules the agent follows |
| `scripts/ingfah_api.py` | Dependency-free request script; enforces the allowlist and the confirmation gate |
| `references/prompt-authoring.md` | How to write an agent's identity, task, and conversation flow |
| `references/outcome-design.md` | How to design disposition outcomes and an outcome metadata schema |
| `tests/` | Unit tests for the script |

## Requirements

- Python 3.9+ (standard library only — no packages to install)
- An Ingfah client API key, with the scopes for what you intend to do

## Install

Clone the repository somewhere permanent, then link it into your agent's
skills directory. Linking rather than copying means `git pull` updates the
installed skill.

### Claude Code

Personal skill, available in every project:

```bash
git clone git@github.com:100x-fi/ingfah-skill.git ~/src/ingfah-skill
mkdir -p ~/.claude/skills
ln -s ~/src/ingfah-skill ~/.claude/skills/ingfah-skill
```

Or scoped to one project, for a repo where the whole team should have it:

```bash
mkdir -p .claude/skills
git clone git@github.com:100x-fi/ingfah-skill.git .claude/skills/ingfah-skill
```

Start a new session afterwards — skills are discovered at startup. Confirm it
loaded by asking the agent to list your Ingfah products.

### Other agents

Any agent that reads `SKILL.md`-style skills works the same way: place or link
the directory wherever that tool looks for skills. The skill has no
tool-specific dependencies — the agent only needs to be able to run
`python3 scripts/ingfah_api.py`.

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
python3 -m unittest tests.test_ingfah_api          # 16 tests, no network
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

```bash
cd ~/src/ingfah-skill && git pull
```

Restart your agent session to pick up the changes.
