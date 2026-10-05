# Handing a text chat to a person

Read this before giving a text (LINE, web chat) agent a way to hand a chat to
staff, before switching the AI on or off in a customer's conversation, and
before advising a client on either. For voice calls, read
`references/voice-handoff.md`.

Two pieces work together:

- **`handoff_to_human`**, a text chat tool the AI calls itself. The call turns
  the AI off for that conversation.
- **The bot switch**, two API routes that turn the AI on or off for one
  conversation from outside: a CRM, a ticketing system, or a script.

## The `handoff_to_human` tool

It is a global text chat tool, listed by `GET /client/text-chat-tools`
(`ai_agents:read`). The AI calls it with two arguments:

| Argument | Values |
|---|---|
| `reason` | `customer_requested_human`, `cannot_answer`, `sensitive_topic` |
| `summary` | a short factual summary of the chat for the staff member, up to 4000 characters |

When the AI calls it, the platform turns the AI off for that conversation in
the same transaction that records the AI's reply. The customer never sees the
handoff message while the AI is still on. The AI is told to say briefly, in
the customer's language, that a person will take over.

**A new agent does not get it automatically.** Bind it the way every tool is
bound: put its id in `text_chat_tools` on a new revision of a **text** agent,
then publish that revision. An audio agent's `text_chat_tools` are dropped.
`text_chat_tools` is one of the lists every later revision must re-send (see
`agents-and-teams.md` → "Carry the tools into every revision"). The script
refuses a text agent's revision that would drop it.

## What to settle with the client first

Ask these before binding the tool. Each answer changes the prompt or the setup.

1. **Who answers, and when?** After a handoff the AI stays silent until
   someone turns it back on. Nobody replies unless staff watch the Inbox. If
   the chat has no staff at night, the prompt must not promise an immediate
   reply. Have it say when a person will answer, or skip the handoff out of
   hours and collect a callback number instead.
2. **When should the AI hand off?** The three `reason` values are the
   platform's categories. Write the client's real triggers into the prompt
   under them: "asks to cancel the policy" → `customer_requested_human`, a
   complaint about a claim → `sensitive_topic`, and so on. A prompt that only
   says "hand off when needed" hands off too often or never.
3. **Who turns the AI back on?** Either an admin in the Inbox, or the
   client's system through the bot switch below when a ticket closes. Without
   an owner, handed-off conversations stay silent for good, and the customer's
   next question weeks later gets no answer.
4. **Does anything need to fire on a handoff?** As of backend `main` on
   2026-10-05, a handoff writes no automation event, so a Chat Automation
   cannot react to it yet. A client who needs a ticket opened should poll
   `GET /client/text-chats/conversations` for `bot_enabled: false` meanwhile.

## The bot switch

Scope `text_chat_conversations:write`. Both routes take `{"bot_enabled": true}`
or `{"bot_enabled": false}`, and with an API key nothing else (any other field
is a `400`).

- `PUT /client/chat-conversations/{uuid}` names the conversation by Ingfah's
  UUID, from `GET /client/text-chats/conversations`.
- `PUT /client/text-chats/{provider_type}/channels/{channel_identifier}/conversations/{provider_conversation_id}`
  names it by the provider's own ids, so a client's system can call it
  without looking up the UUID. Only Boonterm conversations carry a provider
  conversation id. This route is API-key only.

Behaviour, both routes:

- `true` lets the AI answer again and releases the admin answering by hand.
- `false` stops the AI and leaves the handling admin as they are.
- Sending the value the conversation already has changes nothing, so a
  client's system can safely retry.
- Another client's conversation, or one not found on the channel, is a `404`.

The response is `{id, bot_enabled, handling_admin_id}`.

Turning the AI off or on changes what a real customer experiences. Confirm
with the user before every call, naming the conversation.

## Testing a handoff

Chat-session tests (`GET /client/agents/{slug}/chat-session-tests`) never
offer text chat tools to the AI, so a test run cannot show a handoff
happening. Test the decision in promptfoo instead (`references/testing.md`).
Give the model the tool's schema and assert it calls `handoff_to_human` with
the right `reason` on the client's trigger phrases, and does not call it on
ordinary questions. Then try one real chat on a staging channel before go-live.
