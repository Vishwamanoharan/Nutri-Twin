import numpy as np
import random
from collections import deque
from datetime import datetime, timedelta
import plotly.graph_objects as go
from config import ORGAN_BASELINES, ORGAN_DEFINITIONS, ORGAN_WEIGHTS

class OrganDigitalTwin:
    """Real-time digital twin of 10 vital organs"""
    
    def __init__(self):
        # Initialize organs with realistic physiology
        self.organs = {}
        self._previous_overall_health = 0.5
        self._initialize_organs()
        
        # Simulation state
        self.history = {organ: deque(maxlen=100) for organ in self.organs}
        self.current_time = datetime.now()
        self.nutrient_history = []
        self.intervention_history = []
    
    def _initialize_organs(self):
        """Initialize all organs with their properties"""
        for organ_name, props in ORGAN_DEFINITIONS.items():
            self.organs[organ_name] = {
                "health": 0.7 + (random.random() * 0.2),  # Start with 70-90% health
                **props
            }
            # Initialize metrics if not already defined
            if "metrics" not in self.organs[organ_name]:
                self.organs[organ_name]["metrics"] = ORGAN_BASELINES.get(organ_name, {}).copy()
    
    def simulate_meal_impact(self, nutrients, portion_g=100, meal_name="Meal"):
        """Simulate the impact of a meal on all organs"""
        
        scale = portion_g / 100
        impacts = {}
        organ_states_before = self.get_organ_states()
        self._previous_overall_health = self.get_overall_health()
        
        for organ_name, organ_data in self.organs.items():
            # Calculate organ-specific impact
            impact = self._calculate_organ_impact(organ_name, nutrients, scale)
            
            # Apply impact
            new_health = organ_data["health"] + impact
            
            # Apply bounds and recovery
            new_health = np.clip(new_health, 0.1, 1.0)
            new_health = min(1.0, new_health + 0.001)  # Natural recovery
            
            # Update organ
            organ_data["health"] = new_health
            
            # Update metrics
            self._update_organ_metrics(organ_name, new_health)
            
            # Update color
            self._update_organ_color(organ_name, new_health)
            
            # Record impact
            impacts[organ_name] = {
                "impact": impact,
                "new_health": new_health,
                "stress_level": abs(impact) * 100
            }
            
            # Record history
            self.history[organ_name].append({
                "timestamp": self.current_time,
                "health": new_health,
                "impact": impact,
                "meal": meal_name,
                "nutrients": nutrients.copy()
            })
        
        # Calculate reward for RL agent
        organ_states_after = self.get_organ_states()
        reward = self._calculate_reward(organ_states_before, organ_states_after)
        
        # Record nutrient history
        self.nutrient_history.append({
            "timestamp": self.current_time,
            "meal": meal_name,
            "nutrients": nutrients.copy(),
            "portion": portion_g,
            "overall_impact": np.mean([impacts[o]["impact"] for o in impacts]),
            "organ_states": organ_states_before,
            "reward": reward,
            "overall_health_before": self._previous_overall_health,
            "overall_health_after": self.get_overall_health()
        })
        
        self.current_time += timedelta(hours=1)  # Advance simulation time
        
        return impacts, reward
    
    def _calculate_organ_impact(self, organ_name, nutrients, scale):
        """Calculate organ-specific impact using sensitivity coefficients"""
        organ = self.organs[organ_name]
        impact = 0
        
        for nutrient, sensitivity in organ["sensitivity"].items():
            if nutrient in nutrients:
                nutrient_value = nutrients[nutrient]
                
                # Normalize nutrient values
                if nutrient == "sodium":
                    norm_value = nutrient_value / 2300  # Daily limit
                elif nutrient == "sugar":
                    norm_value = nutrient_value / 50    # Daily limit
                elif nutrient == "fiber":
                    norm_value = nutrient_value / 25    # Daily target
                elif nutrient == "protein":
                    norm_value = nutrient_value / 100   # Typical max
                elif nutrient == "calories":
                    norm_value = nutrient_value / 2000  # Daily average
                elif nutrient == "fat":
                    norm_value = nutrient_value / 100   # Generic normalization
                else:
                    norm_value = nutrient_value / 100   # Generic normalization
                
                # Calculate impact (negative sensitivity means beneficial)
                impact += sensitivity * norm_value * scale
        
        # Add some randomness for realism
        impact += random.uniform(-0.02, 0.02)
        return impact
    
    def _update_organ_metrics(self, organ_name, new_health):
        """Update organ metrics based on health"""
        organ = self.organs[organ_name]
        
        # Update metrics proportionally to health
        health_factor = 0.6 + (new_health * 0.4)  # Maps 0.1-1.0 to 0.64-1.0
        
        for metric in organ["metrics"]:
            # Use baseline values if available
            base_value = ORGAN_BASELINES.get(organ_name, {}).get(metric, 100)
            current_value = organ["metrics"][metric]
            
            # Move toward target value
            target_value = base_value * health_factor
            adjustment = (target_value - current_value) * 0.1
            
            # Apply bounds based on metric type
            if "pressure" in metric or "creatinine" in metric or "inflammation" in metric:
                organ["metrics"][metric] = np.clip(current_value + adjustment, 
                                                  base_value * 0.5, base_value * 1.5)
            else:
                organ["metrics"][metric] = np.clip(current_value + adjustment, 
                                                  base_value * 0.3, base_value * 1.2)
    
    def _calculate_reward(self, states_before, states_after):
        """Calculate reward for RL agent"""
        # Reward for overall health improvement
        health_before = sum(states_before.values()) / len(states_before)
        health_after = sum(states_after.values()) / len(states_after)
        health_reward = (health_after - health_before) * 50  # Increased from 10 to 50
        
        # Penalty for organs in critical condition
        critical_organs = sum(1 for health in states_after.values() if health < 0.6)
        critical_penalty = -critical_organs * 0.5
        
        # Reward for balanced health (low variance)
        health_variance = np.var(list(states_after.values()))
        balance_reward = -health_variance * 2
        
        # Reward for improving worst organ
        worst_organ_before = min(states_before.values()) if states_before else 0.5
        worst_organ_after = min(states_after.values()) if states_after else 0.5
        worst_organ_reward = (worst_organ_after - worst_organ_before) * 20  # Increased from 5 to 20
        
        total_reward = health_reward + critical_penalty + balance_reward + worst_organ_reward
        return total_reward
    
    def _update_organ_color(self, organ_name, health):
        """Update organ color based on health status"""
        organ = self.organs[organ_name]
        
        if health >= 0.8:
            # Green: Healthy
            r = int(255 * (1 - (health - 0.8) * 5))
            g = 255
            b = r
            organ["color"] = f"rgb({r}, {g}, {b})"
        elif health >= 0.6:
            # Yellow: Moderate
            intensity = int(255 * (health - 0.6) * 5)
            r = 255
            g = 255 - intensity // 2
            b = 0
            organ["color"] = f"rgb({r}, {g}, {b})"
        else:
            # Red: At risk
            intensity = int(255 * (0.6 - health) * 5)
            r = 255
            g = max(50, 255 - intensity)
            b = max(50, 255 - intensity)
            organ["color"] = f"rgb({r}, {g}, {b})"
    
    def apply_intervention(self, intervention_type, intensity=1.0):
        """Apply a health intervention"""
        impacts = {}
        
        for organ_name in self.organs:
            organ = self.organs[organ_name]
            base_health = organ["health"]
            
            # Calculate intervention impact
            if intervention_type == "exercise":
                impact = 0.02 * intensity if organ_name in ["heart", "lungs", "muscles"] else 0.01 * intensity
            elif intervention_type == "hydration":
                impact = 0.015 * intensity if organ_name in ["kidneys", "brain", "skin"] else 0.008 * intensity
            elif intervention_type == "sleep":
                impact = 0.025 * intensity if organ_name in ["brain", "immune"] else 0.01 * intensity
            elif intervention_type == "stress_reduction":
                impact = 0.03 * intensity if organ_name in ["brain", "heart", "gut"] else 0.015 * intensity
            else:
                impact = 0.01 * intensity
            
            # Apply impact
            new_health = np.clip(base_health + impact, 0.1, 1.0)
            organ["health"] = new_health
            
            # Update metrics and color
            self._update_organ_metrics(organ_name, new_health)
            self._update_organ_color(organ_name, new_health)
            
            impacts[organ_name] = {
                "impact": impact,
                "new_health": new_health
            }
        
        # Record intervention
        self.intervention_history.append({
            "timestamp": self.current_time,
            "intervention": intervention_type,
            "intensity": intensity,
            "impacts": impacts
        })
        
        return impacts
    
    def get_organ_states(self):
        """Get current organ states"""
        return {name: data["health"] for name, data in self.organs.items()}
    
    def get_overall_health(self):
        """Calculate overall health score"""
        total = 0
        for organ_name, weight in ORGAN_WEIGHTS.items():
            if organ_name in self.organs:
                total += self.organs[organ_name]["health"] * weight
        
        return total
    
    def get_overall_health_previous(self):
        """Get previous overall health for delta calculation"""
        return self._previous_overall_health
    
    def create_3d_visualization(self):
        """Create 3D visualization of organs"""
        fig = go.Figure()
        
        # Add organs
        for organ_name, organ_data in self.organs.items():
            x, y, z = organ_data["position"]
            size = organ_data["size"] * 35
            
            fig.add_trace(go.Scatter3d(
                x=[x],
                y=[y],
                z=[z],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color=organ_data["color"],
                    opacity=0.9,
                    symbol='circle',
                    line=dict(color='white', width=2)
                ),
                text=[organ_name.title()],
                textposition="bottom center",
                name=organ_name.title(),
                hoverinfo='text',
                hovertext=f"""
                <b>{organ_name.title()}</b><br>
                Health: {organ_data['health']:.1%}<br>
                System: {organ_data['system']}<br>
                Risk Level: {'Low' if organ_data['health'] >= 0.8 else 'Medium' if organ_data['health'] >= 0.6 else 'High'}
                """
            ))
        
        # Add connections
        connections = [
            ("heart", "lungs"), ("heart", "brain"), ("liver", "pancreas"),
            ("gut", "liver"), ("kidneys", "heart")
        ]
        
        for org1, org2 in connections:
            if org1 in self.organs and org2 in self.organs:
                x1, y1, z1 = self.organs[org1]["position"]
                x2, y2, z2 = self.organs[org2]["position"]
                
                fig.add_trace(go.Scatter3d(
                    x=[x1, x2, None],
                    y=[y1, y2, None],
                    z=[z1, z2, None],
                    mode='lines',
                    line=dict(color='rgba(100, 100, 100, 0.3)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Layout
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False, range=[-1, 1]),
                yaxis=dict(visible=False, range=[-1, 1]),
                zaxis=dict(visible=False, range=[0, 1.5]),
                bgcolor='rgba(10, 10, 20, 1)',
                camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))
            ),
            paper_bgcolor='rgba(10, 10, 20, 1)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=500
        )
        
        return fig