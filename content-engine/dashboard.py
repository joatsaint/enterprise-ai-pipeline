#!/usr/bin/env python3
"""
dashboard.py  .  content-engine/

Three-view content pipeline dashboard:
  - Articles: per-article progress board with 6-stage checkboxes per content piece
  - Week View: 7-day posting calendar with article assignment
  - Performance: engagement analytics by topic and hook type

Usage
-----
  python dashboard.py              # port 5000
  python dashboard.py --port 8080

Access
------
  This PC:     http://localhost:5000
  LAN (3rd monitor):  http://<dedicated-pc-ip>:5000
"""

from flask import Flask, jsonify, request
import json, re, sys, argparse
from datetime import datetime
from pathlib import Path

app  = Flask(__name__, static_folder=None)
HERE = Path(__file__).parent
STATE_FILE = HERE / "dashboard_state.json"

STAGES = ["pending", "approved", "scheduled", "published"]

PIECES = [
    {"key": "linkedin-article",   "label": "LinkedIn Article",   "day": "Mon",      "manual": False, "tool": None, "task_overrides": {"scheduled": "Ready"}, "track_engagement": True},
    {"key": "article-hero-image", "label": "Article Hero Image", "day": "Mon",      "manual": True,  "tool": "ChatGPT — landscape hero (article header)",    "track_engagement": False},
    {"key": "carousel",           "label": "Carousel",           "day": "Mon / Thu","manual": True,  "tool": "Canva — paste slide copy from carousel.md",    "track_engagement": True},
    {"key": "text-post",          "label": "Text Feed Post",     "day": "Wed",      "manual": False, "tool": None, "track_engagement": True},
    {"key": "image-post",         "label": "Image Post",         "day": "Sat",      "manual": True,  "tool": "ChatGPT image generator",                      "track_engagement": True},
    {"key": "newsletter",         "label": "Newsletter",         "day": "Sun",      "manual": False, "tool": None, "track_engagement": True},
    {"key": "first-comments",     "label": "First Comments",     "day": "--",       "manual": False, "tool": None, "track_engagement": False},
    {"key": "poll",               "label": "Poll",               "day": "--",       "manual": False, "tool": None, "track_engagement": False},
    {"key": "buffer-schedule",    "label": "Buffer Schedule",    "day": "Plan",     "manual": False, "tool": None, "track_engagement": False},
]

TASKS = [
    {"key": "written",       "label": "Written"},
    {"key": "reviewed",      "label": "Reviewed"},
    {"key": "approved",      "label": "Approved"},
    {"key": "scheduled",     "label": "In Buffer"},
    {"key": "published",     "label": "Published"},
    {"key": "launch_window", "label": "90-min"},
]

TOPICS = [
    "job-security", "ai-risk", "skill-building",
    "enterprise-story", "personal-story", "tool-tutorial", "career-advice",
]

HOOK_TYPES = [
    "transformation", "pain-first", "contrarian",
    "framework-list", "question", "story",
]

WEEK = [
    {"wd": 0, "day": "Mon", "keys": ["linkedin-article","article-hero-image","carousel"], "label": "Article + Carousel", "time": "8:00 AM ET",  "time_cdt": "7:00 AM CDT", "engage": False, "launch": True},
    {"wd": 1, "day": "Tue", "keys": [],                                                   "label": "Engagement Day",    "time": "",            "time_cdt": "",            "engage": True,  "launch": False},
    {"wd": 2, "day": "Wed", "keys": ["text-post"],                                        "label": "Text Post",         "time": "9:00 AM ET",  "time_cdt": "8:00 AM CDT", "engage": False, "launch": True},
    {"wd": 3, "day": "Thu", "keys": ["carousel"],                                         "label": "Carousel / Infog.", "time": "8:30 AM ET",  "time_cdt": "7:30 AM CDT", "engage": False, "launch": True},
    {"wd": 4, "day": "Fri", "keys": [],                                                   "label": "Engagement Day",    "time": "",            "time_cdt": "",            "engage": True,  "launch": False},
    {"wd": 5, "day": "Sat", "keys": ["image-post"],                                       "label": "Text + Image",      "time": "10:00 AM ET", "time_cdt": "9:00 AM CDT", "engage": False, "launch": True},
    {"wd": 6, "day": "Sun", "keys": ["newsletter"],                                       "label": "Newsletter",        "time": "7:00 PM ET",  "time_cdt": "6:00 PM CDT", "engage": False, "launch": True},
]

# -- state ---------------------------------------------------------------

def _load_raw():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {"articles": {}}

def _save(state):
    state["saved"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), "utf-8")

def _scan():
    found = {}
    rank  = {s: i for i, s in enumerate(STAGES)}
    for stage in STAGES:
        folder = HERE / stage
        if not folder.exists():
            continue
        for sub in sorted(folder.iterdir()):
            if not sub.is_dir():
                continue
            slug = sub.name
            publish_date = None
            readme = sub / "_README.md"
            if readme.exists():
                m = re.search(r'\*\*Publish date:\*\*\s*(\S+)', readme.read_text("utf-8"))
                if m:
                    publish_date = m.group(1)
            m = re.match(r'(ART\d+)', slug, re.I)
            art_num = m.group(1).upper() if m else None
            if slug not in found or rank[stage] > rank[found[slug]["stage"]]:
                found[slug] = {"stage": stage, "publish_date": publish_date, "art_num": art_num}
    return found

