# Moral Reflective Equilibrium for LLMs

This repository contains an experimental pipeline for studying whether LLMs develop more consistent preferences when fine-tuned on reflections about their own inconsistencies.

## Overview

The experiment tests the hypothesis that:
1. LLMs display preference inconsistencies (transitivity violations) when making ethical judgments
2. When prompted to reflect on these inconsistencies, they can generate principled resolutions
3. Fine-tuning on these reflections leads to more consistent preferences
4. This improved consistency generalizes to held-out scenarios

**📊 NEW: Evaluation Results Available** - See [`RESULTS.md`](RESULTS.md) for completed evaluation showing that chain-of-thought reasoning increased inconsistencies by 7x in GPT-4o-mini (February 14, 2026).

## Project Structure

```
experiments/moral_reflective_equilibrium/
├── README.md                 # This file
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
├── run_experiment.py         # Main experiment runner
├── data/                     # Generated data files
├── scripts/                  # Individual pipeline steps
│   ├── 1_generate_scenarios.py
│   ├── 2_collect_preferences.py
│   ├── 3_detect_inconsistencies.py
│   ├── 4_generate_reflections.py
│   ├── 5_prepare_finetuning.py
│   ├── 6_run_finetuning.py
│   ├── 7_evaluate.py
│   └── 8_analyze_results.py
└── results/                  # Evaluation results and visualizations
```

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key with access to GPT-4 and finetuning

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## Running the Experiment

### Quick Start

Run the entire pipeline:
```bash
python run_experiment.py
```

Skip finetuning (for testing):
```bash
python run_experiment.py --skip-finetuning
```

Run specific steps only:
```bash
python run_experiment.py --steps 1,2,3,4,5
```

Evaluate with existing finetuned model:
```bash
python run_experiment.py --steps 7,8 --finetuned-model ft:gpt-4o-mini-2024-07-18:your-org:moral-reflective:suffix
```

### Step-by-Step

#### 1. Generate Scenarios
Creates ethical dilemmas with multiple options designed to elicit inconsistencies.

```bash
python scripts/1_generate_scenarios.py
```

**Domains included:**
- Public health resource allocation
- Tax policy preferences
- Legal decisions
- Assistant response preferences
- Literary judgments

**Output:** `data/scenarios.json`

#### 2. Collect Preferences
Collects pairwise preferences from the model on all option pairs.

```bash
python scripts/2_collect_preferences.py
```

**Output:** `data/preferences.json`

#### 3. Detect Inconsistencies
Finds cycles in preference graphs (A > B > C > A).

```bash
python scripts/3_detect_inconsistencies.py
```

**Output:** `data/inconsistencies.json`

#### 4. Generate Reflections
Presents inconsistencies to the model and collects reflections.

```bash
python scripts/4_generate_reflections.py
```

**Output:** `data/reflections.json`

#### 5. Prepare Finetuning Data
Converts reflections into OpenAI finetuning format.

```bash
python scripts/5_prepare_finetuning.py
```

**Outputs:**
- `data/finetuning_train.jsonl`
- `data/finetuning_val.jsonl`
- `data/finetuning_full.json`

#### 6. Run Finetuning
Uploads data and creates finetuning job via OpenAI API.

```bash
python scripts/6_run_finetuning.py
```

**Note:** This can take 20-60 minutes. The script will monitor progress and save the model ID.

**Output:** `data/finetune_job_info.json`

#### 7. Evaluate Models
Evaluates both baseline and finetuned models.

```bash
# Baseline model
python scripts/7_evaluate.py --model gpt-4-turbo-preview --eval-type original

# Finetuned model
python scripts/7_evaluate.py --model ft:gpt-4o-mini-2024-07-18:org:suffix --eval-type original

# Held-out in-distribution scenarios
python scripts/7_evaluate.py --model <model> --eval-type held-out --scenarios scenarios_held_out.json

# Out-of-distribution scenarios
python scripts/7_evaluate.py --model <model> --eval-type ood --scenarios scenarios_ood.json
```

**Outputs:** `results/eval_<type>_<model>.json`

#### 8. Analyze Results
Compares baseline and finetuned models with statistical tests and visualizations.

```bash
python scripts/8_analyze_results.py \
  --baseline eval_original_gpt-4-turbo-preview.json \
  --finetuned eval_original_ft_gpt-4o-mini-2024-07-18_org_suffix.json \
  --output-prefix final_analysis
```

**Outputs:**
- `results/final_analysis_comparison.json` - Detailed metrics
- `results/final_analysis_comparison.png` - Visualization plots

## Configuration

Edit `config.py` to adjust:
- Model selection (`MODEL`, `FINETUNE_BASE_MODEL`)
- Temperature and other generation parameters
- Number of reflection variations per inconsistency
- Train/validation split ratio
- Finetuning hyperparameters

## Expected Results

The experiment will produce:

1. **Quantitative metrics:**
   - Total inconsistencies (before vs after)
   - Inconsistency rate per scenario
   - Number of scenarios with inconsistencies
   - Statistical significance tests (t-test, Wilcoxon)

2. **Visualizations:**
   - Overall inconsistency comparison
   - Per-domain breakdown
   - Distribution histograms
   - Scenario-by-scenario scatter plots

3. **Insights for iteration:**
   - Which domains show most/least improvement
   - Types of inconsistencies that persist
   - Quality of reflections generated
   - Suggestions for dataset improvements

## Evaluation Results

**Initial evaluation completed** - See [`RESULTS.md`](RESULTS.md) for detailed findings:

- GPT-4o-mini baseline evaluation (No-CoT vs CoT)
- **Key finding**: CoT increased inconsistencies by 7x
- Implications for fine-tuning strategy
- Recommendations for next steps

## Iteration Strategy

After the first finetuning run:

1. **Analyze failure modes:** Which inconsistencies persist?
2. **Improve scenario generation:** Create more challenging or diverse scenarios
3. **Enhance reflection prompting:** Experiment with different elicitation strategies
4. **Augment training data:** Generate more examples in underperforming domains
5. **Test OOD generalization:** Create scenarios in entirely new domains

## Cost Estimates

Approximate costs for full pipeline (based on OpenAI pricing):
- Scenario generation: $1-5
- Preference collection: $5-15
- Reflection generation: $10-30
- Finetuning: $5-20 (depending on dataset size)
- Evaluation: $5-15
- **Total: ~$25-85 for one complete run**

## Limitations & Future Work

**Current limitations:**
- Single finetuning run with limited iteration
- Relatively small scenario dataset
- Focus on pairwise transitivity only
- Limited domain diversity

**Future improvements:**
- Multiple finetuning iterations with progressive refinement
- Larger and more diverse scenario sets
- Test different reflection elicitation strategies
- Explore other consistency metrics beyond transitivity
- Compare different model sizes and families
- Test whether consistency improves real-world alignment

## Citation

If you use this code, please cite:
```
[Work test implementation for moral reflective equilibrium study]
[Your name], 2026
```

## License

MIT License - see LICENSE file for details
