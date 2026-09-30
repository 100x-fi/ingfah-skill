// Plays one whole conversation per test against the agent exported from Ingfah.
//
// It reads agent.json (GET /client/agents/{slug}, saved with --output) and
// tools.json (built by build-tools.js), composes a system prompt in the same
// order the platform uses (Identity, Task, Conversation States, then the
// call's data at the end), speaks the greeting as the first assistant turn,
// and then runs each user turn against the model live.
//
// The platform also adds its own rules to the prompt, which are not
// exported. The suite therefore tests the agent's own fields; a test call in
// the dashboard (ทดลอง) remains the final check.
//
// Test vars:
//   turnsJson        JSON array of turns (JSON-encoded so promptfoo does not
//                    expand it into a matrix). Each turn is one of:
//                      { "user": "..." }                    live model call
//                      { "user": "...", "script": [msgs] }  fixed reply, no model call
//                      { "user": "...", "inject": [msgs] }  extra messages before the call
//   customerContext  object, the per-call data (name, amount, due date, ...)
//   now              optional, e.g. "Wednesday, 30 September 2026 (พุธที่ 30 กันยายน พ.ศ. 2569) เวลา 10:00"
//   toolMocksJson    optional JSON object { toolName: resultObject } — when the
//                    model calls a tool named here, the result is returned to
//                    it and it is called again to speak the answer
//
// Output: { greeting, turns: [{ user, assistant, toolCalls }] }. `assistant`
// holds only what text-to-speech would say; tool calls are kept separately in
// `toolCalls`, so a tool name inside `assistant` is a real defect.

const fs = require('fs');
const path = require('path');
const nunjucks = require('nunjucks');

const env = new nunjucks.Environment(null, { autoescape: false, throwOnUndefined: false });

function loadJson(file) {
  const raw = JSON.parse(fs.readFileSync(path.resolve(__dirname, file), 'utf8'));
  return raw && raw.data !== undefined ? raw.data : raw;
}

function render(text, ctx) {
  return text ? env.renderString(text, ctx) : '';
}

