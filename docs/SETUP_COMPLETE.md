# Setup Complete ✓

The **Moral Reflective Equilibrium** experiment has been successfully integrated into the CoTShield repository and is ready to run!

## 📁 Location
```
/mnt/nw/home/j.li/CoTShield/experiments/moral_reflective_equilibrium/
```

## ✅ What's Included

### Core Implementation (8 Pipeline Scripts)
All scripts are complete and functional:

1. **`scripts/1_generate_scenarios.py`** - Generates ethical dilemma scenarios across 5 domains
2. **`scripts/2_collect_preferences.py`** - Collects pairwise preferences from LLM
3. **`scripts/3_detect_inconsistencies.py`** - Detects transitivity violations (A>B>C>A cycles)
4. **`scripts/4_generate_reflections.py`** - Prompts model to reflect on inconsistencies
5. **`scripts/5_prepare_finetuning.py`** - Formats reflections for OpenAI fine-tuning API
6. **`scripts/6_run_finetuning.py`** - Submits and monitors fine-tuning job
7. **`scripts/7_evaluate.py`** - Evaluates baseline vs fine-tuned model
8. **`scripts/8_analyze_results.py`** - Statistical analysis and visualization

### Configuration & Utilities
- **`config.py`** - All experiment parameters (editable)
- **`test_setup.py`** - Validates environment and dependencies
- **`run_pipeline.sh`** - Automated pipeline runner (executable)
- **`scripts/monitor_finetuning.py`** - Standalone fine-tuning monitor
- **`requirements.txt`** - Python dependencies

### Documentation
- **`README.md`** - Main experiment documentation
- **`QUICKSTART.md`** - Quick start guide
- **`IMPLEMENTATION_GUIDE.md`** - Technical implementation details
- **`PROJECT_SUMMARY.md`** - Research overview
- **`INTEGRATION.md`** - CoTShield integration details
- **`WRITEUP_TEMPLATE.md`** - Template for results writeup

### Directories
- **`data/`** - Created automatically for experiment data
- **`results/`** - Created automatically for results and visualizations

## 🚀 Quick Start

### 1. Test Your Setup
```bash
cd /mnt/nw/home/j.li/CoTShield/experiments/moral_reflective_equilibrium
python test_setup.py
```

This will verify:
- All Python packages are installed
- OpenAI API key is set
- All scripts are present
- Configuration is valid

### 2. Set Your API Key
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Or add to your `~/.bashrc` or `~/.zshrc` for persistence.

### 3. Run the Experiment

**Option A: Full automated pipeline**
```bash
./run_pipeline.sh all
```

**Option B: Step-by-step**
```bash
# Data generation (Steps 1-5)
./run_pipeline.sh data

# Fine-tuning (Step 6) - takes 30-60 minutes
./run_pipeline.sh finetune

# Evaluation (Steps 7-8)
./run_pipeline.sh eval <your-finetuned-model-id>
```

**Option C: Manual execution**
```bash
# Run each script individually
python scripts/1_generate_scenarios.py
python scripts/2_collect_preferences.py
python scripts/3_detect_inconsistencies.py
python scripts/4_generate_reflections.py
python scripts/5_prepare_finetuning.py
python scripts/6_run_finetuning.py
# ... and so on
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Key parameters to adjust:
MODEL = "gpt-4-turbo-preview"  # Model for data collection
FINETUNE_BASE_MODEL = "gpt-4o-mini-2024-07-18"  # Base for fine-tuning
NUM_SCENARIOS_PER_DOMAIN = 10  # Number of scenarios (10 = ~50 total)
REFLECTION_VARIATIONS = 2  # Reflections per inconsistency
FINETUNE_EPOCHS = 3  # Training epochs
TRAIN_SPLIT = 0.8  # Train/validation split
```

### Cost Estimation

**For default settings** (10 scenarios/domain = ~50 total):
- **Data Generation** (Steps 1-5): ~$5-10
  - Scenario generation: $2-3
  - Preference collection: $2-4 (6 comparisons × 50 scenarios)
  - Reflection generation: $1-3
- **Fine-tuning** (Step 6): $3-8
  - Depends on training examples (~100-200 examples)
  - Takes 30-60 minutes
- **Evaluation** (Steps 7-8): $3-5
  - Baseline + fine-tuned evaluation
- **Total**: ~$11-23 for full experiment