def get_state():
    raw   = _load_raw()
    found = _scan()
    for slug, meta in found.items():
        if slug not in raw["articles"]:
            raw["articles"][slug] = {
                "slug": slug, "art_num": meta["art_num"], "title": None,
                "publish_date": meta["publish_date"], "stage": meta["stage"],
                "topic": None, "hook_type": None,
                "pieces": {}, "engagement": {},
            }
        else:
            a = raw["articles"][slug]
            a["stage"]        = meta["stage"]
            a["publish_date"] = meta["publish_date"]
            if not a.get("art_num"):
                a["art_num"] = meta["art_num"]
            if "topic"     not in a: a["topic"]     = None
            if "hook_type" not in a: a["hook_type"] = None
            if "engagement" not in a: a["engagement"] = {}
        a = raw["articles"][slug]
        for p in PIECES:
            if p["key"] not in a["pieces"]:
                a["pieces"][p["key"]] = {t["key"]: False for t in TASKS}
            if p.get("track_engagement") and p["key"] not in a["engagement"]:
                a["engagement"][p["key"]] = {"impressions": None, "comments": None, "reactions": None}
    return raw

# -- routes --------------------------------------------------------------

@app.route("/api/data")
def api_data():
    state = get_state()
    return jsonify({
        "articles": list(state["articles"].values()),
        "pieces":   PIECES,
        "tasks":    TASKS,
        "week":     WEEK,
        "topics":   TOPICS,
        "hook_types": HOOK_TYPES,
    })

@app.route("/api/checkbox", methods=["POST"])
def api_checkbox():
    d     = request.get_json()
    state = get_state()
    try:
        state["articles"][d["slug"]]["pieces"][d["piece"]][d["task"]] = d["checked"]
        _save(state)
        return jsonify({"ok": True})
    except KeyError:
        return jsonify({"ok": False}), 404

@app.route("/api/title", methods=["POST"])
def api_title():
    d     = request.get_json()
    state = get_state()
    slug  = d.get("slug", "")
    if slug in state["articles"]:
        state["articles"][slug]["title"] = d.get("title") or None
        _save(state)
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 404

@app.route("/api/tags", methods=["POST"])
def api_tags():
    d     = request.get_json()
    state = get_state()
    slug  = d.get("slug", "")
    if slug not in state["articles"]:
        return jsonify({"ok": False}), 404
    if "topic"     in d: state["articles"][slug]["topic"]     = d["topic"] or None
    if "hook_type" in d: state["articles"][slug]["hook_type"] = d["hook_type"] or None
    _save(state)
    return jsonify({"ok": True})

@app.route("/api/engagement", methods=["POST"])
def api_engagement():
    d     = request.get_json()
    state = get_state()
    slug  = d.get("slug", "")
    piece = d.get("piece", "")
    if slug not in state["articles"]:
        return jsonify({"ok": False}), 404
    if "engagement" not in state["articles"][slug]:
        state["articles"][slug]["engagement"] = {}
    if piece not in state["articles"][slug]["engagement"]:
        state["articles"][slug]["engagement"][piece] = {}
    for field in ("impressions", "comments", "reactions"):
        if field in d:
            val = d[field]
            state["articles"][slug]["engagement"][piece][field] = int(val) if val not in (None, "", "null") else None
    _save(state)
    return jsonify({"ok": True})

@app.route("/")
def index():
    return HTML

