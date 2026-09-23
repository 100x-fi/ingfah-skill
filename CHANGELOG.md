# Changelog

All notable changes to this skill are recorded here. Versions follow
[Semantic Versioning](https://semver.org/); the version is also sent in the
request `User-Agent` as `ingfah-skill/<version>`.

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

[1.0.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.0
