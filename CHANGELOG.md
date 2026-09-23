# Changelog

All notable changes to this skill are recorded here. Versions follow
[Semantic Versioning](https://semver.org/); the version is also sent in the
request `User-Agent` as `ingfah-skill/<version>`.

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

[1.0.2]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.2
[1.0.1]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.1
[1.0.0]: https://github.com/100x-fi/ingfah-skill/releases/tag/v1.0.0
