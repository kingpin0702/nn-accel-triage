#!/usr/bin/env python3
"""Build the self-contained interactive HTML deck for NN-Accel-Triage.

Embeds the dashboard PNGs + pipeline GIF as base64 so the single .html file is
fully portable (no external assets, no CDN).
"""
from __future__ import annotations
import base64, pathlib

ROOT = pathlib.Path("/home/user/nn-accel-triage")
OUT = ROOT / "presentation" / "nn_accel_triage_deck.html"


def b64(rel: str) -> str:
    p = ROOT / rel
    data = base64.b64encode(p.read_bytes()).decode()
    mime = "image/gif" if p.suffix == ".gif" else "image/png"
    return f"data:{mime};base64,{data}"


GIF = b64("presentation/assets/pipeline_animation.gif")
IMG_VERIFY = b64("reports/dash_verification.png")
IMG_EXPLAIN = b64("reports/dash_explain_debug.png")
IMG_PACK = b64("reports/dash_packaging.png")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NN-Accel-Triage — Presentation</title>
<style>
  :root{
    --ink:#1a202c; --mute:#5a6b82; --accent:#2b6cb0; --accent2:#2f855a;
    --border:#e2e8f0; --panel:#f7f9fc; --panel2:#eef2f7; --dark:#141b2d;
    --good:#2f855a; --warn:#b7791f; --bad:#c53030;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  html,body{height:100%;}
  body{
    font-family:"Helvetica Neue",Arial,"Segoe UI",sans-serif;
    background:#0b1020; color:var(--ink);
    display:flex; align-items:center; justify-content:center; overflow:hidden;
  }
  #stage{ position:relative; width:100vw; height:100vh; }
  .slide{
    position:absolute; top:50%; left:50%;
    width:1280px; height:720px;
    transform:translate(-50%,-50%) scale(var(--scale,1));
    transform-origin:center center;
    background:#fff; overflow:hidden;
    display:none; box-shadow:0 30px 90px rgba(0,0,0,.55);
  }
  .slide.active{display:block;}
  /* ---- shared chrome ---- */
  .kicker{ position:absolute; top:54px; left:70px; font-size:15px; font-weight:700;
    letter-spacing:.14em; text-transform:uppercase; color:var(--accent); }
  h1.title{ position:absolute; top:76px; left:70px; right:70px;
    font-size:34px; font-weight:800; line-height:1.12; color:var(--ink);}
  .rule{ position:absolute; top:172px; left:70px; right:70px; height:3px;
    background:linear-gradient(90deg,var(--accent),#63b3ed 60%,transparent);}
  .foot{ position:absolute; bottom:26px; left:70px; right:70px;
    display:flex; justify-content:space-between; font-size:13px; color:var(--mute);
    border-top:1px solid var(--border); padding-top:10px;}
  .body{ position:absolute; top:198px; left:70px; right:70px; bottom:64px; }
  /* ---- lists / cards ---- */
  ul.lead{ list-style:none; }
  ul.lead li{ position:relative; padding:9px 0 9px 34px; font-size:21px; line-height:1.42;
    color:#2d3748;}
  ul.lead li::before{ content:""; position:absolute; left:4px; top:19px; width:12px; height:12px;
    border-radius:3px; background:var(--accent); }
  ul.lead li b{ color:var(--ink); }
  .sub{ color:var(--mute); font-size:17px; }
  .grid2{ display:grid; grid-template-columns:1fr 1fr; gap:22px; height:100%;}
  .grid3{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px;}
  .card{ background:var(--panel); border:1px solid var(--border); border-radius:14px;
    padding:20px 22px;}
  .card h3{ font-size:19px; color:var(--accent); margin-bottom:8px;}
  .card p{ font-size:16.5px; color:#3a4658; line-height:1.4;}
  .obj{ display:flex; gap:16px; align-items:flex-start; padding:12px 0;}
  .obj .n{ flex:none; width:44px; height:44px; border-radius:11px; background:var(--accent);
    color:#fff; font-weight:800; font-size:20px; display:flex; align-items:center; justify-content:center;}
  .obj .n.g{ background:var(--accent2);}
  .obj .t{ font-size:19px; line-height:1.34; color:#2d3748;} .obj .t b{color:var(--ink);}
  /* ---- flow (methodology) ---- */
  .flow{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px 34px; position:relative;}
  .fnode{ background:#fff; border:2px solid var(--border); border-radius:13px; padding:12px 14px;
    position:relative;}
  .fnode .fn{ font-size:12.5px; font-weight:800; color:var(--accent); letter-spacing:.05em;}
  .fnode .ft{ font-size:16px; font-weight:700; color:var(--ink); margin:3px 0 4px;}
  .fnode .fd{ font-size:13.5px; color:var(--mute); line-height:1.3;}
  .fnode.alt{ border-color:#bcd3ea; background:#f3f8fd;}
  .fnode.win{ border-color:#bfe3cf; background:#f1faf4;}
  /* ---- table ---- */
  table{ border-collapse:collapse; width:100%; font-size:15.5px;}
  th{ text-align:left; background:var(--panel2); color:#33415c; font-size:13px; letter-spacing:.05em;
    text-transform:uppercase; padding:10px 12px; border-bottom:2px solid var(--border);}
  td{ padding:9px 12px; border-bottom:1px solid #edf1f6; color:#2d3748;}
  tr:nth-child(even) td{ background:#fafcfe;}
  td.mono,.mono{ font-family:"DejaVu Sans Mono","Liberation Mono",monospace; font-size:14px;}
  .pill{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:12.5px; font-weight:700;}
  .pill.g{ background:#e6f4ec; color:var(--good);}
  .pill.b{ background:#fdecec; color:var(--bad);}
  .pill.w{ background:#fbf1dd; color:var(--warn);}
  /* ---- stat tiles ---- */
  .tiles{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px;}
  .tile{ background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:16px 18px;}
  .tile .v{ font-size:34px; font-weight:800; color:var(--accent);}
  .tile .v.g{color:var(--accent2);} .tile .v.k{color:var(--ink);}
  .tile .l{ font-size:14px; color:var(--mute); margin-top:2px;}
  .imgwrap{ height:100%; display:flex; align-items:center; justify-content:center;}
  .imgwrap img{ max-width:100%; max-height:100%; border:1px solid var(--border); border-radius:10px;
    box-shadow:0 8px 26px rgba(20,40,80,.12);}
  .cap{ position:absolute; bottom:64px; left:70px; right:70px; font-size:14px; color:var(--mute);
    font-style:italic; text-align:center;}
  /* ---- title slide ---- */
  #s0{ background:radial-gradient(1200px 700px at 70% -10%,#1c2b4a 0%,#0e1526 55%,#0b111f 100%);}
  #s0 *{ color:#fff;}
  #s0 .ey{ position:absolute; top:150px; left:80px; font-size:15px; letter-spacing:.32em;
    text-transform:uppercase; color:#8fb4e6;}
  #s0 .ti{ position:absolute; top:205px; left:80px; right:80px; font-size:60px; font-weight:800;
    line-height:1.05;}
  #s0 .st{ position:absolute; top:405px; left:80px; right:120px; font-size:24px; color:#c9d6ea;
    line-height:1.4; font-weight:400;}
  #s0 .badges{ position:absolute; bottom:150px; left:80px; display:flex; gap:14px;}
  #s0 .bdg{ background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.22);
    padding:10px 18px; border-radius:30px; font-size:16px; font-weight:600;}
  #s0 .bdg b{ color:#7fd0a3;}
  #s0 .meta{ position:absolute; bottom:70px; left:80px; font-size:15px; color:#8fa3c4;}
  /* ---- live pipeline animation ---- */
  .anim{ position:relative; height:340px; margin-top:6px;}
  .track{ position:absolute; top:120px; left:2%; right:2%; height:4px; background:var(--border); border-radius:4px;}
  .trackfill{ position:absolute; top:120px; left:2%; height:4px; background:var(--accent); border-radius:4px;
    width:0; transition:width .6s ease;}
  .stages{ position:absolute; top:40px; left:0; right:0; display:flex; justify-content:space-between;}
  .stg{ width:15.5%; text-align:center;}
  .stg .dot{ width:34px; height:34px; border-radius:50%; background:#fff; border:3px solid var(--border);
    margin:0 auto 12px; position:relative; z-index:2; transition:all .3s;}
  .stg .nm{ font-size:15px; font-weight:700; color:#4a5568;}
  .stg .sc{ font-size:12.5px; color:var(--mute); margin-top:2px; min-height:16px;}
  .stg.on .dot{ background:var(--accent); border-color:var(--accent); box-shadow:0 0 0 6px rgba(43,108,176,.16);}
  .stg.done .dot{ background:var(--accent2); border-color:var(--accent2);}
  .stg.on .nm{ color:var(--accent);}
  .token{ position:absolute; top:104px; width:56px; height:36px; margin-left:-28px; border-radius:9px;
    background:var(--accent); color:#fff; font-size:13px; font-weight:800; display:flex; align-items:center;
    justify-content:center; z-index:5; transition:left .55s cubic-bezier(.6,.05,.3,1);
    box-shadow:0 6px 16px rgba(43,108,176,.4);}
  .capband{ position:absolute; bottom:6px; left:0; right:0; background:var(--dark); color:#eef2f7;
    border-radius:12px; padding:16px 22px; font-size:19px; line-height:1.35; min-height:60px;}
  .capband b{ color:#7fb0ea;}
  /* nav */
  #dots{ position:fixed; bottom:14px; left:50%; transform:translateX(-50%); display:flex; gap:8px; z-index:50;}
  #dots i{ width:9px; height:9px; border-radius:50%; background:#41506e; cursor:pointer;}
  #dots i.on{ background:#8fb4e6; width:22px; border-radius:5px;}
  #hint{ position:fixed; top:12px; right:16px; color:#5b6b8a; font-size:12px; z-index:50;}
</style>
</head>
<body>
<div id="stage">

  <!-- 0 TITLE -->
  <section class="slide active" id="s0">
    <div class="ey">Neural-Network Accelerator Verification</div>
    <div class="ti">NN-Accel-Triage</div>
    <div class="st">Agentic AI for Failure Triage and Root-Cause Hinting<br>in Neural-Network Accelerator Verification</div>
    <div class="badges">
      <div class="bdg"><b>342.6×</b> faster triage</div>
      <div class="bdg"><b>100%</b> triage accuracy</div>
      <div class="bdg"><b>123</b> tests passing</div>
    </div>
    <div class="meta">Research project presentation · 2026 · RTL + CocoTB/Verilator + Claude</div>
  </section>

  <!-- 1 INTRODUCTION -->
  <section class="slide" id="s1">
    <div class="kicker">1 · Introduction</div>
    <h1 class="title">Verifying NN accelerators produces failures faster than humans can triage</h1>
    <div class="rule"></div>
    <div class="body">
      <ul class="lead">
        <li>Neural-network accelerators (systolic <b>MAC arrays</b> + <b>quantization</b> units) are now everywhere — and functional correctness across tensor shapes, quantization modes, and memory behavior is safety-critical.</li>
        <li>Verification runs <b>large nightly regressions</b>. When tests fail, engineers <b>triage by hand</b>: reading logs, waveforms, scoreboard diffs, and commit history to find the root cause.</li>
        <li>Manual triage is <b>slow (~3 hours per regression here), inconsistent, and does not scale</b> as the design and test suite grow.</li>
        <li>We present <b>NN-Accel-Triage</b>: a layered testbench plus an <b>agentic AI</b> that clusters failures, explains likely root causes, and recommends the next debug steps.</li>
      </ul>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Introduction</span></div>
  </section>

  <!-- 2 PROBLEM STATEMENT -->
  <section class="slide" id="s2">
    <div class="kicker">2 · Problem Statement</div>
    <h1 class="title">Automate what a verification engineer does after a failing regression</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="grid2">
        <div>
          <ul class="lead">
            <li><b>Input:</b> a regression database of RTL simulation mismatches (logs, scoreboard diffs, traces, config, commit metadata).</li>
            <li><b>Required output:</b> automatically <b>(a) group</b> failures by root cause, <b>(b) explain</b> each in natural language, and <b>(c) recommend</b> debug steps — <b>reproducibly</b> and faster than manual.</li>
          </ul>
        </div>
        <div class="card" style="align-self:start">
          <h3>Why it is hard</h3>
          <p style="margin-bottom:8px">• Failure signals are <b>heterogeneous</b> — mismatch rate, error magnitude, first-divergence cycle, config.</p>
          <p style="margin-bottom:8px">• The <b>number of distinct root causes is unknown</b> a-priori.</p>
          <p style="margin-bottom:8px">• Explanations must be <b>domain-grounded</b>, not generic.</p>
          <p>• Needs a <b>fair, repeatable benchmark</b> against the manual baseline.</p>
        </div>
      </div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Problem Statement</span></div>
  </section>

  <!-- 3 OBJECTIVES -->
  <section class="slide" id="s3">
    <div class="kicker">3 · Objectives</div>
    <h1 class="title">Five core objectives</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="obj"><div class="n">i</div><div class="t"><b>Verify functional correctness</b> across tensor shapes, quantization modes, and memory behaviors.</div></div>
      <div class="obj"><div class="n">ii</div><div class="t"><b>Cluster regression failures automatically</b> by symptom / root cause.</div></div>
      <div class="obj"><div class="n">iii</div><div class="t"><b>Generate natural-language debug summaries</b> and likely root-cause hints.</div></div>
      <div class="obj"><div class="n">iv</div><div class="t"><b>Benchmark triage time</b> against manual methods.</div></div>
      <div class="obj"><div class="n g">v</div><div class="t"><b>Package a reproducible</b> failure-analysis benchmark others can run.</div></div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Objectives</span></div>
  </section>

  <!-- 4 METHODOLOGY FLOWCHART -->
  <section class="slide" id="s4">
    <div class="kicker">4 · Methodology</div>
    <h1 class="title">A seven-stage pipeline: from RTL fault to root-cause report</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="flow">
        <div class="fnode"><div class="fn">STAGE 1</div><div class="ft">Design &amp; Fault Injection</div><div class="fd">Parameterized RTL; 13 fault variants across 8 categories (frozen ground truth).</div></div>
        <div class="fnode"><div class="fn">STAGE 2</div><div class="ft">Simulation &amp; Logging</div><div class="fd">CocoTB + Verilator vs NumPy golden model; append 1 JSON record per test.</div></div>
        <div class="fnode"><div class="fn">STAGE 3</div><div class="ft">Feature Extraction</div><div class="fd">13 features / record (+ optional VCD divergence signals).</div></div>
        <div class="fnode alt"><div class="fn">STAGE 4</div><div class="ft">Clustering</div><div class="fd">DBSCAN over feature vectors + rule-based symptom labels.</div></div>
        <div class="fnode alt"><div class="fn">STAGE 5</div><div class="ft">Agentic Triage</div><div class="fd">Claude + RAG (TF-IDF) + multi-turn debug loop &rarr; cause, confidence, steps.</div></div>
        <div class="fnode alt"><div class="fn">STAGE 6</div><div class="ft">Benchmark &amp; Eval</div><div class="fd">Per-label P/R/F1 &amp; accuracy vs ground truth; time &amp; speedup; no-LLM baseline.</div></div>
        <div class="fnode win"><div class="fn">STAGE 7</div><div class="ft">Packaging</div><div class="fd">Docker one-command pipeline, HTML dashboard, released dataset.</div></div>
        <div class="fnode" style="border-style:dashed;background:#fff"><div class="fn">FLOW</div><div class="ft">1&rarr;2&rarr;3&rarr;4&rarr;5&rarr;6&rarr;7</div><div class="fd">Every test run appends to the append-only regression_db.jsonl, the shared bus.</div></div>
      </div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Methodology</span></div>
  </section>

  <!-- 5 SYSTEM WORKING (ANIMATION) -->
  <section class="slide" id="s5">
    <div class="kicker">5 · System in Action</div>
    <h1 class="title">Watch one failing test flow through the pipeline</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="anim">
        <div class="stages" id="stages">
          <div class="stg" data-sc="fault_acc_overflow"><div class="dot"></div><div class="nm">RTL Fault</div><div class="sc"></div></div>
          <div class="stg" data-sc="N×N MAC · INT8"><div class="dot"></div><div class="nm">Verilator Sim</div><div class="sc"></div></div>
          <div class="stg" data-sc="regression_db"><div class="dot"></div><div class="nm">Mismatch Rec.</div><div class="sc"></div></div>
          <div class="stg" data-sc="→ overflow_fault"><div class="dot"></div><div class="nm">Cluster</div><div class="sc"></div></div>
          <div class="stg" data-sc="RAG + agent"><div class="dot"></div><div class="nm">Claude Triage</div><div class="sc"></div></div>
          <div class="stg" data-sc="cause+conf"><div class="dot"></div><div class="nm">Report</div><div class="sc"></div></div>
        </div>
        <div class="track"></div><div class="trackfill" id="tfill"></div>
        <div class="token" id="token">BUG</div>
        <div class="capband" id="capband"><b>STEP 1/6</b> &nbsp; Injected RTL fault variant selected from the frozen fault library.</div>
      </div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>System in Action &nbsp;·&nbsp; auto-loops — press → to advance slide</span></div>
  </section>

  <!-- 6 VISUALS -->
  <section class="slide" id="s6">
    <div class="kicker">6 · Visuals — Triage Dashboard</div>
    <h1 class="title">One dashboard covers verification, explanation, and packaging</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="grid3" style="height:100%">
        <div class="card" style="padding:12px; display:flex; flex-direction:column">
          <h3 style="font-size:16px">Verification</h3>
          <div class="imgwrap" style="flex:1"><img src="__VERIFY__" alt="verification"></div>
          <p style="font-size:13px; margin-top:6px">Cluster summary + 27 records (15 pass / 12 fail).</p>
        </div>
        <div class="card" style="padding:12px; display:flex; flex-direction:column">
          <h3 style="font-size:16px">Explanation + Debugging</h3>
          <div class="imgwrap" style="flex:1"><img src="__EXPLAIN__" alt="explain"></div>
          <p style="font-size:13px; margin-top:6px">Per-cluster likely cause + debug steps.</p>
        </div>
        <div class="card" style="padding:12px; display:flex; flex-direction:column">
          <h3 style="font-size:16px">Packaging / Benchmark</h3>
          <div class="imgwrap" style="flex:1"><img src="__PACK__" alt="pack"></div>
          <p style="font-size:13px; margin-top:6px">Stage timing + headline metrics.</p>
        </div>
      </div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Visuals</span></div>
  </section>

  <!-- 7a OUTPUTS: fault dataset -->
  <section class="slide" id="s7">
    <div class="kicker">7 · Outputs — Fault Dataset</div>
    <h1 class="title">13 fault variants mapped to 8 ground-truth root-cause categories</h1>
    <div class="rule"></div>
    <div class="body" style="top:206px">
      <table>
        <tr><th>Variant</th><th>Injected bug</th><th>Ground-truth label</th></tr>
        <tr><td class="mono">fault_acc_overflow</td><td>Accumulator 32&rarr;16 bit; sums overflow silently</td><td><span class="pill w">accumulator_overflow</span></td></tr>
        <tr><td class="mono">fault_acc_w24 / w20</td><td>Accumulator narrowed to 24 / 20 bit</td><td><span class="pill w">accumulator_overflow</span></td></tr>
        <tr><td class="mono">fault_wrong_sign</td><td>Weight cast signed&rarr;unsigned; no sign-extend</td><td><span class="pill w">sign_extension_error</span></td></tr>
        <tr><td class="mono">fault_b_unsigned</td><td>B_reg loses signed qualifier</td><td><span class="pill w">sign_extension_error</span></td></tr>
        <tr><td class="mono">fault_off_by_one</td><td>Outer loop ends at N-2; last column dropped</td><td><span class="pill w">loop_boundary_error</span></td></tr>
        <tr><td class="mono">fault_loop_over</td><td>Spatial loop runs N+1×; OOB extra product</td><td><span class="pill w">loop_boundary_error</span></td></tr>
        <tr><td class="mono">fault_subtract</td><td>Accumulator subtracts instead of adds</td><td><span class="pill w">arithmetic_error</span></td></tr>
        <tr><td class="mono">fault_reset / quant_reset</td><td>Reset polarity inverted; stale outputs</td><td><span class="pill w">reset_polarity_error</span></td></tr>
        <tr><td class="mono">fault_quant_shift_fixed</td><td>Per-channel shift replaced by fixed &gt;&gt;1</td><td><span class="pill w">shift_error</span></td></tr>
        <tr><td class="mono">fault_quant_no_clamp</td><td>INT8 saturation clamp removed; wraps</td><td><span class="pill w">saturation_error</span></td></tr>
        <tr><td class="mono">fault_quant_wrong_sign_zp</td><td>zero_pt added unsigned instead of signed</td><td><span class="pill w">zero_point_error</span></td></tr>
      </table>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Outputs · Fault Dataset</span></div>
  </section>

  <!-- 7b OUTPUTS: eval metrics -->
  <section class="slide" id="s8">
    <div class="kicker">7 · Outputs — Evaluation Metrics</div>
    <h1 class="title">Per-label triage evaluation vs ground truth (27-record benchmark)</h1>
    <div class="rule"></div>
    <div class="body" style="top:206px">
      <div class="grid2" style="grid-template-columns:1.35fr 1fr; align-items:start">
        <table>
          <tr><th>Root-cause label</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr>
          <tr><td class="mono">no_fault</td><td>1.00</td><td>1.00</td><td>1.00</td><td>15</td></tr>
          <tr><td class="mono">accumulator_overflow</td><td>1.00</td><td>1.00</td><td>1.00</td><td>3</td></tr>
          <tr><td class="mono">loop_boundary_error</td><td>1.00</td><td>1.00</td><td>1.00</td><td>3</td></tr>
          <tr><td class="mono">reset_polarity_error</td><td>1.00</td><td>1.00</td><td>1.00</td><td>3</td></tr>
          <tr><td class="mono">sign_extension_error</td><td>1.00</td><td>1.00</td><td>1.00</td><td>3</td></tr>
        </table>
        <div>
          <div class="tiles" style="grid-template-columns:1fr 1fr">
            <div class="tile"><div class="v g">100%</div><div class="l">Overall accuracy</div></div>
            <div class="tile"><div class="v">1.000</div><div class="l">Mean confidence</div></div>
            <div class="tile"><div class="v k">27</div><div class="l">Records evaluated</div></div>
            <div class="tile"><div class="v k">1.00</div><div class="l">Macro-F1</div></div>
          </div>
          <p class="sub" style="margin-top:16px">Two accumulator-width faults (w24/w20) are <b>mathematically latent</b> for N=4 INT8 (max sum 64,516 &lt; 2²⁰) and correctly appear as passing.</p>
        </div>
      </div>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Outputs · Evaluation</span></div>
  </section>

  <!-- 8 RESULTS & CONCLUSION -->
  <section class="slide" id="s9">
    <div class="kicker">8 · Results &amp; Conclusion</div>
    <h1 class="title">Agentic triage: 100% accurate and 342× faster than manual</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="tiles">
        <div class="tile"><div class="v g">100%</div><div class="l">Triage accuracy (LLM)</div></div>
        <div class="tile"><div class="v">342.6×</div><div class="l">Speedup vs manual</div></div>
        <div class="tile"><div class="v k">31.5 s</div><div class="l">vs ~180 min manual</div></div>
        <div class="tile"><div class="v k">123</div><div class="l">Automated tests pass</div></div>
      </div>
      <table style="margin-top:20px">
        <tr><th>Method</th><th>Accuracy</th><th>Mean conf.</th><th>Triage time</th><th>Note</th></tr>
        <tr><td><b>Manual (human)</b></td><td>baseline</td><td>—</td><td>~180 min</td><td>Reference baseline</td></tr>
        <tr><td>Rule-based (no LLM)</td><td><span class="pill w">72.7%</span></td><td>0.000</td><td>~0.07 s</td><td>Ablation — clustering only</td></tr>
        <tr><td><b>LLM-augmented (ours)</b></td><td><span class="pill g">100%</span></td><td>1.000</td><td>31.5 s</td><td>Full agentic pipeline</td></tr>
      </table>
      <ul class="lead" style="margin-top:10px">
        <li><b>Conclusion:</b> the agentic component lifts accuracy 72.7%&rarr;100% and confidence 0&rarr;1.0 — while a fully reproducible Docker pipeline + released dataset let others re-run the benchmark.</li>
      </ul>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>Results &amp; Conclusion</span></div>
  </section>

  <!-- 9 REFERENCES -->
  <section class="slide" id="s10">
    <div class="kicker">9 · References</div>
    <h1 class="title">References</h1>
    <div class="rule"></div>
    <div class="body">
      <div class="grid2" style="align-items:start">
        <ol class="mono" style="list-style:decimal; padding-left:24px; font-size:14.5px; line-height:1.9; color:#33415c">
          <li>W. Snyder et al. <i>Verilator</i> — open-source SystemVerilog simulator. veripool.org.</li>
          <li><i>cocotb</i> — Coroutine-based Cosimulation Testbench. cocotb.org.</li>
          <li>M. Ester, H.-P. Kriegel, J. Sander, X. Xu. "A Density-Based Algorithm for Discovering Clusters (DBSCAN)." <i>KDD</i>, 1996.</li>
          <li>F. Pedregosa et al. "scikit-learn: Machine Learning in Python." <i>JMLR</i> 12, 2011.</li>
          <li>P. Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." <i>NeurIPS</i>, 2020.</li>
        </ol>
        <ol class="mono" start="6" style="list-style:decimal; padding-left:24px; font-size:14.5px; line-height:1.9; color:#33415c">
          <li>G. Salton, C. Buckley. "Term-Weighting Approaches in Automatic Text Retrieval (TF-IDF)." <i>Info. Proc. &amp; Mgmt.</i>, 1988.</li>
          <li>Anthropic. "Claude Models &amp; Messages API." Technical documentation, 2024–2026.</li>
          <li>N. Jouppi et al. "In-Datacenter Performance Analysis of a Tensor Processing Unit." <i>ISCA</i>, 2017.</li>
          <li>Accellera. <i>Universal Verification Methodology (UVM) 1.2</i> Standard, 2014.</li>
          <li>Jacob et al. "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic Inference." <i>CVPR</i>, 2018.</li>
        </ol>
      </div>
      <p class="sub" style="position:absolute; bottom:0; left:0">Related-work references compiled for context — verify/replace specifics before final submission.</p>
    </div>
    <div class="foot"><span>NN-Accel-Triage</span><span>References</span></div>
  </section>

</div>

<div id="dots"></div>
<div id="hint">← / → or Space · F fullscreen</div>

<script>
const slides=[...document.querySelectorAll('.slide')];
let cur=0;
const dots=document.getElementById('dots');
slides.forEach((_,i)=>{const b=document.createElement('i'); b.onclick=()=>go(i); dots.appendChild(b);});
function fit(){
  const s=Math.min(window.innerWidth/1280, window.innerHeight/720);
  document.documentElement.style.setProperty('--scale', s);
}
window.addEventListener('resize',fit); fit();
function go(i){
  cur=Math.max(0,Math.min(slides.length-1,i));
  slides.forEach((s,j)=>s.classList.toggle('active',j===cur));
  [...dots.children].forEach((d,j)=>d.classList.toggle('on',j===cur));
  if(cur===5) startAnim(); else stopAnim();
}
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' '){go(cur+1); e.preventDefault();}
  else if(e.key==='ArrowLeft'){go(cur-1);}
  else if(e.key==='f'||e.key==='F'){ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen();}
  else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(slides.length-1);}
});
/* ---- live pipeline animation ---- */
const CAP=[
 ['STEP 1/6','Injected RTL fault variant selected from the frozen fault library.'],
 ['STEP 2/6','Verilator simulates the tile; scoreboard checks DUT against the golden model.'],
 ['STEP 3/6','Output mismatch detected — one JSON record is appended to the regression DB.'],
 ['STEP 4/6','13-D feature vector is clustered by DBSCAN → symptom label <b>overflow_fault</b>.'],
 ['STEP 5/6','Claude retrieves similar past cases (RAG) and reasons over the cluster.'],
 ['STEP 6/6','Structured report: likely cause, confidence, and recommended debug steps.'],
];
const TOK=['BUG','SIM','{ }','vec','LLM','card'];
let ai=null, step=0;
function render(){
  const stg=[...document.querySelectorAll('#s5 .stg')];
  const N=stg.length;
  stg.forEach((s,i)=>{ s.classList.toggle('on',i===step); s.classList.toggle('done',i<step);
     s.querySelector('.sc').innerHTML = (i<=step)? s.dataset.sc : ''; });
  const pct=2 + (step/(N-1))*96;
  document.getElementById('token').style.left=pct+'%';
  document.getElementById('token').textContent=TOK[step];
  document.getElementById('tfill').style.width=(step/(N-1))*96+'%';
  const c=CAP[step]; document.getElementById('capband').innerHTML='<b>'+c[0]+'</b> &nbsp; '+c[1];
}
function tick(){ step=(step+1)%6; render(); }
function startAnim(){ step=0; render(); stopAnim(); ai=setInterval(tick,1500); }
function stopAnim(){ if(ai){clearInterval(ai); ai=null;} }

/* init last, so animation state is fully defined before any startAnim() */
go( location.hash ? (parseInt(location.hash.slice(1))||0) : 0 );
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__VERIFY__", IMG_VERIFY)
        .replace("__EXPLAIN__", IMG_EXPLAIN)
        .replace("__PACK__", IMG_PACK))

OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
