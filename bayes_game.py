# lost_painting_heist_adaptive.py
# Deluxe + Adaptive Tutoring version of: The Lost Painting Heist
# Streamlit game that teaches Bayesian inference + ethics with dynamic, context-aware coaching.

import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# --------------------------------------------------------------------------------------
# ------------------------------- PAGE CONFIG & THEME ----------------------------------
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="🖼️ The Lost Painting Heist — Adaptive",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# A little CSS polish
st.markdown(
    """
    <style>
    .big-title {font-size: 2.2rem; font-weight: 800; margin-top: .5rem;}
    .subtitle {font-size: 1.05rem; opacity: .8; margin-bottom: 1rem;}
    .tag {
        display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem;
        margin-right: 6px; margin-top: 4px; color: white;
    }
    .tag-neutral { background: #6366F1; }
    .tag-biased { background: #F97316; }
    .tag-unethical { background: #EF4444; }
    .tag-rare { background: #9333EA; }
    .glass {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    .soft {
        background: rgba(255,255,255,0.06);
        border-radius: 8px; padding: 0.75rem 1rem; margin: .2rem 0;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .dim {opacity: .7;}
    .scorebox {
        background: #0F172A; border-radius: 12px; padding: 1rem; color: #E2E8F0; text-align:center;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .scorebox h2 { margin: 0; font-size: 2rem; }
    .scorebox span { font-size: .8rem; opacity: .8; display:block; margin-top: .25rem; }
    .modal {
        position: fixed; left:0; top:0; width:100%; height:100%;
        background: rgba(0,0,0,.75); display: flex; justify-content: center; align-items: center;
        z-index: 9999;
        backdrop-filter: blur(3px);
    }
    .modal-inner {
        background: #1E293B; padding: 2.5rem; border-radius: 16px; max-width: 720px; color: #E2E8F0;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    .step-dot { width: 10px; height: 10px; border-radius: 50%; background: #334155; display: inline-block; margin-right: 4px; }
    .step-dot.active { background: #6366F1; }
    .step-dot.done { background: #22C55E; }
    .footer-tip { font-size: .8rem; opacity: .6; text-align: center; margin-top: 2rem;}
    .tutor {
        background: #1E293B; border: 1px solid rgba(255,255,255,.05); border-radius: 10px; padding: .9rem 1rem; margin-bottom: .75rem;
    }
    .tutor h4 { margin: .1rem 0 .5rem 0; font-size: 1rem;}
    .tutor small { opacity:.6; }
    </style>
    """,
    unsafe_allow_html=True
)

GuardID = Literal["A", "B", "C"]

# --------------------------------------------------------------------------------------
# ----------------------------- GAME CONSTANTS / CONFIG --------------------------------
# --------------------------------------------------------------------------------------
RNG = random.Random()
START_INTEGRITY = 100
INTEGRITY_COST = {"CCTV": 0, "RUMOR": 5, "INTERROGATION": 15}
ACCURACY_WEIGHT = 0.50
INTEGRITY_WEIGHT = 0.25
EFFICIENCY_WEIGHT = 0.15
CAUTION_WEIGHT = 0.10
ESCAPE_RISK_INCREASE_PER_ROUND = 9
MAX_ESCAPE_RISK = 100
EPS = 1e-6

# Adaptive tutoring thresholds
LOW_CONFIDENCE_THRESHOLD = 0.6
LOW_INTEGRITY_THRESHOLD = 70
TOO_MANY_INVASIVE_IN_ROW = 2

@dataclass
class EvidenceCard:
    id: str
    source: Literal["CCTV", "RUMOR", "INTERROGATION"]
    text: str
    likelihood: Dict[GuardID, float]  # P(evidence | guard i)
    unethical: bool = False
    biased_against: Optional[GuardID] = None
    rarity: Literal["common", "rare"] = "common"

