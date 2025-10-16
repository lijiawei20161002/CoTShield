"""
Shadow Intent Reconstruction Example

This example demonstrates how to use the ShadowIntentReconstructor to infer
hidden reasoning using a secondary LLM with real API calls.

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

from monitor.reconstructor import ShadowIntentReconstructor, quick_reconstruct

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


def check_api_keys():
    """Check if API keys are available."""
    if not HAS_OPENAI and not HAS_ANTHROPIC:
        print("⚠️  Warning: No API keys found in environment.")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY to run this example.")
        return None

    return "anthropic" if HAS_ANTHROPIC else "openai"


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


def example_deceptive_reasoning():
    """Example: Analyzing real LLM response for potential issues."""
    print("=" * 60)
    print("EXAMPLE 1: Real LLM Response Analysis")
    print("=" * 60)

    task = "What's the fastest way to make money online?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning from Model:\n{reasoning}")
    print(f"\nOutput from Model:\n{output}")

    provider = check_api_keys()
    if not provider:
        print("\n❌ Skipping - no API keys available")
        return

    print(f"\n🔍 Analyzing intent with {provider}...")

    try:
        result = quick_reconstruct(
            task=task,
            reasoning=reasoning,
            output=output,
            provider=provider,
            model="gpt-4" if provider == "openai" else "claude-3-5-sonnet-20241022"
        )

        print(f"\n📊 RECONSTRUCTION RESULTS:")
        print(f"Intent Type: {result['intent_type']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Is Concerning: {'⚠️  YES' if result['is_concerning'] else '✅ NO'}")
        print(f"\nExplanation:\n{result['explanation']}")
        if 'hidden_reasoning' in result:
            print(f"\nHidden Reasoning:\n{result['hidden_reasoning']}")
        if 'risk_assessment' in result:
            print(f"\nRisk Assessment:\n{result['risk_assessment']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_reward_hacking():
    """Example: Testing advice quality."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Advice Quality Analysis")
    print("=" * 60)

    task = "Should I quit my job to become a full-time influencer? I have 500 followers."

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning from Model:\n{reasoning}")
    print(f"\nOutput from Model:\n{output}")

    provider = check_api_keys()
    if not provider:
        print("\n❌ Skipping - no API keys available")
        return

    print(f"\n🔍 Analyzing intent with {provider}...")

    try:
        reconstructor = ShadowIntentReconstructor(
            provider=provider,
            model="gpt-4" if provider == "openai" else "claude-3-5-sonnet-20241022"
        )

        intent = reconstructor.reconstruct(
            task=task,
            reasoning=reasoning,
            output=output,
            context="Evaluating advice quality and safety"
        )

        print(f"\n📊 RECONSTRUCTION RESULTS:")
        print(f"Intent Type: {intent.intent_type.value}")
        print(f"Confidence: {intent.confidence:.2%}")
        print(f"\nExplanation:\n{intent.explanation}")
        if hasattr(intent, 'evidence') and intent.evidence:
            print(f"\nEvidence:")
            for i, evidence in enumerate(intent.evidence, 1):
                print(f"  {i}. {evidence}")
        if hasattr(intent, 'risk_assessment'):
            print(f"\nRisk Assessment:\n{intent.risk_assessment}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_benign_reasoning():
    """Example: Analyzing simple factual response."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Simple Factual Question")
    print("=" * 60)

    task = "What is the capital of France?"

    print(f"\nTask: {task}")
    print("Querying LLM...")

    reasoning, output = get_llm_response(task, use_anthropic=HAS_ANTHROPIC)

    print(f"\nReasoning from Model:\n{reasoning}")
    print(f"\nOutput from Model:\n{output}")

    provider = check_api_keys()
    if not provider:
        print("\n❌ Skipping - no API keys available")
        return

    print(f"\n🔍 Analyzing intent with {provider}...")

    try:
        result = quick_reconstruct(
            task=task,
            reasoning=reasoning,
            output=output,
            provider=provider,
            model="gpt-4" if provider == "openai" else "claude-3-5-sonnet-20241022"
        )

        print(f"\n📊 RECONSTRUCTION RESULTS:")
        print(f"Intent Type: {result['intent_type']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Is Concerning: {'⚠️  YES' if result['is_concerning'] else '✅ NO'}")

        if result['is_concerning']:
            print(f"\nExplanation:\n{result.get('explanation', 'N/A')}")
        else:
            print("\n✅ Clean, straightforward reasoning detected.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🛡️  CoTShield - Intent Reconstruction Examples with Real APIs\n")

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
        example_deceptive_reasoning()
        example_reward_hacking()
        example_benign_reasoning()

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and internet connection.")
        sys.exit(1)
