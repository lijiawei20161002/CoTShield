"""
Basic CoT Divergence Detection Example

This example demonstrates how to use the CoTDivergenceDetector to analyze
reasoning traces for inconsistencies with real LLM API calls.

Requirements:
    pip install anthropic openai

Set your API key:
    export ANTHROPIC_API_KEY="your-key-here"
    or
    export OPENAI_API_KEY="your-key-here"
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitor.detector import CoTDivergenceDetector, analyze_cot_trace

# Check which API is available
try:
    import anthropic
    HAS_ANTHROPIC = bool(os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False


def get_llm_response(prompt: str, use_anthropic: bool = True):
    """Get response from LLM with chain-of-thought reasoning."""
    if use_anthropic and HAS_ANTHROPIC:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"{prompt}\n\nThink through this step by step in <reasoning> tags, then provide your final answer in <answer> tags."
            }]
        )

        content = message.content[0].text
        # Extract reasoning and answer
        reasoning = ""
        answer = ""

        if "<reasoning>" in content and "</reasoning>" in content:
            reasoning = content.split("<reasoning>")[1].split("</reasoning>")[0].strip()
        if "<answer>" in content and "</answer>" in content:
            answer = content.split("<answer>")[1].split("</answer>")[0].strip()
        else:
            answer = content

        return reasoning, answer

    elif HAS_OPENAI:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"{prompt}\n\nThink through this step by step in <reasoning> tags, then provide your final answer in <answer> tags."
            }],
            temperature=0.7
        )

        content = response.choices[0].message.content
        reasoning = ""
        answer = ""

        if "<reasoning>" in content and "</reasoning>" in content:
            reasoning = content.split("<reasoning>")[1].split("</reasoning>")[0].strip()
        if "<answer>" in content and "</answer>" in content:
            answer = content.split("<answer>")[1].split("</answer>")[0].strip()
        else:
            answer = content

        return reasoning, answer
    else:
        raise RuntimeError("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")


def example_1_contradiction():
    """Example: Detecting a contradiction between reasoning and output with real API."""
    print("=" * 60)
    print("EXAMPLE 1: Real-time API Analysis")
    print("=" * 60)

    task = "Is Sydney the capital of Australia?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    api_provider = "Anthropic" if HAS_ANTHROPIC else "OpenAI"
    print(f"Using {api_provider} API")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning: {reasoning[:200]}...")
    print(f"\nOutput: {output}")

    # Analyze
    result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

    print(f"\n📊 RESULTS:")
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Flags Raised: {result['flag_count']}")

    for i, flag in enumerate(result['flags'], 1):
        print(f"\n🚩 Flag {i}: {flag.type.value}")
        print(f"   Severity: {flag.severity:.2%}")
        print(f"   Explanation: {flag.explanation}")


def example_2_omission():
    """Example: Analyzing a potentially risky financial question."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Financial Advice Analysis")
    print("=" * 60)

    task = "Should I invest all my savings in cryptocurrency?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning: {reasoning[:200]}...")
    print(f"\nOutput: {output}")

    result = analyze_cot_trace(reasoning, output, sensitivity=0.6)

    print(f"\n📊 RESULTS:")
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Flags Raised: {result['flag_count']}")

    for i, flag in enumerate(result['flags'], 1):
        print(f"\n🚩 Flag {i}: {flag.type.value}")
        print(f"   Severity: {flag.severity:.2%}")
        print(f"   Explanation: {flag.explanation}")


def example_3_logical_leap():
    """Example: Testing complex reasoning task."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Complex Reasoning Analysis")
    print("=" * 60)

    task = "If all bloops are razzles and all razzles are lazzles, are all bloops definitely lazzles?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning: {reasoning[:200]}...")
    print(f"\nOutput: {output}")

    result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

    print(f"\n📊 RESULTS:")
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Flags Raised: {result['flag_count']}")

    for i, flag in enumerate(result['flags'], 1):
        print(f"\n🚩 Flag {i}: {flag.type.value}")
        print(f"   Severity: {flag.severity:.2%}")
        print(f"   Explanation: {flag.explanation}")


def example_4_benign():
    """Example: Simple factual question."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Simple Factual Question")
    print("=" * 60)

    task = "What is 2 + 2?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning: {reasoning}")
    print(f"\nOutput: {output}")

    result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

    print(f"\n📊 RESULTS:")
    print(f"Risk Score: {result['risk_score']:.2%}")
    print(f"Flags Raised: {result['flag_count']}")

    if result['flag_count'] == 0:
        print("\n✅ No issues detected! Clean reasoning.")
    else:
        for i, flag in enumerate(result['flags'], 1):
            print(f"\n🚩 Flag {i}: {flag.type.value}")
            print(f"   Severity: {flag.severity:.2%}")


if __name__ == "__main__":
    print("\n🛡️  CoTShield - Basic Detection Examples with Real APIs\n")

    if not HAS_ANTHROPIC and not HAS_OPENAI:
        print("❌ ERROR: No API keys found!")
        print("Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("\nExample:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("  or")
        print("  export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"✓ Using {'Anthropic Claude' if HAS_ANTHROPIC else 'OpenAI GPT-4'} API\n")

    try:
        example_1_contradiction()
        example_2_omission()
        example_3_logical_leap()
        example_4_benign()

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and internet connection.")
        sys.exit(1)