# Evidence pools
CCTV_POOL: List[EvidenceCard] = [
    EvidenceCard("cctv_keycard_a_905","CCTV","Keycard swipe recorded at 9:05 PM by Guard A.",
                 {"A":0.75,"B":0.15,"C":0.10}),
    EvidenceCard("cctv_b_missing_5mins","CCTV","Guard B is missing from the corridor for 5 minutes on CCTV.",
                 {"A":0.20,"B":0.70,"C":0.10}),
    EvidenceCard("cctv_c_wrong_wing","CCTV","Guard C seen walking towards the wrong wing right before the alarm.",
                 {"A":0.10,"B":0.20,"C":0.70}),
    EvidenceCard("cctv_glove_b","CCTV","A missing glove found near the vault resembles Guard B’s uniform.",
                 {"A":0.10,"B":0.80,"C":0.10}),
    EvidenceCard("cctv_motion_off_a","CCTV","Motion sensor logs show the detector in Guard A’s zone was manually disabled.",
                 {"A":0.80,"B":0.10,"C":0.10}, rarity="rare"),
]

RUMOR_POOL: List[EvidenceCard] = [
    EvidenceCard("rumor_a_debt","RUMOR","Staff say Guard A has gambling debts and needed money.",
                 {"A":0.65,"B":0.25,"C":0.10}, biased_against="A"),
    EvidenceCard("rumor_b_attitude","RUMOR","People say Guard B’s been acting cocky about 'big changes' coming.",
                 {"A":0.20,"B":0.65,"C":0.15}, biased_against="B"),
    EvidenceCard("rumor_c_new_car","RUMOR","Rumor says Guard C just bought a new car in cash.",
                 {"A":0.15,"B":0.20,"C":0.65}, biased_against="C"),
]

INTERROGATION_POOL: List[EvidenceCard] = [
    EvidenceCard("int_a_slip","INTERROGATION","Under aggressive questioning, Guard A slips up on the timeline.",
                 {"A":0.85,"B":0.10,"C":0.05}, unethical=True),
    EvidenceCard("int_b_sweat","INTERROGATION","Guard B starts sweating when asked about keycards.",
                 {"A":0.10,"B":0.80,"C":0.10}, unethical=True),
    EvidenceCard("int_c_alibi","INTERROGATION","Guard C’s alibi breaks under repeated questioning.",
                 {"A":0.05,"B":0.15,"C":0.80}, unethical=True),
]

POOL_BY_SOURCE = {"CCTV": CCTV_POOL, "RUMOR": RUMOR_POOL, "INTERROGATION": INTERROGATION_POOL}

# --------------------------------------------------------------------------------------
# --------------------------------- STATE HELPERS --------------------------------------
# --------------------------------------------------------------------------------------
def init_state():
    if "g" not in st.session_state:
        st.session_state.g = {
            "guilty": RNG.choice(["A","B","C"]),
            "priors": {"A":1/3,"B":1/3,"C":1/3},
            "posteriors": {"A":1/3,"B":1/3,"C":1/3},
            "integrity": START_INTEGRITY,
            "round": 0,
            "escape_risk": 0,
            "evidence_log": [],
            "used_ids": set(),
            "done": False,
            "accused": None,
            "scores": dict(),
            "show_math": False,
            "step": 0,  # 0-intro, 1-evidence, 2-accuse (modal), 3-debrief
            "show_tutorial": True,
            "show_ethics_modal": False,
            "last_card": None,
            "caution_points": 0,
            "achievement_flags": set(),
            # Adaptive tutoring
            "tutor_messages": [],
            "tutor_seen": set(),
            "pending_accuse": None,
            "show_accuse_modal": False,
        }

def reset_game():
    st.session_state.pop("g", None)
    init_state()

def normalize(d):
    s = sum(d.values())
    if s == 0:
        return {"A":1/3,"B":1/3,"C":1/3}
    return {k:v/s for k,v in d.items()}

def bayesian_update(posterior, card: EvidenceCard):
    updated = {g: max(posterior[g]*card.likelihood[g], EPS) for g in posterior}
    return normalize(updated)

def suspicion_df(posteriors):
    return pd.DataFrame([{"Guard":k, "Suspicion":100*v} for k,v in posteriors.items()]).sort_values("Guard")

