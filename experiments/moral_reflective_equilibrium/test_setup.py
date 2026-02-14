"""
Quick test to verify setup is correct
Run this before starting the main experiment
"""

import sys
from pathlib import Path
import os

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")

    required_packages = [
        ('openai', 'OpenAI API client'),
        ('numpy', 'Numerical computing'),
        ('pandas', 'Data analysis'),
        ('matplotlib', 'Plotting'),
        ('seaborn', 'Statistical visualization'),
        ('networkx', 'Graph algorithms'),
        ('tqdm', 'Progress bars'),
        ('scipy', 'Statistical tests'),
    ]

    all_ok = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package:<15} ({description})")
        except ImportError:
            print(f"  ✗ {package:<15} ({description}) - NOT FOUND")
            all_ok = False

    return all_ok


def test_api_key():
    """Test that OpenAI API key is set"""
    print("\nTesting API key...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ✗ OPENAI_API_KEY not set")
        print("    Set it with: export OPENAI_API_KEY='your-key'")
        return False

    if api_key.startswith('sk-'):
        print(f"  ✓ OPENAI_API_KEY is set (starts with 'sk-')")
        return True
    else:
        print(f"  ⚠ OPENAI_API_KEY is set but doesn't start with 'sk-'")
        print("    This might be an invalid key format")
        return False


def test_api_connection():
    """Test connection to OpenAI API"""
    print("\nTesting API connection...")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Try a simple API call
        response = client.models.list()

        print(f"  ✓ Successfully connected to OpenAI API")
        print(f"  ✓ Found {len(list(response.data))} models")
        return True

    except Exception as e:
        print(f"  ✗ Failed to connect: {e}")
        return False


def test_directories():
    """Test that required directories exist"""
    print("\nTesting directory structure...")

    base_dir = Path(__file__).parent
    required_dirs = [
        ('scripts', 'Pipeline scripts'),
        ('data', 'Data storage'),
        ('results', 'Results storage'),
    ]

    all_ok = True
    for dir_name, description in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name:<15} ({description})")
        else:
            print(f"  ✗ {dir_name:<15} ({description}) - NOT FOUND")
            all_ok = False

    return all_ok


def test_scripts():
    """Test that all required scripts exist"""
    print("\nTesting pipeline scripts...")

    base_dir = Path(__file__).parent
    scripts_dir = base_dir / "scripts"

    required_scripts = [
        '1_generate_scenarios.py',
        '2_collect_preferences.py',
        '3_detect_inconsistencies.py',
        '4_generate_reflections.py',
        '5_prepare_finetuning.py',
        '6_run_finetuning.py',
        '7_evaluate.py',
        '8_analyze_results.py',
    ]

    all_ok = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"  ✓ {script}")
        else:
            print(f"  ✗ {script} - NOT FOUND")
            all_ok = False

    return all_ok


def test_config():
    """Test that config can be imported"""
    print("\nTesting configuration...")

    try:
        sys.path.append(str(Path(__file__).parent))
        import config

        print(f"  ✓ Config imported successfully")
        print(f"  ✓ Model: {config.MODEL}")
        print(f"  ✓ Finetune base: {config.FINETUNE_BASE_MODEL}")
        print(f"  ✓ Scenarios per domain: {config.NUM_SCENARIOS_PER_DOMAIN}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to import config: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("MORAL REFLECTIVE EQUILIBRIUM - SETUP TEST")
    print("="*70)

    results = {
        'Imports': test_imports(),
        'API Key': test_api_key(),
        'API Connection': test_api_connection(),
        'Directories': test_directories(),
        'Scripts': test_scripts(),
        'Configuration': test_config(),
    }

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n✓ All tests passed! You're ready to run the experiment.")
        print("\nNext steps:")
        print("  1. Review config.py and adjust parameters if needed")
        print("  2. Run the experiment:")
        print("     python run_experiment.py")
        print("  or")
        print("     ./run_pipeline.sh data")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Set API key: export OPENAI_API_KEY='your-key'")
        print("  - Create missing directories: mkdir -p data results")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
