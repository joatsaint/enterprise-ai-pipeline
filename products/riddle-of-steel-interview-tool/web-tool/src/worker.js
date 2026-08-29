// Riddle of Steel — Operator Evidence Interview (Stage 1 MVP)
// A live, no-copy-paste version of the "Total Recall" interview prompts
// already written in the guide itself (knowledge/products/lead-magnets/
// steel_server_room_lead_magnet_final/steel_server_room_lead_magnet_final.md,
// Section 09, Prompts 1-3). Those prompts already assumed the visitor would
// paste them into their own ChatGPT/Claude account by hand — this tool does
// that step for them. Same 3-tier fallback / rate-limit / disclaimer
// pattern as products/texas-landlord-guide/web-tool (that build is the
// template this one reuses).
//
// Flow:
//   1. AI interviews the visitor one question at a time (Prompt 1, verbatim
//      from the guide) about outages/migrations/workarounds/judgment calls.
//   2. After INTERVIEW_TURNS_BEFORE_OFFER real answers, the page offers to
//      generate the Operator Evidence Brief.
//   3. Email required before the brief is shown (two-tier funnel — same
//      role the PDF opt-in already plays).
//   4. Finalize call combines Prompt 2 (incident brief) + Prompt 3 (resume
//      bullets) into one output, run against the actual conversation.
//
// Real decisions still needed from Randy before this goes live (see
// web-tool/README.md): RATE_LIMIT_PER_DAY value, where captured emails
// actually go (KV only, for now — no ESP wired up yet), and the deploy
// go-ahead itself.

// RATE_LIMIT_PER_DAY counts /chat calls only (/finalize doesn't increment
// it — the 4-turn interview requirement is what naturally throttles that).
// 10, then 30, both ran out during Randy's own repeated same-day testing
// (each restart burns another 4+ calls, all from the same IP). Raised to
// 100 for this Stage 1 validation period specifically — cheap enough in
// real API cost to not worry about one person iterating on it, and this
// value should come back DOWN (10-20) once this is real public traffic,
// not testing. Flagged here so it isn't forgotten before a real launch.
const RATE_LIMIT_PER_DAY = 100;
const INTERVIEW_TURNS_BEFORE_OFFER = 4; // real visitor answers before "generate my brief" appears
const PRIMARY_MODEL = "claude-sonnet-4-6";
const GEMINI_MODEL = "gemini-2.5-flash";
const WORKERS_AI_MODEL = "@cf/meta/llama-3.1-8b-instruct";

// Verbatim from the guide's own Section 09, Prompt 1 — not new copywriting.
const INTERVIEW_SYSTEM_PROMPT = `Act as a senior IT hiring manager and infrastructure leader.

Interview the visitor one question at a time to help them uncover real examples from their sysadmin or IT career that prove their value beyond routine task completion.

Help them remember:
- outages
- migrations
- fragile systems
- undocumented dependencies
- ugly but important workarounds
- security decisions
- business-risk situations
- moments where human judgment mattered

Do not write their resume yet. Ask exactly ONE question at a time, short and conversational. Do not invent details — only work from what they actually tell you. If an answer is thin, ask one specific follow-up before moving to a new topic area, rather than accepting a one-line answer and moving on.`;

// Verbatim structure from Prompt 2 + Prompt 3 in the same section.
// Real bug fixed 2026-08-21: the model kept asking another interview
// question instead of finalizing, because nothing here told it to stop --
// it just pattern-matched on its own prior interview-style turns already
// in the conversation history. The explicit "do not ask" line is the fix,
// confirmed live against a real conversation before and after.
const FINALIZE_SYSTEM_PROMPT = `The interview is over. Do not ask any more questions. Do not continue the interview. Based only on the interview conversation below, produce two things now:

1. An incident brief using this structure: What happened / What made it risky / What people thought was happening / What was actually happening / What human judgment mattered / What AI could have helped with / What AI would likely have missed / What skill this proves. Keep it factual. Do not exaggerate. Do not invent details.

2. Three resume bullet options for an experienced sysadmin or infrastructure professional, focused on operational risk, business impact, troubleshooting judgment, documentation, cross-team communication, and AI-era relevance. Do not invent metrics — if a metric is missing, note what they should verify or estimate instead of making one up.

Base both sections only on what the visitor actually said in the interview. If the interview didn't cover enough to fill a section, say so honestly within that section rather than asking a follow-up question or inventing material.`;