def suspicion_chart(post):
    df = suspicion_df(post)
    ch = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Guard:N", sort=["A","B","C"]),
            y=alt.Y("Suspicion:Q", scale=alt.Scale(domain=[0,100])),
            color=alt.Color("Guard:N", legend=None),
            tooltip=["Guard", alt.Tooltip("Suspicion:Q", format=".1f")]
        )
        .properties(height=180)
    )
    st.altair_chart(ch, use_container_width=True)

def pick_evidence(source):
    g = st.session_state.g
    pool = [e for e in POOL_BY_SOURCE[source] if e.id not in g["used_ids"]]
    if not pool:
        pool = POOL_BY_SOURCE[source]
    return RNG.choice(pool)

def add_evidence(card: EvidenceCard):
    g = st.session_state.g
    g["round"] += 1
    g["escape_risk"] = min(MAX_ESCAPE_RISK, g["escape_risk"] + ESCAPE_RISK_INCREASE_PER_ROUND)
    new_post = bayesian_update(g["posteriors"], card)
    g["posteriors"] = new_post
    g["integrity"] = max(0, g["integrity"] - INTEGRITY_COST[card.source])
    g["caution_points"] += {"CCTV": 2, "RUMOR": 1, "INTERROGATION": 0}[card.source]

    g["evidence_log"].append({
        "round": g["round"],
        "card": card,
        "posteriors": new_post.copy(),
        "integrity": g["integrity"],
        "escape_risk": g["escape_risk"]
    })
    g["used_ids"].add(card.id)
    g["last_card"] = card

    # potentially open ethics modal
    if card.source in ("RUMOR","INTERROGATION") and RNG.random() < 0.35:
        g["show_ethics_modal"] = True

    # run adaptive tutoring triggers after each evidence
    run_tutoring_triggers(event="after_evidence")

def accuse(guard: GuardID):
    g = st.session_state.g
    if g["done"]:
        return
    g["accused"] = guard
    correct = (guard == g["guilty"])
    g["done"] = True
    g["step"] = 3
    g["scores"] = compute_final_scores(correct)

    if correct and g["integrity"] >= 90:
        g["achievement_flags"].add("High Integrity")
    if correct and len(g["evidence_log"]) <= 3:
        g["achievement_flags"].add("Sherlock")
    if correct and g["escape_risk"] >= 80:
        g["achievement_flags"].add("Clutch Call")
    if g["scores"]["final"] >= 90 and correct:
        st.balloons()

def compute_final_scores(correct: bool):
    g = st.session_state.g
    accuracy = 100.0 if correct else 0.0
    n = len(g["evidence_log"])
    efficiency = max(0.0, 100.0 - (n-1)*12.5)
    integrity = g["integrity"]
    max_possible = 2 * max(1, g["round"])
    caution_raw = g["caution_points"] / max_possible
    caution = int(100 * caution_raw)
    final = (
        ACCURACY_WEIGHT * accuracy +
        INTEGRITY_WEIGHT * integrity +
        EFFICIENCY_WEIGHT * efficiency +
        CAUTION_WEIGHT * caution
    )
    return dict(
        final=final,
        accuracy=accuracy,
        integrity=integrity,
        efficiency=efficiency,
        caution=caution
    )

def suspicion_history():
    g = st.session_state.g
    rows = []
    for log in g["evidence_log"]:
        r = log["round"]
        for guard, prob in log["posteriors"].items():
            rows.append({"Round": r, "Guard": guard, "Suspicion": prob * 100.0})
    return pd.DataFrame(rows)

def suspicion_history_chart():
    dfh = suspicion_history()
    if dfh.empty:
        st.info("No evidence yet → no history to plot.")
        return
    ch = (
        alt.Chart(dfh)
        .mark_line(point=True)
        .encode(
            x=alt.X("Round:Q"),
            y=alt.Y("Suspicion:Q", scale=alt.Scale(domain=[0,100])),
            color=alt.Color("Guard:N"),
            tooltip=["Round","Guard","Suspicion"]
        )
        .properties(height=250)
    )
    st.altair_chart(ch, use_container_width=True)

