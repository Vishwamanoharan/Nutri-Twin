# Configuration and constants

ORGAN_BASELINES = {
    "heart": {
        "blood_pressure": 120,
        "cardiac_output": 5.0,
        "oxygen_delivery": 95,
        "arterial_stiffness": 15
    },
    "lungs": {
        "oxygen_saturation": 98,
        "lung_capacity": 4.5,
        "airway_resistance": 2.1,
        "inflammation_markers": 1.2
    },
    "brain": {
        "cognitive_score": 92,
        "blood_flow": 750,
        "neurotransmitters": 88,
        "inflammation": 1.5
    },
    "kidneys": {
        "gfr": 95,
        "creatinine": 0.9,
        "electrolyte_balance": 92,
        "toxin_clearance": 88
    },
    "pancreas": {
        "insulin_sensitivity": 85,
        "beta_cell_function": 78,
        "enzyme_production": 90,
        "inflammation": 2.1
    },
    "liver": {
        "detox_rate": 88,
        "fat_content": 18,
        "enzyme_levels": 92,
        "inflammation": 1.8
    },
    "gut": {
        "microbiome_diversity": 65,
        "absorption_rate": 78,
        "barrier_integrity": 82,
        "inflammation": 2.3
    }
}

# Organ definitions with all properties
ORGAN_DEFINITIONS = {
    "heart": {
        "position": (0, 0, 1.0),
        "size": 0.40,
        "color": "#FF6B6B",
        "system": "Cardiovascular",
        "sensitivity": {
            "sodium": 0.8,
            "fat": 0.6,
            "fiber": -0.4,
            "potassium": -0.3
        },
        "function": "Blood circulation & oxygen transport",
        "risk_factors": ["Hypertension", "Atherosclerosis", "Arrhythmia"]
    },
    "lungs": {
        "position": (-0.5, 0.5, 0.8),
        "size": 0.25,
        "color": "#87CEEB",
        "system": "Respiratory",
        "sensitivity": {
            "sugar": 0.7,
            "antioxidants": -0.5,
            "omega3": -0.4,
            "pollutants": 0.9
        },
        "function": "Gas exchange & oxygenation",
        "risk_factors": ["COPD", "Asthma", "Fibrosis"]
    },
    "brain": {
        "position": (0, 0.8, 1.1),
        "size": 0.18,
        "color": "#DDA0DD",
        "system": "Neurological",
        "sensitivity": {
            "sugar": 0.6,
            "healthy_fats": -0.5,
            "protein": -0.3,
            "sleep": -0.7
        },
        "function": "Cognition, memory, coordination",
        "risk_factors": ["Neuroinflammation", "Cognitive decline", "Stroke"]
    },
    "kidneys": {
        "position": (0.6, -0.4, 0.6),
        "size": 0.12,
        "color": "#96CEB4",
        "system": "Renal",
        "sensitivity": {
            "sodium": 0.9,
            "protein": 0.4,
            "water": -0.6,
            "potassium": -0.3
        },
        "function": "Filtration & waste removal",
        "risk_factors": ["CKD", "Stones", "Hypertension"]
    },
    "pancreas": {
        "position": (0.5, 0.2, 0.7),
        "size": 0.08,
        "color": "#45B7D1",
        "system": "Endocrine",
        "sensitivity": {
            "sugar": 0.9,
            "fiber": -0.6,
            "chromium": -0.4,
            "stress": 0.7
        },
        "function": "Blood sugar regulation & digestion",
        "risk_factors": ["Diabetes", "Pancreatitis", "Metabolic syndrome"]
    },
    "liver": {
        "position": (0.7, -0.3, 0.8),
        "size": 0.22,
        "color": "#4ECDC4",
        "system": "Metabolic",
        "sensitivity": {
            "sugar": 0.8,
            "alcohol": 0.9,
            "antioxidants": -0.5,
            "protein": -0.3
        },
        "function": "Detoxification & metabolism",
        "risk_factors": ["Fatty liver", "Cirrhosis", "Hepatitis"]
    },
    "gut": {
        "position": (0, -0.5, 0.4),
        "size": 0.25,
        "color": "#FFEAA7",
        "system": "Digestive",
        "sensitivity": {
            "fiber": -0.7,
            "sugar": 0.6,
            "probiotics": -0.5,
            "processed_foods": 0.8
        },
        "function": "Digestion & nutrient absorption",
        "risk_factors": ["IBD", "Leaky gut", "Dysbiosis"]
    },
    "skin": {
        "position": (0.3, -0.7, 0.3),
        "size": 0.15,
        "color": "#F4A460",
        "system": "Integumentary",
        "sensitivity": {"water": -0.5, "vitamins": -0.4, "sun_exposure": 0.6},
        "function": "Protection & temperature regulation",
        "risk_factors": ["Dehydration", "Sun damage", "Inflammation"],
        "metrics": {"hydration": 85, "elasticity": 75, "barrier_function": 80}
    },
    "immune": {
        "position": (-0.3, -0.7, 0.3),
        "size": 0.12,
        "color": "#9370DB",
        "system": "Immune",
        "sensitivity": {"sleep": -0.6, "stress": 0.7, "antioxidants": -0.5},
        "function": "Pathogen defense & immune regulation",
        "risk_factors": ["Autoimmunity", "Immunodeficiency", "Chronic inflammation"],
        "metrics": {"immune_response": 78, "antibody_levels": 82, "inflammation_control": 75}
    },
    "muscles": {
        "position": (0, 0.2, 0.2),
        "size": 0.18,
        "color": "#6495ED",
        "system": "Musculoskeletal",
        "sensitivity": {"protein": -0.5, "exercise": -0.6, "inflammation": 0.5},
        "function": "Movement & metabolism",
        "risk_factors": ["Atrophy", "Fatigue", "Injury"],
        "metrics": {"strength": 85, "endurance": 78, "recovery_rate": 72}
    }
}

# Additional configuration
DEFAULT_NUTRIENTS = {
    'calories': 300.0,
    'carbs': 45.0,
    'protein': 20.0,
    'fat': 12.0,
    'sugar': 8.0,
    'fiber': 6.0,
    'sodium': 500.0,
    'calcium': 200.0,
    'iron': 3.0
}

# DQN Agent configuration
DQN_CONFIG = {
    "state_size": 23,
    "action_size": 8,
    "gamma": 0.95,
    "epsilon": 0.3,
    "epsilon_decay": 0.995,
    "epsilon_min": 0.05,
    "memory_size": 2000,
    "batch_size": 32,
    "learning_rate": 0.001,
    "target_update_freq": 10
}

# Organ health weights for overall health calculation
ORGAN_WEIGHTS = {
    "heart": 0.15,
    "brain": 0.15,
    "lungs": 0.12,
    "liver": 0.12,
    "kidneys": 0.10,
    "pancreas": 0.10,
    "gut": 0.10,
    "skin": 0.06,
    "immune": 0.10,
    "muscles": 0.10
}