const DISCLAIMER_HTML = `<p style="font-size:13px;color:#666;border-top:1px solid #ddd;padding-top:12px;margin-top:24px;">
This is educational, not career or legal advice. <strong>Do not paste real
company names, customer data, credentials, IP addresses, hostnames, or
security details into this tool</strong> — sanitize your story the same way
the guide itself tells you to. Verify anything time-sensitive with your own
judgment before using it in a resume, interview, or internal document.
</p>
<p style="font-size:13px;margin-top:12px;">
Grab the free
<a href="https://rskiles.com/operator" target="_blank" rel="noopener">Hockey Puck Thinking prompt kit</a>.
</p>`;

const PAGE_HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Operator Evidence Interview — free, from The Steel and the Server Room</title>
<style>
  body { font-family: -apple-system, Segoe UI, Arial, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; color: #1a1a1a; }
  h1 { font-size: 22px; }
  #chat { border: 1px solid #ddd; border-radius: 6px; padding: 12px; min-height: 200px; margin-top: 16px; }
  .msg { margin: 10px 0; line-height: 1.5; white-space: pre-wrap; }
  .msg.ai { color: #1a1a1a; }
  .msg.user { color: #444; text-align: right; }
  .msg .label { font-size: 11px; text-transform: uppercase; color: #999; display: block; }
  textarea { width: 100%; min-height: 60px; font-size: 15px; padding: 10px; box-sizing: border-box; margin-top: 12px; }
  button { margin-top: 10px; padding: 10px 20px; font-size: 15px; cursor: pointer; }
  #status { color: #666; font-size: 13px; margin-top: 8px; }
  .backup-banner { background: #fff3cd; border: 1px solid #ffe69c; padding: 8px 12px; border-radius: 4px; font-size: 13px; margin-bottom: 12px; }
  #offer, #emailGate, #result { display: none; margin-top: 20px; }
  #emailGate input { font-size: 15px; padding: 8px; width: 100%; box-sizing: border-box; margin-top: 8px; }
</style>
</head>
<body>
<h1>Operator Evidence Interview</h1>
<p>Free. No signup to start. From <em>The Steel and the Server Room</em> —
answer a few real questions about your IT career, get a real incident brief
and resume language back.</p>

<div id="chat"></div>
<textarea id="answer" placeholder="Type your answer... (Enter to send, Shift+Enter for a new line)" onkeydown="handleAnswerKeydown(event)"></textarea><br>
<button id="sendBtn" onclick="send()">Send</button>
<div id="status"></div>

<div id="offer">
  <p><strong>You've given enough to work with.</strong> Ready for your Operator Evidence Brief?</p>
  <button onclick="showEmailGate()">Generate My Evidence Brief</button>
</div>

<div id="emailGate">
  <p>Where should this go? (also adds you to early access for the full field manual)</p>
  <input type="email" id="email" placeholder="you@example.com" onkeydown="if (event.key === 'Enter') { event.preventDefault(); finalize(); }">
  <button onclick="finalize()">Get My Brief</button>
</div>

<div id="result"></div>

<script>
let history = [];
let turnCount = 0;

// Real, hardcoded opener — no API call needed for this, and it means the
// visitor sees a question the instant the page loads instead of a blank
// chat box waiting for them to type first (real gap found 2026-08-13).
const OPENING_QUESTION = "Let's start simple: how many years have you been in sysadmin or IT ops, and what's your current role?";

function renderMsg(role, text) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg ' + (role === 'assistant' ? 'ai' : 'user');
  const label = document.createElement('span');
  label.className = 'label';
  label.textContent = role === 'assistant' ? 'Interviewer' : 'You';
  const body = document.createElement('span');
  body.textContent = text;
  div.appendChild(label);
  div.appendChild(body);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function handleAnswerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    send();
  }
}

async function send() {
  const box = document.getElementById('answer');
  const text = box.value.trim();
  if (!text) return;
  const btn = document.getElementById('sendBtn');
  renderMsg('user', text);
  history.push({ role: 'user', content: text });
  box.value = '';
  btn.disabled = true;
  document.getElementById('status').textContent = 'Thinking...';
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history })
    });
    const data = await res.json();
    if (!res.ok) {
      document.getElementById('status').textContent = data.error || 'Something went wrong.';
      return;
    }
    document.getElementById('status').textContent = '';
    if (data.tierUsed !== 'anthropic') {
      renderMsg('assistant', '⚠️ (backup model) ' + data.reply);
    } else {
      renderMsg('assistant', data.reply);
    }
    history.push({ role: 'assistant', content: data.reply });
    turnCount++;
    if (turnCount >= ${INTERVIEW_TURNS_BEFORE_OFFER}) {
      document.getElementById('offer').style.display = 'block';
    }
  } catch (e) {
    document.getElementById('status').textContent = 'Network error — try again.';
  } finally {
    btn.disabled = false;
  }
}

