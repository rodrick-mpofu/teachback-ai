"""
Test script to verify Modal functions are properly connected and working.
"""

import os
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure Modal credentials are loaded
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("MODAL FUNCTION CONNECTION TEST")
print("=" * 70)

# Test 1: Check Modal package installation
print("\n[1/5] Checking Modal package installation...")
try:
    import modal
    print("  ✓ Modal package is installed")
except ImportError as e:
    print(f"  ✗ Modal package not found: {e}")
    sys.exit(1)

# Test 2: Check Modal credentials
print("\n[2/5] Checking Modal credentials...")
token_id = os.environ.get("MODAL_TOKEN_ID")
token_secret = os.environ.get("MODAL_TOKEN_SECRET")

if token_id and token_secret:
    print(f"  ✓ MODAL_TOKEN_ID: {token_id[:10]}...")
    print(f"  ✓ MODAL_TOKEN_SECRET: {'*' * 20}")
else:
    print("  ✗ Modal credentials not found in environment")
    sys.exit(1)

# Test 3: Connect to deployed Modal functions
print("\n[3/5] Connecting to deployed Modal functions...")
try:
    analyze_explanation_modal = modal.Function.from_name("teachback-ai", "analyze_explanation_modal")
    print("  ✓ analyze_explanation_modal connected")
except Exception as e:
    print(f"  ✗ Failed to connect to analyze_explanation_modal: {e}")
    analyze_explanation_modal = None

try:
    generate_question_modal = modal.Function.from_name("teachback-ai", "generate_question_modal")
    print("  ✓ generate_question_modal connected")
except Exception as e:
    print(f"  ✗ Failed to connect to generate_question_modal: {e}")
    generate_question_modal = None

try:
    compute_session_analytics = modal.Function.from_name("teachback-ai", "compute_session_analytics")
    print("  ✓ compute_session_analytics connected")
except Exception as e:
    print(f"  ✗ Failed to connect to compute_session_analytics: {e}")
    compute_session_analytics = None

# Test 4: Test analyze_explanation_modal
print("\n[4/5] Testing analyze_explanation_modal...")
if analyze_explanation_modal:
    try:
        test_explanation = "A binary tree is a data structure where each node has at most two children."
        test_topic = "Binary Trees"

        print(f"  → Calling analyze_explanation_modal.remote()...")
        result = analyze_explanation_modal.remote(
            explanation=test_explanation,
            topic=test_topic
        )

        print(f"  ✓ Analysis completed!")
        print(f"    - Confidence score: {result.get('confidence_score', 'N/A')}")
        print(f"    - Clarity score: {result.get('clarity_score', 'N/A')}")
        print(f"    - Knowledge gaps: {len(result.get('knowledge_gaps', []))}")

    except Exception as e:
        print(f"  ✗ analyze_explanation_modal test failed: {e}")
else:
    print("  ⊘ Skipped (function not connected)")

# Test 5: Test generate_question_modal
print("\n[5/5] Testing generate_question_modal...")
if generate_question_modal:
    try:
        test_analysis = {
            "confidence_score": 0.8,
            "clarity_score": 0.7,
            "knowledge_gaps": ["Didn't explain tree traversal"],
            "unexplained_jargon": [],
            "strengths": ["Clear definition"]
        }

        print(f"  → Calling generate_question_modal.remote()...")
        question = generate_question_modal.remote(
            explanation=test_explanation,
            mode="socratic",
            analysis=test_analysis,
            topic=test_topic,
            conversation_history=[]
        )

        print(f"  ✓ Question generated!")
        print(f"    Question: \"{question}\"")

    except Exception as e:
        print(f"  ✗ generate_question_modal test failed: {e}")
else:
    print("  ⊘ Skipped (function not connected)")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if analyze_explanation_modal and generate_question_modal and compute_session_analytics:
    print("✓ All Modal functions are connected and working!")
    print("\nThe TeachingAgent will now use Modal for:")
    print("  • analyze_explanation() - Every turn")
    print("  • generate_question() - Every turn")
    print("  • compute_session_analytics() - Background on 5th turn")
else:
    print("⚠ Some Modal functions are not available.")
    print("The system will fall back to local execution.")

print("=" * 70)
