# Security policy

This skill handles Ingfah client API keys and can place real outbound calls,
publish live agents, and send customer data to webhooks. Please report any way
to get around its guardrails privately.

## Reporting a vulnerability

Use GitHub's private reporting: **Security → Report a vulnerability** on
<https://github.com/100x-fi/ingfah-skill/security/advisories/new>. Do not open
a public issue.

Worth reporting, for example:

- a request that reaches a route outside the allowlist in `SKILL.md`
- a mutation that goes through without `--confirm`
- an API key, webhook header, or `hmac_secret` appearing in output, logs, or
  files
- instructions in `SKILL.md` or `references/` that lead an agent to leak data
  or act without confirmation

Vulnerabilities in the Ingfah platform or API itself are out of scope here;
report those to the Ingfah team.

## Supported versions

Only the latest commit on `main` is supported. Installs through the `skills`
CLI track `main`, so a fix reaches users on their next update.
