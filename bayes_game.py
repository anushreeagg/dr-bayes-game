import streamlit as st
import numpy as np
from scipy.stats import norm

# --- Game Data ---
SCENARIOS = [
    {
        "title": "Fever Test",
        "description": "A patient has a fever of 38.5°C. Group A (flu patients) have fevers with mean 38.7°C, std 0.5°C. Group B (healthy) have mean 37.0°C, std 0.4°C. What is the probability this patient has the flu?",
        "mean_a": 38.7,
        "std_a": 0.5,
        "mean_b": 37.0,
        "std_b": 0.4,
        "obs": 38.5,
        "prior_a": 0.5,
        "prior_b": 0.5,
        "unit": "°C"
    },
    {
        "title": "Candy Inspector",
        "description": "A candy weighs 5.2g. Group A (factory A) produces candies with mean 5.0g, std 0.2g. Group B (factory B) produces candies with mean 4.7g, std 0.15g. What is the probability this candy came from factory A?",
        "mean_a": 5.0,
        "std_a": 0.2,
        "mean_b": 4.7,
        "std_b": 0.15,
        "obs": 5.2,
        "prior_a": 0.5,
        "prior_b": 0.5,
        "unit": "g"
    },
    {
        "title": "Genetic Marker",
        "description": "A person’s gene expression level is 2.1. Group A (disease) has mean 2.0, std 0.3. Group B (healthy) has mean 1.5, std 0.2. What is the probability this person has the disease?",
        "mean_a": 2.0,
        "std_a": 0.3,
        "mean_b": 1.5,
        "std_b": 0.2,
        "obs": 2.1,
        "prior_a": 0.5,
        "prior_b": 0.5,
        "unit": ""
    },
    {
        "title": "IQ Admission",
        "description": "A student scores 132 on an IQ test. Group A (admitted) has mean 130, std 5. Group B (not admitted) has mean 110, std 10. What is the probability this student was admitted?",
        "mean_a": 130,
        "std_a": 5,
        "mean_b": 110,
        "std_b": 10,
        "obs": 132,
        "prior_a": 0.5,
        "prior_b": 0.5,
        "unit": ""
    },
    {
        "title": "Drug Detection",
        "description": "A test result is 0.8. Group A (drug users) have mean 0.9, std 0.1. Group B (non-users) have mean 0.3, std 0.2. What is the probability this person is a drug user?",
        "mean_a": 0.9,
        "std_a": 0.1,
        "mean_b": 0.3,
        "std_b": 0.2,
        "obs": 0.8,
        "prior_a": 0.5,
        "prior_b": 0.5,
        "unit": ""
    },
]

# --- Helper Functions ---
def bayes_posterior(mean_a, std_a, mean_b, std_b, obs, prior_a, prior_b):
    like_a = norm.pdf(obs, mean_a, std_a)
    like_b = norm.pdf(obs, mean_b, std_b)
    num = like_a * prior_a
    denom = like_a * prior_a + like_b * prior_b
    if denom == 0:
        return 0.5  # fallback
    return num / denom

def score_guess(user_guess, true_prob):
    # Score out of 10, max if within 2%, linear drop to 0 at 20% off
    diff = abs(user_guess - true_prob)
    if diff <= 0.02:
        return 10
    elif diff >= 0.2:
        return 0
    else:
        return int(round(10 * (1 - (diff - 0.02) / 0.18)))

def format_pct(p):
    return f"{int(round(100*p))}%"

# --- Streamlit App ---
st.set_page_config(page_title="Dr. Bayes: Diagnose or Dismiss?", page_icon="🧑‍⚕️", layout="centered")

