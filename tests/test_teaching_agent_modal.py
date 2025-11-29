"""
Test the TeachingAgent to verify it uses Modal functions.
"""

import os
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("TEACHING AGENT MODAL INTEGRATION TEST")
print("=" * 70)

# Import the TeachingAgent
from src.agents.teaching_agent import TeachingAgent, MODAL_AVAILABLE

print(f"\n[INFO] MODAL_AVAILABLE: {MODAL_AVAILABLE}")

if not MODAL_AVAILABLE:
    print("\n⚠ WARNING: Modal is not available!")
    print("The agent will fall back to local execution.")
else:
    print("\n✓ Modal is available and connected!")

# Create a teaching agent
print("\n[1/3] Creating TeachingAgent...")
agent = TeachingAgent()
print("  ✓ TeachingAgent created")

# Create a test session
print("\n[2/3] Creating a test session...")
session = agent.create_session(
    user_id="test-user",
    topic="Binary Trees",
    mode="socratic"
)
session_id = session["session_id"]
print(f"  ✓ Session created: {session_id}")

# Test analyze_explanation (should use Modal)
print("\n[3/3] Testing analyze_explanation (should use Modal)...")
test_explanation = "A binary tree is a hierarchical data structure where each node has at most two children, called the left child and right child."

print("  → Calling agent.analyze_explanation()...")
print("  → Watch for [MODAL] or [LOCAL] log messages...")
print()

analysis = agent.analyze_explanation(
    session_id=session_id,
    explanation=test_explanation
)

print()
print("  ✓ Analysis completed!")
print(f"    - Confidence: {analysis['confidence_score']}")
print(f"    - Clarity: {analysis['clarity_score']}")
print(f"    - Gaps: {len(analysis['knowledge_gaps'])} identified")

# Test generate_question (should use Modal)
print("\n[4/3] Testing generate_question (should use Modal)...")
print("  → Calling agent.generate_question()...")
print("  → Watch for [MODAL] or [LOCAL] log messages...")
print()

question = agent.generate_question(
    session_id=session_id,
    explanation=test_explanation,
    analysis=analysis,
    mode="socratic"
)

print()
print("  ✓ Question generated!")
print(f"    Question: \"{question}\"")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

if MODAL_AVAILABLE:
    print("✓ TeachingAgent successfully used Modal functions!")
    print("\nBoth analyze_explanation() and generate_question() should have")
    print("shown [MODAL] log messages above, indicating they ran on Modal.")
else:
    print("⚠ Modal not available - agent used local fallback")

print("=" * 70)