function thaiNow(date = new Date()) {
  const tz = { timeZone: 'Asia/Bangkok' };
  const en = date.toLocaleDateString('en-GB', { ...tz, weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const th = date.toLocaleDateString('th-TH', { ...tz, weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const hm = date.toLocaleTimeString('en-GB', { ...tz, hour: '2-digit', minute: '2-digit', hour12: false });
  return `${en.replace(/^(\w+) /, '$1, ')} (${th}) เวลา ${hm}`;
}

function stripPositions(flow) {
  return (flow || []).map(({ position, ...state }) => state);
}

function composeSystemPrompt(agent, vars) {
  const now = vars.now || thaiNow();
  const hour = Number((now.match(/เวลา\s+(\d{1,2})/) || [])[1] || new Date().getHours());
  const customerContext = vars.customerContext || {};
  const ctx = {
    ...(agent.ai_instruction_variables || {}),
    agentName: agent.name,
    customerContext,
    now,
    hour,
  };
  const flow = stripPositions(agent.ai_instruction_flow);
  const contextLines = Object.entries(customerContext).map(([k, v]) => `- ${k}: ${v}`).join('\n');
  return [
    `# Identity\n\n${render(agent.ai_instruction_identity, ctx)}`,
    `# Task\n\n${render(agent.ai_instruction_task, ctx)}`,
    flow.length ? `# Conversation States\n\n${render(JSON.stringify(flow, null, 2), ctx)}` : '',
    `# ข้อมูลของการคุยครั้งนี้\n\nวันเวลาขณะสนทนา: ${now}\n\nข้อมูลลูกค้า:\n${contextLines || '-'}`,
  ].filter(Boolean).join('\n\n');
}

async function chat({ apiBaseUrl, apiKey, model, messages, tools, temperature, maxTokens }) {
  const body = { model, messages, temperature, max_tokens: maxTokens };
  if (tools && tools.length) body.tools = tools;
  let lastError;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(`${apiBaseUrl.replace(/\/$/, '')}/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(json.error || json).slice(0, 300)}`);
      return { message: json.choices[0].message, usage: json.usage || {} };
    } catch (err) {
      lastError = err;
      await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
    }
  }
  throw lastError;
}

function parseToolCalls(raw) {
  return (raw || []).map((c) => {
    let args = {};
    try { args = JSON.parse(c.function?.arguments || '{}'); } catch (e) { /* keep {} */ }
    return { id: c.id, name: c.function?.name, arguments: args };
  });
}

class AgentProvider {
  constructor(options = {}) {
    this.config = options.config || {};
    this.providerId = options.id || 'ingfah-agent';
  }

  id() {
    return this.providerId;
  }

  async callApi(_prompt, context) {
    const vars = (context && context.vars) || {};
    const cfg = this.config;
    const apiKey = process.env[cfg.apiKeyEnvar || 'OPENROUTER_API_KEY'];
    if (!apiKey) return { error: `set ${cfg.apiKeyEnvar || 'OPENROUTER_API_KEY'} in .env` };
    const agent = loadJson(cfg.agentFile || 'agent.json');
    const tools = fs.existsSync(path.resolve(__dirname, cfg.toolsFile || 'tools.json'))
      ? loadJson(cfg.toolsFile || 'tools.json')
      : [];
    const tokenUsage = { prompt: 0, completion: 0, total: 0, numRequests: 0 };
    let cost = 0;
    const call = async (messages) => {
      const { message, usage } = await chatOnce(messages);
      tokenUsage.prompt += usage.prompt_tokens || 0;
      tokenUsage.completion += usage.completion_tokens || 0;
      tokenUsage.total += usage.total_tokens || 0;
      tokenUsage.numRequests += 1;
      cost += usage.cost || 0; // OpenRouter reports the dollar cost per request
      return message;
    };
    const chatOnce = (messages) => chat({
      apiBaseUrl: cfg.apiBaseUrl || 'https://openrouter.ai/api/v1',
      apiKey,
      model: cfg.model,
      messages,
      tools,
      temperature: cfg.temperature ?? 0.5,
      maxTokens: cfg.max_tokens ?? 768,
    });

    const baseCtx = { ...(agent.ai_instruction_variables || {}), agentName: agent.name, customerContext: vars.customerContext || {} };
    const greeting = render(agent.ai_greeting_message, baseCtx);
    const messages = [{ role: 'system', content: composeSystemPrompt(agent, vars) }];
    if (greeting) messages.push({ role: 'assistant', content: greeting });

    const mocks = JSON.parse(vars.toolMocksJson || '{}');
    const turns = [];
    for (const turn of JSON.parse(vars.turnsJson || '[]')) {
      if (turn.user !== undefined) messages.push({ role: 'user', content: turn.user });
      if (Array.isArray(turn.script)) {
        messages.push(...turn.script);
        const said = [...turn.script].reverse().find((m) => m.role === 'assistant');
        turns.push({ user: turn.user ?? '', assistant: said?.content || '', toolCalls: [], scripted: true });
        continue;
      }
      if (Array.isArray(turn.inject)) messages.push(...turn.inject);

      let spoken = '';
      const toolCalls = [];
      // A tool call with a mocked result is answered and the model is called
      // again to speak it; at most 3 rounds per turn.
      for (let round = 0; round < 3; round++) {
        const msg = await call(messages);
        const calls = parseToolCalls(msg.tool_calls);
        spoken += (spoken && msg.content ? ' ' : '') + (msg.content || '');
        toolCalls.push(...calls.map(({ name, arguments: a }) => ({ name, arguments: a })));
        messages.push({ role: 'assistant', content: msg.content || '', ...(msg.tool_calls ? { tool_calls: msg.tool_calls } : {}) });
        const mocked = calls.filter((c) => mocks[c.name] !== undefined);
        if (!mocked.length) break;
        for (const c of mocked) {
          messages.push({ role: 'tool', tool_call_id: c.id, content: JSON.stringify(mocks[c.name]) });
        }
      }
      turns.push({ user: turn.user ?? '', assistant: spoken, toolCalls });
    }
    return { output: JSON.stringify({ greeting, turns }), tokenUsage, ...(cost ? { cost } : {}) };
  }
}

module.exports = AgentProvider;
module.exports.composeSystemPrompt = composeSystemPrompt;
