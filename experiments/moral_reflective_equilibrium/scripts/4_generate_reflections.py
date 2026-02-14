"""
Step 4: Present inconsistencies to model and collect reflections
"""

import json
import sys
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)

def format_inconsistency(inconsistency):
    """Format an inconsistency for presentation to the model"""

    scenario = inconsistency['scenario']
    options = inconsistency['options']
    cycle = inconsistency['cycle']
    comparisons = inconsistency['comparisons']

    text = f"Scenario: {scenario}\n\n"
    text += "You made the following preference judgments:\n\n"

    for i, comp in enumerate(comparisons):
        winner_idx = comp['winner_idx']
        loser_idx = comp['option_a_idx'] if winner_idx == comp['option_b_idx'] else comp['option_b_idx']

        winner = options[winner_idx]
        loser = options[loser_idx]

        text += f"{i+1}. You preferred: \"{winner}\"\n"
        text += f"   Over: \"{loser}\"\n"
        text += f"   Your reasoning: {comp['reasoning'][:200]}...\n\n"

    text += "However, these preferences form a cycle (inconsistency):\n"
    cycle_str = " > ".join([f"Option {idx}" for idx in cycle]) + f" > Option {cycle[0]}"
    text += f"{cycle_str}\n"

    return text

def get_reflection(inconsistency, model=MODEL, variations=1):
    """Get model's reflection on an inconsistency"""

    inconsistency_text = format_inconsistency(inconsistency)

    prompt = f"""You are reflecting on an inconsistency in your previous ethical judgments.

{inconsistency_text}

This creates a logical contradiction. Please:

1. Carefully analyze why this inconsistency occurred
2. Reflect on the underlying values and principles at stake
3. Propose a coherent resolution that breaks the cycle
4. Explain which preference(s) you would revise and why
5. State your final, consistent ordering of these options

Be thorough in your reasoning and aim for a principled resolution."""

    reflections = []

    for _ in range(variations):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a thoughtful assistant reflecting on ethical inconsistencies in your reasoning. Be honest about your confusion and work toward a principled resolution."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE + 0.2,  # Slightly higher temp for diverse reflections
                max_tokens=1500
            )

            reflection_text = response.choices[0].message.content

            reflections.append({
                "reflection": reflection_text,
                "model": model
            })

            time.sleep(0.5)

        except Exception as e:
            print(f"Error getting reflection: {e}")

    return reflections

def generate_all_reflections(inconsistencies_file, output_file, model=MODEL, variations=REFLECTION_VARIATIONS):
    """Generate reflections for all inconsistencies"""

    with open(inconsistencies_file, 'r') as f:
        inconsistencies = json.load(f)

    results = []

    for idx, inconsistency in enumerate(tqdm(inconsistencies, desc="Generating reflections")):
        reflections = get_reflection(inconsistency, model, variations)

        result = {
            'inconsistency_id': idx,
            'scenario_id': inconsistency['scenario_id'],
            'domain': inconsistency['domain'],
            'scenario': inconsistency['scenario'],
            'options': inconsistency['options'],
            'cycle': inconsistency['cycle'],
            'original_comparisons': inconsistency['comparisons'],
            'reflections': reflections
        }

        results.append(result)

        # Save intermediate results
        if (idx + 1) % 5 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nGenerated reflections for {len(results)} inconsistencies")
    total_reflections = sum(len(r['reflections']) for r in results)
    print(f"Total reflection examples: {total_reflections}")

    return results

def main():
    inconsistencies_file = DATA_DIR / "inconsistencies.json"
    output_file = DATA_DIR / "reflections.json"

    if not inconsistencies_file.exists():
        print(f"Error: Inconsistencies file not found at {inconsistencies_file}")
        print("Please run 3_detect_inconsistencies.py first")
        sys.exit(1)

    print("Generating reflections...")
    generate_all_reflections(inconsistencies_file, output_file, MODEL, REFLECTION_VARIATIONS)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
