# Handing a voice call to a person

Read this before giving a voice agent a way to transfer a call to staff, and
before advising a client on how a transfer should work. The text-chat
counterpart is `references/text-chat-handoff.md`.

## The two transfer tools

Both are phone tools (`GET /client/phone-tools`), bound through a revision's
`phone_tools`. Neither takes arguments, so the AI cannot pass a reason or a
summary. When the AI calls the tool, the tool's description in its row is all
it has to go on. The prompt must say when to transfer.

| | Cold transfer (`transfer_sip_call`) | Warm transfer (`warm_transfer_to_human`) |
|---|---|---|
| Caller hears | a dial tone | an optional hold notice, then hold music |
| Staff member hears | the call ringing, with no context | an AI briefing that summarises the call, then is asked whether to connect |
| Numbers | one | one, or a list tried in order |
| Staff busy or not answering | the AI cannot tell; the call is gone | the next number is tried; when all fail the caller hears "all lines are busy" and stays with the AI |
| Staff declines | n/a | the caller stays with the AI |

Recommend the warm transfer unless the client has a reason not to. The
staff member starts with context, and a missed transfer does not drop the
caller.

## What only Ingfah's team can set

An API key can read phone tools but not create or edit them. The transfer
number lives on the tool itself, not on the agent, so two agents that must
reach different numbers need two tool rows. Ask Ingfah's team (backoffice)
for any of these:

- the number or numbers to dial, and `target_dtmf` to reach an extension or
  an IVR path after the line answers;
- `ring_timeout_seconds` (default: none). **A list of numbers needs it.**
  Without it the first number rings forever and the rest are never tried;
- `timeout_seconds`, an overall ceiling (default: none). It covers a staff
  member who answers but never confirms;
- the hold notice, hold music, the message spoken when nobody answers, and
  extra briefing instructions;
- `transcribe_after_merge` (default off). Turn it on only when the client
  needs a transcript of the human part of the call; it roughly doubles
  speech-to-text cost.

## What to settle with the client first

1. **Who answers, at which number, and in which hours?** Get real numbers. A
   direct line or a mobile works best. A queue or IVR number may make the AI
   brief into hold music.
2. **What happens out of hours or when everyone is busy?** The caller stays
   with the AI after a failed warm transfer. The prompt must then say what to
   offer: a callback, a LINE contact, office hours. Otherwise the AI improvises.
3. **When should the AI transfer?** List the client's real triggers in the
   prompt: asked for a person twice, a complaint, a request the agent cannot
   handle. Also say when it must *not* transfer, such as a question the
   knowledge base answers.
4. **Does the client need a record?** A warm transfer's result (`success`,
   `no_answer`, `error`, `aborted`) is stored as the tool's response in the
   call's messages. Design an outcome or postprocessor around it if the
   client reports on transfers (`references/outcome-design.md`).

## Verifying a transfer

- Read the call's messages (`GET /client/chat-sessions/{uuid}`). A real
  transfer is a `role: tool` message named after the tool. The AI *saying*
  it is transferring, with no tool message, means the tool was not bound or
  not called (see `references/troubleshooting.md`).
- Before go-live, place one real call per number on the list, including one
  where nobody answers, to hear the fallback message.
