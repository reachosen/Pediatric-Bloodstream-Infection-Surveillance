from __future__ import annotations

import json
from datetime import datetime, timedelta
from html import escape
from typing import Any

from engine import (
    bedside_copy,
    bedside_tone,
    evaluate_case,
    lookup_organism,
    parse_iso,
    sir_copy,
    summarize_queue,
    surveillance_tone,
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&display=swap');

:root {
  --bg: #f3efe6;
  --bg-elevated: #faf8f3;
  --surface: #fffcf7;
  --ink: #1c1a16;
  --ink-muted: #5e5a53;
  --ink-subtle: #8a857c;
  --line: #e4dfd4;
  --accent: #1a4a46;
  --accent-fg: #f3efe6;
  --accent-soft: #dce8e6;
  --danger: #c45c6a;
  --danger-soft: #f8e2e5;
  --warn: #c4892a;
  --warn-soft: #f6e9cc;
  --ok: #1a4a46;
  --ok-soft: #d7ebe6;
  --shadow: 0 0 0 1px rgb(28 26 22 / 0.06), 0 1px 2px -1px rgb(28 26 22 / 0.06), 0 2px 4px 0 rgb(28 26 22 / 0.04);
}

html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--ink);
  font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
}
.stApp > header,
header[data-testid="stHeader"] {
  display: none !important;
  height: 0 !important;
}
[data-testid="stAppViewContainer"] > .main { background: var(--bg) !important; }
.block-container {
  max-width: 72rem !important;
  padding: 0 1.25rem 3rem !important;
}
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stMarkdown, .stMarkdown p { color: var(--ink); }
a { color: var(--accent); text-decoration: none; }

.aegis-shell { color: var(--ink); }
.aegis-header {
  display: flex !important; align-items: center; justify-content: space-between; gap: 1rem;
  padding: 0.85rem 0; border-bottom: 1px solid var(--line); margin-bottom: 1.75rem;
}
.brand { display: flex !important; align-items: center; gap: 0.7rem; color: var(--ink); }
.brand-mark {
  width: 28px; height: 28px; flex-shrink: 0; color: var(--accent); position: relative; display: block;
}
.brand-mark::before {
  content: ""; position: absolute; inset: 0;
  border: 1.6px solid currentColor;
  border-radius: 42% 42% 38% 38% / 28% 28% 54% 54%;
}
.brand-mark::after {
  content: ""; position: absolute; left: 50%; top: 50%;
  width: 12px; height: 12px; transform: translate(-50%, -50%);
  background:
    linear-gradient(currentColor, currentColor) center / 12px 1.6px no-repeat,
    linear-gradient(currentColor, currentColor) center / 1.6px 12px no-repeat;
}
.brand-name { font-family: "Source Serif 4", Georgia, serif; font-size: 1.15rem; line-height: 1.1; }
.brand-sub { display: block; font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-subtle); margin-top: 2px; }
.nav { display: flex !important; gap: 0.25rem; }
.nav a {
  display: inline-flex; align-items: center; height: 44px; padding: 0 0.85rem;
  border-radius: 8px; font-size: 0.9rem; font-weight: 500; color: var(--ink-muted);
}
.nav a.current { background: var(--accent-soft); color: var(--accent); }
.window-meta { text-align: right; font-size: 0.75rem; color: var(--ink-muted); }
.window-meta strong { display: block; color: var(--ink); font-weight: 500; font-variant-numeric: tabular-nums; margin-top: 2px; }

.label-micro {
  display: block;
  font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--ink-subtle);
}
h1.display, h2.display, h3.display, .display {
  font-family: "Source Serif 4", Georgia, serif; letter-spacing: -0.02em; line-height: 1.15; color: var(--ink);
  font-weight: 500; margin: 0;
}
h1.display { font-size: clamp(2rem, 4vw, 3rem); margin-top: 0.75rem; }
h2.display { font-size: 1.5rem; }
p.lede { max-width: 40rem; color: var(--ink-muted); font-size: 1.05rem; line-height: 1.55; margin-top: 1rem; }

.stats { display: grid !important; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin: 2rem 0; }
@media (min-width: 720px) { .stats { grid-template-columns: repeat(4, 1fr); } }
.stat { background: var(--surface); box-shadow: var(--shadow); border-radius: 12px; padding: 1rem; }
.stat.em { background: var(--accent); color: var(--accent-fg); }
.stat.ok { background: var(--ok-soft); color: var(--ok); }
.stat.danger { background: var(--danger-soft); color: var(--danger); }
.stat .k { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-subtle); }
.stat.em .k, .stat.em .h { color: rgb(243 239 230 / 0.7); }
.stat.ok .k, .stat.ok .h, .stat.danger .k, .stat.danger .h { color: inherit; opacity: 0.72; }
.stat .v { font-family: "Source Serif 4", Georgia, serif; font-size: 1.85rem; font-variant-numeric: tabular-nums; margin-top: 0.5rem; line-height: 1; }
.stat .h { font-size: 0.75rem; color: var(--ink-muted); margin-top: 0.5rem; }

