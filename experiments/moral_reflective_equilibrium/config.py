"""
Configuration for moral reflective equilibrium experiments
"""

import os
from pathlib import Path

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4-turbo-preview"  # Model for initial preference collection and reflections
FINETUNE_BASE_MODEL = "gpt-4o-mini-2024-07-18"  # Base model for finetuning

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Generation Parameters
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Scenario Configuration
NUM_SCENARIOS_PER_DOMAIN = 10  # Adjustable based on time budget
NUM_OPTIONS_PER_SCENARIO = 4   # Minimum for interesting cycles

# Reflection Parameters
REFLECTION_VARIATIONS = 2  # Number of different reflections per inconsistency

# Finetuning Configuration
TRAIN_SPLIT = 0.8  # 80% training, 20% validation
FINETUNE_EPOCHS = 3  # Number of finetuning epochs

# Evaluation
EVAL_MAX_SCENARIOS = None  # Set to limit evaluation size (None = all)

# Domains for scenarios
DOMAINS = [
    "public_health",
    "tax_policy",
    "legal_decisions",
    "assistant_preferences",
    "literary_judgment"
]
