"""
Utility functions for the moral reflective equilibrium experiment
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
import hashlib


def load_json(file_path: Path) -> Any:
    """Load JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Any, file_path: Path, indent: int = 2):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


def load_jsonl(file_path: Path) -> List[Dict]:
    """Load JSONL file"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def save_jsonl(data: List[Dict], file_path: Path):
    """Save data to JSONL file"""
    with open(file_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')


def rate_limit_sleep(seconds: float = 0.5):
    """Sleep to respect API rate limits"""
    time.sleep(seconds)


def hash_string(s: str) -> str:
    """Generate hash of a string for deduplication"""
    return hashlib.md5(s.encode()).hexdigest()


def deduplicate_scenarios(scenarios: List[Dict]) -> List[Dict]:
    """Remove duplicate scenarios based on scenario text"""
    seen_hashes = set()
    unique_scenarios = []

    for scenario in scenarios:
        text_hash = hash_string(scenario['scenario'])
        if text_hash not in seen_hashes:
            seen_hashes.add(text_hash)
            unique_scenarios.append(scenario)

    return unique_scenarios


def validate_scenario(scenario: Dict) -> bool:
    """Validate scenario has required fields"""
    required_fields = ['scenario', 'options']

    if not all(field in scenario for field in required_fields):
        return False

    if not isinstance(scenario['options'], list):
        return False

    if len(scenario['options']) < 3:
        return False

    return True


def validate_finetuning_data(data: List[Dict]) -> tuple:
    """
    Validate finetuning data format for OpenAI API
    Returns (is_valid, error_message)
    """
    for i, example in enumerate(data):
        # Check has messages field
        if 'messages' not in example:
            return False, f"Example {i}: Missing 'messages' field"

        messages = example['messages']

        if not isinstance(messages, list):
            return False, f"Example {i}: 'messages' must be a list"

        if len(messages) < 2:
            return False, f"Example {i}: Must have at least 2 messages"

        # Check message format
        for j, msg in enumerate(messages):
            if 'role' not in msg:
                return False, f"Example {i}, message {j}: Missing 'role'"

            if 'content' not in msg:
                return False, f"Example {i}, message {j}: Missing 'content'"

            if msg['role'] not in ['system', 'user', 'assistant']:
                return False, f"Example {i}, message {j}: Invalid role '{msg['role']}'"

        # Check last message is from assistant
        if messages[-1]['role'] != 'assistant':
            return False, f"Example {i}: Last message must be from assistant"

    return True, "Valid"


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimate of token count
    More accurate would use tiktoken library
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4


def estimate_api_cost(
    num_scenarios: int,
    options_per_scenario: int = 4,
    reflection_variations: int = 2,
    model_input_price_per_1k: float = 0.01,
    model_output_price_per_1k: float = 0.03
) -> Dict[str, float]:
    """
    Estimate API costs for experiment
    Prices are examples - update based on actual OpenAI pricing
    """

    # Pairwise comparisons
    num_comparisons = num_scenarios * (options_per_scenario * (options_per_scenario - 1)) // 2

    # Estimate tokens per comparison
    input_tokens_per_comparison = 300
    output_tokens_per_comparison = 500

    comparison_cost = (
        (num_comparisons * input_tokens_per_comparison / 1000 * model_input_price_per_1k) +
        (num_comparisons * output_tokens_per_comparison / 1000 * model_output_price_per_1k)
    )

    # Estimate inconsistencies (assume 30% of scenarios have inconsistencies)
    num_inconsistencies = int(num_scenarios * 0.3)
    num_reflections = num_inconsistencies * reflection_variations

    input_tokens_per_reflection = 800
    output_tokens_per_reflection = 1000

    reflection_cost = (
        (num_reflections * input_tokens_per_reflection / 1000 * model_input_price_per_1k) +
        (num_reflections * output_tokens_per_reflection / 1000 * model_output_price_per_1k)
    )

    # Finetuning (rough estimate: $0.008 per 1k tokens for gpt-4o-mini)
    finetuning_tokens = num_reflections * (input_tokens_per_reflection + output_tokens_per_reflection)
    finetuning_cost = finetuning_tokens / 1000 * 0.008

    # Evaluation (both baseline and finetuned)
    eval_cost = comparison_cost * 2

    return {
        'comparison': comparison_cost,
        'reflection': reflection_cost,
        'finetuning': finetuning_cost,
        'evaluation': eval_cost,
        'total': comparison_cost + reflection_cost + finetuning_cost + eval_cost
    }


def print_cost_estimate(num_scenarios: int, options_per_scenario: int = 4):
    """Print cost estimate"""
    costs = estimate_api_cost(num_scenarios, options_per_scenario)

    print("\n" + "="*50)
    print("ESTIMATED API COSTS")
    print("="*50)
    print(f"Number of scenarios: {num_scenarios}")
    print(f"Options per scenario: {options_per_scenario}")
    print(f"\nBreakdown:")
    print(f"  Preference collection: ${costs['comparison']:.2f}")
    print(f"  Reflection generation: ${costs['reflection']:.2f}")
    print(f"  Fine-tuning: ${costs['finetuning']:.2f}")
    print(f"  Evaluation: ${costs['evaluation']:.2f}")
    print(f"\nTotal estimated cost: ${costs['total']:.2f}")
    print("="*50)


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def print_progress_summary(
    scenarios_done: int,
    total_scenarios: int,
    start_time: float
):
    """Print progress summary"""
    elapsed = time.time() - start_time
    rate = scenarios_done / elapsed if elapsed > 0 else 0
    remaining = (total_scenarios - scenarios_done) / rate if rate > 0 else 0

    print(f"\nProgress: {scenarios_done}/{total_scenarios} scenarios")
    print(f"Elapsed: {format_time(elapsed)}")
    print(f"Rate: {rate*60:.1f} scenarios/min")
    print(f"Est. remaining: {format_time(remaining)}")


if __name__ == "__main__":
    # Example usage
    print("Moral Reflective Equilibrium - Utilities")
    print_cost_estimate(num_scenarios=50, options_per_scenario=4)
