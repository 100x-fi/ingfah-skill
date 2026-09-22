---
name: ingfah-skill
description: Interact with the Ingfah client platform through client API-key authenticated APIs. Use this skill when the user asks to inspect or manage Ingfah products, AI agents, chat sessions, or outbound batches. Do not use backoffice APIs or JWT-only client APIs.
---

# Ingfah client API

Use the user's Ingfah client API key to call only the client API routes listed below.

The default Ingfah API base URL is `https://api.ingfah.ai`. Use another base URL only when the user explicitly provides one.

## Authentication

- Send the key only in the `X-Api-Key` request header.
- If no key is available, ask the user to provide their Ingfah client API key.
- Never echo, log, save, commit, or include the key in generated files, URLs, or error messages.
- Do not ask the user to put the key in this repository.
- Treat the key as available only for the current task unless the user explicitly requests persistent configuration.
- Use HTTPS and the configured Ingfah API base URL.
- Before making a request, explain when the requested operation requires a write scope.
- Ask for explicit confirmation immediately before creating, deleting, pausing, resuming, or cancelling anything.
- Redact secrets from all displayed request and response details.

## Client API-key scopes and routes

### `client_products:read`

- `GET /client/ai-agent-teams`
- `GET /client/disposition-outcomes`
- `GET /client/ai-agent-teams/{id}/customer-context-variables`
- `GET /client/products`

### `ai_agents:read`

- `GET /client/ai-agents`
- `GET /client/agent-templates`
- `GET /client/agents/{slug}`
- `GET /client/agents/{slug}/revisions`
- `GET /client/agents/{slug}/revisions/{id}`

### `ai_agents:write`

- `POST /client/agents`
- `DELETE /client/agents/{slug}`

### `chat_sessions:read`

- `GET /client/chat-sessions`
- `GET /client/chat-sessions/{uuid}`
- `GET /client/chat-sessions/{uuid}/record`
- `GET /client/chat-sessions/{uuid}/record/download`
- `GET /client/chat-sessions/{uuid}/record/checksum`
- `GET /client/chat-sessions-list`
- `GET /client/chat-sessions-list/csv`
- `GET /client/agents/{slug}/chat-session-tests`
- `GET /client/agents/{slug}/chat-session-tests/{uuid}`

### `client_outbound_options:read`

- `GET /client/outbound/options`
- `GET /client/outbound/options/{id}`

### `client_outbound_batches:read`

- `GET /client/outbound/batches/{id}`
- `GET /client/outbound/batches/{id}/records`
- `GET /client/outbound/batches/{id}/records/download`

### `client_outbound_batches:write`

- `POST /client/outbound/batches`
- `POST /client/outbound/batches/{id}/pause`
- `POST /client/outbound/batches/{id}/resume`
- `POST /client/outbound/batches/{id}/cancel`

## Scope handling

Before calling an endpoint, identify its required scope and check the user's intended action against that scope. If the API returns an authorization or insufficient-scope error, explain the missing scope without exposing the API key.

Do not call backoffice routes, API-key management routes, or client routes not listed in this file. Do not infer that a JWT-only route is available to an API-key caller.

## Response handling

Return concise, structured summaries. Preserve identifiers, statuses, timestamps, and relevant error details, but remove credentials and unrelated personal or sensitive data. For downloads, save or present the result only when the user explicitly requests it.
