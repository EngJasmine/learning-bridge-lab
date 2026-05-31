import html
import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "activities.json"
DB_PATH = BASE_DIR / "learning_bridge_lab_progress_v3_clean.db"
APP_VERSION = "Learning Bridge Lab - Grade-Band Redesign"

SUBJECTS = ["Math", "Reading", "Science Reading", "Writing", "Social Studies", "Character"]
GRADE_BANDS = ["Kindergarten", "Grades 2-3", "Grades 4-5", "Grade 6"]
COLORS = {
    "Math": "#2563eb",
    "Reading": "#7c3aed",
    "Science Reading": "#0891b2",
    "Writing": "#f97316",
    "Social Studies": "#b45309",
    "Character": "#0d9488",
}
ICONS = {
    "Math": "🧮",
    "Reading": "📚",
    "Science Reading": "🔬",
    "Writing": "✍️",
    "Social Studies": "🌎",
    "Character": "💛",
}

st.set_page_config(page_title="Learning Bridge Lab", page_icon="🎒", layout="wide")

st.markdown(
    """
<style>
:root {
  --ink:#172033;
  --muted:#5b6475;
  --paper:#ffffff;
  --soft:#eef6ff;
  --sky:#dff4ff;
  --lav:#f0e9ff;
  --pink:#ffe8f1;
  --green:#e8fff4;
  --gold:#fff5d6;
}
html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp {
  background:
    radial-gradient(circle at 12% 16%, rgba(255,255,255,.95) 0 0.9rem, transparent 1rem),
    radial-gradient(circle at 20% 20%, rgba(255,255,255,.75) 0 1.1rem, transparent 1.2rem),
    radial-gradient(circle at 84% 12%, rgba(255,255,255,.88) 0 1.2rem, transparent 1.3rem),
    linear-gradient(135deg,#dff4ff 0%, #eef1ff 44%, #f7ecff 100%);
  background-attachment: fixed;
}
.block-container { padding-top: .9rem; max-width: 1280px; }
[data-testid="stHeader"] { background: rgba(255,255,255,0); }

.hero {
  position:relative;
  overflow:hidden;
  background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(244,249,255,.96));
  border-radius:34px;
  padding:1.45rem 1.65rem;
  box-shadow:0 22px 55px rgba(50,70,120,.13);
  border:1px solid rgba(191,219,254,.9);
  margin-bottom:1rem;
}
.hero::before {
  content:"";
  position:absolute;
  right:-80px; top:-80px;
  width:260px; height:260px;
  border-radius:50%;
  background:radial-gradient(circle,#fde68a 0 34%,rgba(253,230,138,.25) 35% 55%,transparent 56%);
}
.hero-title { font-size:clamp(2rem,4.5vw,4.4rem); font-weight:950; letter-spacing:-.055em; color:var(--ink); margin:0; line-height:.95; }
.hero-sub { color:var(--muted); margin:.65rem 0 0 0; font-size:1.22rem; line-height:1.55; max-width:760px; }
.hero-kicker { display:inline-flex; gap:.45rem; align-items:center; background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; padding:.45rem .8rem; border-radius:999px; font-weight:900; margin-bottom:.75rem; }
.hero-art { font-size:4.8rem; text-align:center; line-height:1.18; filter: drop-shadow(0 12px 16px rgba(15,23,42,.12)); }

.home-card, .nav-card, .question-card, .work-card, .target-card {
  background:rgba(255,255,255,.96);
  border:1px solid rgba(219,234,254,.95);
  box-shadow:0 14px 34px rgba(15,23,42,.07);
}
.home-card {
  border-radius:28px;
  padding:1.2rem 1.25rem;
  min-height:170px;
}
.home-icon {
  width:62px; height:62px;
  display:flex; align-items:center; justify-content:center;
  border-radius:22px;
  font-size:2rem;
  margin-bottom:.7rem;
  background:linear-gradient(135deg,#dbeafe,#f5d0fe);
}
.home-card h3 { font-size:1.45rem; margin:.2rem 0 .45rem; color:var(--ink); letter-spacing:-.02em; }
.home-card p, .home-card li { font-size:1.08rem; line-height:1.55; color:#475569; }
.grade-strip { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:1rem 0; }
.grade-pill { border-radius:24px; padding:1rem; background:rgba(255,255,255,.92); border:2px solid #dbeafe; box-shadow:0 8px 22px rgba(15,23,42,.05); }
.grade-pill b { display:block; font-size:1.15rem; color:#172033; }
.grade-pill span { font-size:.98rem; color:#64748b; }
.showcase { background:linear-gradient(135deg,#ffffff,#f8fbff); border-radius:30px; padding:1.25rem; border:1px solid #dbeafe; box-shadow:0 16px 42px rgba(15,23,42,.08); margin:1rem 0; }
.showcase-title { font-size:1.7rem; font-weight:950; color:#172033; margin:0 0 .6rem; }
.teacher-note { font-size:1.12rem; line-height:1.65; color:#334155; }

.nav-card { border-radius:26px; padding:1rem 1.1rem; margin-bottom:1rem; }
.question-card { border-radius:28px; padding:1.12rem 1.35rem; margin-bottom:1rem; }
.question-grid { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(260px,.82fr); gap:1rem; align-items:center; }
.question-title { font-size:clamp(1.35rem,1.75vw,1.9rem); font-weight:850; color:var(--ink); margin:0 0 .55rem 0; letter-spacing:-.025em; line-height:1.12; }
.question-text { font-size:clamp(1.03rem,1.18vw,1.18rem); line-height:1.42; color:#111827; margin-top:.72rem; font-weight:520; }
.question-text.k { font-size:clamp(1.22rem,1.55vw,1.55rem); line-height:1.32; font-weight:650; }
.meta-line { color:#64748b; font-size:.94rem; margin-bottom:.48rem; font-weight:650; }
.badge { display:inline-flex; align-items:center; gap:.34rem; padding:.32rem .66rem; border-radius:999px; border:1px solid #bfdbfe; background:#eff6ff; color:#1e3a8a; font-size:.84rem; font-weight:850; margin:.14rem .2rem .14rem 0; }
.badge.subject { color:white; border-color:transparent; }
.target-card { border-radius:22px; padding:1rem 1.15rem; margin:.85rem 0; color:#334155; font-size:1.13rem; line-height:1.6; }
.work-card { border-radius:28px; padding:1.15rem 1.25rem; margin:.9rem 0; }
.teacher-suggestion { background:linear-gradient(135deg,#fff,#eef6ff); border:1px solid #bfdbfe; border-radius:24px; padding:1rem 1.15rem; margin:1rem 0; color:#334155; font-size:1.1rem; line-height:1.55; box-shadow:0 10px 26px rgba(15,23,42,.06); }
.passage { background:#fff; border-left:9px solid #93c5fd; border-radius:24px; padding:1.15rem 1.25rem; line-height:1.8; font-size:1.28rem; color:#1f2937; box-shadow:0 10px 28px rgba(15,23,42,.05); }
.passage p { margin:.45rem 0 .9rem 0; }
.mini-title { font-size:1.55rem; font-weight:950; color:#172033; margin:.25rem 0 .65rem 0; }
.diagram { background:#f8fafc; border:2px solid #dbeafe; border-radius:24px; padding:.75rem; min-height:155px; display:flex; align-items:center; justify-content:center; }
.diagram svg { max-width:100%; height:auto; }
.k-objects { font-size:3rem; letter-spacing:.35rem; line-height:1.8; text-align:center; }
.success { background:#dcfce7; border:1px solid #86efac; color:#166534; border-radius:20px; padding:.95rem 1.1rem; font-weight:900; font-size:1.1rem; }
.try { background:#fff7ed; border:1px solid #fdba74; color:#9a3412; border-radius:20px; padding:.95rem 1.1rem; font-weight:900; font-size:1.1rem; }
.footer-note { font-size:.95rem; color:#64748b; }

.stButton>button {
  border-radius:18px;
  font-weight:900;
  border:0;
  padding:.65rem 1.1rem;
  font-size:1.05rem;
  box-shadow:0 8px 18px rgba(37,99,235,.16);
}
button[kind="primary"] { background:#2563eb !important; }
div[data-testid="stSelectbox"] label, div[data-testid="stRadio"] label, div[data-testid="stTextArea"] label, div[data-testid="stTextInput"] label { font-weight:900; color:#334155; font-size:1.22rem; }
div[data-testid="stRadio"] p, div[data-testid="stRadio"] label, .stRadio label { font-size:1.26rem !important; }
div[data-testid="stSelectbox"] div, div[data-baseweb="select"] span { font-size:1.16rem; }
div[data-testid="stTextArea"] label,
div[data-testid="stTextInput"] label {
  font-size: 1.55rem !important;
  font-weight: 900 !important;
  color: #172033 !important;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
  border-radius: 20px !important;
  font-size: 1.45rem !important;
  line-height: 1.55 !important;
  min-height: 5.5rem !important;
  padding: 1rem 1.1rem !important;
  color: #111827 !important;
  background: #ffffff !important;
  border: 2px solid #c7d2fe !important;
}
.stTabs [data-baseweb="tab"] { font-size:1.05rem; font-weight:900; }

@media (max-width: 900px) {
  .question-grid, .grade-strip { grid-template-columns:1fr; }
  .hero-title { font-size:2.2rem; }
  .hero-sub { font-size:1.05rem; }
  .question-text { font-size:1.08rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


def load_activities():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            student TEXT,
            activity_id TEXT,
            grade_band TEXT,
            subject TEXT,
            skill TEXT,
            title TEXT,
            result TEXT,
            response TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_attempt(activity, result, response, student="Student"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO attempts (ts,student,activity_id,grade_band,subject,skill,title,result,response) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            datetime.now().isoformat(timespec="seconds"),
            student,
            activity["id"],
            activity["grade_band"],
            activity["subject"],
            activity["skill"],
            activity["title"],
            result,
            response,
        ),
    )
    conn.commit()
    conn.close()


def attempts_df():
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM attempts ORDER BY ts DESC", conn)
    conn.close()
    return df


def esc(x):
    return html.escape(str(x))


def badges(activity):
    color = COLORS.get(activity["subject"], "#2563eb")
    return (
        f"<span class='badge'>{esc(activity['grade_band'])}</span>"
        f"<span class='badge subject' style='background:{color}'>{ICONS.get(activity['subject'],'•')} {esc(activity['subject'])}</span>"
        f"<span class='badge'>Skill: {esc(activity['skill'])}</span>"
    )


def svg_objects(v):
    emoji = esc(v.get("emoji", "●"))
    count = int(v.get("count", 5))
    return f"<div class='k-objects'>{' '.join([emoji]*count)}</div>"


def svg_compare(v):
    emoji = esc(v.get("emoji", "●"))
    left = int(v.get("left", 3)); right = int(v.get("right", 5))
    return f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;text-align:center;font-size:2rem'><div><b>Jar A</b><br>{' '.join([emoji]*left)}</div><div><b>Jar B</b><br>{' '.join([emoji]*right)}</div></div>"


def svg_add(v):
    emoji = esc(v.get("emoji", "●"))
    a = int(v.get("a", 2)); b = int(v.get("b", 3))
    return f"<div class='k-objects'>{' '.join([emoji]*a)} <span style='font-size:1.5rem'>+</span> {' '.join([emoji]*b)}</div>"


def svg_shapes():
    return """
<svg width='310' height='150' viewBox='0 0 310 150' aria-label='shape choices'>
<circle cx='55' cy='75' r='38' fill='#dbeafe' stroke='#2563eb' stroke-width='4'/>
<polygon points='155,35 110,115 200,115' fill='#fde68a' stroke='#f59e0b' stroke-width='4'/>
<rect x='230' y='38' width='76' height='76' rx='10' fill='#dcfce7' stroke='#16a34a' stroke-width='4'/>
</svg>"""


def svg_fraction_bar(v):
    num, den = int(v.get("num", 3)), int(v.get("den", 8))
    w = 360; h = 58; x = 20; y = 50
    parts = []
    for i in range(den):
        fill = '#60a5fa' if i < num else '#ffffff'
        parts.append(f"<rect x='{x+i*w/den}' y='{y}' width='{w/den}' height='{h}' fill='{fill}' stroke='#334155' stroke-width='2'/>")
    return f"<svg width='420' height='160' viewBox='0 0 420 160'><text x='20' y='30' font-size='20' font-weight='700' fill='#334155'>Fraction model</text>{''.join(parts)}<text x='160' y='135' font-size='28' font-weight='800' fill='#1e3a8a'>{num}/{den}</text></svg>"


def svg_array(v):
    rows, cols = int(v.get('rows', 4)), int(v.get('cols', 5))
    cell = 26; x0=40; y0=28
    rects=[]
    for r in range(rows):
        for c in range(cols):
            rects.append(f"<rect x='{x0+c*cell}' y='{y0+r*cell}' width='22' height='22' rx='5' fill='#bfdbfe' stroke='#2563eb'/>")
    return f"<svg width='320' height='230' viewBox='0 0 320 230'>{''.join(rects)}<text x='40' y='{y0+rows*cell+35}' font-size='22' font-weight='800' fill='#334155'>{rows} rows × {cols} columns</text></svg>"


def svg_bar_chart(v):
    labels = v.get('labels', []); vals = v.get('values', [])
    maxv=max(vals) if vals else 1
    bars=[]
    for i,(lab,val) in enumerate(zip(labels, vals)):
        x=50+i*85; h=val/maxv*120; y=160-h
        bars.append(f"<rect x='{x}' y='{y}' width='45' height='{h}' rx='7' fill='#60a5fa'/><text x='{x+8}' y='188' font-size='16'>{esc(lab)}</text><text x='{x+15}' y='{y-8}' font-size='16' font-weight='800'>{val}</text>")
    return f"<svg width='330' height='210' viewBox='0 0 330 210'><line x1='35' y1='160' x2='295' y2='160' stroke='#334155'/>{''.join(bars)}</svg>"


def svg_bar_model(v):
    vals=v.get('values',[1,2,3]); colors=['#93c5fd','#86efac','#fde68a']; x=30; parts=[]
    total=sum(vals)
    for i,val in enumerate(vals):
        width=max(50, val/total*300)
        parts.append(f"<rect x='{x}' y='70' width='{width}' height='55' rx='8' fill='{colors[i%3]}' stroke='#334155'/><text x='{x+10}' y='104' font-size='18' font-weight='800'>{val}</text>")
        x += width
    return f"<svg width='430' height='180' viewBox='0 0 430 180'><text x='30' y='35' font-size='20' font-weight='800' fill='#334155'>Part + part + part</text>{''.join(parts)}</svg>"


def svg_equation(v):
    text=esc(v.get('text','x + 1 = 5'))
    return f"<svg width='420' height='150' viewBox='0 0 420 150'><rect x='30' y='35' width='360' height='80' rx='20' fill='#eff6ff' stroke='#2563eb' stroke-width='3'/><text x='60' y='88' font-size='32' font-weight='900' fill='#1e3a8a'>{text}</text></svg>"


def svg_prism(v):
    length = esc(v.get("length", "length"))
    width = esc(v.get("width", "width"))
    height = esc(v.get("height", "height"))
    return f"""
<svg width='420' height='270' viewBox='0 0 420 270'>
  <polygon points='110,55 270,55 330,105 170,105'
           fill='#dbeafe' stroke='#2563eb' stroke-width='4'/>
  <polygon points='170,105 330,105 330,190 170,190'
           fill='#93c5fd' stroke='#2563eb' stroke-width='4'/>
  <polygon points='110,55 170,105 170,190 110,140'
           fill='#bfdbfe' stroke='#2563eb' stroke-width='4'/>

  <line x1='170' y1='210' x2='330' y2='210' stroke='#334155' stroke-width='3'/>
  <text x='220' y='242' font-size='20' font-weight='800' fill='#334155'>{length}</text>

  <line x1='345' y1='105' x2='345' y2='190' stroke='#334155' stroke-width='3'/>
  <text x='356' y='153' font-size='20' font-weight='800' fill='#334155'>{height}</text>

  <line x1='105' y1='150' x2='165' y2='202' stroke='#334155' stroke-width='3'/>
  <text x='55' y='205' font-size='20' font-weight='800' fill='#334155'>{width}</text>
</svg>"""


def svg_line_plot(v):
    labels=v.get('labels',[]); counts=v.get('counts',[]); x0=45; step=70; y=150
    chunks=[f"<line x1='{x0-15}' y1='{y}' x2='{x0+step*(len(labels)-1)+25}' y2='{y}' stroke='#334155' stroke-width='3'/> "]
    for i,(lab,cnt) in enumerate(zip(labels,counts)):
        x=x0+i*step
        chunks.append(f"<line x1='{x}' y1='{y-8}' x2='{x}' y2='{y+8}' stroke='#334155' stroke-width='2'/><text x='{x-22}' y='{y+32}' font-size='14'>{esc(lab)}</text>")
        for k in range(cnt):
            chunks.append(f"<text x='{x-8}' y='{y-18-k*24}' font-size='24' font-weight='800' fill='#16a34a'>x</text>")
    return f"<svg width='440' height='220' viewBox='0 0 440 220'>{''.join(chunks)}</svg>"


def svg_coordinate_rect(v):
    pts=v.get('points',[(2,1),(9,1),(9,5),(2,5)]); scale=25; ox=55; oy=175
    def xy(p): return ox+p[0]*scale, oy-p[1]*scale
    pointstr=' '.join(f"{xy(p)[0]},{xy(p)[1]}" for p in pts)
    grid=[]
    for i in range(0,11):
        grid.append(f"<line x1='{ox+i*scale}' y1='{oy}' x2='{ox+i*scale}' y2='{oy-7*scale}' stroke='#e2e8f0'/><line x1='{ox}' y1='{oy-i*scale}' x2='{ox+10*scale}' y2='{oy-i*scale}' stroke='#e2e8f0'/>")
    dots=''.join(f"<circle cx='{xy(p)[0]}' cy='{xy(p)[1]}' r='5' fill='#ef4444'/><text x='{xy(p)[0]+6}' y='{xy(p)[1]-6}' font-size='12'>({p[0]},{p[1]})</text>" for p in pts)
    return f"<svg width='390' height='230' viewBox='0 0 390 230'>{''.join(grid)}<line x1='{ox}' y1='{oy}' x2='{ox+280}' y2='{oy}' stroke='#334155' stroke-width='3'/><line x1='{ox}' y1='{oy}' x2='{ox}' y2='15' stroke='#334155' stroke-width='3'/><polygon points='{pointstr}' fill='#bfdbfe99' stroke='#2563eb' stroke-width='4'/>{dots}</svg>"


def svg_rate_table(v):
    rows=v.get('rows',[])
    trs=''.join(f"<tr><td>{esc(r[0])}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td><td><b>{esc(r[3])}</b></td></tr>" for r in rows)
    return f"<table style='border-collapse:collapse;font-size:1rem;background:white'><tr><th>Trial</th><th>Distance</th><th>Time</th><th>Rate</th></tr>{trs}</table><style>td,th{{border:1px solid #cbd5e1;padding:.45rem .7rem;text-align:center}}</style>"


def svg_dot_plot(v):
    vals=v.get('values',[]); minv=min(vals); maxv=max(vals); x0=40; y=130; w=300
    chunks=[f"<line x1='{x0}' y1='{y}' x2='{x0+w}' y2='{y}' stroke='#334155' stroke-width='3'/>"]
    for val in vals:
        x=x0+(val-minv)/(maxv-minv)*w if maxv>minv else x0+w/2
        chunks.append(f"<circle cx='{x}' cy='{y-35}' r='7' fill='#7c3aed'/>")
    chunks.append(f"<text x='{x0-5}' y='{y+28}' font-size='14'>{minv}</text><text x='{x0+w-15}' y='{y+28}' font-size='14'>{maxv}</text>")
    return f"<svg width='390' height='190' viewBox='0 0 390 190'>{''.join(chunks)}<text x='95' y='40' font-size='18' font-weight='800'>Dot plot of quiz scores</text></svg>"


def svg_number_line(v):
    pts=v.get('points',[-120,-75,-145]); minv=min(pts)-15; maxv=max(pts)+15; x0=45; y=115; w=300
    chunks=[f"<line x1='{x0}' y1='{y}' x2='{x0+w}' y2='{y}' stroke='#334155' stroke-width='3'/>"]
    for val in pts:
        x=x0+(val-minv)/(maxv-minv)*w
        chunks.append(f"<circle cx='{x}' cy='{y}' r='7' fill='#ef4444'/><text x='{x-22}' y='{y-16}' font-size='13'>{val}</text>")
    return f"<svg width='390' height='170' viewBox='0 0 390 170'>{''.join(chunks)}</svg>"


def render_visual(v):
    if not v:
        return ""
    t=v.get('type')
    if t=='objects': return svg_objects(v)
    if t=='compare_objects': return svg_compare(v)
    if t=='add_objects': return svg_add(v)
    if t=='shapes': return svg_shapes()
    if t=='fraction_bar': return svg_fraction_bar(v)
    if t=='array': return svg_array(v)
    if t=='bar_chart': return svg_bar_chart(v)
    if t=='bar_model': return svg_bar_model(v)
    if t in ['fraction_equation','equation']: return svg_equation(v)
    if t=='prism': return svg_prism(v)
    if t=='line_plot': return svg_line_plot(v)
    if t=='coordinate_rect': return svg_coordinate_rect(v)
    if t=='rate_table': return svg_rate_table(v)
    if t=='dot_plot': return svg_dot_plot(v)
    if t=='number_line': return svg_number_line(v)
    return ""


def safe_math_visual(activity):
    """Return only visuals that support thinking without displaying the answer setup."""
    visual = activity.get("visual") or {}
    visual_type = visual.get("type")
    # Equation cards can accidentally reveal the operation or answer path, so keep them out of the question header.
    blocked = {"equation", "fraction_equation", "bar_model"}
    if visual_type in blocked:
        return ""
    return render_visual(visual)


def show_activity_header(activity, include_visual=True):
    color = COLORS.get(activity["subject"], "#2563eb")
    visual_html = safe_math_visual(activity) if include_visual and activity.get("subject") in ["Math"] else ""
    visual_block = f"<div class='diagram'>{visual_html}</div>" if visual_html else ""
    grid_class = "question-grid" if visual_html else ""
    question_class = "question-text k" if activity["grade_band"] == "Kindergarten" else "question-text"
    content = f"""
    <div class='question-card' style='border-top:8px solid {color}'>
      <div class='{grid_class}'>
        <div>
          <div class='meta-line'>{esc(activity.get('learning_target','Practice thoughtfully and explain your thinking.'))}</div>
          <div>{badges(activity)}</div>
          <h2 class='question-title'>{esc(activity['title'])}</h2>
          <div class='{question_class}'>{esc(activity.get('prompt','Read the passage and answer the questions.'))}</div>
        </div>
        {visual_block}
      </div>
    </div>
    """
    st.markdown(content, unsafe_allow_html=True)


def show_target(activity):
    if activity.get('success') or activity.get('learning_target'):
        st.markdown(
            f"<div class='target-card'><b>Learning target:</b> {esc(activity.get('learning_target',''))}<br><b>Success move:</b> {esc(activity.get('success','Use evidence, a model, or a clear reason.'))}</div>",
            unsafe_allow_html=True,
        )


def render_choice(activity):
    show_activity_header(activity)
    show_target(activity)
    key = f"ans_{activity['id']}"
    answer = st.radio("Choose your answer", activity.get('choices', []), key=key, index=None)
    explain = st.text_area("Explain your strategy or reason. Younger students can say it aloud to an adult.", key=f"explain_{activity['id']}", height=90)
    c1,c2,c3 = st.columns([1,1,3])
    with c1:
        if st.button("Submit", type="primary", key=f"submit_{activity['id']}"):
            if answer == activity.get('answer'):
                st.markdown("<div class='success'>Correct — strong thinking!</div>", unsafe_allow_html=True)
                save_attempt(activity, 'correct', f"{answer} | {explain}")
            else:
                st.markdown(f"<div class='try'>Not yet. The answer is <b>{esc(activity.get('answer'))}</b>. Try to explain why.</div>", unsafe_allow_html=True)
                save_attempt(activity, 'try_again', f"{answer} | {explain}")
    with c2:
        if st.button("Show model", key=f"model_{activity['id']}"):
            st.info(activity.get('model_it') or activity.get('hint') or 'Use a model, reread the question, and eliminate choices that cannot work.')


def render_passage(activity):
    show_activity_header(activity, include_visual=False)
    show_target(activity)
    paragraphs = str(activity.get('passage','')).split('\n\n')
    st.markdown("<div class='passage'>" + ''.join(f"<p>{esc(p)}</p>" for p in paragraphs if p.strip()) + "</div>", unsafe_allow_html=True)
    correct=0; total=len(activity.get('questions', [])); responses=[]
    st.markdown("<div class='work-card'><div class='mini-title'>Questions</div>", unsafe_allow_html=True)
    for i,ques in enumerate(activity.get('questions', []), start=1):
        ans = st.radio(f"{i}. {ques['prompt']}", ques['choices'], key=f"q_{activity['id']}_{i}", index=None)
        responses.append(f"Q{i}:{ans}")
        if ans == ques['answer']:
            correct += 1
        if ques.get('evidence'):
            st.caption(f"Evidence hint: {ques['evidence']}")
    written = st.text_area("Written response: Use one detail from the text to explain your thinking.", key=f"wr_{activity['id']}", height=100)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Submit reading work", type="primary", key=f"submit_{activity['id']}"):
        if correct == total:
            st.markdown(f"<div class='success'>Excellent — {correct}/{total} correct. Your next goal is to make the written response specific.</div>", unsafe_allow_html=True)
            result='correct'
        else:
            st.markdown(f"<div class='try'>You got {correct}/{total}. Reread the evidence hints and revise.</div>", unsafe_allow_html=True)
            result='partial'
        save_attempt(activity, result, ' | '.join(responses) + ' | WR:' + written)


def render_writing(activity):
    show_activity_header(activity, include_visual=False)
    show_target(activity)
    st.markdown("<div class='teacher-suggestion'>✍️ <b>Writing mission:</b> Plan your ideas first, then write a clear draft. Good writing grows from strong thinking, details, and revision.</div>", unsafe_allow_html=True)
    st.markdown("<div class='work-card'><div class='mini-title'>Planning organizer</div>", unsafe_allow_html=True)
    answers=[]
    for field in activity.get('organizer', []):
        answers.append(
            f"{field}: " + st.text_area(
                field,
                key=f"{activity['id']}_{field}",
                height=90
            )
        )
    draft = st.text_area(
        "Draft your response",
        key=f"draft_{activity['id']}",
        height=240
    )
    st.markdown("<div class='mini-title'>Checklist</div>", unsafe_allow_html=True)
    checks=[]
    for item in activity.get('checklist', []):
        checks.append(st.checkbox(item, key=f"check_{activity['id']}_{item}"))
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Save writing", type="primary", key=f"save_{activity['id']}"):
        completeness = sum(1 for x in checks if x)
        st.markdown(f"<div class='success'>Saved. Checklist items marked: {completeness}/{len(checks)}. Revise once before calling it finished.</div>", unsafe_allow_html=True)
        save_attempt(activity, 'saved_writing', ' | '.join(answers) + ' | Draft:' + draft)


def render_activity(activity):
    if activity['activity_type'] == 'passage':
        render_passage(activity)
    elif activity['activity_type'] == 'writing':
        render_writing(activity)
    else:
        render_choice(activity)


def pick_random(filtered):
    if not filtered:
        return None
    return random.choice(filtered)


def home_page(activities):
    st.caption("Build version: shiny-ui-2026-05-31")
    total = len(activities)
    subjects = sorted(set(a["subject"] for a in activities), key=lambda s: SUBJECTS.index(s) if s in SUBJECTS else 99)
    grade_bands = [g for g in GRADE_BANDS if any(a["grade_band"] == g for a in activities)]
    st.markdown(
        """
        <div class='hero'>
          <div class='hero-kicker'>🚀 Prototype learning tool for school support</div>
          <div style='display:grid;grid-template-columns:minmax(0,1.55fr) minmax(240px,.75fr);gap:1rem;align-items:center'>
            <div>
              <h1 class='hero-title'>Learning Bridge Lab</h1>
              <p class='hero-sub'>A colorful grade-band practice app that helps students review core skills, think with evidence, explain their reasoning, and build confidence through short guided activities.</p>
            </div>
            <div class='hero-art'>☁️ 🎒<br>📚 ✨ 🧠</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='home-card'>
          <div class='home-icon'>🎯</div>
          <h3>Purpose</h3>
          <p>Give students a safe practice space for homework support, review, enrichment, and confidence-building across grade bands.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='home-card'>
          <div class='home-icon'>🧩</div>
          <h3>How it helps</h3>
          <p>Students answer, explain, reread, model, and revise. The app records local attempts so teachers can see practice patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='home-card'>
          <div class='home-icon'>🌱</div>
          <h3>Expandable</h3>
          <p>This is a prototype foundation. More content, standards, images, audio, and interactive tasks can be added over time.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='grade-strip'>", unsafe_allow_html=True)
    grade_notes = {
        "Kindergarten": "picture-first, no writing, simple choices",
        "Grades 2-3": "short texts, early explanations, skill fluency",
        "Grades 4-5": "multi-step reasoning, evidence, richer reading",
        "Grade 6": "deeper analysis, argument, data, and independence",
    }
    cols = st.columns(4)
    for i, grade in enumerate(grade_bands[:4]):
        with cols[i]:
            st.markdown(f"<div class='grade-pill'><b>{esc(grade)}</b><span>{esc(grade_notes.get(grade,''))}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='showcase'>
          <div class='showcase-title'>What a teacher or principal can see</div>
          <div class='teacher-note'>
            This small prototype demonstrates a practical learning workflow: choose a grade band, choose a subject, practice a task, explain thinking, save progress, and review attempts in a teacher dashboard. It currently includes <b>{total}</b> activities across <b>{len(subjects)}</b> subjects, with different expectations for early learners and older students.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class='showcase'>
      <div class='showcase-title'>Technology used in a practical way</div>
      <div class='teacher-note'>
        The app is intentionally simple to run locally: Streamlit for the interface, JSON for editable learning content, and SQLite for local progress. This makes it easy for a teacher, parent, or developer to improve content gradually without rebuilding the whole system.
      </div>
    </div>
    <div class='showcase'>
      <div class='showcase-title'>Suggested next improvements</div>
      <div class='teacher-note'>
        The strongest next step is to add a <b>student journey map</b>: placement check → recommended skill path → practice set → review mistake → teacher note. After that, the prototype can grow with audio support for early grades, drag-and-drop models, standards tags, and richer reports by skill.
      </div>
    </div>
    """, unsafe_allow_html=True)

def dashboard():
    st.markdown("<div class='hero'><h1 class='hero-title'>Teacher Dashboard</h1><p class='hero-sub'>Local progress only. This package ships with no database file, so you start clean.</p></div>", unsafe_allow_html=True)
    df=attempts_df()
    c1,c2,c3=st.columns(3)
    with c1: st.metric('Attempts', 0 if df.empty else len(df))
    with c2: st.metric('Correct', 0 if df.empty else int((df['result']=='correct').sum()))
    with c3: st.metric('Saved writing', 0 if df.empty else int((df['result']=='saved_writing').sum()))
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button('Download attempts CSV', df.to_csv(index=False).encode('utf-8'), file_name='learning_bridge_attempts.csv')
    if st.button('Reset all local progress data'):
        if DB_PATH.exists():
            DB_PATH.unlink()
        init_db()
        st.success('Progress database reset.')
        st.rerun()


def main():
    init_db()
    activities = load_activities()

    # st.segmented_control is not available in some Streamlit versions.
    # Use a horizontal radio menu so the app runs on older installs too.
    mode = st.radio(
        "Navigation",
        ["Home", "Student Practice", "Teacher Dashboard"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "Home":
        home_page(activities)
        return

    if mode == "Teacher Dashboard":
        dashboard()
        return

    st.markdown(
        """
        <div class='hero'>
          <div class='hero-kicker'>🧠 Student Practice</div>
          <h1 class='hero-title'>Choose a learning mission</h1>
          <p class='hero-sub'>Pick a grade band and subject, then solve one focused activity. Use a model, evidence, or a clear explanation to show your thinking.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1.05, 1.05, 1.75, .9])
    with col1:
        grade = st.selectbox("Grade band", GRADE_BANDS, index=0)
    possible_subjects = sorted(
        set(a["subject"] for a in activities if a["grade_band"] == grade),
        key=lambda s: SUBJECTS.index(s) if s in SUBJECTS else 99,
    )
    with col2:
        subject = st.selectbox("Subject", possible_subjects, index=0)
    filtered = [a for a in activities if a["grade_band"] == grade and a["subject"] == subject]
    missions = [f"{a['title']} — {a['skill']}" for a in filtered]
    if "mission_index" not in st.session_state:
        st.session_state.mission_index = 0
    if missions and st.session_state.mission_index >= len(missions):
        st.session_state.mission_index = 0
    with col3:
        mission = st.selectbox("Activity", missions, index=st.session_state.mission_index if missions else 0)
    with col4:
        st.write("")
        if st.button("Another activity", type="primary") and missions:
            st.session_state.mission_index = random.randrange(len(missions))
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if not filtered:
        st.warning("No activities for this grade and subject yet.")
        return

    selected_title = mission.split(" — ")[0]
    activity = next(a for a in filtered if a["title"] == selected_title)
    render_activity(activity)
    st.markdown(
        f"<p class='footer-note'>{APP_VERSION} • Clean database name: {DB_PATH.name} • Arabic removed for this version.</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