function showEmailGate() {
  document.getElementById('emailGate').style.display = 'block';
}

async function finalize() {
  const email = document.getElementById('email').value.trim();
  if (!email || !email.includes('@')) {
    alert('Enter a real email to get your brief.');
    return;
  }
  const btns = document.querySelectorAll('#emailGate button, #offer button');
  btns.forEach(function(b) { b.disabled = true; });
  document.getElementById('status').textContent = 'Building your brief...';
  try {
    const res = await fetch('/finalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history, email })
    });
    const data = await res.json();
    if (!res.ok) {
      document.getElementById('status').textContent = data.error || 'Something went wrong.';
      return;
    }
    document.getElementById('status').textContent = '';
    document.getElementById('emailGate').style.display = 'none';
    document.getElementById('offer').style.display = 'none';
    const result = document.getElementById('result');
    result.style.display = 'block';
    const banner = data.tierUsed !== 'anthropic'
      ? '<div class="backup-banner">⚠️ Backup model used for this result — verify it against your own memory before reusing it.</div>'
      : '';
    result.innerHTML = banner + data.briefHtml;
  } catch (e) {
    document.getElementById('status').textContent = 'Network error — try again.';
  } finally {
    btns.forEach(function(b) { b.disabled = false; });
  }
}

// Show the first question immediately on load — no API call, no rate-limit
// cost, and the visitor never sees an empty chat box (real gap found
// 2026-08-13: previously nothing appeared until after their first reply).
renderMsg('assistant', OPENING_QUESTION);
history.push({ role: 'assistant', content: OPENING_QUESTION });
</script>
</body>
</html>`;

async function callAnthropic(env, systemPrompt, messages, temperature) {
  const body = {
    model: PRIMARY_MODEL,
    max_tokens: 1024,
    system: systemPrompt,
    messages,
  };
  if (typeof temperature === "number") body.temperature = temperature;
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Anthropic API error: ${res.status}`);
  const data = await res.json();
  return data.content[0].text;
}

async function callGemini(env, systemPrompt, messages) {
  const contents = messages.map((m) => ({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{ text: m.content }],
  }));
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${env.GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents,
      }),
    }
  );
  if (!res.ok) throw new Error(`Gemini API error: ${res.status}`);
  const data = await res.json();
  return data.candidates[0].content.parts[0].text;
}

async function callWorkersAiFallback(env, systemPrompt, messages) {
  const result = await env.AI.run(WORKERS_AI_MODEL, {
    messages: [{ role: "system", content: systemPrompt }, ...messages],
  });
  return result.response;
}

async function runTiered(env, systemPrompt, messages, temperature) {
  try {
    return { text: await callAnthropic(env, systemPrompt, messages, temperature), tierUsed: "anthropic" };
  } catch (e1) {
    try {
      return { text: await callGemini(env, systemPrompt, messages), tierUsed: "gemini" };
    } catch (e2) {
      return { text: await callWorkersAiFallback(env, systemPrompt, messages), tierUsed: "workers-ai" };
    }
  }
}

// Real bug fixed 2026-08-21: even with the FINALIZE_SYSTEM_PROMPT's
// explicit "do not ask any more questions" instruction and a clean history,
// the model still ignored it intermittently (confirmed 1-in-3 in live
// testing) and returned a bare follow-up question instead of the brief.
// Cheap, deterministic check — no extra AI call unless the first attempt
// actually violated the instruction.
function looksLikeFinalizeBrief(text) {
  const t = text.trim();
  if (t.length < 200) return false;
  if (/incident brief/i.test(t)) return true;
  return false;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function checkRateLimit(env, request) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const today = new Date().toISOString().slice(0, 10);
  return { ip, key: `rl:${ip}:${today}` };
}

