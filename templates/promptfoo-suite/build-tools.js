// Builds tools.json — the function schemas the model is offered — from the
// agent's real tool bindings.
//
// Save these first (see references/testing.md):
//   agent.json                  GET /client/agents/{slug}
//   phone-tools.json            GET /client/phone-tools?ids=<agent.phone_tools ids>
//   plugin-functions/<id>.json  GET /client/plugin-functions/{id}, one per agent.ai_plugin_functions id
//
// Run: node build-tools.js
//
// Phone tools that work by listening for a phrase (end_call_keyword and
// similar, which carry `params.keywords`) are not functions the model calls,
// so they are left out. Transfer-type phone tools take no arguments.

const fs = require('fs');
const path = require('path');

const dir = __dirname;
const read = (f) => {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  return raw && raw.data !== undefined ? raw.data : raw;
};

const agent = read('agent.json');
const boundPhone = new Set((agent.phone_tools || []).map((t) => t.id));
const boundFns = new Set((agent.ai_plugin_functions || []).map((f) => f.id));
const tools = [];

if (fs.existsSync(path.join(dir, 'phone-tools.json'))) {
  for (const t of read('phone-tools.json')) {
    if (!boundPhone.has(t.id)) continue;
    if (t.params && Array.isArray(t.params.keywords)) continue; // phrase listener, not a callable function
    tools.push({
      type: 'function',
      function: { name: t.name, description: t.description || '', parameters: { type: 'object', properties: {} } },
    });
  }
}

const fnDir = path.join(dir, 'plugin-functions');
if (fs.existsSync(fnDir)) {
  for (const file of fs.readdirSync(fnDir).filter((f) => f.endsWith('.json'))) {
    const fn = read(path.join('plugin-functions', file));
    if (!boundFns.has(fn.id)) continue;
    const properties = {};
    const required = [];
    for (const p of fn.parameters || []) {
      properties[p.name] = { type: p.type || 'string', description: p.description || '' };
      if (p.required) required.push(p.name);
    }
    tools.push({
      type: 'function',
      function: {
        name: fn.signature,
        description: fn.description || '',
        parameters: { type: 'object', properties, ...(required.length ? { required } : {}) },
      },
    });
  }
}

const missing = [...boundFns].filter((id) => !fs.existsSync(path.join(fnDir, `${id}.json`)));
if (missing.length) console.warn(`warning: plugin functions ${missing.join(', ')} are bound but not saved under plugin-functions/`);
fs.writeFileSync(path.join(dir, 'tools.json'), JSON.stringify(tools, null, 2) + '\n');
console.log(`tools.json: ${tools.map((t) => t.function.name).join(', ') || '(none)'}`);