st.markdown("""
<style>
body, .stApp {
    background: #f7fafd;
    color: #222 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}
.stSlider { margin-bottom: 1.5em; }
.stButton>button {
    background: #2563eb;
    color: #222 !important;
    border-radius: 8px;
    padding: 0.6em 2em;
    font-size: 1.1em;
    font-weight: 500;
    border: none;
    box-shadow: none;
    transition: background 0.2s;
}
.stButton>button:active { background: #1e40af; }
.st-bb { font-family: 'Source Code Pro', monospace; }
.spinner { display: flex; justify-content: center; align-items: center; height: 60px; }
.spinner:after {
    content: '';
    width: 32px; height: 32px;
    border: 4px solid #2563eb;
    border-top: 4px solid #f7fafd;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
.scenario-card {
    background: #f0f4f8;
    border-radius: 12px;
    padding: 1.5em 1.5em 1em 1.5em;
    box-shadow: 0 2px 12px #0001;
    margin-bottom: 2em;
    border-left: 6px solid #2563eb;
}
.slider-label {
    font-size: 1.1em;
    font-weight: 600;
    color: #2563eb;
    margin-bottom: 0.2em;
    margin-top: 1em;
}
/* Ensure metric text is dark */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #222 !important;
}
</style>
""", unsafe_allow_html=True)

SCENARIO_ICONS = ["🌡️", "🍬", "🧬", "🧠", "💊"]

st.title("👩🏻‍⚕️ Dr. Bayes: Diagnose or Dismiss?")
st.write("Estimate the probability that an observation came from Group A. Outsmart Dr. Bayes and collect all the trophies!")

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.scores = []
    st.session_state.guesses = []
    st.session_state.show_result = False
    st.session_state.total_score = 0

def reset_game():
    st.session_state.step = 0
    st.session_state.scores = []
    st.session_state.guesses = []
    st.session_state.show_result = False
    st.session_state.total_score = 0

if st.session_state.step >= len(SCENARIOS):
    st.success(f"Game Over! Your final score: {sum(st.session_state.scores)} / 50")
    st.write("**Thanks for playing Dr. Bayes!**")
    if st.button("Play Again"):
        reset_game()
    st.stop()

sc = SCENARIOS[st.session_state.step]

# Progress bar and scenario icon
progress = (st.session_state.step) / len(SCENARIOS)
st.progress(progress, text=f"Scenario {st.session_state.step+1} of {len(SCENARIOS)}")

with st.container():
    st.markdown(f'<div class="scenario-card"><span style="font-size:2em;">{SCENARIO_ICONS[st.session_state.step]}</span> <span style="font-size:1.5em;font-weight:700;">Scenario {st.session_state.step+1}: {sc["title"]}</span><br><span style="font-size:1.1em;">{sc["description"]}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="slider-label">Your estimate: Probability it\'s Group A</div>', unsafe_allow_html=True)
user_guess = st.slider(
    " ",  # Hide default label
    min_value=0,
    max_value=100,
    value=50,
    step=1,
    key=f"slider_{st.session_state.step}"
)

if st.button("Submit", key=f"submit_{st.session_state.step}"):
    true_prob = bayes_posterior(
        sc['mean_a'], sc['std_a'], sc['mean_b'], sc['std_b'],
        sc['obs'], sc['prior_a'], sc['prior_b']
    )
    user_prob = user_guess / 100
    score = score_guess(user_prob, true_prob)
    st.session_state.scores.append(score)
    st.session_state.guesses.append(user_guess)
    st.session_state.show_result = True
    st.session_state.total_score = sum(st.session_state.scores)

if st.session_state.show_result:
    true_prob = bayes_posterior(
        sc['mean_a'], sc['std_a'], sc['mean_b'], sc['std_b'],
        sc['obs'], sc['prior_a'], sc['prior_b']
    )
    user_prob = st.session_state.guesses[-1] / 100
    score = st.session_state.scores[-1]
    col1, col2 = st.columns(2)
    with col1:
        st.metric("True probability", format_pct(true_prob))
        st.metric("Your guess", format_pct(user_prob))
    with col2:
        st.metric("Round score", f"{score} / 10")
        st.metric("Total score so far", f"{st.session_state.total_score} / 50")
    # Subtle, text-based feedback only
    if abs(user_prob - true_prob) <= 0.02:
        st.success("Excellent! Your Bayesian intuition is spot on.")
    elif abs(user_prob - true_prob) <= 0.05:
        st.info("Very close! You're thinking like Dr. Bayes.")
    elif abs(user_prob - true_prob) <= 0.1:
        st.warning("Not bad, but you can get even closer.")
    else:
        st.error("Keep practicing your Bayesian skills!")
    if st.button("Next Scenario"):
        st.session_state.step += 1
        st.session_state.show_result = False
        st.experimental_rerun() 