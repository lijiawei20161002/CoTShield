# Quick Start Guide

## Setup (2 minutes)

```bash
# Navigate to the experiment directory
cd experiments/moral_reflective_equilibrium

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## Run Full Experiment

### Option 1: Automated Pipeline (Recommended for Work Test)

```bash
# Run steps 1-5 (everything before finetuning)
python run_experiment.py --steps 1,2,3,4,5

# This will:
# 1. Generate ~50 scenarios across 5 domains (2-3 min)
# 2. Collect pairwise preferences (15-20 min)
# 3. Detect inconsistencies (<1 min)
# 4. Generate reflections (20-30 min)
# 5. Prepare finetuning data (<1 min)
```

### Option 2: Manual Step-by-Step

```bash
# Step 1: Generate scenarios (2-3 min)
python scripts/1_generate_scenarios.py

# Step 2: Collect preferences (15-20 min)
python scripts/2_collect_preferences.py

# Step 3: Detect inconsistencies (<1 min)
python scripts/3_detect_inconsistencies.py

# Step 4: Generate reflections (20-30 min)
python scripts/4_generate_reflections.py

# Step 5: Prepare finetuning data (<1 min)
python scripts/5_prepare_finetuning.py
```

## Start Finetuning (Do While Working on Other Things)

```bash
# Step 6: Start finetuning (20-60 min)
python scripts/6_run_finetuning.py

# The script will upload data and start the job
# It will print a job ID - save this!

# Monitor in another terminal
python scripts/monitor_finetuning.py <job-id>
```

## Evaluate and Analyze

```bash
# Step 7: Evaluate models (10-15 min)
# Replace <finetuned-model-id> with your model from step 6

# Evaluate baseline
python scripts/7_evaluate.py \
  --model gpt-4-turbo-preview \
  --eval-type original

# Evaluate finetuned
python scripts/7_evaluate.py \
  --model <finetuned-model-id> \
  --eval-type original

# Step 8: Analyze results (<1 min)
python scripts/8_analyze_results.py \
  --baseline eval_original_gpt-4-turbo-preview.json \
  --finetuned eval_original_<finetuned-model-id>.json \
  --output-prefix final_analysis
```

## Time Budget Breakdown (3.5 hours)

- **Setup**: 5 min
- **Generate scenarios**: 3 min
- **Collect preferences**: 20 min
- **Detect inconsistencies**: 1 min
- **Generate reflections**: 30 min
- **Prepare finetuning**: 1 min
- **Start finetuning job**: 5 min
- **Wait for finetuning**: 30-60 min (work on Part 2 or analysis during this)
- **Evaluate baseline**: 10 min
- **Evaluate finetuned**: 10 min
- **Analyze results**: 5 min
- **Write writeup**: 30 min

**Total active time**: ~2 hours
**Total elapsed time**: ~2.5-3 hours (including finetuning wait)

## Tips for Work Test

1. **Start finetuning early**: Once you have the reflections, start finetuning and work on other things while it runs

2. **Adjust dataset size**: In `config.py`, you can reduce `NUM_SCENARIOS_PER_DOMAIN` to speed up data collection (minimum 5 per domain recommended)

3. **Test on subset first**: Use `--max-scenarios 20` in evaluation to quickly test before running full eval

4. **Parallel work**: While waiting for API calls or finetuning:
   - Polish your Part 2 writeup
   - Draft your Part 3 writeup outline
   - Generate additional scenarios for held-out sets

5. **Cost optimization**:
   - Use `gpt-4o-mini` for initial experiments (cheaper)
   - Limit to 5-8 scenarios per domain (30-40 total)
   - Single finetuning run as recommended

## Quick Test Run (15 minutes)

For testing the pipeline before the full run:

```bash
# Edit config.py: set NUM_SCENARIOS_PER_DOMAIN = 2
nano config.py

# Run steps 1-5
python run_experiment.py --steps 1,2,3,4,5 --skip-finetuning

# Check outputs
ls -lh data/
cat data/inconsistencies.json | head -50
```

## Troubleshooting

**"No inconsistencies found"**:
- Increase `TEMPERATURE` in config.py
- Generate more scenarios per domain
- Try different scenario templates

**"Finetuning job failed"**:
- Check you have enough finetuning credits
- Verify data format: `python -c "import json; json.load(open('data/finetuning_train.jsonl'))"`
- Reduce dataset size if too large

**"Rate limit errors"**:
- Increase `time.sleep()` delays in collection scripts
- Use a higher-tier API key
- Process in smaller batches

## Next Steps After First Run

1. **Analyze failure modes**: Which inconsistencies persist?
2. **Generate new scenarios**: Create held-out and OOD test sets
3. **Iterate on prompts**: Improve reflection elicitation
4. **Document findings**: Write up what worked and what didn't

## Files Generated

```
data/
├── scenarios.json           # Generated scenarios
├── preferences.json         # Pairwise preferences
├── inconsistencies.json     # Detected cycles
├── reflections.json         # Model reflections
├── finetuning_train.jsonl   # Training data
├── finetuning_val.jsonl     # Validation data
└── finetune_job_info.json   # Finetuning job details

results/
├── eval_original_<model>.json              # Evaluation results
├── final_analysis_comparison.json          # Statistical comparison
└── final_analysis_comparison.png           # Visualization plots
```

## Example Writeup Outline

For your PDF submission (~1 page):

### Approach
- Dataset: X scenarios across 5 domains
- Generated Y inconsistencies, created Z reflection examples
- Finetuned gpt-4o-mini for N epochs

### Results
- Baseline: X inconsistencies across Y scenarios (Z per scenario)
- Finetuned: A inconsistencies across Y scenarios (B per scenario)
- Improvement: C% reduction (p=0.XX via paired t-test)
- Per-domain breakdown: [table or bullets]

### Key Findings
- Which domains improved most/least
- Types of inconsistencies that persisted
- Quality observations about reflections

### Takeaways
- What worked well in elicitation/reflection
- Proposed improvements for next iteration
- Dataset changes you would make (even if not implemented)

### References
- Link to GitHub repo
- Specific files/folders containing data and results
