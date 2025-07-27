import streamlit as st
import numpy as np
import time
import random
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="🕵️ Truth Detective: The Ethics of Inference", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: 'Inter', sans-serif;
        }
        
        .main-container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .game-title {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .game-subtitle {
            font-size: 1.3rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .level-header {
            background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            border-left: 5px solid #1e3c72;
        }
        
        .level-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .scene-text {
            font-size: 1.2rem;
            color: #4b5563;
            line-height: 1.6;
        }
        
        .confidence-bar {
            background: #e5e7eb;
            border-radius: 10px;
            height: 30px;
            margin: 0.5rem 0;
            overflow: hidden;
            position: relative;
        }
        
        .confidence-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        
        .evidence-card {
            background: linear-gradient(135deg, #fef3c7, #fed7aa);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 2px solid #f59e0b;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .ethical-popup {
            background: linear-gradient(135deg, #fee2e2, #fecaca);
            padding: 1.5rem;
            border-radius: 15px;
            border: 3px solid #ef4444;
            margin: 1rem 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        
        .timer {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 1rem 0;
        }
        
        .scoreboard {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 1.5rem;
            border-radius: 15px;
            border: 3px solid #10b981;
            margin: 1rem 0;
        }
        
        .score-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #065f46;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .score-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }
        
        .score-item {
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            border: 2px solid #10b981;
        }
        
        .score-value {
            font-size: 2rem;
            font-weight: 700;
            color: #065f46;
        }
        
        .score-label {
            font-size: 0.9rem;
            color: #6b7280;
            font-weight: 500;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4);
        }
        
        .suspect-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .suspect-card {
            background: white;
            border: 3px solid #e5e7eb;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .suspect-card:hover {
            border-color: #1e3c72;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .suspect-avatar {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .suspect-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .evidence-area {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            padding: 1.5rem;
            border-radius: 15px;
            border: 2px solid #e2e8f0;
            margin: 1rem 0;
            min-height: 200px;
        }
        
        .evidence-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 1rem;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- Game Data ---
LEVELS = [
    {
        "name": "The Cookie Jar Mystery",
        "scene": "Cozy kitchen with a jar on the counter, crumbs scattered, 3 chefs smiling suspiciously",
        "intro": "A cookie jar is empty! Which chef took the cookies? Collect evidence and decide carefully.",
        "suspects": [
            {"name": "Chef A", "avatar": "👨‍🍳", "color": "#ef4444", "evidence": ["chocolate chip", "vanilla", "mixed"]},
            {"name": "Chef B", "avatar": "👩‍🍳", "color": "#10b981", "evidence": ["raisin", "oatmeal", "mixed"]},
            {"name": "Chef C", "avatar": "🧑‍🍳", "color": "#3b82f6", "evidence": ["sugar", "butter", "mixed"]}
        ],
        "evidence_types": ["chocolate chip", "raisin", "vanilla", "oatmeal", "sugar", "butter", "mixed"],
        "culprit": None,  # Will be set randomly
        "ethical_choices": []
    },
    {
        "name": "The Park Theft",
        "scene": "Park bench, 3 suspects in different colored jackets",
        "intro": "A wallet has been stolen! Evidence can be misleading—watch out for bias.",
        "suspects": [
            {"name": "Alex", "avatar": "👤", "color": "#ef4444", "evidence": ["red jacket", "tall person", "running"]},
            {"name": "Jamie", "avatar": "👤", "color": "#10b981", "evidence": ["blue jacket", "medium height", "walking"]},
            {"name": "Casey", "avatar": "👤", "color": "#3b82f6", "evidence": ["green jacket", "short person", "standing"]}
        ],
        "evidence_types": ["red jacket", "blue jacket", "green jacket", "tall person", "medium height", "short person", "running", "walking", "standing"],
        "culprit": None,
        "ethical_choices": [
            {
                "trigger": 3,  # After 3 evidence collections
                "question": "Police claim Casey has a past record. This may be bias. Use this info?",
                "options": [
                    {"text": "Use It (Fast but Biased)", "integrity_penalty": -20, "confidence_boost": 0.4},
                    {"text": "Ignore (Ethical)", "integrity_penalty": 0, "confidence_boost": 0}
                ]
            }
        ]
    },
    {
        "name": "Social Media Scandal",
        "scene": "Newsroom with flashing 'BREAKING NEWS'",
        "intro": "A rumor about a politician is trending. Is it true or false?",
        "suspects": [
            {"name": "True", "avatar": "✅", "color": "#10b981", "evidence": ["official statement", "verified source", "fact check"]},
            {"name": "False", "avatar": "❌", "color": "#ef4444", "evidence": ["debunked", "fake news", "retraction"]}
        ],
        "evidence_types": ["tweets", "local news", "official statement", "verified source", "fact check", "debunked", "fake news", "retraction"],
        "culprit": None,
        "ethical_choices": [
            {
                "trigger": 2,
                "question": "Do you publish your story now, based only on trending tweets?",
                "options": [
                    {"text": "Publish Now (Fast but High Risk)", "integrity_penalty": -30, "speed_bonus": 20},
                    {"text": "Wait (Delays but Ensures Credibility)", "integrity_penalty": 0, "speed_bonus": 0}
                ]
            }
        ]
    },
    {
        "name": "The Lab Experiment",
        "scene": "Science lab, test tubes, patients waiting",
        "intro": "You are testing a new medicine. Does it work?",
        "suspects": [
            {"name": "Medicine Works", "avatar": "💊", "color": "#10b981", "evidence": ["young patients improve", "older patients improve", "mixed results"]},
            {"name": "Doesn't Work", "avatar": "🚫", "color": "#ef4444", "evidence": ["young patients worsen", "older patients worsen", "no effect"]}
        ],
        "evidence_types": ["young patients improve", "young patients worsen", "older patients improve", "older patients worsen", "mixed results", "no effect"],
        "culprit": None,
        "ethical_choices": [
            {
                "trigger": 2,
                "question": "Results are only from young patients. Publish results now?",
                "options": [
                    {"text": "Publish Early (Unethical)", "integrity_penalty": -25, "speed_bonus": 15},
                    {"text": "Test More Groups (Slower but Fair)", "integrity_penalty": 0, "speed_bonus": 0}
                ]
            }
        ]
    },
    {
        "name": "The City Fire",
        "scene": "City skyline with buildings, smoke rising",
        "intro": "Which building started the fire? Act fast to save others.",
        "suspects": [
            {"name": "Building A", "avatar": "🏢", "color": "#ef4444", "evidence": ["smoke from A", "witness saw sparks A", "alarm A"]},
            {"name": "Building B", "avatar": "🏢", "color": "#10b981", "evidence": ["smoke from B", "witness saw sparks B", "alarm B"]},
            {"name": "Building C", "avatar": "🏢", "color": "#3b82f6", "evidence": ["smoke from C", "witness saw sparks C", "alarm C"]}
        ],
        "evidence_types": ["smoke from A", "smoke from B", "smoke from C", "witness saw sparks A", "witness saw sparks B", "witness saw sparks C", "alarm A", "alarm B", "alarm C"],
        "culprit": None,
        "ethical_choices": [
            {
                "trigger": 2,
                "question": "Evacuate Building A now (low confidence) or gather more evidence?",
                "options": [
                    {"text": "Evacuate Now (Fast)", "integrity_penalty": -15, "speed_bonus": 25},
                    {"text": "Wait for More Info", "integrity_penalty": 0, "speed_bonus": 0}
                ]
            }
        ],
        "timer": 60  # 60 seconds for urgency
    }
]

# --- Helper Functions ---
def create_confidence_bar(name, percentage, color):
    return f"""
    <div style="margin: 1rem 0;">
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #1f2937;">{name}</div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="background: {color}; width: {percentage}%;">
                {percentage:.0f}%
            </div>
        </div>
    </div>
    """

def create_evidence_card(evidence):
    return f"""
    <div class="evidence-card">
        <div style="font-weight: 600; color: #92400e;">🔍 Found: {evidence}</div>
    </div>
    """

def create_ethical_popup(question, options):
    return f"""
    <div class="ethical-popup">
        <h3 style="color: #dc2626; margin-bottom: 1rem;">⚖️ Ethical Decision Required</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">{question}</p>
    </div>
    """

def calculate_confidence(evidence, suspects):
    """Calculate confidence percentages based on collected evidence"""
    total_evidence = len(evidence)
    if total_evidence == 0:
        return [33.33, 33.33, 33.34] if len(suspects) == 3 else [50, 50]
    
    scores = [0] * len(suspects)
    
    for ev in evidence:
        for i, suspect in enumerate(suspects):
            if ev in suspect["evidence"]:
                scores[i] += 1
    
    total_score = sum(scores)
    if total_score == 0:
        return [100/len(suspects)] * len(suspects)
    
    return [round((score / total_score) * 100, 1) for score in scores]

# --- Session State Initialization ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'
    st.session_state.current_level = 0
    st.session_state.current_scene = 'intro'
    st.session_state.collected_evidence = []
    st.session_state.confidence = []
    st.session_state.scores = {'accuracy': 0, 'speed': 0, 'integrity': 100}
    st.session_state.level_scores = []
    st.session_state.ethical_choice_made = False
    st.session_state.start_time = None
    st.session_state.timer_start = None

# --- Main Game Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Main Menu
if st.session_state.game_state == 'menu':
    st.markdown('<h1 class="game-title">🕵️ Truth Detective: The Ethics of Inference</h1>', unsafe_allow_html=True)
    st.markdown('<p class="game-subtitle">Master the art of ethical decision-making through interactive investigations!</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎮 Play Game", key="play_button"):
            st.session_state.game_state = 'playing'
            st.session_state.current_level = 0
            st.session_state.current_scene = 'intro'
            st.experimental_rerun()
        
        if st.button("📖 How to Play", key="how_to_play"):
            st.session_state.game_state = 'instructions'
            st.experimental_rerun()

# Instructions
elif st.session_state.game_state == 'instructions':
    st.markdown('<h1 class="game-title">📖 How to Play</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Your Mission
    You are a detective solving cases while learning about ethical inference in probability!
    
    ### 🎮 Game Mechanics
    1. **Evidence Collection**: Click to gather clues and update your confidence
    2. **Ethical Decisions**: Face moral dilemmas that test your integrity
    3. **Final Decision**: Choose your suspect based on the evidence
    4. **Scoring**: Earn points for accuracy, speed, and ethical choices
    
    ### 📊 Scoring System
    - **Accuracy**: Correctly identifying the culprit
    - **Speed**: Making decisions efficiently (fewer evidence collections)
    - **Integrity**: Making ethical choices throughout the investigation
    
    ### 🎪 Levels
    1. **Cookie Jar Mystery**: Basic evidence collection
    2. **Park Theft**: Introduction to bias
    3. **Social Media Scandal**: Credibility vs speed
    4. **Lab Experiment**: Sampling bias
    5. **City Fire**: Urgency vs accuracy
    
    Ready to become a Truth Detective?
    """)
    
    if st.button("🚀 Start Investigation", key="start_investigation"):
        st.session_state.game_state = 'playing'
        st.session_state.current_level = 0
        st.session_state.current_scene = 'intro'
        st.experimental_rerun()

# Main Game
elif st.session_state.game_state == 'playing':
    if st.session_state.current_level >= len(LEVELS):
        # Game Complete
        final_accuracy = (st.session_state.scores['accuracy'] / len(LEVELS)) * 100
        final_speed = st.session_state.scores['speed']
        final_integrity = st.session_state.scores['integrity']
        
        st.markdown('<h1 class="game-title">🎉 Investigation Complete!</h1>', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="scoreboard">
            <div class="score-title">Final Detective Report</div>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-value">{final_accuracy:.0f}%</div>
                    <div class="score-label">Accuracy</div>
                </div>
                <div class="score-item">
                    <div class="score-value">{final_speed}</div>
                    <div class="score-label">Speed Bonus</div>
                </div>
                <div class="score-item">
                    <div class="score-value">{final_integrity}</div>
                    <div class="score-label">Integrity</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if final_accuracy >= 80 and final_integrity >= 80:
            st.balloons()
            st.success("🏆 Outstanding! You're a master of ethical inference!")
        elif final_accuracy >= 60 and final_integrity >= 60:
            st.info("👍 Good work! You're developing strong detective skills!")
        else:
            st.warning("📚 Keep practicing! Ethical inference takes time to master.")
        
        if st.button("🔄 Play Again", key="play_again_final"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    level = LEVELS[st.session_state.current_level]
    
    # Initialize level if needed
    if level["culprit"] is None:
        level["culprit"] = random.randint(0, len(level["suspects"]) - 1)
    
    # Level Header
    st.markdown(f'''
    <div class="level-header">
        <div class="level-title">Level {st.session_state.current_level + 1}: {level["name"]}</div>
        <div class="scene-text">{level["scene"]}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Intro Scene
    if st.session_state.current_scene == 'intro':
        st.markdown(f"### 🎭 Scene Setup")
        st.info(f"**{level['intro']}**")
        
        # Show suspects
        st.markdown("### 👥 Suspects")
        suspect_cols = st.columns(len(level["suspects"]))
        for i, suspect in enumerate(level["suspects"]):
            with suspect_cols[i]:
                st.markdown(f'''
                <div class="suspect-card">
                    <div class="suspect-avatar">{suspect["avatar"]}</div>
                    <div class="suspect-name">{suspect["name"]}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        if st.button("🔍 Start Collecting Evidence", key=f"start_evidence_{st.session_state.current_level}"):
            st.session_state.current_scene = 'evidence'
            st.session_state.collected_evidence = []
            st.session_state.confidence = [100/len(level["suspects"])] * len(level["suspects"])
            st.session_state.ethical_choice_made = False
            st.session_state.start_time = time.time()
            if level.get("timer"):
                st.session_state.timer_start = time.time()
            st.experimental_rerun()
    
    # Evidence Collection Scene
    elif st.session_state.current_scene == 'evidence':
        # Timer for urgent scenarios
        if level.get("timer") and st.session_state.timer_start:
            elapsed = time.time() - st.session_state.timer_start
            remaining = max(0, level["timer"] - elapsed)
            
            if remaining <= 0:
                st.error("⏰ Time's up! You must make a decision now!")
                st.session_state.current_scene = 'decision'
                st.experimental_rerun()
            else:
                st.markdown(f'''
                <div class="timer">
                    ⏰ Time Remaining: {int(remaining)} seconds
                </div>
                ''', unsafe_allow_html=True)
        
        # Evidence Area
        st.markdown("### 🔍 Evidence Collection")
        
        evidence_cols = st.columns([1, 2, 1])
        
        with evidence_cols[0]:
            st.markdown("### 📊 Confidence Levels")
            for i, suspect in enumerate(level["suspects"]):
                st.markdown(create_confidence_bar(suspect["name"], st.session_state.confidence[i], suspect["color"]), unsafe_allow_html=True)
        
        with evidence_cols[1]:
            st.markdown("### 🕵️ Collected Evidence")
            evidence_area = st.container()
            
            if st.session_state.collected_evidence:
                for evidence in st.session_state.collected_evidence:
                    evidence_area.markdown(create_evidence_card(evidence), unsafe_allow_html=True)
            else:
                evidence_area.info("No evidence collected yet. Click 'Collect Evidence' to start!")
            
            if st.button("🔍 Collect Evidence", key=f"collect_evidence_{len(st.session_state.collected_evidence)}"):
                # Generate new evidence
                new_evidence = random.choice(level["evidence_types"])
                st.session_state.collected_evidence.append(new_evidence)
                
                # Update confidence
                st.session_state.confidence = calculate_confidence(st.session_state.collected_evidence, level["suspects"])
                
                # Check for ethical choices
                if not st.session_state.ethical_choice_made and level["ethical_choices"]:
                    for choice in level["ethical_choices"]:
                        if len(st.session_state.collected_evidence) == choice["trigger"]:
                            st.session_state.current_scene = 'ethical_choice'
                            st.session_state.current_ethical_choice = choice
                            st.experimental_rerun()
                
                st.experimental_rerun()
        
        with evidence_cols[2]:
            st.markdown("### 🎯 Actions")
            if st.button("🤔 Make Decision", key=f"make_decision_{st.session_state.current_level}"):
                st.session_state.current_scene = 'decision'
                st.experimental_rerun()
    
    # Ethical Choice Scene
    elif st.session_state.current_scene == 'ethical_choice':
        choice = st.session_state.current_ethical_choice
        
        st.markdown(create_ethical_popup(choice["question"], choice["options"]), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(choice["options"][0]["text"], key=f"ethical_choice_1_{st.session_state.current_level}"):
                st.session_state.scores["integrity"] += choice["options"][0]["integrity_penalty"]
                st.session_state.scores["speed"] += choice["options"][0].get("speed_bonus", 0)
                st.session_state.ethical_choice_made = True
                st.session_state.current_scene = 'evidence'
                st.experimental_rerun()
        
        with col2:
            if st.button(choice["options"][1]["text"], key=f"ethical_choice_2_{st.session_state.current_level}"):
                st.session_state.scores["integrity"] += choice["options"][1]["integrity_penalty"]
                st.session_state.scores["speed"] += choice["options"][1].get("speed_bonus", 0)
                st.session_state.ethical_choice_made = True
                st.session_state.current_scene = 'evidence'
                st.experimental_rerun()
    
    # Decision Scene
    elif st.session_state.current_scene == 'decision':
        st.markdown("### 🎯 Final Decision")
        st.info("**Do you have enough evidence? Who is the culprit?**")
        
        # Show final confidence levels
        st.markdown("### 📊 Final Confidence Levels")
        for i, suspect in enumerate(level["suspects"]):
            st.markdown(create_confidence_bar(suspect["name"], st.session_state.confidence[i], suspect["color"]), unsafe_allow_html=True)
        
        # Decision buttons
        st.markdown("### 🤔 Your Verdict")
        suspect_cols = st.columns(len(level["suspects"]))
        for i, suspect in enumerate(level["suspects"]):
            with suspect_cols[i]:
                if st.button(f"🎯 {suspect['name']}", key=f"decision_{i}_{st.session_state.current_level}"):
                    st.session_state.current_scene = 'outcome'
                    st.session_state.user_decision = i
                    st.experimental_rerun()
    
    # Outcome Scene
    elif st.session_state.current_scene == 'outcome':
        correct = st.session_state.user_decision == level["culprit"]
        
        if correct:
            st.success(f"🎉 Correct! {level['suspects'][level['culprit']]['name']} was the culprit!")
            st.session_state.scores["accuracy"] += 1
        else:
            st.error(f"❌ Wrong! {level['suspects'][level['culprit']]['name']} was the actual culprit.")
        
        # Calculate speed bonus
        if st.session_state.start_time:
            time_taken = time.time() - st.session_state.start_time
            evidence_count = len(st.session_state.collected_evidence)
            speed_bonus = max(0, 10 - evidence_count)  # Bonus for fewer evidence collections
            st.session_state.scores["speed"] += speed_bonus
        
        # Show level scoreboard
        st.markdown(f'''
        <div class="scoreboard">
            <div class="score-title">Level {st.session_state.current_level + 1} Results</div>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-value">{'✅' if correct else '❌'}</div>
                    <div class="score-label">Accuracy</div>
                </div>
                <div class="score-item">
                    <div class="score-value">{len(st.session_state.collected_evidence)}</div>
                    <div class="score-label">Evidence Used</div>
                </div>
                <div class="score-item">
                    <div class="score-value">{st.session_state.scores['integrity']}</div>
                    <div class="score-label">Integrity</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Learning tip
        if level["name"] == "The Cookie Jar Mystery":
            st.info("💡 **Learning Tip:** Collecting more evidence increases your confidence in your decision!")
        elif level["name"] == "The Park Theft":
            st.info("💡 **Learning Tip:** Be careful of biased information that might mislead your investigation!")
        elif level["name"] == "Social Media Scandal":
            st.info("💡 **Learning Tip:** Credible sources are more reliable than fast, unverified information!")
        elif level["name"] == "The Lab Experiment":
            st.info("💡 **Learning Tip:** Representative sampling leads to fairer and more accurate conclusions!")
        elif level["name"] == "The City Fire":
            st.info("💡 **Learning Tip:** Sometimes you must balance speed with accuracy in urgent situations!")
        
        if st.button("➡️ Next Level", key=f"next_level_{st.session_state.current_level}"):
            st.session_state.current_level += 1
            st.session_state.current_scene = 'intro'
            st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)