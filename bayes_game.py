import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import norm
import plotly.graph_objects as go
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="🧠 Bayes Detective Academy", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Inter', sans-serif;
        }
        
        .main-container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .game-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .game-subtitle {
            font-size: 1.2rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .round-header {
            background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            border-left: 5px solid #667eea;
        }
        
        .round-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .scenario-text {
            font-size: 1.1rem;
            color: #4b5563;
            line-height: 1.6;
        }
        
        .measurement-card {
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            border: 2px solid #f59e0b;
        }
        
        .measurement-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #d97706;
            margin-bottom: 0.5rem;
        }
        
        .measurement-label {
            font-size: 1.1rem;
            color: #92400e;
            font-weight: 500;
        }
        
        .clue-box {
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #3b82f6;
        }
        
        .clue-text {
            font-size: 1rem;
            color: #1e40af;
            font-weight: 500;
        }
        
        .score-display {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .score-text {
            font-size: 1.2rem;
            font-weight: 600;
            color: #065f46;
        }
        
        .result-correct {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 5px solid #10b981;
            margin: 1rem 0;
        }
        
        .result-incorrect {
            background: linear-gradient(135deg, #fee2e2, #fecaca);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 5px solid #ef4444;
            margin: 1rem 0;
        }
        
        .final-score {
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            border: 3px solid #f59e0b;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# --- Game Configuration ---
SCENARIOS = [
    {
        "title": "🌡️ Emergency Room Fever Check",
        "description": "A patient walks into the ER with complaints of feeling unwell. You take their temperature with a digital thermometer.",
        "group_a": {"name": "Has Fever", "mean": 39.2, "std": 0.5, "color": "#ef4444"},
        "group_b": {"name": "No Fever", "mean": 37.0, "std": 0.8, "color": "#10b981"},
        "unit": "°C",
        "measurement_name": "Body Temperature",
        "clue_func": lambda x: "🔥 The thermometer is showing very high!" if x > 38.5 else "😊 Temperature seems normal range",
        "context": "Normal body temperature is around 37°C. Fever typically starts around 38°C."
    },
    {
        "title": "🩸 Blood Test Analysis",
        "description": "A routine blood test shows hemoglobin levels. You need to determine if this indicates anemia.",
        "group_a": {"name": "Anemia", "mean": 9.5, "std": 1.0, "color": "#ef4444"},
        "group_b": {"name": "Normal", "mean": 14.0, "std": 1.5, "color": "#10b981"},
        "unit": "g/dL",
        "measurement_name": "Hemoglobin Level",
        "clue_func": lambda x: "⚠️ The blood count looks concerning" if x < 12 else "✅ Blood levels appear healthy",
        "context": "Normal hemoglobin: 12-16 g/dL for women, 14-18 g/dL for men. Below 12 may indicate anemia."
    },
    {
        "title": "💓 Heart Rate Monitor",
        "description": "A patient's heart rate is measured during a routine checkup. Determine if this indicates a heart condition.",
        "group_a": {"name": "Tachycardia", "mean": 110, "std": 8, "color": "#ef4444"},
        "group_b": {"name": "Normal HR", "mean": 72, "std": 12, "color": "#10b981"},
        "unit": "BPM",
        "measurement_name": "Heart Rate",
        "clue_func": lambda x: "💨 Heart is beating quite fast!" if x > 90 else "💗 Steady, normal rhythm",
        "context": "Normal resting heart rate: 60-100 BPM. Tachycardia is typically >100 BPM."
    },
    {
        "title": "🩺 Blood Pressure Reading",
        "description": "Taking a blood pressure measurement to check for hypertension during a health screening.",
        "group_a": {"name": "Hypertension", "mean": 155, "std": 10, "color": "#ef4444"},
        "group_b": {"name": "Normal BP", "mean": 120, "std": 15, "color": "#10b981"},
        "unit": "mmHg",
        "measurement_name": "Systolic BP",
        "clue_func": lambda x: "⬆️ Pressure reading is quite elevated" if x > 140 else "👍 Blood pressure in good range",
        "context": "Normal systolic BP: <120 mmHg. Hypertension: ≥140 mmHg."
    },
    {
        "title": "🧪 Glucose Test",
        "description": "A fasting blood glucose test to screen for diabetes. The lab results just came in.",
        "group_a": {"name": "Diabetes", "mean": 180, "std": 25, "color": "#ef4444"},
        "group_b": {"name": "Normal", "mean": 90, "std": 15, "color": "#10b981"},
        "unit": "mg/dL",
        "measurement_name": "Blood Glucose",
        "clue_func": lambda x: "📈 Glucose levels are very high!" if x > 140 else "📊 Sugar levels look normal",
        "context": "Normal fasting glucose: 70-100 mg/dL. Diabetes: ≥126 mg/dL fasting."
    }
]

def calculate_bayes_probability(observation, mean_a, std_a, mean_b, std_b, prior_a=0.5):
    """Calculate posterior probability using Bayes' theorem"""
    likelihood_a = norm.pdf(observation, mean_a, std_a)
    likelihood_b = norm.pdf(observation, mean_b, std_b)
    
    posterior_a = (likelihood_a * prior_a) / (likelihood_a * prior_a + likelihood_b * (1 - prior_a))
    return posterior_a

def create_distribution_plot(scenario, observation):
    """Create an interactive plot showing the distributions and observation"""
    x_range = np.linspace(
        min(scenario["group_a"]["mean"] - 3*scenario["group_a"]["std"], 
            scenario["group_b"]["mean"] - 3*scenario["group_b"]["std"]),
        max(scenario["group_a"]["mean"] + 3*scenario["group_a"]["std"], 
            scenario["group_b"]["mean"] + 3*scenario["group_b"]["std"]),
        300
    )
    
    y_a = norm.pdf(x_range, scenario["group_a"]["mean"], scenario["group_a"]["std"])
    y_b = norm.pdf(x_range, scenario["group_b"]["mean"], scenario["group_b"]["std"])
    
    fig = go.Figure()
    
    # Add distribution curves
    fig.add_trace(go.Scatter(
        x=x_range, y=y_a,
        mode='lines',
        name=scenario["group_a"]["name"],
        line=dict(color=scenario["group_a"]["color"], width=3),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=x_range, y=y_b,
        mode='lines',
        name=scenario["group_b"]["name"],
        line=dict(color=scenario["group_b"]["color"], width=3),
        fill='tozeroy'
    ))
    
    # Add observation line
    fig.add_vline(
        x=observation,
        line_dash="dash",
        line_color="black",
        line_width=3,
        annotation_text=f"Your observation: {observation:.1f} {scenario['unit']}"
    )
    
    fig.update_layout(
        title="Distribution of Values for Each Group",
        xaxis_title=f"{scenario['measurement_name']} ({scenario['unit']})",
        yaxis_title="Probability Density",
        height=400,
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

# --- Session State Initialization ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'playing'
    st.session_state.current_round = 0
    st.session_state.score = 0
    st.session_state.round_data = None
    st.session_state.user_guess = None
    st.session_state.show_result = False
    st.session_state.show_explanation = False

# --- Main Game Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="game-title">🧠 Bayes Detective Academy</h1>', unsafe_allow_html=True)
st.markdown('<p class="game-subtitle">Master the art of probabilistic reasoning through medical diagnosis!</p>', unsafe_allow_html=True)

# Score Display
if st.session_state.current_round > 0:
    st.markdown(f'''
        <div class="score-display">
            <div class="score-text">
                Round {st.session_state.current_round} of {len(SCENARIOS)} | 
                Score: {st.session_state.score}/{st.session_state.current_round - (1 if st.session_state.show_result else 0)}
            </div>
        </div>
    ''', unsafe_allow_html=True)

# Game Over Screen
if st.session_state.current_round >= len(SCENARIOS) and st.session_state.show_result:
    final_percentage = (st.session_state.score / len(SCENARIOS)) * 100
    
    st.markdown(f'''
        <div class="final-score">
            <h2>🎉 Game Complete!</h2>
            <h3>Final Score: {st.session_state.score}/{len(SCENARIOS)} ({final_percentage:.0f}%)</h3>
            <p>You've completed your training at the Bayes Detective Academy!</p>
        </div>
    ''', unsafe_allow_html=True)
    
    if final_percentage >= 80:
        st.balloons()
        st.markdown("### 🏆 Excellent! You have a strong intuition for Bayesian reasoning!")
    elif final_percentage >= 60:
        st.markdown("### 👍 Good job! You're getting the hang of probabilistic thinking!")
    else:
        st.markdown("### 📚 Keep practicing! Bayesian reasoning takes time to master.")
    
    if st.button("🔄 Play Again", key="play_again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Initialize round data if needed
if st.session_state.round_data is None and st.session_state.current_round < len(SCENARIOS):
    scenario = SCENARIOS[st.session_state.current_round]
    
    # Randomly choose which group the observation comes from
    true_group = np.random.choice(['a', 'b'])
    if true_group == 'a':
        observation = np.random.normal(scenario["group_a"]["mean"], scenario["group_a"]["std"])
    else:
        observation = np.random.normal(scenario["group_b"]["mean"], scenario["group_b"]["std"])
    
    # Calculate true posterior probability
    true_prob = calculate_bayes_probability(
        observation,
        scenario["group_a"]["mean"], scenario["group_a"]["std"],
        scenario["group_b"]["mean"], scenario["group_b"]["std"]
    )
    
    st.session_state.round_data = {
        'scenario': scenario,
        'observation': observation,
        'true_probability': true_prob,
        'true_group': true_group
    }

# Current Round Display
if st.session_state.current_round < len(SCENARIOS) and st.session_state.round_data:
    round_data = st.session_state.round_data
    scenario = round_data['scenario']
    observation = round_data['observation']
    
    # Round Header
    st.markdown(f'''
        <div class="round-header">
            <div class="round-title">{scenario["title"]}</div>
            <div class="scenario-text">{scenario["description"]}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Context Information
    st.info(f"📋 **Medical Context:** {scenario['context']}")
    
    # Measurement Display
    st.markdown(f'''
        <div class="measurement-card">
            <div class="measurement-value">{observation:.1f} {scenario["unit"]}</div>
            <div class="measurement-label">{scenario["measurement_name"]}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Clue
    clue_text = scenario["clue_func"](observation)
    st.markdown(f'''
        <div class="clue-box">
            <div class="clue-text">💡 Clinical Observation: {clue_text}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Question
    st.markdown("### 🤔 Your Task:")
    st.markdown(f"**What's the probability that this patient has {scenario['group_a']['name'].lower()}?**")
    st.markdown("*Move the slider to indicate your best guess (0% = definitely no, 100% = definitely yes)*")
    
    # User Input
    if not st.session_state.show_result:
        user_guess = st.slider(
            "Your probability estimate:",
            min_value=0,
            max_value=100,
            value=50,
            step=1,
            format="%d%%"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Submit Diagnosis", key=f"submit_{st.session_state.current_round}"):
                st.session_state.user_guess = user_guess
                st.session_state.show_result = True
                st.experimental_rerun()
    
    # Show Results
    if st.session_state.show_result:
        true_prob_percent = round_data['true_probability'] * 100
        user_guess_percent = st.session_state.user_guess
        error = abs(true_prob_percent - user_guess_percent)
        
        # Scoring (generous scoring to encourage learning)
        if error <= 10:
            points = 1
            accuracy_msg = "🎯 Excellent! Very close!"
        elif error <= 20:
            points = 0.5
            accuracy_msg = "👍 Good estimate!"
        else:
            points = 0
            accuracy_msg = "📚 Keep learning!"
        
        st.session_state.score += points
        
        # Results display
        if points > 0:
            st.markdown(f'''
                <div class="result-correct">
                    <h4>{accuracy_msg}</h4>
                    <p><strong>Your guess:</strong> {user_guess_percent}%</p>
                    <p><strong>Actual probability:</strong> {true_prob_percent:.1f}%</p>
                    <p><strong>Difference:</strong> {error:.1f} percentage points</p>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="result-incorrect">
                    <h4>{accuracy_msg}</h4>
                    <p><strong>Your guess:</strong> {user_guess_percent}%</p>
                    <p><strong>Actual probability:</strong> {true_prob_percent:.1f}%</p>
                    <p><strong>Difference:</strong> {error:.1f} percentage points</p>
                </div>
            ''', unsafe_allow_html=True)
        
        # Show explanation button
        if not st.session_state.show_explanation:
            if st.button("📊 Show Bayesian Explanation", key=f"explain_{st.session_state.current_round}"):
                st.session_state.show_explanation = True
                st.experimental_rerun()
        
        # Bayesian Explanation
        if st.session_state.show_explanation:
            st.markdown("### 🧮 How Bayes' Theorem Calculated This:")
            
            # Show the distributions
            fig = create_distribution_plot(scenario, observation)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mathematical explanation
            likelihood_a = norm.pdf(observation, scenario["group_a"]["mean"], scenario["group_a"]["std"])
            likelihood_b = norm.pdf(observation, scenario["group_b"]["mean"], scenario["group_b"]["std"])
            
            st.markdown(f"""
            **Bayes' Theorem in Action:**
            
            1. **Prior beliefs:** We assumed 50% chance for each condition initially
            2. **Likelihood of observation:**
               - If {scenario["group_a"]["name"]}: {likelihood_a:.4f}
               - If {scenario["group_b"]["name"]}: {likelihood_b:.4f}
            3. **Posterior probability:** {true_prob_percent:.1f}% chance of {scenario["group_a"]["name"]}
            
            The formula: P(Condition|Test) = P(Test|Condition) × P(Condition) / P(Test)
            """)
        
        # Next button
        if st.session_state.current_round < len(SCENARIOS) - 1:
            if st.button("➡️ Next Patient", key=f"next_{st.session_state.current_round}"):
                st.session_state.current_round += 1
                st.session_state.round_data = None
                st.session_state.show_result = False
                st.session_state.show_explanation = False
                st.session_state.user_guess = None
                st.experimental_rerun()
        else:
            if st.button("🏁 See Final Results", key="final_results"):
                st.session_state.current_round += 1
                st.experimental_rerun()

# Welcome Screen for New Players
if st.session_state.current_round == 0 and st.session_state.round_data is None:
    st.markdown("""
    ### 🎯 Welcome to Bayes Detective Academy!
    
    You're training to become a master of probabilistic reasoning! In each round, you'll:
    
    1. 👀 **Observe** a medical measurement from a patient
    2. 🧠 **Think** about what this measurement tells you
    3. 🎯 **Estimate** the probability of a medical condition
    4. 📊 **Learn** how Bayes' Theorem calculated the exact answer
    
    **Your Goal:** Develop intuition for how evidence updates our beliefs!
    
    Ready to start your training?
    """)
    
    if st.button("🚀 Begin Training", key="start_game"):
        st.session_state.current_round = 0
        st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- Instructions for Deployment ---
st.markdown("---")
with st.expander("🚀 Deployment Instructions"):
    st.markdown("""
    ## How to Deploy This App:
    
    ### 1. Local Development:
    ```bash
    pip install streamlit numpy scipy plotly pandas
    streamlit run bayes_inference_game.py
    ```
    
    ### 2. Deploy to Streamlit Cloud:
    1. Create a GitHub repository
    2. Add this file as `app.py` or `streamlit_app.py`
    3. Create `requirements.txt`:
       ```
       streamlit
       numpy
       scipy
       plotly
       pandas
       ```
    4. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
    5. Connect your GitHub repo
    6. Deploy!
    
    ### 3. Alternative: Deploy to Heroku, Railway, or other platforms
    - Most Python hosting platforms support Streamlit apps
    - Just ensure the requirements.txt includes all dependencies
    """)