.queue { background: var(--surface); box-shadow: var(--shadow); border-radius: 16px; overflow: hidden; }
.q-head, a.q-row, .q-row {
  display: grid !important; grid-template-columns: 1.35fr 0.95fr minmax(0, 2.6fr);
  gap: 0.85rem; align-items: stretch; padding: 0.85rem 1.15rem;
  text-decoration: none !important;
}
.q-head {
  font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-subtle);
  border-bottom: 1px solid var(--line); align-items: center;
}
.q-row { border-top: 1px solid var(--line); color: inherit !important; }
.q-row:first-of-type { border-top: 0; }
a.q-row { color: inherit !important; }
a.q-row:hover { background: var(--bg-elevated); }
.q-name { font-weight: 500; color: var(--ink); }
.q-sub { display: block; font-size: 0.85rem; color: var(--ink-muted); }
.org { font-family: "Source Serif 4", Georgia, serif; font-style: italic; }
.seq {
  display: inline-flex; width: 24px; height: 24px; border-radius: 999px; align-items: center; justify-content: center;
  font-size: 0.75rem; background: var(--line); color: var(--ink-muted); font-variant-numeric: tabular-nums; margin-right: 0.6rem;
}
.seq.ok { background: var(--ok-soft); color: var(--ok); }

.pair {
  display: grid !important;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-radius: 12px;
  overflow: hidden;
  min-height: 100%;
  box-shadow: inset 0 0 0 1px rgb(28 26 22 / 0.08);
}
.pair-head {
  display: grid !important;
  grid-template-columns: 1fr 1fr;
}
.pair-head > span { padding: 0 1rem; }
.lane {
  display: block !important;
  padding: 0.7rem 1rem 0.8rem;
  border-left: 5px solid var(--ink-subtle);
  background: var(--bg);
  min-width: 0;
}
.lane.ok { border-left-color: var(--ok); background: var(--ok-soft); }
.lane.danger { border-left-color: var(--danger); background: var(--danger-soft); }
.lane.warn { border-left-color: var(--warn); background: var(--warn-soft); }
.lane + .lane { box-shadow: inset 1px 0 0 rgb(28 26 22 / 0.08); }
.lane-title {
  display: block;
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.05rem;
  line-height: 1.2;
  margin: 0.2rem 0 0.15rem;
  color: inherit;
}
.lane.ok, .lane.ok .lane-title { color: var(--ok); }
.lane.danger, .lane.danger .lane-title { color: var(--danger); }
.lane.warn, .lane.warn .lane-title { color: var(--warn); }
.lane-sub { display: block; font-size: 0.78rem; color: var(--ink-muted); margin: 0; line-height: 1.35; }
.pair.pair-lg { border-radius: 16px; box-shadow: var(--shadow); }
.pair.pair-lg .lane { padding: 1.15rem 1.25rem; }
.pair.pair-lg .lane-title { font-size: 1.55rem; }
.legend {
  display: flex; flex-wrap: wrap; gap: 0.85rem 1.25rem;
  margin: 0.65rem 0 1rem; font-size: 0.75rem; color: var(--ink-muted);
}
.swatch {
  display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  margin-right: 0.4rem; vertical-align: -1px;
}
.swatch.ok { background: var(--ok); }
.swatch.danger { background: var(--danger); }
.swatch.warn { background: var(--warn); }

.badge {
  display: inline-flex; align-items: center; border-radius: 999px; padding: 0.15rem 0.65rem;
  font-size: 0.75rem; font-weight: 500; letter-spacing: 0.02em; white-space: nowrap;
}
.badge-danger { background: var(--danger-soft); color: var(--danger); }
.badge-ok { background: var(--ok-soft); color: var(--ok); }
.badge-warn { background: var(--warn-soft); color: var(--warn); }
.badge-accent { background: var(--accent-soft); color: var(--accent); }
.badge-muted { background: var(--line); color: var(--ink-muted); }
.badge-ink { background: var(--ink); color: var(--accent-fg); }

