// Builds the classifier request from the team's real disposition settings.
//
// Save the team first: GET /client/products/{id} --output product.json (in this
// folder). Its `postprocessors` entry with type "disposition" holds the outcome
// names, each outcome's criteria (`prompt`), and the business `instruction`.
//
// The platform wraps these in its own default classifier prompt, which is not
// exported. This generic wrapper tests what the team controls: whether the
// outcomes and their criteria separate real calls cleanly.

const fs = require('fs');
const path = require('path');

const product = (() => {
  const raw = JSON.parse(fs.readFileSync(path.join(__dirname, 'product.json'), 'utf8'));
  return raw.data !== undefined ? raw.data : raw;
})();
const pp = (product.postprocessors || []).find((p) => p.type === 'disposition');
if (!pp) throw new Error('product.json has no disposition postprocessor');

module.exports = function ({ vars }) {
  const outcomes = [...(pp.disposition_outcomes || [])]
    .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
    .map((o) => `- "${o.outcome}": ${o.prompt}`)
    .join('\n');
  const system = [
    'You label a finished phone call between an AI agent and a customer with exactly one outcome.',
    `Outcomes (name: when to choose it):\n${outcomes}`,
    pp.instruction ? `Additional instruction:\n${pp.instruction}` : '',
    'Reply with JSON only: {"outcome": "<one outcome name exactly as written>", "reason": "<one sentence>"}',
  ].filter(Boolean).join('\n\n');
  return [
    { role: 'system', content: system },
    { role: 'user', content: `Call transcript:\n${vars.transcript}` },
  ];
};
