"""
Moral Reflective Equilibrium Experiment

Studies whether LLMs develop more consistent preferences when fine-tuned
on reflections about their own inconsistencies.
"""

from pathlib import Path

__version__ = "1.0.0"
__experiment_name__ = "moral_reflective_equilibrium"

# Experiment paths
EXPERIMENT_ROOT = Path(__file__).parent
DATA_DIR = EXPERIMENT_ROOT / "data"
RESULTS_DIR = EXPERIMENT_ROOT / "results"
SCRIPTS_DIR = EXPERIMENT_ROOT / "scripts"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