def radar_chart(scores: Dict[str, float]):
    cats = ["accuracy", "integrity", "efficiency", "caution"]
    data = pd.DataFrame({
        "category": cats,
        "score": [scores[c] for c in cats]
    })
    data_loop = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    angle = {"accuracy":0,"integrity":90,"efficiency":180,"caution":270}
    data_loop["angle"] = data_loop["category"].map(angle)
    data_loop["x"] = data_loop["score"] * np.cos(np.deg2rad(data_loop["angle"]))
    data_loop["y"] = data_loop["score"] * np.sin(np.deg2rad(data_loop["angle"]))

    base = alt.Chart(data_loop).encode(
        x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[-110,110])),
        y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[-110,110]))
    )
    polygon = base.mark_line(point=True, stroke="#6366F1", strokeWidth=3).encode(
        tooltip=["category:N","score:Q"]
    )
    zero_df = pd.DataFrame({
        "x":[0,0,0,0],
        "y":[0,0,0,0],
        "category":cats,
        "angle":[angle[c] for c in cats]
    })
    spokes = alt.Chart(zero_df).mark_rule(stroke="#334155", strokeWidth=1).encode(
        x="x:Q", y="y:Q", x2=alt.value(100*np.cos(np.deg2rad(zero_df["angle"]))),
        y2=alt.value(100*np.sin(np.deg2rad(zero_df["angle"])))
    )
    circle_df = pd.DataFrame({"r":[25,50,75,100]})
    circles = alt.Chart(circle_df).mark_circle(stroke="#475569", fillOpacity=0.0).encode(
        x=alt.value(0), y=alt.value(0), size="r:Q"
    ).transform_calculate(size="pow(datum.r,2)")
    return (circles + spokes + polygon).properties(height=350)

# ------------------------------ Adaptive Tutoring -------------------------------------

def push_tutor_message(key: str, title: str, body: str, show_math_button: bool = False):
    g = st.session_state.g
    if key in g["tutor_seen"]:
        return
    g["tutor_seen"].add(key)
    g["tutor_messages"].append({
        "key": key,
        "title": title,
        "body": body,
        "show_math_button": show_math_button
    })

def run_tutoring_triggers(event: str):
    """Call after certain events to push context-aware hints."""
    g = st.session_state.g
    post = g["posteriors"]
    max_post = max(post.values()) if post else 0.0

    # 1) Low confidence after 2+ rounds
    if g["round"] >= 2 and max_post < LOW_CONFIDENCE_THRESHOLD:
        push_tutor_message(
            "low_confidence_midgame",
            "Your suspicion is still low 🤔",
            "Your top suspicion is under 60%. Inference often needs more evidence. "
            "Try pulling a neutral CCTV clue instead of a biased source to raise confidence reliably.",
            show_math_button=True
        )

    # 2) Low integrity after 3+ rounds
    if g["round"] >= 3 and g["integrity"] < LOW_INTEGRITY_THRESHOLD:
        push_tutor_message(
            "integrity_warning",
            "Integrity is dropping fast ⚠️",
            "Biased or unethical methods can push your probabilities hard — but at the cost of integrity. "
            "Consider switching back to CCTV to balance ethics and accuracy.",
            show_math_button=False
        )

    # 3) Two invasive/biased in a row
    if len(g["evidence_log"]) >= TOO_MANY_INVASIVE_IN_ROW:
        last_two = g["evidence_log"][-TOO_MANY_INVASIVE_IN_ROW:]
        if all(ev["card"].source in ("RUMOR","INTERROGATION") for ev in last_two):
            push_tutor_message(
                "too_many_invasive",
                "You're leaning heavily on risky evidence 😬",
                "Two invasive/biased clues in a row. This can nuke your integrity and teach the wrong inference habit. "
                "Try balancing with some neutral CCTV instead.",
                show_math_button=False
            )

def accuse_guard_with_check(guard: GuardID):
    """Pre-accuse hook: show adaptive confirmation if confidence is low."""
    g = st.session_state.g
    max_post = max(g["posteriors"].values())
    # trigger a modal if low confidence or integrity is too low, to teach
    if (max_post < LOW_CONFIDENCE_THRESHOLD) or (g["integrity"] < LOW_INTEGRITY_THRESHOLD):
        g["pending_accuse"] = guard
        g["show_accuse_modal"] = True
    else:
        accuse(guard)

