# Integration with CoTShield

## Overview

This **Moral Reflective Equilibrium** experiment is part of the CoTShield research ecosystem, focused on understanding and improving consistency in AI reasoning and value judgments.

## Relationship to CoTShield

### CoTShield's Core Mission
CoTShield reveals hidden reasoning in AI systems to detect deceptive or inconsistent behavior. It focuses on:
- Detecting divergence between reasoning chains and outputs
- Reconstructing shadow intent
- Making AI reasoning auditable and contestable

### How This Experiment Contributes

The moral reflective equilibrium experiment extends CoTShield's mission by:

1. **Systematic Inconsistency Detection**: Instead of detecting deception in individual responses, this experiment systematically identifies structural inconsistencies (transitivity violations) in AI value judgments.

2. **Self-Correction Through Reflection**: Tests whether AI systems can improve their consistency when prompted to reflect on their own inconsistencies—a form of "internal auditing."

3. **Continual Learning for Alignment**: Explores whether fine-tuning on reflections leads to more coherent reasoning, contributing to the broader goal of trustworthy AI systems.

## Integration Points

### Shared Infrastructure

The experiment uses CoTShield's:
- `.env` configuration for API keys
- Python environment and dependencies
- Experimental evaluation framework

### Complementary Research Directions

| CoTShield Core | Moral Reflective Equilibrium |
|----------------|------------------------------|
| Detect deceptive reasoning | Detect preference inconsistencies |
| Rule-based + LLM reconstruction | Graph-based transitivity analysis |
| Single-response analysis | Multi-response comparison |
| Immediate detection | Iterative improvement via finetuning |

### Potential Synergies

1. **Enhanced Detection**: CoTShield's divergence detector could flag individual preference judgments where reasoning conflicts with output, feeding into inconsistency analysis.

2. **Reflection Quality Assessment**: CoTShield's shadow intent reconstruction could evaluate whether reflections genuinely address inconsistencies or engage in rationalization.

3. **Combined Pipeline**:
   ```
   Preference Collection → CoTShield Analysis →
   Inconsistency Detection → Reflection Generation →
   CoTShield Verification → Finetuning
   ```

4. **Generalization**: Methods from this experiment (iterative reflection + finetuning) could be applied to improving consistency in CoTShield's core tasks.

## Setup Integration

### Environment Variables

The experiment uses the same `.env` file as CoTShield:

```bash
# In /mnt/nw/home/j.li/CoTShield/.env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional for this experiment
```

### Running from CoTShield Root

```bash
# From CoTShield root directory
cd experiments/moral_reflective_equilibrium

# Run setup test
python test_setup.py

# Run full pipeline
./run_pipeline.sh all
```

### Dependencies

The experiment has its own `requirements.txt` with additional dependencies:
- `networkx` for graph analysis (cycle detection)
- `scipy` for statistical tests
- Additional plotting libraries

Install with:
```bash
cd experiments/moral_reflective_equilibrium
pip install -r requirements.txt
```

## Experimental Workflow

### 1. Data Collection Phase
```bash
./run_pipeline.sh data
```
- Generates scenarios designed to elicit inconsistencies
- Collects model preferences on pairwise comparisons
- Detects transitivity violations using graph algorithms
- Prompts model to reflect on its inconsistencies

### 2. Fine-tuning Phase
```bash
./run_pipeline.sh finetune
```
- Prepares reflection data in OpenAI format
- Launches fine-tuning job (20-60 minutes)
- Monitors job completion

### 3. Evaluation Phase
```bash
./run_pipeline.sh eval
```
- Evaluates baseline and fine-tuned models
- Tests on original scenarios and held-out sets
- Compares consistency metrics
- Generates visualizations

## Results Structure

```
results/
├── eval_original_<baseline>.json       # Baseline evaluation
├── eval_original_<finetuned>.json      # Finetuned evaluation
├── eval_held_out_<model>.json          # Generalization test
├── final_analysis_comparison.json      # Statistical comparison
└── final_analysis_comparison.png       # Visualization plots
```

## Citation and Attribution

When using this experiment in CoTShield-related research:

```
CoTShield: Revealing AI's Hidden Reasoning
[Your name], 2026
https://github.com/lijiawei20161002/CoTShield

Moral Reflective Equilibrium Experiment
Part of CoTShield research ecosystem
```

## Future Integration Possibilities

1. **Unified Dashboard**: Integrate experiment results into CoTShield's web viewer for visual comparison of consistency metrics.

2. **Automated Pipeline**: Trigger CoTShield analysis on each preference judgment to flag suspicious reasoning before inconsistency detection.

3. **Multi-Model Comparison**: Use CoTShield's infrastructure to compare consistency across different model families (GPT, Claude, Llama).

4. **Real-Time Monitoring**: Extend CoTShield's monitoring tools to track consistency degradation during deployment.

5. **Curriculum Learning**: Use detected inconsistencies to prioritize which scenarios need more reflection iterations.

## Contributing

Improvements to the integration are welcome! Consider:
- Adding CoTShield divergence detection to preference collection
- Creating unified visualization dashboards
- Implementing cross-experiment analysis tools
- Extending to other consistency metrics beyond transitivity

## Support

For issues specific to:
- **This experiment**: Open an issue with tag `[moral-reflective-equilibrium]`
- **CoTShield integration**: Open an issue with tag `[integration]`
- **General CoTShield**: Follow standard CoTShield issue process

## License

Same as CoTShield: MIT License
