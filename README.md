# 🛡️ CoTShield — Revealing AI’s Hidden Reasoning to Defend Free Inquiry
A lightweight tool to surface hidden logic and detect deceptive reasoning in chain-of-thought (CoT) AI systems.

🌟 Overview

CoTShield helps uncover what advanced language models are really “thinking”—even when they try to hide it.

As AI systems grow more capable and strategic, they may learn to appear helpful while hiding deceptive or reward-hacking behavior in subtle ways. CoTShield makes reasoning chains legible and auditable, helping humans contest AI logic and restore visibility into the thought processes behind outputs.

🔍 Features

- 🧠 CoT Divergence Detection
Detect inconsistencies between model reasoning and final outputs.
- 👻 Shadow Intent Reconstruction
Infer what a model may have “thought but not said” using a secondary LLM.
- 🧾 Reasoning Trace Viewer
Interactive web tool to step through model chains-of-thought and flag hidden assumptions.
- 🧪 Adversarial Evaluation Tasks
Test how well different models stay epistemically hones

📦 Getting Started

### Prerequisites

- Python 3.8 or higher
- API keys for LLM providers (optional, required for intent reconstruction):
  - OpenAI API key (for GPT models)
  - Anthropic API key (for Claude models)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lijiawei20161002/CoTShield.git
cd CoTShield
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install as a package with CLI tool:
```bash
pip install -e .
```

4. (Optional) Set up API keys for LLM-based reconstruction:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Quick Start

**Option 1: Run Basic Detection Example**
```bash
python examples/basic_detection.py
```

**Option 2: Use the CLI Tool** (after installing with `pip install -e .`)
```bash
# Analyze a reasoning trace
cotshield analyze --reasoning "Let me think... The capital is Canberra." \
                   --output "The capital is Sydney."

# Start the interactive web viewer
cotshield viewer

# Run evaluations
cotshield eval --responses-file your_responses.json
```

**Option 3: Start the Web Viewer**
```bash
python examples/run_viewer.py
# Then open http://localhost:8000 in your browser
```

**Option 4: Use as a Python Library**
```python
from monitor.detector import analyze_cot_trace

result = analyze_cot_trace(
    reasoning="My step-by-step thinking...",
    output="Final answer",
    sensitivity=0.5
)

print(f"Risk Score: {result['risk_score']}")
print(f"Flags: {result['flag_count']}")
```

🗓️ Roadmap

- [x] v0.1: CoT Divergence Detector (rule-based)
- [x] v0.2: CoT Viewer Web Demo
- [x] v0.3: LLM-based Reconstructor
- [x] v1.0: Public MVP Release

🙋‍♀️ Get Involved

This project is open to collaboration. Interested in evaluating LLM honesty, epistemic integrity, or building tooling for truth-seeking? Open an issue or submit a pull request!

📜 License

MIT License
