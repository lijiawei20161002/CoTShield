"""
Step 5: Prepare finetuning data from reflections
Converts reflections into OpenAI finetuning format
"""

import json
import sys
from pathlib import Path
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

def create_finetuning_example(reflection_data):
    """Create a finetuning example from a reflection"""

    scenario = reflection_data['scenario']
    options = reflection_data['options']
    cycle = reflection_data['cycle']
    original_comparisons = reflection_data['original_comparisons']

    # Format the inconsistency
    user_message = f"Scenario: {scenario}\n\n"
    user_message += "You previously made these preference judgments:\n\n"

    for i, comp in enumerate(original_comparisons):
        winner_idx = comp['winner_idx']
        loser_idx = comp['option_a_idx'] if winner_idx == comp['option_b_idx'] else comp['option_b_idx']
        winner = options[winner_idx]
        loser = options[loser_idx]

        user_message += f"{i+1}. Preferred: \"{winner}\"\n   Over: \"{loser}\"\n\n"

    user_message += "These preferences form a cycle (inconsistency). "
    user_message += "Please reflect on this inconsistency and provide a coherent resolution."

    # Each reflection becomes a training example
    examples = []
    for reflection in reflection_data['reflections']:
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a thoughtful assistant that reflects on ethical inconsistencies and provides principled resolutions."
                },
                {
                    "role": "user",
                    "content": user_message
                },
                {
                    "role": "assistant",
                    "content": reflection['reflection']
                }
            ]
        }
        examples.append(example)

    return examples

def prepare_finetuning_data(reflections_file, output_file, train_split=TRAIN_SPLIT):
    """Prepare finetuning data in OpenAI format"""

    with open(reflections_file, 'r') as f:
        reflections = json.load(f)

    all_examples = []

    for reflection_data in reflections:
        examples = create_finetuning_example(reflection_data)
        for ex in examples:
            ex['metadata'] = {
                'scenario_id': reflection_data['scenario_id'],
                'domain': reflection_data['domain'],
                'inconsistency_id': reflection_data['inconsistency_id']
            }
        all_examples.extend(examples)

    # Shuffle
    random.shuffle(all_examples)

    # Split train/validation
    split_idx = int(len(all_examples) * train_split)
    train_examples = all_examples[:split_idx]
    val_examples = all_examples[split_idx:]

    # Save training data (without metadata for finetuning API)
    train_file = output_file.parent / "finetuning_train.jsonl"
    with open(train_file, 'w') as f:
        for ex in train_examples:
            # Remove metadata for API submission
            clean_ex = {"messages": ex["messages"]}
            f.write(json.dumps(clean_ex) + '\n')

    # Save validation data
    val_file = output_file.parent / "finetuning_val.jsonl"
    with open(val_file, 'w') as f:
        for ex in val_examples:
            clean_ex = {"messages": ex["messages"]}
            f.write(json.dumps(clean_ex) + '\n')

    # Save full data with metadata for reference
    full_file = output_file.parent / "finetuning_full.json"
    with open(full_file, 'w') as f:
        json.dump({
            'train': train_examples,
            'val': val_examples
        }, f, indent=2)

    print(f"\nPrepared {len(all_examples)} total finetuning examples")
    print(f"  Training: {len(train_examples)}")
    print(f"  Validation: {len(val_examples)}")

    # Print domain distribution
    from collections import Counter
    train_domains = Counter([ex['metadata']['domain'] for ex in train_examples])
    print("\nTraining examples by domain:")
    for domain, count in train_domains.most_common():
        print(f"  {domain}: {count}")

    print(f"\nFiles saved:")
    print(f"  {train_file}")
    print(f"  {val_file}")
    print(f"  {full_file}")

    return train_file, val_file

def main():
    reflections_file = DATA_DIR / "reflections.json"
    output_file = DATA_DIR / "finetuning_data.json"

    if not reflections_file.exists():
        print(f"Error: Reflections file not found at {reflections_file}")
        print("Please run 4_generate_reflections.py first")
        sys.exit(1)

    print("Preparing finetuning data...")
    prepare_finetuning_data(reflections_file, output_file)

if __name__ == "__main__":
    main()