.card { background: var(--surface); box-shadow: var(--shadow); border-radius: 16px; padding: 1.15rem 1.25rem; }
.card.warn { box-shadow: var(--shadow), inset 5px 0 0 var(--warn); }
.card + .card, .stack > * + * { margin-top: 1rem; }
.grid-2 { display: grid !important; gap: 1rem; }
@media (min-width: 900px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
.facts { list-style: none; padding: 0; margin: 0; }
.facts li { display: flex; justify-content: space-between; gap: 1rem; font-size: 0.9rem; padding: 0.25rem 0; }
.facts .k { color: var(--ink-muted); }
.facts .ok { color: var(--ok); }
.facts .warn { color: var(--warn); }
.facts .danger { color: var(--danger); }
.verdict-bar {
  margin-top: 0.75rem; background: var(--bg); border-radius: 8px; padding: 0.5rem 0.75rem;
  font-family: "Source Serif 4", Georgia, serif; font-size: 0.95rem;
}
.iwp { display: grid !important; grid-template-columns: repeat(7, 1fr); gap: 0.35rem; margin-top: 0.75rem; }
.iwp-day { background: var(--bg); border-radius: 8px; text-align: center; padding: 0.5rem 0.2rem; }
.iwp-day.doe { background: var(--accent); color: var(--accent-fg); }
.iwp-day .wd { font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-subtle); }
.iwp-day.doe .wd { color: rgb(243 239 230 / 0.7); }
.iwp-day .dn { font-family: "Source Serif 4", Georgia, serif; font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.iwp-day .anc { font-family: "IBM Plex Mono", monospace; font-size: 0.65rem; margin-top: 0.4rem; color: var(--ink-muted); }
.iwp-day.doe .anc { color: rgb(243 239 230 / 0.85); }
.dots { display: flex; justify-content: center; gap: 3px; height: 8px; margin-top: 0.4rem; }
.dot { width: 6px; height: 6px; border-radius: 99px; background: var(--danger); }
.dot.ev { background: var(--ok); }
.dot.fe { background: var(--warn); }
.iwp-day.doe .dot { background: var(--accent-fg); }

.phases { display: grid !important; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.9rem; }
@media (min-width: 900px) { .phases { grid-template-columns: repeat(4, 1fr); } }
.phase { background: var(--bg); border-radius: 12px; padding: 0.75rem; }
.phase.skipped { opacity: 0.6; }
.phase p { font-size: 0.75rem; color: var(--ink-muted); line-height: 1.45; margin: 0.4rem 0 0; }

.gauge-track { position: relative; height: 8px; background: var(--bg); border-radius: 99px; margin: 0.5rem 0 1rem; }
.gauge-mid { position: absolute; top: 0; bottom: 0; left: 50%; width: 1px; background: var(--warn); }
.gauge-knob {
  position: absolute; top: 50%; width: 12px; height: 12px; border-radius: 99px; transform: translate(-50%, -50%);
}
.delta { font-family: "Source Serif 4", Georgia, serif; font-size: 2rem; font-variant-numeric: tabular-nums; line-height: 1; }
.stamp { font-family: "Source Serif 4", Georgia, serif; font-size: 1.6rem; line-height: 1.15; margin-top: 0.4rem; }
.stamp.danger { color: var(--danger); }
.stamp.ok { color: var(--ok); }
.stamp.warn { color: var(--warn); }
.stamp.muted { color: var(--ink-muted); }
.stamp.accent { color: var(--ok); }

.two-col { display: grid !important; gap: 1.5rem; margin-top: 1rem; }
@media (min-width: 900px) { .two-col { grid-template-columns: 1fr auto; } }
.foot { display: grid !important; gap: 1.5rem; border-top: 1px solid var(--line); padding-top: 2rem; margin-top: 2.5rem; }
@media (min-width: 700px) { .foot { grid-template-columns: 1fr 1fr; } }
.muted { color: var(--ink-muted); font-size: 0.9rem; line-height: 1.5; }
.mono { font-family: "IBM Plex Mono", monospace; font-size: 0.75rem; line-height: 1.5; background: var(--bg); border-radius: 12px; padding: 1rem; overflow: auto; white-space: pre-wrap; }
.gap-item { background: var(--bg); border-radius: 8px; padding: 0.75rem; margin-top: 0.6rem; }
.gap-item.lane { border-radius: 8px; }
.action { display: inline-flex; margin-left: 0.4rem; background: var(--warn-soft); color: var(--warn); border-radius: 99px; padding: 0.1rem 0.5rem; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
.back { display: inline-flex; align-items: center; height: 44px; color: var(--ink-muted); font-size: 0.9rem; }
.chart { width: 100%; height: 140px; margin-top: 0.5rem; }
.edition { font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-subtle); }

@media (max-width: 800px) {
  .q-head { display: none; }
  .q-row, a.q-row { grid-template-columns: 1fr; gap: 0.5rem; }
  .window-meta { display: none; }
}
@media (max-width: 560px) {
  .pair { grid-template-columns: 1fr; }
  .pair .lane + .lane { box-shadow: inset 0 1px 0 rgb(28 26 22 / 0.08); }
}

div[data-testid="stButton"] > button {
  background: var(--accent) !important; color: var(--accent-fg) !important;
  border: 0 !important; border-radius: 8px !important; height: 44px !important;
  font-weight: 500 !important; font-family: "Source Sans 3", sans-serif !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.92; }
.stTextArea textarea {
  background: var(--bg) !important; color: var(--ink) !important;
  border: 0 !important; box-shadow: var(--shadow) !important; border-radius: 12px !important;
  font-family: "Source Sans 3", sans-serif !important;
}
.stTextArea label { color: var(--ink-muted) !important; font-size: 0.8rem !important; }
[data-testid="stMarkdownContainer"] pre { display: none !important; }
[data-testid="stHtml"] { color: inherit; }
.anc-bars {
  display: flex; align-items: flex-end; gap: 0.45rem; height: 120px; margin-top: 0.6rem;
}
.anc-col {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  height: 100%; min-width: 0;
}
.anc-bar {
  width: 70%; max-width: 28px; background: var(--accent); border-radius: 4px 4px 0 0; min-height: 4px;
}
.anc-lab { font-size: 0.65rem; color: var(--ink-subtle); margin-top: 0.3rem; font-variant-numeric: tabular-nums; }
</style>
"""

MARK = ""


def badge(text: str, tone: str) -> str:
    return f'<span class="badge badge-{escape(tone)}">{escape(text)}</span>'


def bedside_sub(result: dict) -> str:
    status = result["bedside"]["status"]
    delta = result["bedside"]["deltaTtpMinutes"]
    if status == "missing-data":
        return "No paired peripheral · ΔTTP unknown"
    if delta is None:
        return result["phases"]["bedside"]["verdict"]
    return f"ΔTTP {round(delta)} min"


def verdict_pair(result: dict, large: bool = False) -> str:
    st_tone = surveillance_tone(result["surveillance"]["label"])
    bd_tone = bedside_tone(result["bedside"]["status"])
    size = " pair-lg" if large else ""
    extra_s = ""
    extra_b = ""
    if large:
        badges = []
        if result["surveillance"]["lcbiType"]:
            badges.append(badge(result["surveillance"]["lcbiType"], st_tone))
        if result["surveillance"]["mbiType"]:
            badges.append(badge(result["surveillance"]["mbiType"], "ok"))
        extra_s = (
            f'<div style="margin-top:0.7rem">{" ".join(badges)}</div>' if badges else ""
        )
        extra_b = (
            f'<p class="lane-sub" style="margin-top:0.7rem">{escape(result["bedside"]["recommendation"])}</p>'
        )
    tag = "div" if large else "span"
    return f"""
<{tag} class="pair{size}">
  <{tag} class="lane {st_tone}">
    <{tag} class="label-micro">Surveillance class · quality</{tag}>
    <{tag} class="lane-title">{escape(result["surveillance"]["label"])}</{tag}>
    <{tag} class="lane-sub">{escape(sir_copy(result["surveillance"]["sirImpact"]))}</{tag}>
    {extra_s}
  </{tag}>
  <{tag} class="lane {bd_tone}">
    <{tag} class="label-micro">Bedside action · clinical</{tag}>
    <{tag} class="lane-title">{escape(bedside_copy(result["bedside"]["status"]))}</{tag}>
    <{tag} class="lane-sub">{escape(bedside_sub(result))}</{tag}>
    {extra_b}
  </{tag}>
</{tag}>
"""


def header_html(active: str, window_label: str) -> str:
    q = "current" if active in ("queue", "case") else ""
    s = "current" if active == "spec" else ""
    return f"""
<div class="aegis-shell">
  <header class="aegis-header">
    <a class="brand" href="?page=queue">
      <span class="brand-mark" aria-hidden="true"></span>
      <span>
        <span class="brand-name">Aegis</span>
        <span class="brand-sub">BSI adjudication</span>
      </span>
    </a>
    <nav class="nav">
      <a class="{q}" href="?page=queue">Queue</a>
      <a class="{s}" href="?page=spec">Spec</a>
    </nav>
    <p class="window-meta">Synthetic review window<strong>{escape(window_label)}</strong></p>
  </header>
</div>
"""


def fmt_day(iso: str) -> str:
    d = parse_iso(iso if "T" in iso else iso + "T12:00:00")
    return d.strftime("%-d %b")


def fmt_full(iso: str) -> str:
    d = parse_iso(iso if "T" in iso else iso + "T12:00:00")
    return d.strftime("%-d %B %Y")


def fmt_dt(iso: str) -> str:
    return parse_iso(iso).strftime("%-d %b %H:%M")


def queue_html(cases: list[dict], accepted: dict[str, bool]) -> str:
    results = [evaluate_case(c) for c in cases]
    summary = summarize_queue(cases, results)
    rows = []
    for c, r in zip(cases, results):
        org = lookup_organism(c["bloodCultures"][0]["organismKey"])
        seq_cls = "seq ok" if accepted.get(c["id"]) else "seq"
        seq_txt = "✓" if accepted.get(c["id"]) else str(c["sequence"])
        rows.append(
            f"""
<a class="q-row" href="?page=case&id={escape(c['id'])}">
  <span><span class="{seq_cls}">{seq_txt}</span><span class="q-name">{escape(c['patient']['name'])}</span>
    <span class="q-sub">{escape(c['patient']['unit'])}</span></span>
  <span><span class="org">{escape(org['short'])}</span><span class="q-sub">{escape(fmt_day(r['doe']))} · MRN {escape(c['patient']['mrn'])}</span></span>
  {verdict_pair(r)}
</a>"""
        )
    return f"""
<p class="label-micro">Why this workbench exists</p>
<p class="edition">Streamlit edition · synthetic cases</p>
<h1 class="display">A positive blood culture is not a CLABSI.</h1>
<p class="lede">Five <strong>synthetic</strong> flagged cultures — invented patients, MRNs, and labs, not real records. A naive “line plus bug” rule would have added all five to the SIR. Two belong there. The rest are mucosa, lung, or a single contaminated bottle — and two of the lines should stay in.</p>
<div class="stats">
  <div class="stat"><div class="k">Naive CLABSI calls</div><div class="v">{summary['naiveClabsi']}</div><div class="h">Every positive + a line</div></div>
  <div class="stat em"><div class="k">Aegis SIR numerator</div><div class="v">{summary['sirNumerator']}</div><div class="h">What NHSN should count</div></div>
  <div class="stat ok"><div class="k">Lines to salvage</div><div class="v">{summary['salvage']}</div><div class="h">ΔTTP under 120 min</div></div>
  <div class="stat danger"><div class="k">Lines to extract</div><div class="v">{summary['extract']}</div><div class="h">Biofilm pattern supported</div></div>
</div>
<div style="display:flex;justify-content:space-between;align-items:end;gap:1rem;flex-wrap:wrap;margin:0 0 0.35rem;">
  <div><p class="label-micro">Synthetic adjudication queue</p><h2 class="display">Open events</h2></div>
  <p class="muted" style="margin:0">{summary['excluded']} of {summary['total']} excluded from the SIR</p>
</div>
<p class="legend">
  <span><span class="swatch ok"></span>Teal — excluded / salvage</span>
  <span><span class="swatch danger"></span>Pink — CLABSI / extract</span>
  <span><span class="swatch warn"></span>Gold — actionable gap</span>
</p>
<div class="queue">
  <div class="q-head">
    <span>Patient</span>
    <span>Organism</span>
    <span class="pair-head"><span>Surveillance class</span><span>Bedside action</span></span>
  </div>
  {''.join(rows)}
</div>
<div class="foot">
  <div><p class="label-micro">Quality value</p><h3 class="display">Protect the SIR</h3>
    <p class="muted">MBI-LCBI and secondary BSI are reportable in NHSN but do not belong in the CLABSI Standardized Infection Ratio. Aegis isolates them before they become an unfair penalty.</p></div>
  <div><p class="label-micro">Clinical value</p><h3 class="display">Salvage the line</h3>
    <p class="muted">Differential time to positivity is invisible to surveillance. The bedside lane uses it so a Broviac in neutropenia is not pulled on reflex — and a biofilm-positive PICC is not left in.</p></div>
</div>
"""



def _iwp_days(c: dict, result: dict) -> list[dict[str, Any]]:
    start = datetime.fromisoformat(result["iwp"]["start"] + "T12:00:00")
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        iso = d.date().isoformat()
        anc = next((a["anc"] for a in c.get("ancSeries", []) if a["at"][:10] == iso), None)
        days.append(
            {
                "iso": iso,
                "wd": d.strftime("%a").upper()[:3],
                "dn": str(d.day),
                "is_doe": iso == result["doe"],
                "anc": anc,
                "cultures": sum(1 for b in c["bloodCultures"] if b["drawnAt"][:10] == iso),
                "extra": sum(1 for b in c.get("extraVascularCultures", []) if b["drawnAt"][:10] == iso),
                "fever": any(s["at"][:10] == iso and s["type"] == "fever" for s in c.get("symptoms", [])),
            }
        )
    return days


def anc_svg(series: list[dict]) -> str:
    if not series:
        return '<p class="muted">No ANC values in this case.</p>'
    mx = max(max(p["anc"] for p in series), 600)
    cols = []
    for p in series:
        pct = max(6, min(100, (p["anc"] / mx) * 100))
        cols.append(
            f'<span class="anc-col"><span class="anc-bar" style="height:{pct:.0f}%"></span>'
            f'<span class="anc-lab">{escape(fmt_day(p["at"]))}</span></span>'
        )
    return f'<div class="anc-bars">{"".join(cols)}</div>'


def facts_html(facts: list[dict]) -> str:
    items = []
    for f in facts:
        tone = f.get("tone") or "neutral"
        cls = tone if tone in ("ok", "warn", "danger") else ""
        items.append(
            f'<li><span class="k">{escape(f["label"])}</span><span class="{cls}" style="text-align:right;max-width:60%">{escape(str(f["value"]))}</span></li>'
        )
    return f'<ul class="facts">{"".join(items)}</ul>'


def case_html(c: dict, result: dict, accepted: bool) -> str:
    days = _iwp_days(c, result)
    iwp_cells = []
    for d in days:
        cls = "iwp-day doe" if d["is_doe"] else "iwp-day"
        marks = ""
        if d["cultures"]:
            marks += '<span class="dot"></span>'
        if d["extra"]:
            marks += '<span class="dot ev"></span>'
        if d["fever"]:
            marks += '<span class="dot fe"></span>'
        anc = "—" if d["anc"] is None else str(d["anc"])
        iwp_cells.append(
            f'<div class="{cls}"><div class="wd">{d["wd"]}</div><div class="dn">{d["dn"]}</div><div class="anc">{anc}</div><div class="dots">{marks}</div></div>'
        )

    phases = []
    for i, key in enumerate(("integrity", "source", "mbi", "device"), start=1):
        p = result["phases"][key]
        skipped = " skipped" if p["status"] == "skipped" else ""
        phases.append(
            f'<div class="phase{skipped}"><p class="label-micro">{i}.0 {escape(p["name"])}</p>'
            f'<p class="display" style="font-size:1rem;margin-top:0.4rem">{escape(p["verdict"])}</p>'
            f'<p>{escape(p["math"])}</p></div>'
        )

    delta = result["bedside"]["deltaTtpMinutes"]
    pct = 0 if delta is None else max(0, min(100, (delta / 240) * 100))
    knob = (
        "var(--ink-subtle)"
        if delta is None
        else (
            "var(--danger)"
            if result["bedside"]["status"] == "biofilm-supported"
            else "var(--ok)"
        )
    )
    btone = bedside_tone(result["bedside"]["status"])
    delta_label = "—" if delta is None else str(round(delta))
    delta_unit = "no ΔTTP" if delta is None else "min"

    extras = c.get("extraVascularCultures") or []
    extra_html = (
        "".join(
            f'<div class="gap-item"><strong>{escape(ev["organism"])} · {escape(ev["siteLabel"])}</strong>'
            f'<div class="muted">{escape(fmt_dt(ev["drawnAt"]))}{" · " + ev["nhsNSite"] if ev.get("nhsNSite") else ""}</div></div>'
            for ev in extras
        )
        if extras
        else '<p class="muted">No extravascular isolates on the record.</p>'
    )
    imaging = f'<p class="muted">{escape(c["imagingNotes"])}</p>' if c.get("imagingNotes") else ""

    line = c.get("line")
    line_block = (
        f"""<dl class="facts">
          <li><span class="k">Device</span><span>{escape(line['type'])}</span></li>
          <li><span class="k">Calendar day on DOE</span><span>Day {result['lineCalendarDays']}</span></li>
          <li><span class="k">Placed</span><span>{escape(fmt_full(line['placedAt']))}</span></li>
          <li><span class="k">First inpatient access</span><span>{escape(line['firstAccessLocation'])}</span></li>
        </dl>"""
        if line
        else '<p class="muted">No central line recorded.</p>'
    )

    if result["gaps"]:
        gaps_html = "".join(
            f'<div class="gap-item {"lane warn" if g["actionable"] else ""}"><strong>{escape(g["title"])}'
            f'{"<span class=action>Action</span>" if g["actionable"] else ""}</strong>'
            f'<p class="muted" style="margin:0.35rem 0 0">{escape(g["detail"])}</p></div>'
            for g in result["gaps"]
        )
        gaps_verdict = f"{len(result['gaps'])} gap{'s' if len(result['gaps']) != 1 else ''}"
        gaps_tone = " warn" if any(g["actionable"] for g in result["gaps"]) else ""
    else:
        gaps_html = '<p class="muted">Paired cultures, symptoms, and labs are sufficient for both surveillance and bedside lanes.</p>'
        gaps_verdict = "No actionable gaps"
        gaps_tone = ""

    match = result["fixture"]["matches"]
    expected_json = escape(json.dumps(result["fixture"]["expected"], indent=2))
    actual_json = escape(json.dumps(result["fixture"]["actual"], indent=2))
    mbi_skip = " skipped" if result["phases"]["mbi"]["status"] == "skipped" else ""
    src_skip = " skipped" if result["phases"]["source"]["status"] == "skipped" else ""
    dev_skip = " skipped" if result["phases"]["device"]["status"] == "skipped" else ""

    return f"""
<a class="back" href="?page=queue">← Queue</a>
<p class="label-micro">Synthetic case · {escape(c['patient']['unit'])} · MRN {escape(c['patient']['mrn'])}</p>
<h1 class="display">{escape(c['patient']['name'])}</h1>
<p class="muted">{c['patient']['ageYears']}{escape(c['patient']['sex'])} · {escape(c['patient']['diagnosis'])}</p>
<p class="lede">{escape(c['whyItMatters'])}</p>
<div style="margin-top:1.25rem">{verdict_pair(result, large=True)}</div>
<div class="stack" style="margin-top:1.5rem">
  <section class="card">
    <div style="display:flex;justify-content:space-between"><p class="label-micro">Infection window period</p>
      <p class="muted" style="margin:0">7 days · DOE {escape(result['doe'])}</p></div>
    <div class="iwp">{''.join(iwp_cells)}</div>
    <p class="muted" style="margin-top:0.7rem">Figures are ANC (cells/mm³). Marks: blood, extravascular culture, fever.</p>
  </section>
  <section class="card">
    <p class="label-micro">Surveillance path</p>
    <div class="phases">{''.join(phases)}</div>
  </section>
  <section class="card">
    <div style="display:flex;justify-content:space-between;gap:0.75rem;align-items:start">
      <div><p class="label-micro">Parallel bedside lane · 5.0</p><h2 class="display">Should we pull this line?</h2></div>
      {badge(bedside_copy(result['bedside']['status']), btone)}
    </div>
    <div class="grid-2" style="margin-top:1rem">
      <div>
        <div class="muted" style="display:flex;justify-content:space-between;font-size:0.75rem"><span>Simultaneous</span><span>120 min</span><span>Biofilm</span></div>
        <div class="gauge-track"><div class="gauge-mid"></div>
          <div class="gauge-knob" style="left:{pct}%;background:{knob}"></div>
        </div>
        <div class="delta">{delta_label}<span style="font-size:1rem;color:var(--ink-muted);margin-left:0.3rem">{delta_unit}</span></div>
        {facts_html(result['phases']['bedside']['facts'])}
      </div>
      <div class="lane {btone}" style="border-radius:12px">
        <p class="label-micro">Clinical recommendation</p>
        <p class="lane-title" style="font-size:1.15rem">{escape(result['phases']['bedside']['verdict'])}</p>
        <p class="lane-sub" style="margin-top:0.5rem">{escape(result['bedside']['recommendation'])}</p>
      </div>
    </div>
  </section>
  <div class="grid-2">
    <section class="card{mbi_skip}">
      <p class="label-micro">Card 1</p>
      <h3 class="display">MBI profile</h3>
      <div class="verdict-bar">{escape(result['phases']['mbi']['verdict'])}</div>
      <div style="margin-top:0.9rem">{facts_html(result['phases']['mbi']['facts'])}</div>
      <p class="muted" style="margin:0.8rem 0 0;font-size:0.75rem">ANC trajectory</p>
      {anc_svg(c.get('ancSeries', []))}
    </section>
    <section class="card{src_skip}">
      <p class="label-micro">Card 2</p>
      <h3 class="display">Alternative source</h3>
      <div class="verdict-bar">{escape(result['phases']['source']['verdict'])}</div>
      <div style="margin-top:0.9rem">{facts_html(result['phases']['source']['facts'])}</div>
      <div style="margin-top:0.8rem">{extra_html}{imaging}</div>
    </section>
    <section class="card{dev_skip}">
      <p class="label-micro">Card 3</p>
      <h3 class="display">Line context</h3>
      <div class="verdict-bar">{escape(result['phases']['device']['verdict'])}</div>
      <div style="margin-top:0.9rem">{line_block}</div>
      <p class="muted" style="margin-top:0.8rem">{escape(result['phases']['device']['math'])}</p>
    </section>
    <section class="card{gaps_tone}">
      <p class="label-micro">Card 4</p>
      <h3 class="display">Gaps</h3>
      <div class="verdict-bar">{escape(gaps_verdict)}</div>
      {gaps_html}
    </section>
  </div>
  <section class="card">
    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
      <div>
        <p class="label-micro">Synthetic fixture</p>
        <h2 class="display">{escape(c['title'])}</h2>
        <p class="muted">{escape(c['hook'])} Invented for engine tests — not a real patient.</p>
      </div>
      {badge("Engine matches expected JSON" if match else "Engine diverges from fixture", "ok" if match else "danger")}
    </div>
    <div class="grid-2" style="margin-top:1rem">
      <div><p class="label-micro">Expected</p><pre class="mono">{expected_json}</pre></div>
      <div><p class="label-micro">Computed</p><pre class="mono">{actual_json}</pre></div>
    </div>
  </section>
</div>
"""


def spec_html(cases: list[dict]) -> str:
    steps = [
        ("1.0 Integrity", "Recognized pathogen from ≥1 bottle → LCBI 1. Common commensal from ≥2 specimens plus symptoms → LCBI 2/3. Otherwise contaminant."),
        ("2.0 Source", "Matching extravascular isolate inside the Secondary BSI Attribution Period, or blood as a required element of a site-specific infection → Secondary. Else Primary."),
        ("3.0 Pathophysiology", "MBI organism, no non-MBI co-isolates in the 7-day IWP, and neutropenia (ANC <500 on ≥2 IWP days) or allogeneic HSCT pathway → MBI-LCBI, excluded from SIR."),
        ("4.0 Device", "Eligible central line in place >2 consecutive calendar days after first inpatient access → Primary CLABSI. Else primary non-line LCBI."),
        ("5.0 Bedside (parallel)", "ΔTTP ≥120 min supports intraluminal biofilm (extract). ΔTTP <120 supports salvage. Missing peripheral set is an actionable gap."),
    ]
    step_html = "".join(
        f'<div class="card"><p class="display" style="font-size:1.15rem">{escape(t)}</p><p class="muted">{escape(b)}</p></div>'
        for t, b in steps
    )
    fixtures = []
    for c in cases:
        r = evaluate_case(c)
        payload = {
            "synthetic": True,
            "id": c["id"],
            "patient": c["patient"],
            "line": c["line"],
            "bloodCultures": c["bloodCultures"],
            "extraVascularCultures": c.get("extraVascularCultures", []),
            "ancSeries": c.get("ancSeries", []),
            "symptoms": c.get("symptoms", []),
            "siteSpecificInfection": c.get("siteSpecificInfection"),
            "expected": c["expected"],
        }
        fixtures.append(
            f"""<article class="card">
              <div style="display:flex;justify-content:space-between;gap:0.75rem;flex-wrap:wrap">
                <div><p class="label-micro">Synthetic case {c['sequence']}</p>
                <h3 class="display">{escape(c['title'])}</h3>
                <p class="muted">{escape(c['hook'])}</p></div>
                {badge("Pass" if r['fixture']['matches'] else "Fail", "ok" if r['fixture']['matches'] else "danger")}
              </div>
              <pre class="mono" style="max-height:24rem;margin-top:0.8rem">{escape(json.dumps(payload, indent=2))}</pre>
            </article>"""
        )
    return f"""
<p class="label-micro">Developer spec</p>
<p class="edition">Streamlit edition · synthetic cases</p>
<h1 class="display">Four surveillance layers. One bedside question.</h1>
<p class="lede">The JSON below is the source of truth for expected outcomes. Every test case is synthetic: names, MRNs, units, cultures, and timestamps are invented. The live engine evaluates the same objects.</p>
<div class="grid-2" style="margin-top:1.5rem">{step_html}</div>
<h2 class="display" style="margin:2rem 0 0.5rem">Synthetic JSON test cases</h2>
<p class="muted">Not real patients or PHI. Each fixture carries an expected object. The engine must match it.</p>
<div class="stack" style="margin-top:1rem">{''.join(fixtures)}</div>
"""
