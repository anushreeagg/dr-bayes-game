import streamlit as st
import numpy as np
from scipy.stats import norm

# --- Game Data: Levels ---
LEVELS = [
    {
        "name": "Fever Room",
        "desc": "A patient enters the Fever Room. The thermometer rises...",
        "group_a": {"label": "Disease A", "mean": 38.5, "std": 0.5},
        "group_b": {"label": "Healthy", "mean": 37.0, "std": 0.7},
        "unit": "°C",
        "visual": "thermometer",
        "clue": lambda v: "The spike is near the high zone." if v > 38 else "The spike is in the normal range."
    },
    {
        "name": "Candy Machine",
        "desc": "A chocolate drops onto the scale in the Candy Machine...",
        "group_a": {"label": "Machine A", "mean": 11, "std": 0.2},
        "group_b": {"label": "Machine B", "mean": 10.6, "std": 0.4},
        "unit": "g",
        "visual": "scale",
        "clue": lambda v: "The scale tips toward heavy!" if v > 11 else "The scale is steady."
    },
    {
        "name": "Mutation Scan",
        "desc": "A glowing protein meter pulses in the Mutation Scan...",
        "group_a": {"label": "Gene Variant", "mean": 42, "std": 5},
        "group_b": {"label": "No Variant", "mean": 35, "std": 4},
        "unit": "units",
        "visual": "meter",
        "clue": lambda v: "The meter glows bright!" if v > 40 else "The meter is dim."
    },
    {
        "name": "Brain Boost Test",
        "desc": "The IQ scan whirs in the Brain Boost Test...",
        "group_a": {"label": "Gifted", "mean": 135, "std": 8},
        "group_b": {"label": "General", "mean": 110, "std": 10},
        "unit": "",
        "visual": "iq",
        "clue": lambda v: "The scan flashes genius!" if v > 130 else "The scan is calm."
    },
    {
        "name": "Heart Hackers",
        "desc": "The ECG pulses in Heart Hackers...",
        "group_a": {"label": "Drug Z", "mean": 12, "std": 3},
        "group_b": {"label": "No Drug", "mean": 4, "std": 5},
        "unit": "bpm",
        "visual": "ecg",
        "clue": lambda v: "The ECG spikes high!" if v > 10 else "The ECG is steady."
    },
]

# --- Helper Functions ---
def bayes_posterior(val, mean_a, std_a, mean_b, std_b, prior_a=0.5, prior_b=0.5):
    like_a = norm.pdf(val, mean_a, std_a)
    like_b = norm.pdf(val, mean_b, std_b)
    num = like_a * prior_a
    denom = like_a * prior_a + like_b * prior_b
    if denom == 0:
        return 0.5
    return num / denom

def animated_bar(label, value, minv, maxv, unit, color="#2563eb"):
    pct = (value - minv) / (maxv - minv)
    pct = np.clip(pct, 0, 1)
    bar = f"""
    <div style='margin:1em 0;'>
      <div style='font-weight:600;margin-bottom:0.3em;'>{label}</div>
      <div style='background:#e3eafc;border-radius:8px;height:32px;width:100%;position:relative;'>
        <div style='background:{color};width:{pct*100:.1f}%;height:32px;border-radius:8px;transition:width 0.7s;'></div>
        <div style='position:absolute;top:0;left:calc({pct*100:.1f}% - 32px);height:32px;display:flex;align-items:center;'>
          <span style='font-size:1.2em;font-weight:700;color:{color};padding-left:8px;'>{value:.1f} {unit}</span>
        </div>
      </div>
    </div>
    """
    st.markdown(bar, unsafe_allow_html=True)

def diagnosis_rank(score):
    if score >= 5:
        return "Level 5: Diagnosis Master"
    elif score >= 4:
        return "Level 4: Confident Resident"
    elif score >= 3:
        return "Level 3: Junior Diagnostician"
    elif score >= 2:
        return "Level 2: Medical Intern"
    else:
        return "Level 1: Trainee"

# --- Streamlit App ---
st.set_page_config(page_title="Dr. Bayes: The Diagnosis Arena", page_icon="👩🏻‍⚕️", layout="centered")
st.markdown("""
<style>
body, .stApp { background: #f7fafd; color: #222; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif; }
.stButton>button { background: #2563eb; color: #fff; border-radius: 8px; padding: 0.6em 2em; font-size: 1.1em; font-weight: 500; border: none; box-shadow: none; transition: background 0.2s; }
.stButton>button:active, .stButton>button:hover { background: #1e40af; }
.st-bb { font-family: 'Source Code Pro', monospace; }
</style>
""", unsafe_allow_html=True)

st.title("👩🏻‍⚕️ Dr. Bayes: The Diagnosis Arena")
st.write("Welcome to the Diagnosis Arena! Diagnose or Dismiss each patient based on the evidence. Trust your intuition, but let Bayes be your guide.")