# -- HTML ----------------------------------------------------------------

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content Pipeline</title>
<style>
:root {
  --bg:      #f1f5f9;
  --card:    #fff;
  --border:  #e2e8f0;
  --text:    #1e293b;
  --muted:   #64748b;
  --primary: #3b82f6;
  --success: #16a34a;
  --warn:    #d97706;
  --engage:  #7c3aed;
  --navbg:   #0f172a;
  --perf:    #0891b2;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; }

nav {
  background: var(--navbg); color: #f8fafc;
  display: flex; align-items: center; gap: .75rem;
  padding: .7rem 1.5rem; position: sticky; top: 0; z-index: 10;
  box-shadow: 0 1px 3px rgba(0,0,0,.4);
}
.nav-brand { font-weight: 700; font-size: .95rem; letter-spacing: .03em; margin-right: auto; }
.nav-tabs button {
  background: transparent; color: #94a3b8;
  border: 1px solid #334155; border-radius: 6px;
  padding: .3rem .8rem; cursor: pointer; font-size: .82rem; margin-left: .25rem;
}
.nav-tabs button.active, .nav-tabs button:hover {
  background: #1e293b; color: #f8fafc; border-color: #475569;
}
.nav-date { color: #475569; font-size: .78rem; white-space: nowrap; }

main { max-width: 1200px; margin: 0 auto; padding: 1.25rem 1rem; }

/* STATS */
.stats-bar {
  display: flex; gap: 1.5rem; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; padding: .65rem 1.1rem; margin-bottom: 1rem;
}
.stat-val { font-size: 1.15rem; font-weight: 700; }
.stat-lbl { font-size: .7rem; color: var(--muted); margin-top: .05rem; }

/* ARTICLE CARD */
.article-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; margin-bottom: .75rem; overflow: hidden;
}
.card-header {
  display: flex; align-items: center; gap: .6rem; flex-wrap: wrap;
  padding: .65rem 1rem; cursor: pointer; user-select: none;
}
.card-header:hover { background: #f8fafc; }
.art-badge {
  background: #1e293b; color: #e2e8f0;
  font-size: .68rem; font-weight: 700; padding: .2rem .5rem;
  border-radius: 4px; white-space: nowrap; flex-shrink: 0;
}
.card-title {
  flex: 1; font-weight: 600; font-size: .88rem; min-width: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.card-title span { cursor: text; }
.card-title input {
  font-size: .88rem; font-weight: 600; width: 100%;
  border: none; border-bottom: 2px solid var(--primary);
  outline: none; background: transparent;
}
.card-date { font-size: .73rem; color: var(--muted); white-space: nowrap; flex-shrink: 0; }

.stage-badge {
  font-size: .68rem; font-weight: 700; padding: .18rem .55rem;
  border-radius: 99px; white-space: nowrap; text-transform: uppercase;
  letter-spacing: .05em; flex-shrink: 0;
}
.s-pending   { background: #f1f5f9; color: #64748b; }
.s-approved  { background: #dbeafe; color: #1d4ed8; }
.s-scheduled { background: #fef3c7; color: #92400e; }
.s-published { background: #dcfce7; color: #166534; }

.hdr-bar { width: 72px; flex-shrink: 0; }
.bar { height: 5px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--success); transition: width .25s; }
.bar-pct { font-size: .65rem; color: var(--muted); text-align: right; margin-top: .1rem; }

.chevron { font-size: .65rem; color: var(--muted); transition: transform .2s; flex-shrink: 0; }
.chevron.open { transform: rotate(90deg); }

/* TAGS ROW */
.card-tags {
  display: flex; gap: .5rem; align-items: center;
  padding: .35rem 1rem; background: #f8fafc;
  border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.card-tags label { font-size: .65rem; color: var(--muted); white-space: nowrap; }
.tag-select {
  font-size: .68rem; padding: .18rem .4rem; border: 1px solid var(--border);
  border-radius: 4px; background: #fff; color: var(--text); cursor: pointer;
}
.tag-select.set { background: #eff6ff; border-color: #93c5fd; color: #1d4ed8; font-weight: 600; }

/* PIECE TABLE */
.piece-table { border-collapse: collapse; width: 100%; }
.piece-table td { padding: .5rem .75rem; border-top: 1px solid var(--border); vertical-align: middle; }
.piece-table tr:hover td { background: #fafbfc; }
.piece-name { font-size: .83rem; font-weight: 500; }
.piece-day  { font-size: .68rem; color: var(--muted); margin-top: .1rem; }
.manual-badge {
  display: inline-block; font-size: .6rem; font-weight: 700;
  background: #fef3c7; color: #92400e; border: 1px solid #fcd34d;
  padding: .1rem .38rem; border-radius: 4px; margin-left: .4rem;
  vertical-align: middle; white-space: nowrap; letter-spacing: .03em;
}

.tasks-row { display: flex; gap: .35rem; align-items: flex-end; }
.task-wrap  { display: flex; flex-direction: column; align-items: center; gap: .18rem; }
.task-wrap label { font-size: .6rem; color: var(--muted); text-align: center; line-height: 1.1; cursor: pointer; }

.task-cb {
  width: 22px; height: 22px; border-radius: 50%;
  border: 2px solid #cbd5e1; background: #fff;
  cursor: pointer; appearance: none; -webkit-appearance: none;
  position: relative; transition: all .12s; flex-shrink: 0;
}
.task-cb:checked { background: var(--success); border-color: var(--success); }
.task-cb:checked::after {
  content: "✓"; position: absolute;
  top: 50%; left: 50%; transform: translate(-50%, -54%);
  color: #fff; font-size: 12px; font-weight: 800;
}
.task-cb:hover:not(:checked) { border-color: #94a3b8; }

.piece-prog { width: 60px; text-align: center; }
.piece-prog .bar { width: 100%; }
.piece-prog .bar-pct { text-align: center; }

/* ENGAGEMENT ROW */
.eng-row td { background: #f0fdf4 !important; padding: .4rem .75rem; }
.eng-fields { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.eng-field  { display: flex; align-items: center; gap: .3rem; }
.eng-field span { font-size: .72rem; color: var(--muted); }
.eng-input {
  width: 80px; font-size: .75rem; padding: .18rem .4rem;
  border: 1px solid #bbf7d0; border-radius: 4px; background: #fff;
  text-align: right;
}
.eng-input:focus { outline: none; border-color: var(--success); }
.eng-score {
  font-size: .72rem; font-weight: 700; color: var(--success);
  background: #dcfce7; border-radius: 4px; padding: .18rem .45rem;
  white-space: nowrap;
}

/* WEEK VIEW */
.week-nav {
  display: flex; align-items: center; justify-content: center; gap: 1rem;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; padding: .55rem 1rem; margin-bottom: 1rem;
}
.week-nav button {
  background: none; border: 1px solid var(--border);
  border-radius: 6px; padding: .25rem .65rem; cursor: pointer; font-size: .95rem;
}
.week-nav button:hover { background: var(--bg); }
.week-label { font-weight: 600; font-size: .9rem; min-width: 200px; text-align: center; }

.week-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: .45rem; }
.day-col {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; overflow: hidden; min-width: 0;
}
.day-col.today   { border-color: var(--primary); }
.day-col.engage  { border-color: #ddd6fe; }
.day-header {
  padding: .45rem .5rem; background: #f8fafc;
  border-bottom: 1px solid var(--border); text-align: center;
}
.day-col.engage .day-header { background: #f5f3ff; }
.day-col.today  .day-header { background: #eff6ff; }
.day-name  { font-weight: 700; font-size: .78rem; }
.day-date  { font-size: .68rem; color: var(--muted); }
.day-col.engage .day-name { color: var(--engage); }
.day-col.today  .day-name { color: var(--primary); }
.day-body  { padding: .55rem .45rem; }
.day-type  { font-size: .73rem; font-weight: 600; margin-bottom: .18rem; }
.day-time  { font-size: .63rem; color: var(--muted); margin-bottom: .45rem; }
.day-col.engage .day-type { color: var(--engage); }
.engage-note { font-size: .68rem; color: var(--engage); line-height: 1.4; }
.launch-protocol {
  font-size: .62rem; line-height: 1.55;
  background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
  border-radius: 4px; padding: .3rem .45rem; margin-top: .45rem;
}
.lp-title { font-weight: 700; font-size: .63rem; margin-bottom: .1rem; }
.cdt-time { color: #94a3b8; font-size: .62rem; }
.overdue-badge {
  font-size: .68rem; font-weight: 700; padding: .18rem .5rem;
  background: #fee2e2; color: #dc2626; border-radius: 99px; flex-shrink: 0;
}
.section-hdr {
  font-size: .72rem; font-weight: 700; color: var(--muted);
  text-transform: uppercase; letter-spacing: .08em;
  padding: .6rem .25rem .3rem; display: flex; align-items: center; gap: .5rem;
}
.section-hdr.clickable { cursor: pointer; user-select: none; }
.section-hdr.clickable:hover { color: var(--text); }

.art-chip {
  font-size: .65rem; background: #f1f5f9; border: 1px solid var(--border);
  border-radius: 4px; padding: .18rem .4rem; margin-bottom: .2rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  cursor: pointer;
}
.art-chip:hover { background: #e2e8f0; }
.mini-bar { height: 3px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin-top: .12rem; }
.mini-fill { height: 100%; background: var(--success); }

/* PERFORMANCE VIEW */
.perf-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;
}
@media (max-width: 700px) { .perf-grid { grid-template-columns: 1fr; } }
.perf-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden;
}
.perf-card-hdr {
  padding: .6rem 1rem; background: #f8fafc;
  border-bottom: 1px solid var(--border);
  font-weight: 700; font-size: .83rem; color: var(--perf);
}
.perf-table { border-collapse: collapse; width: 100%; }
.perf-table th {
  font-size: .65rem; font-weight: 700; color: var(--muted);
  text-transform: uppercase; letter-spacing: .06em;
  padding: .4rem .75rem; border-bottom: 1px solid var(--border);
  text-align: left;
}
.perf-table th:last-child, .perf-table td:last-child { text-align: right; }
.perf-table td { font-size: .78rem; padding: .45rem .75rem; border-top: 1px solid var(--border); }
.perf-table tr:hover td { background: #f8fafc; }
.score-pill {
  display: inline-block; font-size: .68rem; font-weight: 700;
  padding: .15rem .5rem; border-radius: 99px;
}
.score-high { background: #dcfce7; color: #166534; }
.score-mid  { background: #fef3c7; color: #92400e; }
.score-low  { background: #fee2e2; color: #dc2626; }
.no-data    { color: var(--muted); font-style: italic; }

.perf-recommendation {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: .85rem 1.1rem;
}
.perf-rec-hdr { font-weight: 700; font-size: .83rem; color: var(--perf); margin-bottom: .5rem; }
.perf-rec-body { font-size: .83rem; line-height: 1.6; color: var(--text); }
.perf-rec-body strong { color: var(--success); }
.perf-no-data {
  text-align: center; padding: 3rem 1rem; color: var(--muted);
}
.perf-no-data h3 { font-size: 1rem; margin-bottom: .5rem; color: var(--text); }

.empty { text-align: center; padding: 3rem 1rem; color: var(--muted); }
.empty h3 { font-size: 1.05rem; margin-bottom: .5rem; color: var(--text); }

[hidden] { display: none !important; }
</style>
</head>
<body>

<nav>
  <span class="nav-brand">Content Pipeline</span>
  <div class="nav-tabs">
    <button id="tab-articles"    class="active" onclick="switchView('articles')">Articles</button>
    <button id="tab-week"                       onclick="switchView('week')">Week View</button>
    <button id="tab-performance"                onclick="switchView('performance')">Performance</button>
  </div>
  <span class="nav-date" id="nav-date"></span>
</nav>

<main>
  <div id="articles-view">
    <div class="stats-bar" id="stats-bar"></div>
    <div id="article-list"></div>
  </div>
  <div id="week-view" hidden>
    <div class="week-nav">
      <button onclick="shiftWeek(-1)">&#8592;</button>
      <span class="week-label" id="week-label"></span>
      <button onclick="shiftWeek(1)">&#8594;</button>
      <button onclick="weekOffset=0;renderWeek()" style="font-size:.78rem;padding:.25rem .6rem;">This Week</button>
    </div>
    <div class="week-grid" id="week-grid"></div>
  </div>
  <div id="performance-view" hidden>
    <div class="perf-grid" id="perf-grid"></div>
    <div class="perf-recommendation" id="perf-rec"></div>
  </div>
</main>

<script>
let D = { articles:[], pieces:[], tasks:[], week:[], topics:[], hook_types:[] };
let weekOffset = 0;

document.getElementById("nav-date").textContent =
  new Date().toLocaleDateString("en-US", {weekday:"short",month:"short",day:"numeric",year:"numeric"});

async function init() {
  const r = await fetch("/api/data");
  D = await r.json();
  renderArticles();
}

// -- view switch -------------------------------------------------------
function switchView(v) {
  document.getElementById("articles-view").hidden    = v !== "articles";
  document.getElementById("week-view").hidden        = v !== "week";
  document.getElementById("performance-view").hidden = v !== "performance";
  ["articles","week","performance"].forEach(t =>
    document.getElementById(`tab-${t}`).classList.toggle("active", v === t));
  if (v === "week")        renderWeek();
  if (v === "performance") renderPerformance();
}

// -- articles view -----------------------------------------------------
function isOverdue(a) {
  if (!a.publish_date) return false;
  if (a.publish_date >= toISO(new Date())) return false;
  return D.pieces.some(p => !(a.pieces[p.key]||{}).published);
}

function renderArticles() {
  const today    = toISO(new Date());
  const upcoming = [...D.articles]
    .filter(a => !a.publish_date || a.publish_date >= today)
    .sort((a,b) => {
      if (!a.publish_date && !b.publish_date) return 0;
      if (!a.publish_date) return 1;
      if (!b.publish_date) return -1;
      return a.publish_date.localeCompare(b.publish_date);
    });
  const past = [...D.articles]
    .filter(a => a.publish_date && a.publish_date < today)
    .sort((a,b) => b.publish_date.localeCompare(a.publish_date));

  renderStats([...upcoming, ...past]);

  if (!upcoming.length && !past.length) {
    document.getElementById("article-list").innerHTML =
      `<div class="empty"><h3>No articles found</h3>
       <p>Run the atomizer to generate content in pending/</p></div>`;
    return;
  }

  let html = "";
  if (upcoming.length) {
    html += `<div class="section-hdr">Upcoming &amp; Active (${upcoming.length})</div>`;
    html += upcoming.map(a => cardHtml(a)).join("");
  }
  if (past.length) {
    html += `<div class="section-hdr clickable" onclick="togglePast()">
      Past (${past.length}) <span id="past-chev">&#9654;</span>
    </div>`;
    html += `<div id="past-section" hidden>${past.map(a => cardHtml(a)).join("")}</div>`;
  }
  document.getElementById("article-list").innerHTML = html;
}

function togglePast() {
  const el = document.getElementById("past-section");
  const ch = document.getElementById("past-chev");
  if (!el) return;
  el.hidden = !el.hidden;
  ch.textContent = el.hidden ? "▶" : "▼";
}

function renderStats(arts) {
  const total = arts.length;
  let tp=0, dp=0;
  for (const a of arts) for (const p of D.pieces) {
    tp++;
    if (Object.values(a.pieces[p.key]||{}).every(Boolean)) dp++;
  }
  const tagged = arts.filter(a => a.topic && a.hook_type).length;
  document.getElementById("stats-bar").innerHTML = `
    <div><div class="stat-val">${total}</div><div class="stat-lbl">Articles</div></div>
    <div><div class="stat-val" id="sv-pieces">${dp}/${tp}</div><div class="stat-lbl">Pieces Done</div></div>
    <div><div class="stat-val">${arts.filter(a=>a.stage==="published").length}</div><div class="stat-lbl">Published</div></div>
    <div><div class="stat-val">${arts.filter(a=>a.stage==="scheduled").length}</div><div class="stat-lbl">Scheduled</div></div>
    <div><div class="stat-val">${arts.filter(a=>a.stage==="approved").length}</div><div class="stat-lbl">Approved</div></div>
    <div><div class="stat-val">${arts.filter(a=>a.stage==="pending").length}</div><div class="stat-lbl">Pending</div></div>
    <div><div class="stat-val">${tagged}/${total}</div><div class="stat-lbl">Tagged</div></div>`;
}

function pct(a) {
  let d=0, t=0;
  for (const p of D.pieces) for (const v of Object.values(a.pieces[p.key]||{})) { t++; if(v) d++; }
  return t ? Math.round(d/t*100) : 0;
}

function engScore(eng) {
  if (!eng) return null;
  const c = eng.comments   || 0;
  const r = eng.reactions  || 0;
  const i = eng.impressions|| 0;
  if (!c && !r && !i) return null;
  return c * 3 + r + Math.round(i / 100);
}

function cardHtml(a) {
  const p      = pct(a);
  const id     = CSS.escape(a.slug);
  const num    = a.art_num ? `<span class="art-badge">${a.art_num}</span>` : "";
  const od     = isOverdue(a) ? `<span class="overdue-badge">OVERDUE</span>` : "";
  const ttl    = a.title || a.slug;
  const dt     = a.publish_date ? fmtDate(a.publish_date) : "No date";
  const rows   = D.pieces.map(pc => rowHtml(a, pc)).join("");

  const topicOpts = D.topics.map(t =>
    `<option value="${t}" ${a.topic===t?"selected":""}>${t}</option>`).join("");
  const hookOpts  = D.hook_types.map(h =>
    `<option value="${h}" ${a.hook_type===h?"selected":""}>${h}</option>`).join("");
  const topicCls  = a.topic     ? "tag-select set" : "tag-select";
  const hookCls   = a.hook_type ? "tag-select set" : "tag-select";

  return `
<div class="article-card" id="card-${id}">
  <div class="card-header" onclick="toggleCard('${a.slug}')">
    ${num}${od}
    <span class="card-title">
      <span ondblclick="editTitle('${a.slug}',this);event.stopPropagation()" title="Double-click to edit">${ttl}</span>
    </span>
    <span class="card-date">${dt}</span>
    <span class="stage-badge s-${a.stage}">${a.stage}</span>
    <div class="hdr-bar">
      <div class="bar"><div class="bar-fill" id="hb-${id}" style="width:${p}%"></div></div>
      <div class="bar-pct" id="hp-${id}">${p}%</div>
    </div>
    <span class="chevron" id="chev-${id}">&#9654;</span>
  </div>
  <div id="body-${id}" hidden>
    <div class="card-tags" onclick="event.stopPropagation()">
      <label>Topic</label>
      <select class="${topicCls}" id="topic-${id}"
              onchange="saveTag('${a.slug}','topic',this.value,this)">
        <option value="">-- select topic --</option>${topicOpts}
      </select>
      <label style="margin-left:.5rem">Hook</label>
      <select class="${hookCls}" id="hook-${id}"
              onchange="saveTag('${a.slug}','hook_type',this.value,this)">
        <option value="">-- select hook --</option>${hookOpts}
      </select>
    </div>
    <table class="piece-table"><tbody>${rows}</tbody></table>
  </div>
</div>`;
}

function rowHtml(a, piece) {
  const tasks = a.pieces[piece.key] || {};
  const done  = Object.values(tasks).filter(v => typeof v === "boolean").filter(Boolean).length;
  const total = D.tasks.length;
  const p     = Math.round(done/total*100);
  const id    = CSS.escape(a.slug);
  const overrides = piece.task_overrides || {};
  const cbs   = D.tasks.map(t => `
    <div class="task-wrap">
      <input type="checkbox" class="task-cb"
             id="cb-${id}-${piece.key}-${t.key}"
             ${tasks[t.key] ? "checked" : ""}
             onchange="toggleCb('${a.slug}','${piece.key}','${t.key}',this.checked)">
      <label for="cb-${id}-${piece.key}-${t.key}">${overrides[t.key] || t.label}</label>
    </div>`).join("");
  const manualBadge = piece.manual ? `<span class="manual-badge">${piece.tool}</span>` : "";

  let engRow = "";
  if (piece.track_engagement && tasks.published) {
    const eng  = (a.engagement || {})[piece.key] || {};
    const sc   = engScore(eng);
    const scHtml = sc !== null ? `<span class="eng-score">Score: ${sc}</span>` : "";
    engRow = `
<tr class="eng-row">
  <td colspan="3">
    <div class="eng-fields">
      <div class="eng-field">
        <span>Impressions</span>
        <input class="eng-input" type="number" min="0" placeholder="0"
               value="${eng.impressions ?? ""}"
               id="eng-${id}-${piece.key}-impressions"
               onblur="saveEngagement('${a.slug}','${piece.key}','impressions',this.value)"
               onkeydown="if(event.key==='Enter')this.blur()">
      </div>
      <div class="eng-field">
        <span>Comments</span>
        <input class="eng-input" type="number" min="0" placeholder="0"
               value="${eng.comments ?? ""}"
               id="eng-${id}-${piece.key}-comments"
               onblur="saveEngagement('${a.slug}','${piece.key}','comments',this.value)"
               onkeydown="if(event.key==='Enter')this.blur()">
      </div>
      <div class="eng-field">
        <span>Reactions</span>
        <input class="eng-input" type="number" min="0" placeholder="0"
               value="${eng.reactions ?? ""}"
               id="eng-${id}-${piece.key}-reactions"
               onblur="saveEngagement('${a.slug}','${piece.key}','reactions',this.value)"
               onkeydown="if(event.key==='Enter')this.blur()">
      </div>
      ${scHtml}
    </div>
  </td>
</tr>`;
  }

  return `
<tr>
  <td><div class="piece-name">${piece.label}${manualBadge}</div><div class="piece-day">${piece.day}</div></td>
  <td><div class="tasks-row">${cbs}</div></td>
  <td class="piece-prog">
    <div class="bar"><div class="bar-fill" id="pb-${id}-${piece.key}" style="width:${p}%"></div></div>
    <div class="bar-pct">${done}/${total}</div>
  </td>
</tr>${engRow}`;
}

function toggleCard(slug) {
  const id   = CSS.escape(slug);
  const body = document.getElementById(`body-${id}`);
  const chev = document.getElementById(`chev-${id}`);
  if (!body) return;
  body.hidden = !body.hidden;
  chev.classList.toggle("open", !body.hidden);
}

function editTitle(slug, el) {
  const prev = el.textContent;
  const inp  = document.createElement("input");
  inp.value  = prev;
  el.replaceWith(inp);
  inp.focus(); inp.select();
  async function save() {
    const val = inp.value.trim() || prev;
    await fetch("/api/title", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({slug, title: val})
    });
    const span = document.createElement("span");
    span.textContent = val;
    span.title = "Double-click to edit";
    span.ondblclick = e => { editTitle(slug, span); e.stopPropagation(); };
    inp.replaceWith(span);
    const art = D.articles.find(x => x.slug === slug);
    if (art) art.title = val;
  }
  inp.onblur = save;
  inp.onkeydown = e => {
    if (e.key === "Enter")  inp.blur();
    if (e.key === "Escape") { inp.value = prev; inp.blur(); }
  };
}

async function toggleCb(slug, piece, task, checked) {
  await fetch("/api/checkbox", {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({slug, piece, task, checked})
  });
  const art = D.articles.find(x => x.slug === slug);
  if (art && art.pieces[piece]) art.pieces[piece][task] = checked;

  // Re-render just this piece row so engagement fields appear/disappear
  const id      = CSS.escape(slug);
  const pieceObj = D.pieces.find(p => p.key === piece);
  if (art && pieceObj) {
    const allRows = document.querySelectorAll(`#body-${id} .piece-table tbody tr`);
    // Find the row for this piece and update the whole piece section
    const tbody = document.querySelector(`#body-${id} .piece-table tbody`);
    if (tbody) tbody.innerHTML = D.pieces.map(pc => rowHtml(art, pc)).join("");
  }

  // Update card header bar
  const hb = document.getElementById(`hb-${id}`);
  const hp = document.getElementById(`hp-${id}`);
  if (hb && art) { const p = pct(art); hb.style.width=`${p}%`; if(hp) hp.textContent=`${p}%`; }

  // Update stats
  const arts = D.articles;
  let tp=0, dp=0;
  for (const a of arts) for (const pc of D.pieces) {
    tp++;
    if (Object.values(a.pieces[pc.key]||{}).filter(v=>typeof v==="boolean").every(Boolean)) dp++;
  }
  const sv = document.getElementById("sv-pieces");
  if (sv) sv.textContent = `${dp}/${tp}`;
}

async function saveTag(slug, field, value, el) {
  const body = {};
  body[field] = value || null;
  await fetch("/api/tags", {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({slug, ...body})
  });
  const art = D.articles.find(x => x.slug === slug);
  if (art) art[field] = value || null;
  el.className = value ? "tag-select set" : "tag-select";
}

async function saveEngagement(slug, piece, field, value) {
  const body = {slug, piece};
  body[field] = value === "" ? null : parseInt(value, 10);
  await fetch("/api/engagement", {
    method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  const art = D.articles.find(x => x.slug === slug);
  if (art) {
    if (!art.engagement) art.engagement = {};
    if (!art.engagement[piece]) art.engagement[piece] = {};
    art.engagement[piece][field] = body[field];
    // Update score display
    const id  = CSS.escape(slug);
    const sc  = engScore(art.engagement[piece]);
    const scEl = document.querySelector(`#eng-${id}-${piece}-impressions`)
                  ?.closest(".eng-fields")?.querySelector(".eng-score");
    if (sc !== null) {
      if (scEl) { scEl.textContent = `Score: ${sc}`; }
      else {
        const container = document.querySelector(`#eng-${id}-${piece}-impressions`)?.closest(".eng-fields");
        if (container) {
          const s = document.createElement("span");
          s.className = "eng-score";
          s.textContent = `Score: ${sc}`;
          container.appendChild(s);
        }
      }
    }
  }
}

// -- performance view --------------------------------------------------
function renderPerformance() {
  const scored = D.articles.filter(a => {
    const eng = a.engagement || {};
    return Object.values(eng).some(e => engScore(e) !== null);
  });

  if (!scored.length) {
    document.getElementById("perf-grid").innerHTML = "";
    document.getElementById("perf-rec").innerHTML =
      `<div class="perf-no-data"><h3>No engagement data yet</h3>
       <p>After publishing, open an article card and enter impressions, comments, and reactions for each posted piece.</p></div>`;
    return;
  }

  // Aggregate by topic
  const byTopic    = aggregateBy(scored, "topic");
  const byHookType = aggregateBy(scored, "hook_type");

  document.getElementById("perf-grid").innerHTML =
    perfTableHtml("By Topic", byTopic) +
    perfTableHtml("By Hook Type", byHookType);

  document.getElementById("perf-rec").innerHTML = recHtml(byTopic, byHookType);
}

function aggregateBy(arts, field) {
  const map = {};
  for (const a of arts) {
    const key = a[field];
    if (!key) continue;
    const scores = Object.values(a.engagement || {})
      .map(e => engScore(e)).filter(s => s !== null);
    if (!scores.length) continue;
    const avg = scores.reduce((s,v) => s+v, 0) / scores.length;
    if (!map[key]) map[key] = { total: 0, count: 0 };
    map[key].total += avg;
    map[key].count += 1;
  }
  return Object.entries(map)
    .map(([k, v]) => ({ name: k, avg: Math.round(v.total / v.count), count: v.count }))
    .sort((a,b) => b.avg - a.avg);
}

function scoreCls(val, max) {
  if (!max) return "score-mid";
  const ratio = val / max;
  if (ratio >= 0.7) return "score-high";
  if (ratio >= 0.35) return "score-mid";
  return "score-low";
}

function perfTableHtml(title, rows) {
  if (!rows.length) {
    return `<div class="perf-card">
      <div class="perf-card-hdr">${title}</div>
      <div style="padding:.75rem 1rem;font-size:.8rem;color:var(--muted);">No tagged data yet.</div>
    </div>`;
  }
  const max = rows[0].avg;
  const trs = rows.map(r => `
    <tr>
      <td>${r.name}</td>
      <td>${r.count} post${r.count>1?"s":""}</td>
      <td><span class="score-pill ${scoreCls(r.avg,max)}">${r.avg}</span></td>
    </tr>`).join("");
  return `<div class="perf-card">
    <div class="perf-card-hdr">${title}</div>
    <table class="perf-table">
      <thead><tr><th>Name</th><th>Posts</th><th>Avg Score</th></tr></thead>
      <tbody>${trs}</tbody>
    </table>
  </div>`;
}

function recHtml(byTopic, byHookType) {
  const topTopic = byTopic[0];
  const topHook  = byHookType[0];
  const lowTopic = byTopic[byTopic.length - 1];
  const lowHook  = byHookType[byHookType.length - 1];

  let body = "";
  if (topTopic && topHook) {
    body += `<p>Your audience engages most with <strong>${topTopic.name}</strong> topics using a <strong>${topHook.name}</strong> hook.
    Write your next article in this lane.</p>`;
  }
  if (lowTopic && lowTopic !== topTopic) {
    body += `<p style="margin-top:.4rem;color:var(--muted);font-size:.78rem;">
    Lowest performing topic: <strong>${lowTopic.name}</strong> — consider resting this angle or testing a different hook.</p>`;
  }
  if (!body) body = `<p>Keep entering engagement data to get recommendations.</p>`;

  return `<div class="perf-rec-hdr">Next Article Recommendation</div>
  <div class="perf-rec-body">${body}</div>`;
}

// -- week view ---------------------------------------------------------
function getMonday(d) {
  const dt  = new Date(typeof d === "string" ? d + "T00:00:00" : d);
  const day = dt.getDay();
  dt.setDate(dt.getDate() + (day === 0 ? -6 : 1 - day));
  dt.setHours(0,0,0,0);
  return dt;
}

function toISO(d) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
}

function shiftWeek(dir) { weekOffset += dir; renderWeek(); }

function renderWeek() {
  const base = getMonday(new Date());
  base.setDate(base.getDate() + weekOffset * 7);
  const end = new Date(base); end.setDate(end.getDate() + 6);
  document.getElementById("week-label").textContent =
    `Week of ${fmtShort(base)} – ${fmtShort(end)}`;

  const todayISO = toISO(new Date());
  const baseISO  = toISO(base);

  document.getElementById("week-grid").innerHTML = D.week.map(slot => {
    const d       = new Date(base); d.setDate(base.getDate() + slot.wd);
    const dISO    = toISO(d);
    const isToday = dISO === todayISO;
    const active  = D.articles.filter(a => {
      if (!a.publish_date) return false;
      return toISO(getMonday(a.publish_date)) === baseISO;
    });

    let inner = "";
    if (slot.engage) {
      inner = `<div class="engage-note">Comment on 5-10 posts<br>Reply to all comments</div>`;
    } else {
      for (const key of (slot.keys || [])) {
        const pieceInfo  = D.pieces.find(p => p.key === key);
        const pieceLabel = pieceInfo ? pieceInfo.label : key;
        for (const a of active) {
          const tasks = a.pieces[key] || {};
          const done  = Object.values(tasks).filter(v=>typeof v==="boolean").filter(Boolean).length;
          const total = D.tasks.length;
          const p     = Math.round(done/total*100);
          const lbl   = a.art_num || a.slug;
          inner += `
            <div class="art-chip" onclick="goToArticle('${a.slug}')"
                 title="${pieceLabel}: ${a.title||a.slug}">${lbl} · ${pieceLabel}</div>
            <div class="mini-bar"><div class="mini-fill" style="width:${p}%"></div></div>`;
        }
      }
      if (slot.launch) {
        inner += `<div class="launch-protocol">
          <div class="lp-title">Launch Protocol</div>
          <div>T&#8209;15: Comment on 5&#8209;10 posts</div>
          <div>T&#8209;0: Publish</div>
          <div>T+90min: Reply to all comments</div>
        </div>`;
      }
    }

    return `
<div class="day-col${isToday?" today":""}${slot.engage?" engage":""}">
  <div class="day-header">
    <div class="day-name">${slot.day}</div>
    <div class="day-date">${d.getMonth()+1}/${d.getDate()}</div>
  </div>
  <div class="day-body">
    <div class="day-type">${slot.label}</div>
    ${slot.time ? `<div class="day-time">${slot.time} <span class="cdt-time">${slot.time_cdt}</span></div>` : ""}
    ${inner}
  </div>
</div>`;
  }).join("");
}

function goToArticle(slug) {
  switchView("articles");
  const id  = CSS.escape(slug);
  const el  = document.getElementById(`card-${id}`);
  if (!el) return;
  el.scrollIntoView({behavior:"smooth", block:"start"});
  const body = document.getElementById(`body-${id}`);
  const chev = document.getElementById(`chev-${id}`);
  if (body && body.hidden) { body.hidden = false; chev.classList.add("open"); }
}

// -- utils -------------------------------------------------------------
function fmtDate(s) {
  return new Date(s + "T00:00:00").toLocaleDateString("en-US",
    {month:"short", day:"numeric", year:"numeric"});
}
function fmtShort(d) {
  return d.toLocaleDateString("en-US", {month:"short", day:"numeric"});
}

init();

async function refreshData() {
  try {
    const r     = await fetch("/api/data");
    const fresh = await r.json();
    const existing = new Set(D.articles.map(a => a.slug));
    const hasNew   = fresh.articles.some(a => !existing.has(a.slug));
    if (!hasNew) return;
    const expanded = new Set(
      D.articles
        .filter(a => { const el = document.getElementById(`body-${CSS.escape(a.slug)}`); return el && !el.hidden; })
        .map(a => a.slug)
    );
    D = fresh;
    renderArticles();
    for (const slug of expanded) {
      const id = CSS.escape(slug);
      const body = document.getElementById(`body-${id}`);
      const chev = document.getElementById(`chev-${id}`);
      if (body) { body.hidden = false; chev?.classList.add("open"); }
    }
  } catch(e) {}
}
setInterval(refreshData, 60000);
</script>
</body>
</html>"""

# -- entry ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Content Pipeline Dashboard")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    print(f"[dashboard] Listening on http://localhost:{args.port}")
    print(f"[dashboard] LAN access:  http://<this-pc-ip>:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
