import requests
import json
from config import ORGAN_BASELINES

class OllamaDigitalTwinExplainer:
    """Ollama-powered LLM that explains digital twin responses"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "llama3"  # or "mistral", "gemma", etc.
        
    def explain_organ_response(self, organ_name, impact_data, nutrients):
        """Get LLM explanation for organ response"""
        
        prompt = f"""
        You are Dr. AI, a clinical nutritionist explaining organ responses to meals.
        
        ORGAN: {organ_name}
        NUTRIENT INTAKE: {json.dumps(nutrients, indent=2)}
        HEALTH IMPACT: {impact_data['impact']:.3f} (Positive = beneficial, Negative = harmful)
        NEW HEALTH SCORE: {impact_data['new_health']:.1%}
        
        Explain in 3 parts:
        1. WHY this organ responded this way (biological mechanism)
        2. WHAT specific nutrients caused this (cite exact numbers)
        3. PRACTICAL advice for next meal (specific foods to add/avoid)
        
        Keep it concise, medical but understandable, and actionable.
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 300
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return self._fallback_explanation(organ_name, impact_data, nutrients)
                
        except:
            return self._fallback_explanation(organ_name, impact_data, nutrients)
    
    def explain_agent_decision(self, agent_action, organ_states, nutrients, action_idx, reward=None):
        """Explain why the DQN agent chose a specific action"""
        
        prompt = f"""
        Explain why an AI nutrition agent recommended: "{agent_action}"
        
        CURRENT ORGAN HEALTH:
        {json.dumps(organ_states, indent=2)}
        
        CURRENT NUTRIENT INTAKE:
        {json.dumps(nutrients, indent=2)}
        
        {'REWARD FROM LAST ACTION: ' + str(reward) if reward else ''}
        
        As a medical AI, explain:
        1. Which organs are most at risk and why
        2. How this recommendation addresses those risks
        3. The expected physiological benefits
        4. Specific foods that would implement this recommendation
        
        Be scientific but practical. Mention 2-3 research-backed mechanisms.
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 350}
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return self._fallback_agent_explanation(agent_action, action_idx)
        except:
            return self._fallback_agent_explanation(agent_action, action_idx)
    
    def _fallback_explanation(self, organ_name, impact_data, nutrients):
        """Fallback explanation if Ollama is unavailable"""
        explanations = {
            "heart": f" Heart: Sodium ({nutrients.get('sodium',0)}mg) increases blood pressure. Fiber ({nutrients.get('fiber',0)}g) helps reduce cholesterol.",
            "lungs": f" Lungs: Sugar ({nutrients.get('sugar',0)}g) causes inflammation. Antioxidants from colorful veggies would help.",
            "brain": f" Brain: Needs steady glucose. Current sugar ({nutrients.get('sugar',0)}g) may cause energy crashes.",
            "kidneys": f" Kidneys: Processing sodium ({nutrients.get('sodium',0)}mg) and protein ({nutrients.get('protein',0)}g). More water recommended.",
            "pancreas": f" Pancreas: Sugar ({nutrients.get('sugar',0)}g) requires insulin. Add fiber to slow absorption.",
            "liver": f" Liver: Metabolizing sugar ({nutrients.get('sugar',0)}g) and fat ({nutrients.get('fat',0)}g). Antioxidants would support detox.",
            "gut": f" Gut: Fiber ({nutrients.get('fiber',0)}g) feeds good bacteria. More diversity needed for optimal health.",
            "skin": f" Skin: Hydration affects elasticity. Consider more water and vitamins.",
            "immune": f" Immune: Sleep and stress management crucial for optimal function.",
            "muscles": f" Muscles: Protein needed for repair. Current intake: {nutrients.get('protein',0)}g"
        }
        return explanations.get(organ_name, "Organ response analysis unavailable.")
    
    def _fallback_agent_explanation(self, agent_action, action_idx):
        """Fallback agent explanation"""
        explanations = {
            0: " AI suggests increasing protein for organ repair and muscle maintenance.",
            1: " AI recommends reducing sugar to lower systemic inflammation and protect pancreas.",
            2: " AI advises boosting fiber for gut microbiome diversity and digestive health.",
            3: " AI suggests lowering sodium to reduce blood pressure and kidney strain.",
            4: " AI recommends balancing macronutrients for sustained energy and metabolic health.",
            5: " AI advises adding healthy fats for brain function and hormone production.",
            6: " AI suggests improving hydration for kidney function and cellular processes.",
            7: " AI indicates current nutrition pattern is supporting organ health effectively."
        }
        return explanations.get(action_idx, "AI recommendation based on current organ health patterns.")