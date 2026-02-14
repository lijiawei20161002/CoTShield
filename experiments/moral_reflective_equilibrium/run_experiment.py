"""
Main experiment runner for moral reflective equilibrium study
"""

import sys
import subprocess
from pathlib import Path
import argparse

# Add current directory to path
sys.path.append(str(Path(__file__).parent))
from config import *

def run_step(script_name, description, args=[]):
    """Run a step of the experiment"""
    print("\n" + "="*70)
    print(f"STEP: {description}")
    print("="*70)

    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)] + args

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with error code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run moral reflective equilibrium experiment')
    parser.add_argument('--steps', type=str, default='all',
                        help='Comma-separated list of steps to run (e.g., "1,2,3" or "all")')
    parser.add_argument('--skip-finetuning', action='store_true',
                        help='Skip the finetuning step (step 6)')
    parser.add_argument('--finetuned-model', type=str,
                        help='Use existing finetuned model for evaluation')

    args = parser.parse_args()

    print("="*70)
    print("MORAL REFLECTIVE EQUILIBRIUM EXPERIMENT")
    print("="*70)
    print("\nThis experiment will:")
    print("1. Generate scenarios with multiple choices")
    print("2. Collect model preferences on pairwise comparisons")
    print("3. Detect inconsistencies (transitivity violations)")
    print("4. Generate reflections on inconsistencies")
    print("5. Prepare finetuning data")
    print("6. Run finetuning (if not skipped)")
    print("7. Evaluate baseline and finetuned models")
    print("8. Analyze and visualize results")

    if args.steps == 'all':
        steps = list(range(1, 9))
    else:
        steps = [int(s) for s in args.steps.split(',')]

    if args.skip_finetuning and 6 in steps:
        steps.remove(6)

    success = True

    # Step 1: Generate scenarios
    if 1 in steps:
        success = run_step('1_generate_scenarios.py', 'Generate scenarios')
        if not success:
            return

    # Step 2: Collect preferences
    if 2 in steps:
        success = run_step('2_collect_preferences.py', 'Collect model preferences')
        if not success:
            return

    # Step 3: Detect inconsistencies
    if 3 in steps:
        success = run_step('3_detect_inconsistencies.py', 'Detect inconsistencies')
        if not success:
            return

    # Step 4: Generate reflections
    if 4 in steps:
        success = run_step('4_generate_reflections.py', 'Generate reflections')
        if not success:
            return

    # Step 5: Prepare finetuning data
    if 5 in steps:
        success = run_step('5_prepare_finetuning.py', 'Prepare finetuning data')
        if not success:
            return

    # Step 6: Run finetuning
    if 6 in steps:
        print("\n" + "="*70)
        print("STEP 6: Run finetuning")
        print("="*70)
        print("\nNote: Finetuning can take 20-60 minutes.")
        print("You can run this step separately if you prefer:")
        print("  python scripts/6_run_finetuning.py")
        print("\nPress Enter to continue or Ctrl+C to skip...")
        try:
            input()
            success = run_step('6_run_finetuning.py', 'Run finetuning')
            if not success:
                return
        except KeyboardInterrupt:
            print("\nSkipping finetuning step")

    # Step 7: Evaluate
    if 7 in steps:
        print("\n" + "="*70)
        print("STEP 7: Evaluate models")
        print("="*70)

        # Evaluate baseline
        success = run_step('7_evaluate.py', 'Evaluate baseline model',
                           ['--model', MODEL, '--eval-type', 'original'])
        if not success:
            return

        # Evaluate finetuned model
        if args.finetuned_model:
            success = run_step('7_evaluate.py', 'Evaluate fine-tuned model',
                               ['--model', args.finetuned_model, '--eval-type', 'original'])
            if not success:
                return
        else:
            print("\nNote: Finetuned model evaluation requires --finetuned-model argument")

    # Step 8: Analyze results
    if 8 in steps:
        if args.finetuned_model:
            print("\n" + "="*70)
            print("STEP 8: Analyze results")
            print("="*70)

            baseline_file = f"eval_original_{MODEL.replace('/', '_').replace(':', '_')}.json"
            finetuned_file = f"eval_original_{args.finetuned_model.replace('/', '_').replace(':', '_')}.json"

            success = run_step('8_analyze_results.py', 'Analyze results',
                               ['--baseline', baseline_file, '--finetuned', finetuned_file])
        else:
            print("\nNote: Analysis requires --finetuned-model argument")

    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    print("\nResults are saved in the 'results' directory")
    print("See README.md for more information")

if __name__ == "__main__":
    main()
