import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

# Import custom modules
from models.organ_twin import OrganDigitalTwin
from models.dqn_agent import DQNOrganOptimizer
from models.llm_explainer import OllamaDigitalTwinExplainer
from ui.sidebar import render_sidebar
from ui.tabs import render_tabs
from config import DEFAULT_NUTRIENTS

# Set page config
st.set_page_config(page_title="Digital Twin with Ollama", layout="wide")

st.title("🧬 AI-Powered Digital Twin Health System")
st.markdown("### **A Multi-Agent Intelligent Health Simulation Platform**")

# Initialize session state
def initialize_session_state():
    if "digital_twin" not in st.session_state:
        st.session_state.digital_twin = OrganDigitalTwin()
    if "dqn_agent" not in st.session_state:
        st.session_state.dqn_agent = DQNOrganOptimizer(state_size=23, action_size=8)
    if "ollama_explainer" not in st.session_state:
        st.session_state.ollama_explainer = OllamaDigitalTwinExplainer()
    if "meal_history" not in st.session_state:
        st.session_state.meal_history = []
    if "explanations" not in st.session_state:
        st.session_state.explanations = []
    if "last_reward" not in st.session_state:
        st.session_state.last_reward = 0
    if "training_loss_history" not in st.session_state:
        st.session_state.training_loss_history = []

# Initialize session state
initialize_session_state()

# Render sidebar
sidebar_data = render_sidebar(DEFAULT_NUTRIENTS)

# Process simulation if button was clicked
if sidebar_data.get("simulate_clicked", False):
    nutrients = sidebar_data["nutrients"]
    portion_size = sidebar_data["portion_size"]
    meal_name = sidebar_data["meal_name"]
    use_ollama = sidebar_data["use_ollama"]
    show_explanations = sidebar_data["show_explanations"]
    auto_apply_ai = sidebar_data["auto_apply_ai"]
    
    # Get current state
    state = st.session_state.dqn_agent.get_state(
        st.session_state.digital_twin, nutrients
    )
    
    # Select action
    action_idx = st.session_state.dqn_agent.select_action(state)
    
    # Get modified nutrients if auto-apply is enabled
    if auto_apply_ai and action_idx != 7:  # Don't modify if "maintain pattern"
        nutrients = st.session_state.dqn_agent.apply_action_to_nutrients(action_idx, nutrients)
    
    # Simulate impact with the (potentially modified) nutrients
    impacts, reward = st.session_state.digital_twin.simulate_meal_impact(
        nutrients, portion_size, meal_name
    )
    
    st.session_state.last_reward = reward
    
    # Get next state for RL
    next_state = st.session_state.dqn_agent.get_state(
        st.session_state.digital_twin, nutrients
    )
    
    # Store transition for RL training
    done = False  # Episode never ends in this simulation
    st.session_state.dqn_agent.store_transition(
        state.detach(),
        action_idx,
        reward,
        next_state.detach(),
        done
    )
    
    # Train agent if enough data
    if len(st.session_state.dqn_agent.memory) >= st.session_state.dqn_agent.batch_size:
        loss = st.session_state.dqn_agent.replay()
        if loss:
            st.session_state.training_loss_history.append(loss)
    
    # Get recommendation
    recommendation = st.session_state.dqn_agent.get_recommendation(action_idx, nutrients)
    
    # Get LLM explanations if enabled
    if use_ollama and show_explanations:
        with st.spinner(" Getting LLM explanations..."):
            try:
                # Get explanation for most impacted organ
                most_impacted = max(impacts.items(), key=lambda x: abs(x[1]["impact"]))
                organ_name, impact_data = most_impacted
                
                explanation = st.session_state.ollama_explainer.explain_organ_response(
                    organ_name, impact_data, nutrients
                )
                
                st.session_state.explanations.append({
                    "organ": organ_name,
                    "explanation": explanation,
                    "timestamp": datetime.now()
                })
                
                # Get agent decision explanation
                agent_explanation = st.session_state.ollama_explainer.explain_agent_decision(
                    st.session_state.dqn_agent.actions[action_idx],
                    st.session_state.digital_twin.get_organ_states(),
                    nutrients,
                    action_idx,
                    reward
                )
                
                st.session_state.explanations.append({
                    "type": "agent_decision",
                    "explanation": agent_explanation,
                    "timestamp": datetime.now(),
                    "reward": reward
                })
            except Exception as e:
                st.sidebar.error(f"LLM Error: {str(e)[:50]}...")
    
    # Record meal
    health_change = st.session_state.digital_twin.get_overall_health() - st.session_state.digital_twin.get_overall_health_previous()
    st.session_state.meal_history.append({
        "meal": meal_name,
        "nutrients": nutrients.copy(),
        "portion": portion_size,
        "overall_impact": np.mean([impacts[o]["impact"] for o in impacts]),
        "recommendation": recommendation,
        "action": st.session_state.dqn_agent.actions[action_idx],
        "reward": reward,
        "health_change": health_change,
        "timestamp": datetime.now()
    })
    
    st.sidebar.success(f" {meal_name} simulated! Reward: {reward:.3f}")

# Process training if button was clicked
if sidebar_data.get("train_clicked", False):
    if st.session_state.dqn_agent.memory:
        loss = st.session_state.dqn_agent.replay()
        st.session_state.training_loss_history.append(loss)
        st.sidebar.success(f"Agent trained! Loss: {loss:.4f}")
    else:
        st.sidebar.warning("Need more meal data to train agent")

# Process reset if button was clicked
if sidebar_data.get("reset_clicked", False):
    initialize_session_state()
    st.sidebar.success("Digital Twin reset!")
    st.rerun()

# Render main tabs
render_tabs()

# Footer
st.markdown("---")
st.caption("""
**Digital Twin System v2.0** • 10 Organ Simulation • Full DQN RL • Ollama LLM Explanations •
[Reset] • [Train Agent] • [Report Bug]
""")

# Auto-refresh button
if st.button("🔄 Refresh View", key="refresh"):
    st.rerun()