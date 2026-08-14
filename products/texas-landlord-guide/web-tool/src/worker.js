// Texas Landlord Advisor — interactive Stage 1 MVP
// 3-tier answer chain:
//   1. Anthropic API (claude-sonnet-4-6) — primary, real per-call cost
//      (~$0.01-0.02/question, see web-tool/README.md).
//   2. Gemini API (gemini-2.5-flash) — free tier, 1,500 req/day, kicks in
//      if Anthropic errors.
//   3. Cloudflare Workers AI (free, edge-native) — last resort if both
//      of the above fail.
// Every tier below primary shows a visible on-screen "backup mode" banner
// — a degraded-quality answer is never presented as if it were primary.
//
// Decisions still needed from Randy before this goes live (see products/
// texas-landlord-guide/web-tool/README.md):
//   - RATE_LIMIT_PER_DAY value below (default 5, a placeholder)
//   - confirm primary model choice (Sonnet vs Haiku)
//   - the "evidence of market" usage threshold that triggers building the
//     paid version

const RATE_LIMIT_PER_DAY = 5; // placeholder — confirm with Randy before launch
const PRIMARY_MODEL = "claude-sonnet-4-6";
const GEMINI_MODEL = "gemini-2.5-flash";
const WORKERS_AI_MODEL = "@cf/meta/llama-3.1-8b-instruct";

const PROMPT_TEMPLATE = (question) => `Treat each question as completely stand-alone, use only the information
provided, do not assume anything from previous questions or information is
true for this question. Give me the version with the citations. This is
for the state of Texas, cite the exact sources to answer this question,
verify your answers are accurate from legal documents that are current as
of today's date. Give me the answer as though I am 8 years old as a
summary at the top of your answer, vary the introduction sentence. Include
a disclaimer that this is not legal advice and that I should verify with a
licensed Texas attorney or my local Justice of the Peace court clerk
before acting on anything time-sensitive (notices, court filings, or
handling a tenant's property).

Question: ${question}`;

const DISCLAIMER_HTML = `<p style="font-size:13px;color:#666;border-top:1px solid #ddd;padding-top:12px;margin-top:24px;">
<strong>I am not an attorney, and this is not legal advice.</strong> This is
general information verified against the Texas Property Code. Laws change,
and every situation is different. Before you act — especially before
serving a notice, filing in court, or handling a tenant's abandoned
property — verify your specific situation with a licensed Texas attorney
or your local Justice of the Peace court clerk.
</p>`;

