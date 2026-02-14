"""
Step 3: Detect inconsistencies (transitivity violations)
Looks for cycles in preference graphs: A > B > C > A
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import networkx as nx

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

def build_preference_graph(comparisons):
    """Build directed graph from pairwise comparisons"""
    G = nx.DiGraph()

    for comp in comparisons:
        winner = comp['winner_idx']
        loser = comp['option_a_idx'] if winner == comp['option_b_idx'] else comp['option_b_idx']
        G.add_edge(winner, loser)

    return G

def find_cycles(G):
    """Find all simple cycles in the preference graph"""
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except:
        return []

def find_inconsistencies(preferences_file, output_file):
    """Find all transitivity violations in the preferences"""

    with open(preferences_file, 'r') as f:
        preferences = json.load(f)

    inconsistencies = []

    for scenario in preferences:
        scenario_id = scenario['scenario_id']
        comparisons = scenario['comparisons']

        if len(comparisons) < 3:
            continue

        # Build preference graph
        G = build_preference_graph(comparisons)

        # Find cycles (inconsistencies)
        cycles = find_cycles(G)

        for cycle in cycles:
            # Get the comparisons involved in this cycle
            cycle_comparisons = []

            for i in range(len(cycle)):
                from_idx = cycle[i]
                to_idx = cycle[(i + 1) % len(cycle)]

                # Find the comparison between these two options
                for comp in comparisons:
                    if comp['winner_idx'] == from_idx:
                        loser = comp['option_a_idx'] if from_idx == comp['option_b_idx'] else comp['option_b_idx']
                        if loser == to_idx:
                            cycle_comparisons.append(comp)
                            break

            if len(cycle_comparisons) == len(cycle):
                inconsistency = {
                    'scenario_id': scenario_id,
                    'domain': scenario['domain'],
                    'scenario': scenario['scenario'],
                    'options': scenario['options'],
                    'cycle': cycle,
                    'comparisons': cycle_comparisons,
                    'cycle_length': len(cycle)
                }
                inconsistencies.append(inconsistency)

    # Save inconsistencies
    with open(output_file, 'w') as f:
        json.dump(inconsistencies, f, indent=2)

    print(f"\nFound {len(inconsistencies)} inconsistencies across scenarios")

    # Print statistics
    cycle_lengths = defaultdict(int)
    domains = defaultdict(int)

    for incon in inconsistencies:
        cycle_lengths[incon['cycle_length']] += 1
        domains[incon['domain']] += 1

    print("\nInconsistencies by cycle length:")
    for length in sorted(cycle_lengths.keys()):
        print(f"  {length}-cycles: {cycle_lengths[length]}")

    print("\nInconsistencies by domain:")
    for domain in sorted(domains.keys()):
        print(f"  {domain}: {domains[domain]}")

    return inconsistencies

def main():
    preferences_file = DATA_DIR / "preferences.json"
    output_file = DATA_DIR / "inconsistencies.json"

    if not preferences_file.exists():
        print(f"Error: Preferences file not found at {preferences_file}")
        print("Please run 2_collect_preferences.py first")
        sys.exit(1)

    print("Detecting inconsistencies...")
    find_inconsistencies(preferences_file, output_file)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