if 'level' not in st.session_state:
    st.session_state.level = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.patient_val = None
    st.session_state.patient_true = None
    st.session_state.last_posterior = None
    st.session_state.last_decision = None
    st.session_state.revealed = False

def reset_game():
    st.session_state.level = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.patient_val = None
    st.session_state.patient_true = None
    st.session_state.last_posterior = None
    st.session_state.last_decision = None
    st.session_state.revealed = False

if st.session_state.level >= len(LEVELS):
    st.balloons()
    st.success(f"Game Over! Your final score: {st.session_state.score} / {len(LEVELS)}")
    st.info(f"Diagnosis Rank: {diagnosis_rank(st.session_state.score)}")
    if st.button("Play Again"):
        reset_game()
    st.stop()

lvl = LEVELS[st.session_state.level]

# --- Patient Generation ---
if not st.session_state.show_result:
    # Draw a new patient
    val = float(np.round(np.random.normal(lvl['group_a']['mean'] if np.random.rand()<0.5 else lvl['group_b']['mean'],
                                          lvl['group_a']['std'] if np.random.rand()<0.5 else lvl['group_b']['std']), 1))
    st.session_state.patient_val = val
    # Compute true posterior
    post = bayes_posterior(val, lvl['group_a']['mean'], lvl['group_a']['std'], lvl['group_b']['mean'], lvl['group_b']['std'])
    st.session_state.last_posterior = post
    st.session_state.patient_true = 'A' if post > 0.5 else 'B'
    st.session_state.last_decision = None
    st.session_state.revealed = False
else:
    val = st.session_state.patient_val
    post = st.session_state.last_posterior

# --- Visuals ---
st.subheader(f"Level {st.session_state.level+1}: {lvl['name']}")
st.caption(lvl['desc'])

if lvl['visual'] == "thermometer":
    animated_bar("Thermometer", val, 36, 40, lvl['unit'], color="#e4572e")
elif lvl['visual'] == "scale":
    animated_bar("Chocolate Weight", val, 10, 12, lvl['unit'], color="#3a86ff")
elif lvl['visual'] == "meter":
    animated_bar("Protein Meter", val, 30, 50, lvl['unit'], color="#43aa8b")
elif lvl['visual'] == "iq":
    animated_bar("IQ Scan", val, 90, 150, lvl['unit'], color="#ffbe0b")
elif lvl['visual'] == "ecg":
    animated_bar("ECG Heart Rate", val, 0, 20, lvl['unit'], color="#9d4edd")

st.markdown(f"<div style='font-size:1.1em;font-weight:500;margin:0.7em 0 1.2em 0;color:#2563eb;'>Clue: {lvl['clue'](val)}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Diagnose (Disease A)", key=f"diagnose_{st.session_state.level}_{st.session_state.show_result}"):
        st.session_state.last_decision = 'A'
        st.session_state.show_result = True
with col2:
    if st.button("Dismiss (Healthy)", key=f"dismiss_{st.session_state.level}_{st.session_state.show_result}"):
        st.session_state.last_decision = 'B'
        st.session_state.show_result = True

# --- Result & Feedback ---
if st.session_state.show_result:
    st.markdown("---")
    correct = (st.session_state.last_decision == st.session_state.patient_true)
    if correct:
        st.success("Correct! Your decision matches the Bayesian diagnosis.")
        st.session_state.score += 1
    else:
        st.error("Incorrect. The Bayesian diagnosis was different.")
    st.markdown(f"**Bayesian Probability of Disease A:** {int(round(post*100))}%")
    st.markdown(f"**You chose:** {'Diagnose' if st.session_state.last_decision == 'A' else 'Dismiss'}")
    st.markdown(f"**True diagnosis:** {'Disease A' if st.session_state.patient_true == 'A' else 'Healthy'}")
    if st.button("Reveal Insight", key=f"reveal_{st.session_state.level}"):
        st.session_state.revealed = True
    if st.session_state.revealed:
        st.info("Bayes' Theorem: P(Disease A | test) = [P(test | Disease A) * P(Disease A)] / [P(test | Disease A) * P(Disease A) + P(test | Healthy) * P(Healthy)]")
    st.markdown(f"<div style='font-size:1.05em;color:#888;margin-top:0.7em;'>Tip: {lvl['clue'](val)}</div>", unsafe_allow_html=True)
    if st.button("Next Patient", key=f"next_{st.session_state.level}"):
        st.session_state.level += 1
        st.session_state.show_result = False
        st.session_state.patient_val = None
        st.session_state.patient_true = None
        st.session_state.last_posterior = None
        st.session_state.last_decision = None
        st.session_state.revealed = False
        st.experimental_rerun() 