def tutor_panel():
    g = st.session_state.g
    if not g["tutor_messages"]:
        return
    for i, msg in enumerate(g["tutor_messages"]):
        with st.container():
            st.markdown(
                f"""
                <div class="tutor">
                    <h4>📚 {msg['title']}</h4>
                    <p>{msg['body']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            cols = st.columns([1,1,6])
            with cols[0]:
                if msg["show_math_button"]:
                    if st.button("Show math", key=f"math_{msg['key']}"):
                        g["show_math"] = True
                        st.experimental_rerun()
            with cols[1]:
                if st.button("Dismiss", key=f"dismiss_{msg['key']}"):
                    g["tutor_messages"].pop(i)
                    st.experimental_rerun()

def tutorial_modal():
    g = st.session_state.g
    if not g["show_tutorial"]:
        return
    
    # Use a simple centered container instead of a full-screen modal
    st.markdown(
        """
        <div style="
            background: #1E293B; 
            padding: 2.5rem; 
            border-radius: 16px; 
            max-width: 720px; 
            margin: 2rem auto;
            color: #E2E8F0;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        ">
            <h2>Welcome to <em>The Lost Painting Heist</em> 🖼️</h2>
            <p>You must infer which guard stole the painting, using noisy, biased, or unethical evidence sources.</p>
            <ul>
                <li><b>Inference</b>: Your suspicion meter updates as you collect evidence (Bayesian-style).</li>
                <li><b>Ethics</b>: Rumors & interrogations raise certainty quickly but harm integrity.</li>
                <li><b>Pressure</b>: Escape risk rises every round — wait too long and the painting's gone.</li>
                <li><b>Adaptive Tutor</b>: I'll jump in with tips if you're taking risky, low-confidence, or unethical paths.</li>
            </ul>
            <p>Balance accuracy, speed, and integrity. Good luck, detective.</p>
            <div style="text-align: center; margin-top: 2rem;">
                <p style="font-size: 1.1rem; font-weight: 600; color: #6366F1;">Click the button below to start!</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Make the button more prominent and centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Let's go!", key="start_game_button", use_container_width=True):
            g["show_tutorial"] = False
            g["step"] = 1
            st.experimental_rerun()
    
    # Add a close button as alternative
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ Close", key="close_tutorial_button", use_container_width=True):
            g["show_tutorial"] = False
            g["step"] = 1
            st.experimental_rerun()

def ethics_modal():
    g = st.session_state.g
    if not g["show_ethics_modal"]:
        return
    card = g["last_card"]
    if not card:
        g["show_ethics_modal"] = False
        return
    st.markdown(
        f"""
        <div class="modal">
          <div class="modal-inner">
            <h2>Ethical Dilemma ⚖️</h2>
            <p>You just used <b>{card.source}</b> evidence: <em>“{card.text}”</em></p>
            <p>Biased or invasive methods may push your posterior fast — but at a trust cost. Continue?</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("I stand by it"):
            g["show_ethics_modal"] = False
            st.experimental_rerun()
    with c2:
        if st.button("Undo last evidence"):
            if g["evidence_log"]:
                last = g["evidence_log"].pop()
                g["used_ids"].discard(last["card"].id)
                g["round"] -= 1
                g["escape_risk"] = max(0, g["escape_risk"] - ESCAPE_RISK_INCREASE_PER_ROUND)
                # recompute posteriors, integrity, caution from scratch:
                g["posteriors"] = g["priors"].copy()
                g["integrity"] = START_INTEGRITY
                g["caution_points"] = 0
                for ev in g["evidence_log"]:
                    g["posteriors"] = ev["posteriors"].copy()
                    g["integrity"] = ev["integrity"]
                    g["caution_points"] += {"CCTV":2,"RUMOR":1,"INTERROGATION":0}[ev["card"].source]
            g["show_ethics_modal"] = False
            st.experimental_rerun()

def accuse_modal():
    g = st.session_state.g
    if not g["show_accuse_modal"]:
        return
    max_post = max(g["posteriors"].values())
    st.markdown(
        f"""
        <div class="modal">
          <div class="modal-inner">
            <h2>Are you sure you want to accuse now?</h2>
            <p>Your current top suspicion is <b>{max_post*100:.1f}%</b>, and your integrity is <b>{g['integrity']}</b>.</p>
            <p>Inference means waiting until you have enough evidence to be confident. One more neutral clue (CCTV) might help clarify things without hurting your integrity.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Proceed anyway"):
            accuse(g["pending_accuse"])
            g["show_accuse_modal"] = False
            st.experimental_rerun()
    with c2:
        if st.button("Cancel & get more evidence"):
            g["pending_accuse"] = None
            g["show_accuse_modal"] = False
            st.experimental_rerun()

# --------------------------------------------------------------------------------------
# -------------------------------------- UI PARTS --------------------------------------
# --------------------------------------------------------------------------------------
def step_indicator(step:int):
    labels = ["Intro", "Evidence", "Accuse", "Debrief"]
    dots = []
    for i,_ in enumerate(labels):
        cls = "step-dot"
        if i == step:
            cls += " active"
        elif i < step:
            cls += " done"
        dots.append(f"<span class='{cls}'></span>")
    st.markdown(" ".join(dots) + f" <span class='dim'>({labels[step]})</span>", unsafe_allow_html=True)

def evidence_tags(card: EvidenceCard):
    tags = []
    if card.source == "CCTV":
        tags.append('<span class="tag tag-neutral">neutral</span>')
    elif card.source == "RUMOR":
        tags.append('<span class="tag tag-biased">biased</span>')
    elif card.source == "INTERROGATION":
        tags.append('<span class="tag tag-unethical">unethical</span>')
    if card.rarity == "rare":
        tags.append('<span class="tag tag-rare">rare</span>')
    return " ".join(tags)

def evidence_card_view(log):
    card = log["card"]
    tags = evidence_tags(card)
    st.markdown(
        f"""
        <div class="soft">
          <div><strong>Round {log['round']}</strong> — <code>{card.source}</code> {tags}</div>
          <div style="margin:.25rem 0 .5rem 0;">{card.text}</div>
          <div class="dim">Integrity after: {log['integrity']}/100 • Escape Risk: {log['escape_risk']}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.session_state.g["show_math"]:
        like_df = pd.DataFrame(
            [{"Guard": k, "P(evidence|Guard)": v} for k, v in card.likelihood.items()]
        ).sort_values("Guard")
        st.table(like_df.style.format({"P(evidence|Guard)": "{:.2f}"}))
        st.markdown(
            r"""
**Bayes (proportional form):**  
\[
Posterior(G_i) \propto Prior(G_i) \times P(evidence \mid G_i)
\]
Normalize so the posteriors sum to 1.
"""
        )
        suspicion_chart(log["posteriors"])

# --------------------------------------------------------------------------------------
# ----------------------------------- APP EXECUTION ------------------------------------
# --------------------------------------------------------------------------------------
init_state()
g = st.session_state.g

# Modals (top-level)
tutorial_modal()
ethics_modal()
accuse_modal()

# Header
st.markdown('<div class="big-title">🖼️ The Lost Painting Heist — Adaptive</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Inference + ethics, now with context-aware tutoring.</div>', unsafe_allow_html=True)
step_indicator(g["step"])
st.markdown("<br/>", unsafe_allow_html=True)

# INTRO
if g["step"] == 0 and not g["show_tutorial"]:
    st.write(
        "You’re the museum’s lead investigator. A priceless painting is missing. "
        "Three guards — **A, B, C** — were on duty. "
        "Your job: **infer who’s guilty**, balancing speed, certainty, and ethics."
    )
    if st.button("Start Investigation →"):
        g["step"] = 1
        st.experimental_rerun()

# EVIDENCE
if g["step"] == 1:
    # Adaptive tutor panel (top)
    tutor_panel()

    c_top = st.columns([1.2,1,1])
    with c_top[0]:
        st.subheader("Suspicion Meter")
        suspicion_chart(g["posteriors"])
    with c_top[1]:
        st.subheader("Integrity")
        st.progress(int(g["integrity"]), text=f"{g['integrity']}/100")
    with c_top[2]:
        st.subheader("Escape Risk")
        st.progress(int(g["escape_risk"]), text=f"{g['escape_risk']}%")

    with st.expander("Show Bayesian math panel", expanded=False):
        g["show_math"] = st.checkbox("Show math & likelihood tables for each clue", value=g["show_math"])

    st.divider()
    st.subheader("Gather Evidence")
    e1, e2, e3 = st.columns(3)
    with e1:
        if st.button("📹 CCTV Footage", help="Neutral but incomplete. No integrity penalty.", use_container_width=True):
            add_evidence(pick_evidence("CCTV"))
            st.experimental_rerun()
    with e2:
        if st.button("🗣️ Staff Rumors (−5 Integrity)", help="Biased but fast.", use_container_width=True):
            add_evidence(pick_evidence("RUMOR"))
            st.experimental_rerun()
    with e3:
        if st.button("🚨 Aggressive Interrogation (−15 Integrity)", help="Informative but unethical.", use_container_width=True):
            add_evidence(pick_evidence("INTERROGATION"))
            st.experimental_rerun()

    st.divider()
    st.subheader("Evidence Log & Belief Updates")
    if not g["evidence_log"]:
        st.info("No evidence yet. Pull from CCTV, Rumors, or Interrogation above.")
    else:
        for log in g["evidence_log"][::-1]:
            evidence_card_view(log)

    st.divider()
    st.subheader("Suspicion History")
    suspicion_history_chart()

    st.divider()
    st.subheader("Make your call")
    left, mid, right = st.columns([1,1,1])
    with left:
        if st.button("🎯 Accuse Guard A"):
            accuse_guard_with_check("A")
            st.experimental_rerun()
    with mid:
        if st.button("🎯 Accuse Guard B"):
            accuse_guard_with_check("B")
            st.experimental_rerun()
    with right:
        if st.button("🎯 Accuse Guard C"):
            accuse_guard_with_check("C")
            st.experimental_rerun()

# DEBRIEF
if g["step"] == 3 and g["done"]:
    st.divider()
    st.header("🧠 Verdict & Debrief")
    correct = (g["accused"] == g["guilty"])
    if correct:
        st.success(f"✅ You accused Guard {g['accused']} — and you were **RIGHT**! The thief was Guard {g['guilty']}.")
    else:
        st.error(f"❌ You accused Guard {g['accused']} — but the thief was **Guard {g['guilty']}**.")

    s = g["scores"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='scorebox'><h2>{s['accuracy']:.0f}</h2><span>Accuracy</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='scorebox'><h2>{s['integrity']:.0f}</h2><span>Integrity</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='scorebox'><h2>{s['efficiency']:.0f}</h2><span>Efficiency</span></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='scorebox'><h2>{s['caution']:.0f}</h2><span>Caution (Ethical)</span></div>", unsafe_allow_html=True)

    st.subheader(f"🏁 Final Score: **{s['final']:.1f}** / 100")
    st.altair_chart(radar_chart(s), use_container_width=True)

    if g["achievement_flags"]:
        st.subheader("🏅 Achievements")
        for a in g["achievement_flags"]:
            st.markdown(f"- **{a}**")

    st.divider()
    st.subheader("Reflection")
    st.markdown(
        """
- **Inference**: You watched your belief distribution change after each clue—that’s Bayesian updating.
- **Ethics**: Biased/unethical evidence boosted suspicion fast but hurt integrity. Neutral evidence took longer.
- **Decision Theory**: You had to trade off **speed vs. certainty vs. integrity** under escape pressure.
"""
    )

    st.divider()
    st.button("🔁 New Run (random culprit & clues)", on_click=reset_game)

st.markdown('<div class="footer-tip">vAdaptive — built with Streamlit, Altair, Pandas, NumPy. No external deps.</div>', unsafe_allow_html=True)
