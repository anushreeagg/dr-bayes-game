import streamlit as st
import numpy as np
from scipy.stats import norm

# --- Doctor Statuses ---
DOCTOR_STATUSES = [
    "Intern",
    "Resident",
    "Fellow",
    "Attending",
    "Chief of Medicine"
]

# --- Game Data: Medical Levels ---
LEVELS = [
    {
        "name": "Fever Room",
        "desc": "A patient shuffles in, cheeks flushed. The digital thermometer beeps...",
        "group_a": {"label": "Flu", "mean": 39.0, "std": 0.4},
        "group_b": {"label": "Healthy", "mean": 37.0, "std": 0.7},
        "unit": "°C",
        "visual": "thermometer",
        "clue": lambda v: "The thermometer bar is almost maxed out!" if v > 38.5 else "The bar is in the normal range."
    },
    {
        "name": "Blood Lab",
        "desc": "A nurse hands you a blood test strip. The analyzer lights up...",
        "group_a": {"label": "Anemia", "mean": 9.5, "std": 0.7},
        "group_b": {"label": "Normal", "mean": 13.5, "std": 1.2},
        "unit": "g/dL",
        "visual": "blood",
        "clue": lambda v: "The blood bar is looking low..." if v < 11 else "The bar is in the healthy zone."
    },
    {
        "name": "X-ray Chamber",
        "desc": "A shadowy chest X-ray appears on the screen. The AI highlights a region...",
        "group_a": {"label": "Pneumonia", "mean": 0.8, "std": 0.1},
        "group_b": {"label": "Clear", "mean": 0.3, "std": 0.15},
        "unit": "opacity",
        "visual": "xray",
        "clue": lambda v: "The opacity meter is high!" if v > 0.6 else "The scan looks mostly clear."
    },
    {
        "name": "Cardio Arena",
        "desc": "The ECG monitor beeps. The heart rate bar pulses...",
        "group_a": {"label": "Arrhythmia", "mean": 120, "std": 15},
        "group_b": {"label": "Normal", "mean": 75, "std": 10},
        "unit": "bpm",
        "visual": "ecg",
        "clue": lambda v: "The heart rate is racing!" if v > 110 else "The pulse is steady."
    },
    {
        "name": "Neuro Lab",
        "desc": "A patient sits for a reflex test. The response meter jumps...",
        "group_a": {"label": "Nerve Disorder", "mean": 2.2, "std": 0.3},
        "group_b": {"label": "Normal", "mean": 1.2, "std": 0.2},
        "unit": "ms",
        "visual": "reflex",
        "clue": lambda v: "The response is very slow!" if v > 1.8 else "The reflex is quick."
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
          <span style='font-size:1.2em;font-weight:700;color:{color};padding-left:8px;'>{value:.2f} {unit}</span>
        </div>
      </div>
    </div>
    """
    st.markdown(bar, unsafe_allow_html=True)

def get_status(level):
    return DOCTOR_STATUSES[min(level, len(DOCTOR_STATUSES)-1)]

def reset_patient_state():
    st.session_state.show_result = False
    st.session_state.patient_val = None
    st.session_state.patient_true = None
    st.session_state.last_posterior = None
    st.session_state.last_decision = None
    st.session_state.revealed = False

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
st.write("Welcome to the Diagnosis Arena! Diagnose or Dismiss each patient based on the evidence. Get promoted through the doctor ranks by making correct calls!")

if 'level' not in st.session_state:
    st.session_state.level = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.patient_val = None
    st.session_state.patient_true = None
    st.session_state.last_posterior = None
    st.session_state.last_decision = None
    st.session_state.revealed = False
    st.session_state.status = get_status(0)

def reset_game():
    st.session_state.level = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.patient_val = None
    st.session_state.patient_true = None
    st.session_state.last_posterior = None
    st.session_state.last_decision = None
    st.session_state.revealed = False
    st.session_state.status = get_status(0)

if st.session_state.level >= len(LEVELS):
    st.balloons()
    st.success(f"Congratulations! You reached Chief of Medicine! Final score: {st.session_state.score} / {len(LEVELS)}")
    st.info(f"Final Status: {get_status(st.session_state.level)}")
    if st.button("Play Again"):
        reset_game()
    st.stop()

lvl = LEVELS[st.session_state.level]

# --- Patient Generation ---
if not st.session_state.show_result:
    # Draw a new patient
    val = float(np.round(np.random.normal(lvl['group_a']['mean'] if np.random.rand()<0.5 else lvl['group_b']['mean'],
                                          lvl['group_a']['std'] if np.random.rand()<0.5 else lvl['group_b']['std']), 2))
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
st.subheader(f"Level {st.session_state.level+1}: {lvl['name']}  |  Status: {get_status(st.session_state.level)}")
st.caption(lvl['desc'])

if lvl['visual'] == "thermometer":
    animated_bar("Thermometer", val, 36, 40, lvl['unit'], color="#e4572e")
elif lvl['visual'] == "blood":
    animated_bar("Hemoglobin", val, 8, 15, lvl['unit'], color="#d7263d")
elif lvl['visual'] == "xray":
    animated_bar("Opacity Meter", val, 0, 1.2, lvl['unit'], color="#22223b")
elif lvl['visual'] == "ecg":
    animated_bar("Heart Rate", val, 50, 140, lvl['unit'], color="#43aa8b")
elif lvl['visual'] == "reflex":
    animated_bar("Reflex Response", val, 1, 2.5, lvl['unit'], color="#f9c74f")

st.markdown(f"<div style='font-size:1.1em;font-weight:500;margin:0.7em 0 1.2em 0;color:#2563eb;'>Clue: {lvl['clue'](val)}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Diagnose (Disease)", key=f"diagnose_{st.session_state.level}_{st.session_state.show_result}"):
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
        st.success(f"Correct! Promoted to {get_status(st.session_state.level+1)}.")
        st.session_state.score += 1
        st.session_state.level += 1
        st.session_state.status = get_status(st.session_state.level)
        st.markdown(f"**Bayesian Probability of Disease:** {int(round(post*100))}%")
        st.markdown(f"**You chose:** {'Diagnose' if st.session_state.last_decision == 'A' else 'Dismiss'}")
        st.markdown(f"**True diagnosis:** {'Disease' if st.session_state.patient_true == 'A' else 'Healthy'}")
        if st.button("Reveal Insight", key=f"reveal_{st.session_state.level}"):
            st.session_state.revealed = True
        if st.session_state.revealed:
            st.info("Bayes' Theorem: P(Disease | test) = [P(test | Disease) * P(Disease)] / [P(test | Disease) * P(Disease) + P(test | Healthy) * P(Healthy)]")
        st.markdown(f"<div style='font-size:1.05em;color:#888;margin-top:0.7em;'>Tip: {lvl['clue'](val)}</div>", unsafe_allow_html=True)
        if st.button("Next Level", key=f"next_{st.session_state.level}"):
            reset_patient_state()
            st.experimental_rerun()
    else:
        st.error(f"Incorrect. You remain a {get_status(st.session_state.level)}. Try again!")
        st.markdown(f"**Bayesian Probability of Disease:** {int(round(post*100))}%")
        st.markdown(f"**You chose:** {'Diagnose' if st.session_state.last_decision == 'A' else 'Dismiss'}")
        st.markdown(f"**True diagnosis:** {'Disease' if st.session_state.patient_true == 'A' else 'Healthy'}")
        if st.button("Reveal Insight", key=f"reveal_{st.session_state.level}"):
            st.session_state.revealed = True
        if st.session_state.revealed:
            st.info("Bayes' Theorem: P(Disease | test) = [P(test | Disease) * P(Disease)] / [P(test | Disease) * P(Disease) + P(test | Healthy) * P(Healthy)]")
        st.markdown(f"<div style='font-size:1.05em;color:#888;margin-top:0.7em;'>Tip: {lvl['clue'](val)}</div>", unsafe_allow_html=True)
        if st.button("Try Again", key=f"tryagain_{st.session_state.level}"):
            reset_patient_state()
            st.experimental_rerun() 