**To reduce costs:**
- Set `NUM_SCENARIOS_PER_DOMAIN = 5` (halves data costs)
- Use `gpt-3.5-turbo` for initial collection (in config.py)
- Fine-tune on smaller subset

## 📊 Expected Output

After running the full pipeline, you'll get:

### Data Files (in `data/`)
- `scenarios.json` - Generated ethical dilemmas
- `preferences.json` - Model's pairwise preferences
- `inconsistencies.json` - Detected cycles
- `reflections.json` - Model's self-reflections
- `finetuning_train.jsonl` - Training data
- `finetuning_val.jsonl` - Validation data
- `finetune_job_info.json` - Fine-tuning job details

### Results (in `results/`)
- `eval_original_<model>.json` - Baseline evaluation
- `eval_original_<finetuned-model>.json` - Fine-tuned evaluation
- `final_analysis_comparison.json` - Statistical comparison
- `final_analysis_comparison.png` - Visualization (4-panel figure)

### Analysis Output
```
MODEL COMPARISON
================================================================
Baseline Model: gpt-4-turbo-preview
Fine-tuned Model: ft:gpt-4o-mini-2024-07-18:...

METRIC                           BASELINE    FINETUNED    CHANGE
------------------------------------------------------------------
Total inconsistencies                  45          28        -17 (-37.8%)
Inconsistency rate                   0.90        0.56      -0.34 (-37.8%)
Scenarios w/ inconsistencies          32          21        -11

PER-DOMAIN COMPARISON
================================================================
[Detailed breakdown by domain]

STATISTICAL SIGNIFICANCE
================================================================
Paired t-test: p < 0.05 (statistically significant)
```

## 🔬 Research Hypothesis

**Main Question:** Can LLMs develop more consistent preferences when fine-tuned on reflections about their own inconsistencies?

**Expected Results:**
- ✓ Baseline model shows transitivity violations (cycles)
- ✓ Fine-tuned model reduces inconsistency rate by 20-40%
- ✓ Improvement is statistically significant
- ✓ Effect generalizes across multiple domains

## 🛠️ Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-...'
```

### Missing dependencies
```bash
pip install -r requirements.txt
```

### API rate limits
- Add `time.sleep(1)` in collection scripts
- Or reduce `NUM_SCENARIOS_PER_DOMAIN` in config.py

### Fine-tuning job failed
- Check: `data/finetune_job_info.json`
- Monitor: `python scripts/monitor_finetuning.py <job-id>`
- Verify training data format: `head data/finetuning_train.jsonl`

### Permission denied on run_pipeline.sh
```bash
chmod +x run_pipeline.sh
```

## 📖 Documentation

- **Quickstart**: `QUICKSTART.md` - Get running in 5 minutes
- **Technical**: `IMPLEMENTATION_GUIDE.md` - Deep dive into implementation
- **Research**: `PROJECT_SUMMARY.md` - Research context and hypothesis
- **Integration**: `INTEGRATION.md` - How this fits into CoTShield
- **Main README**: `README.md` - Complete documentation

## 🔗 Integration with CoTShield

This experiment integrates with CoTShield's mission to reveal hidden reasoning:

1. **Consistency Detection**: Uses CoTShield's principles to detect inconsistent reasoning
2. **Iterative Refinement**: Tests whether self-reflection improves consistency
3. **Shared Metrics**: Can leverage CoTShield's divergence detection methods
4. **Future Integration**: Results can inform CoTShield's consistency scoring

See `INTEGRATION.md` for detailed connections.

## 📝 Next Steps

After running the experiment:

1. **Analyze Results**: Check `results/` for output
2. **Write Up**: Use `WRITEUP_TEMPLATE.md` for paper/report
3. **Iterate**: Adjust config.py and re-run for different parameters
4. **Extend**:
   - Add new domains to `scripts/1_generate_scenarios.py`
   - Test different base models
   - Try multi-iteration refinement
   - Evaluate on out-of-distribution scenarios

## 🎯 Status

**✅ READY TO RUN**

All implementation is complete. You can start the experiment now!

```bash
cd /mnt/nw/home/j.li/CoTShield/experiments/moral_reflective_equilibrium
python test_setup.py  # Verify setup
./run_pipeline.sh all  # Run experiment
```

---

**Questions or Issues?**
- Check documentation in this directory
- Review CoTShield main README: `../../README.md`
- Open an issue in the CoTShield repository

**Last Updated:** 2026-02-13
