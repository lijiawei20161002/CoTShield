"""
Step 8: Analyze and visualize results
Compare before/after finetuning
"""

import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from collections import defaultdict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

sns.set_style("whitegrid")

def load_results(eval_file):
    """Load evaluation results"""
    with open(eval_file, 'r') as f:
        data = json.load(f)
    return data

def compare_models(baseline_file, finetuned_file, output_prefix):
    """Compare baseline and finetuned models"""

    baseline = load_results(baseline_file)
    finetuned = load_results(finetuned_file)

    baseline_metrics = baseline['metrics']
    finetuned_metrics = finetuned['metrics']

    # Overall comparison
    print("="*70)
    print("MODEL COMPARISON")
    print("="*70)

    print(f"\nBaseline Model: {baseline_metrics['model']}")
    print(f"Fine-tuned Model: {finetuned_metrics['model']}")

    print(f"\nScenarios evaluated: {baseline_metrics['num_scenarios']}")

    print("\n" + "-"*70)
    print("METRIC                           BASELINE    FINETUNED    CHANGE")
    print("-"*70)

    b_incon = baseline_metrics['total_inconsistencies']
    f_incon = finetuned_metrics['total_inconsistencies']
    change_incon = f_incon - b_incon
    pct_change_incon = ((f_incon - b_incon) / b_incon * 100) if b_incon > 0 else 0

    print(f"Total inconsistencies            {b_incon:8d}    {f_incon:8d}    {change_incon:+6d} ({pct_change_incon:+6.1f}%)")

    b_rate = baseline_metrics['inconsistency_rate']
    f_rate = finetuned_metrics['inconsistency_rate']
    change_rate = f_rate - b_rate
    pct_change_rate = ((f_rate - b_rate) / b_rate * 100) if b_rate > 0 else 0

    print(f"Inconsistency rate               {b_rate:8.2f}    {f_rate:8.2f}    {change_rate:+6.2f} ({pct_change_rate:+6.1f}%)")

    b_scenarios = baseline_metrics['scenarios_with_inconsistencies']
    f_scenarios = finetuned_metrics['scenarios_with_inconsistencies']
    change_scenarios = f_scenarios - b_scenarios

    print(f"Scenarios w/ inconsistencies     {b_scenarios:8d}    {f_scenarios:8d}    {change_scenarios:+6d}")

    print("-"*70)

    # Per-domain comparison
    baseline_by_domain = defaultdict(lambda: {'inconsistencies': 0, 'scenarios': 0})
    finetuned_by_domain = defaultdict(lambda: {'inconsistencies': 0, 'scenarios': 0})

    for result in baseline['results']:
        domain = result['domain']
        baseline_by_domain[domain]['inconsistencies'] += result['num_inconsistencies']
        baseline_by_domain[domain]['scenarios'] += 1

    for result in finetuned['results']:
        domain = result['domain']
        finetuned_by_domain[domain]['inconsistencies'] += result['num_inconsistencies']
        finetuned_by_domain[domain]['scenarios'] += 1

    print("\n" + "="*70)
    print("PER-DOMAIN COMPARISON")
    print("="*70)

    for domain in sorted(set(baseline_by_domain.keys()) | set(finetuned_by_domain.keys())):
        b = baseline_by_domain[domain]
        f = finetuned_by_domain[domain]

        b_rate = b['inconsistencies'] / b['scenarios'] if b['scenarios'] > 0 else 0
        f_rate = f['inconsistencies'] / f['scenarios'] if f['scenarios'] > 0 else 0

        print(f"\n{domain}:")
        print(f"  Baseline rate: {b_rate:.2f} ({b['inconsistencies']}/{b['scenarios']})")
        print(f"  Finetuned rate: {f_rate:.2f} ({f['inconsistencies']}/{f['scenarios']})")
        print(f"  Change: {f_rate - b_rate:+.2f}")

    # Statistical test
    print("\n" + "="*70)
    print("STATISTICAL SIGNIFICANCE")
    print("="*70)

    baseline_counts = [r['num_inconsistencies'] for r in baseline['results']]
    finetuned_counts = [r['num_inconsistencies'] for r in finetuned['results']]

    # Paired t-test (assuming same scenarios in same order)
    if len(baseline_counts) == len(finetuned_counts):
        t_stat, p_value = stats.ttest_rel(baseline_counts, finetuned_counts)
        print(f"Paired t-test:")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value: {p_value:.4f}")
        if p_value < 0.05:
            print(f"  Result: Statistically significant difference (p < 0.05)")
        else:
            print(f"  Result: Not statistically significant (p >= 0.05)")

    # Wilcoxon signed-rank test (non-parametric)
    if len(baseline_counts) == len(finetuned_counts):
        w_stat, w_p_value = stats.wilcoxon(baseline_counts, finetuned_counts, zero_method='wilcox', alternative='two-sided')
        print(f"\nWilcoxon signed-rank test:")
        print(f"  statistic: {w_stat:.4f}")
        print(f"  p-value: {w_p_value:.4f}")

    # Create visualizations
    create_visualizations(baseline, finetuned, output_prefix)

    return {
        'baseline_metrics': baseline_metrics,
        'finetuned_metrics': finetuned_metrics,
        'improvement': {
            'absolute': change_incon,
            'percentage': pct_change_incon,
            'rate_change': change_rate
        },
        'statistical_tests': {
            't_test': {'statistic': t_stat, 'p_value': p_value} if len(baseline_counts) == len(finetuned_counts) else None,
            'wilcoxon': {'statistic': w_stat, 'p_value': w_p_value} if len(baseline_counts) == len(finetuned_counts) else None
        }
    }