async function handleChat(request, env) {
  const isAdmin =
    env.ADMIN_BYPASS_KEY &&
    request.headers.get("X-Admin-Key") === env.ADMIN_BYPASS_KEY;

  const { key } = checkRateLimit(env, request);
  const countRaw = await env.RATE_LIMIT.get(key);
  const count = countRaw ? parseInt(countRaw, 10) : 0;
  if (!isAdmin && count >= RATE_LIMIT_PER_DAY) {
    return new Response(
      JSON.stringify({ error: `Daily free limit reached (${RATE_LIMIT_PER_DAY}/day). Try again tomorrow.` }),
      { status: 429, headers: { "content-type": "application/json" } }
    );
  }

  const body = await request.json();
  const history = Array.isArray(body.history) ? body.history.slice(-20) : [];
  if (history.length === 0) {
    return new Response(JSON.stringify({ error: "No conversation provided." }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  const { text, tierUsed } = await runTiered(env, INTERVIEW_SYSTEM_PROMPT, history);

  if (!isAdmin) {
    await env.RATE_LIMIT.put(key, String(count + 1), { expirationTtl: 90000 });
  }

  return new Response(JSON.stringify({ reply: text, tierUsed }), {
    headers: { "content-type": "application/json" },
  });
}

async function handleFinalize(request, env) {
  const isAdmin =
    env.ADMIN_BYPASS_KEY &&
    request.headers.get("X-Admin-Key") === env.ADMIN_BYPASS_KEY;

  const { key } = checkRateLimit(env, request);
  const countRaw = await env.RATE_LIMIT.get(key);
  const count = countRaw ? parseInt(countRaw, 10) : 0;
  if (!isAdmin && count >= RATE_LIMIT_PER_DAY) {
    return new Response(
      JSON.stringify({ error: `Daily free limit reached (${RATE_LIMIT_PER_DAY}/day). Try again tomorrow.` }),
      { status: 429, headers: { "content-type": "application/json" } }
    );
  }

  const body = await request.json();
  let history = Array.isArray(body.history) ? body.history.slice(-20) : [];
  // Real bug fixed 2026-08-21: a visitor can click "finish" right after the
  // AI pushes a new question and before answering it, leaving an unanswered
  // assistant turn as the last entry. That trailing turn made the Anthropic
  // call fail outright (fell through to Gemini/Workers AI), and whichever
  // tier answered would just continue the dangling question instead of
  // producing the brief. Confirmed live: history ending on 'user' finalized
  // correctly every time; history ending on 'assistant' reproduced the bug
  // every time. Drop any unanswered trailing assistant turn(s) before
  // finalizing — the interview's real content is only what the visitor
  // actually answered.
  while (history.length > 0 && history[history.length - 1].role === "assistant") {
    history.pop();
  }
  const email = (body.email || "").slice(0, 200);
  if (!email.includes("@")) {
    return new Response(JSON.stringify({ error: "Valid email required." }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }
  if (history.length === 0) {
    return new Response(JSON.stringify({ error: "No conversation provided." }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  // Stage 1 MVP: log the lead to KV only. No ESP wired up yet — Randy
  // pulls this list manually until real volume justifies wiring one in.
  const leadKey = `lead:${Date.now()}:${email}`;
  await env.RATE_LIMIT.put(leadKey, JSON.stringify({ email, ts: new Date().toISOString() }));

  let { text, tierUsed } = await runTiered(env, FINALIZE_SYSTEM_PROMPT, history, 0);

  // See looksLikeFinalizeBrief's comment above — one deterministic retry,
  // capped per the project's Agentic Reliability Loop Cap, when the model
  // ignored the "no questions" instruction on the first attempt.
  if (!looksLikeFinalizeBrief(text)) {
    const retryPrompt = `${FINALIZE_SYSTEM_PROMPT}\n\nYour previous response asked a question instead of producing the brief. That is not allowed. Respond now with ONLY the incident brief and resume bullets, starting your response with "# Incident Brief". Do not ask anything.`;
    const retry = await runTiered(env, retryPrompt, history, 0);
    text = retry.text;
    tierUsed = retry.tierUsed;
  }

  const briefHtml = `<div>${escapeHtml(text).replace(/\n/g, "<br>")}</div>${DISCLAIMER_HTML}`;
  return new Response(JSON.stringify({ briefHtml, tierUsed }), {
    headers: { "content-type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/chat" && request.method === "POST") {
      return handleChat(request, env);
    }
    if (url.pathname === "/finalize" && request.method === "POST") {
      return handleFinalize(request, env);
    }
    return new Response(PAGE_HTML, {
      headers: { "content-type": "text/html", "cache-control": "no-store" },
    });
  },
};
