// Reusable assertions. Reference one from a test as
//   { type: 'javascript', value: 'file://asserts.js:toolFired', config: { turn: 2, tool: 'transfer_to_human_agent' } }
// `turn` is 1-based and counts the user turns, not the greeting.
// Every failure names the turn and quotes what the agent said, so a red test
// can be read without opening the transcript.

const INVISIBLE = /[\s​-‍﻿⁠]/g;

function parse(output) {
  try {
    return JSON.parse(typeof output === 'string' ? output : JSON.stringify(output));
  } catch (e) {
    return null;
  }
}

function turnAt(data, turn) {
  return (data.turns || [])[turn - 1] || { assistant: '', toolCalls: [] };
}

function fail(turn, why, said) {
  return { pass: false, score: 0, reason: `turn ${turn}: ${why} | got: ${String(said || '').slice(0, 200)}` };
}

// Thai digit words → digits, so "ศูนย์สองหนึ่ง..." matches "021...".
const DIGITS = { ศูนย์: '0', หนึ่ง: '1', สอง: '2', สาม: '3', สี่: '4', ห้า: '5', หก: '6', เจ็ด: '7', แปด: '8', เก้า: '9' };
function digitsOf(text) {
  let t = String(text || '');
  for (const [w, d] of Object.entries(DIGITS)) t = t.split(w).join(d);
  return t.replace(/[^0-9]/g, '');
}

module.exports = {
  // The turn says at least one of `any` (spoken-register variants welcome).
  says(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn, any } = context.config;
    const said = turnAt(data, turn).assistant || '';
    return any.some((w) => said.includes(w)) ? true : fail(turn, `expected one of ${JSON.stringify(any)}`, said);
  },

  // The turn says none of `none`.
  avoids(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn, none } = context.config;
    const said = turnAt(data, turn).assistant || '';
    const hit = none.find((w) => said.includes(w));
    return hit ? fail(turn, `must not say "${hit}"`, said) : true;
  },

  // A phone number or other identifier is spoken, digit words allowed.
  saysDigits(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn, digits } = context.config;
    const said = turnAt(data, turn).assistant || '';
    return digitsOf(said).includes(digits) ? true : fail(turn, `expected the digits ${digits}`, said);
  },

  // The named tool was really called on this turn (a function call, not text).
  toolFired(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn, tool } = context.config;
    const t = turnAt(data, turn);
    return (t.toolCalls || []).some((c) => c.name === tool) ? true : fail(turn, `${tool} was not called`, t.assistant);
  },

  // No tool was called on this turn.
  noTool(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn } = context.config;
    const t = turnAt(data, turn);
    return (t.toolCalls || []).length ? fail(turn, `unexpected tool call ${JSON.stringify(t.toolCalls)}`, t.assistant) : true;
  },

  // The turn is silent (e.g. after a successful transfer).
  silent(output, context) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const { turn } = context.config;
    const t = turnAt(data, turn);
    if ((t.assistant || '').replace(INVISIBLE, '')) return fail(turn, 'expected silence', t.assistant);
    return (t.toolCalls || []).length ? fail(turn, 'expected no further tool call', JSON.stringify(t.toolCalls)) : true;
  },

  // Whole transcript: nothing spoken looks like a tool call or code.
  noToolText(output) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    for (const [i, t] of (data.turns || []).entries()) {
      const said = t.assistant || '';
      if (/[a-z]+_[a-z_]+|[{}]|<\/?[a-z_|]+>/i.test(said)) return fail(i + 1, 'tool name, code or markup spoken aloud', said);
    }
    return true;
  },

  // Whole transcript: no turn repeats the previous agent turn word for word.
  noVerbatimRepeat(output) {
    const data = parse(output); if (!data) return { pass: false, reason: 'unparseable transcript' };
    const said = (data.turns || []).map((t) => (t.assistant || '').replace(INVISIBLE, ''));
    for (let i = 1; i < said.length; i++) {
      if (said[i] && said[i] === said[i - 1]) return fail(i + 1, 'repeated the previous turn word for word', said[i]);
    }
    return true;
  },
};

module.exports.digitsOf = digitsOf;