def create_visualizations(baseline, finetuned, output_prefix):
    """Create comparison visualizations"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Overall inconsistency comparison
    ax = axes[0, 0]
    models = ['Baseline', 'Fine-tuned']
    inconsistencies = [
        baseline['metrics']['total_inconsistencies'],
        finetuned['metrics']['total_inconsistencies']
    ]
    ax.bar(models, inconsistencies, color=['#e74c3c', '#3498db'])
    ax.set_ylabel('Total Inconsistencies')
    ax.set_title('Total Inconsistencies: Baseline vs Fine-tuned')
    for i, v in enumerate(inconsistencies):
        ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

    # 2. Per-domain comparison
    ax = axes[0, 1]

    domains = set()
    for result in baseline['results'] + finetuned['results']:
        domains.add(result['domain'])
    domains = sorted(domains)

    baseline_by_domain = {d: 0 for d in domains}
    finetuned_by_domain = {d: 0 for d in domains}
    baseline_counts = {d: 0 for d in domains}
    finetuned_counts = {d: 0 for d in domains}

    for result in baseline['results']:
        baseline_by_domain[result['domain']] += result['num_inconsistencies']
        baseline_counts[result['domain']] += 1

    for result in finetuned['results']:
        finetuned_by_domain[result['domain']] += result['num_inconsistencies']
        finetuned_counts[result['domain']] += 1

    baseline_rates = [baseline_by_domain[d] / baseline_counts[d] if baseline_counts[d] > 0 else 0 for d in domains]
    finetuned_rates = [finetuned_by_domain[d] / finetuned_counts[d] if finetuned_counts[d] > 0 else 0 for d in domains]

    x = np.arange(len(domains))
    width = 0.35
    ax.bar(x - width/2, baseline_rates, width, label='Baseline', color='#e74c3c')
    ax.bar(x + width/2, finetuned_rates, width, label='Fine-tuned', color='#3498db')
    ax.set_xlabel('Domain')
    ax.set_ylabel('Inconsistency Rate')
    ax.set_title('Inconsistency Rate by Domain')
    ax.set_xticks(x)
    ax.set_xticklabels([d[:15] for d in domains], rotation=45, ha='right')
    ax.legend()

    # 3. Distribution of inconsistencies per scenario
    ax = axes[1, 0]
    baseline_counts = [r['num_inconsistencies'] for r in baseline['results']]
    finetuned_counts = [r['num_inconsistencies'] for r in finetuned['results']]

    ax.hist([baseline_counts, finetuned_counts], bins=range(0, max(max(baseline_counts), max(finetuned_counts)) + 2),
            label=['Baseline', 'Fine-tuned'], color=['#e74c3c', '#3498db'], alpha=0.7)
    ax.set_xlabel('Number of Inconsistencies')
    ax.set_ylabel('Number of Scenarios')
    ax.set_title('Distribution of Inconsistencies per Scenario')
    ax.legend()

    # 4. Scenario-by-scenario comparison
    ax = axes[1, 1]
    if len(baseline_counts) == len(finetuned_counts):
        ax.scatter(baseline_counts, finetuned_counts, alpha=0.6)
        max_val = max(max(baseline_counts), max(finetuned_counts))
        ax.plot([0, max_val], [0, max_val], 'r--', label='No change')
        ax.set_xlabel('Baseline Inconsistencies')
        ax.set_ylabel('Fine-tuned Inconsistencies')
        ax.set_title('Scenario-by-Scenario Comparison')
        ax.legend()
    else:
        ax.text(0.5, 0.5, 'Different number of scenarios', ha='center', va='center', transform=ax.transAxes)

    plt.tight_layout()
    output_file = RESULTS_DIR / f"{output_prefix}_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze evaluation results')
    parser.add_argument('--baseline', type=str, required=True, help='Baseline evaluation file')
    parser.add_argument('--finetuned', type=str, required=True, help='Fine-tuned evaluation file')
    parser.add_argument('--output-prefix', type=str, default='analysis', help='Output file prefix')

    args = parser.parse_args()

    baseline_file = RESULTS_DIR / args.baseline
    finetuned_file = RESULTS_DIR / args.finetuned

    if not baseline_file.exists():
        print(f"Error: Baseline file not found at {baseline_file}")
        sys.exit(1)

    if not finetuned_file.exists():
        print(f"Error: Fine-tuned file not found at {finetuned_file}")
        sys.exit(1)

    comparison = compare_models(baseline_file, finetuned_file, args.output_prefix)

    # Save comparison
    comparison_file = RESULTS_DIR / f"{args.output_prefix}_comparison.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2)

    print(f"\nComparison results saved to {comparison_file}")

if __name__ == "__main__":
    main()