const PAGE_HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Texas Landlord Advisor — free Q&A</title>
<style>
  body { font-family: -apple-system, Segoe UI, Arial, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; color: #1a1a1a; }
  h1 { font-size: 22px; }
  textarea { width: 100%; min-height: 100px; font-size: 15px; padding: 10px; box-sizing: border-box; }
  button { margin-top: 10px; padding: 10px 20px; font-size: 15px; cursor: pointer; }
  #answer { margin-top: 24px; white-space: pre-wrap; line-height: 1.5; }
  #status { color: #666; font-size: 13px; margin-top: 8px; }
  .backup-banner { background: #fff3cd; border: 1px solid #ffe69c; padding: 8px 12px; border-radius: 4px; font-size: 13px; margin-bottom: 12px; }
</style>
</head>
<body>
<h1>Texas Landlord Advisor</h1>
<p>Ask a real Texas landlord-tenant question. Free, no signup.</p>
<textarea id="q" placeholder="e.g. Can I keep a security deposit if the tenant left owing rent? (Enter to ask, Shift+Enter for a new line)" onkeydown="if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); ask(); }"></textarea><br>
<button onclick="ask()">Ask</button>
<div id="status"></div>
<div id="answer"></div>

<script>
async function ask() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  document.getElementById('status').textContent = 'Thinking...';
  document.getElementById('answer').innerHTML = '';
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    if (!res.ok) {
      document.getElementById('status').textContent = data.error || 'Something went wrong.';
      return;
    }
    document.getElementById('status').textContent = '';
    const tierBanners = {
      gemini: '<div class="backup-banner">⚠️ Primary model was unavailable — this answer came from a free backup model (Gemini). Verify citations independently before relying on it.</div>',
      'workers-ai': '<div class="backup-banner">⚠️ Both primary and secondary models were unavailable — this answer came from a last-resort free backup model. Verify citations independently before relying on it.</div>'
    };
    // Safe: answerHtml is server-built from escapeHtml(answer) + static
    // disclaimer/banner markup, not raw user input rendered back verbatim.
    document.getElementById('answer').innerHTML =
      (tierBanners[data.tierUsed] || '') + data.answerHtml;
  } catch (e) {
    document.getElementById('status').textContent = 'Network error — try again.';
  }
}
</script>
</body>
</html>`;

async function callAnthropic(env, question) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: PRIMARY_MODEL,
      max_tokens: 1024,
      messages: [{ role: "user", content: PROMPT_TEMPLATE(question) }],
    }),
  });
  if (!res.ok) throw new Error(`Anthropic API error: ${res.status}`);
  const data = await res.json();
  return data.content[0].text;
}

async function callGemini(env, question) {
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${env.GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: PROMPT_TEMPLATE(question) }] }],
      }),
    }
  );
  if (!res.ok) throw new Error(`Gemini API error: ${res.status}`);
  const data = await res.json();
  return data.candidates[0].content.parts[0].text;
}

async function callWorkersAiFallback(env, question) {
  const result = await env.AI.run(WORKERS_AI_MODEL, {
    messages: [{ role: "user", content: PROMPT_TEMPLATE(question) }],
  });
  return result.response;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

async function handleAsk(request, env) {
  // Admin bypass: a header-only secret, never present in the public page's
  // client-side JS. Set via `wrangler secret put ADMIN_BYPASS_KEY`, then
  // test with curl (see web-tool/README.md) — do not add a UI field for
  // this, that would expose it to anyone viewing page source.
  const isAdmin =
    env.ADMIN_BYPASS_KEY &&
    request.headers.get("X-Admin-Key") === env.ADMIN_BYPASS_KEY;

  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const today = new Date().toISOString().slice(0, 10);
  const rlKey = `rl:${ip}:${today}`;

  const countRaw = await env.RATE_LIMIT.get(rlKey);
  const count = countRaw ? parseInt(countRaw, 10) : 0;
  if (!isAdmin && count >= RATE_LIMIT_PER_DAY) {
    return new Response(
      JSON.stringify({ error: `Daily free question limit reached (${RATE_LIMIT_PER_DAY}/day). Try again tomorrow.` }),
      { status: 429, headers: { "content-type": "application/json" } }
    );
  }

  const body = await request.json();
  const question = (body.question || "").slice(0, 1000); // cap input length
  if (!question) {
    return new Response(JSON.stringify({ error: "No question provided." }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  let answer, tierUsed = "anthropic";
  try {
    answer = await callAnthropic(env, question);
  } catch (e1) {
    try {
      tierUsed = "gemini";
      answer = await callGemini(env, question);
    } catch (e2) {
      tierUsed = "workers-ai";
      answer = await callWorkersAiFallback(env, question);
    }
  }

  if (!isAdmin) {
    await env.RATE_LIMIT.put(rlKey, String(count + 1), { expirationTtl: 90000 });
  }

  const answerHtml = `<div>${escapeHtml(answer).replace(/\n/g, "<br>")}</div>${DISCLAIMER_HTML}`;
  return new Response(JSON.stringify({ answerHtml, tierUsed }), {
    headers: { "content-type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/ask" && request.method === "POST") {
      return handleAsk(request, env);
    }
    return new Response(PAGE_HTML, { headers: { "content-type": "text/html" } });
  },
};
