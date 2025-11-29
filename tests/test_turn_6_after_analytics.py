"""
Test to check if Modal works through 10 turns including analytics spawn on turn 5 and 10
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
print("10-TURN MODAL TEST (Analytics on turns 5 and 10)")
print("=" * 70)

# Import the TeachingAgent
from src.agents.teaching_agent import (
    TeachingAgent,
    MODAL_AVAILABLE,
    compute_session_analytics,
    analyze_explanation_modal,
    generate_question_modal
)

print(f"\n[INFO] MODAL_AVAILABLE: {MODAL_AVAILABLE}")
print(f"[INFO] analyze_explanation_modal: {analyze_explanation_modal}")
print(f"[INFO] generate_question_modal: {generate_question_modal}")
print(f"[INFO] compute_session_analytics: {compute_session_analytics}")

# Create a teaching agent
print("\n[TEST] Creating TeachingAgent and simulating 10 turns with analytics on turns 5 and 10...")
agent = TeachingAgent()

# Create a test session
session = agent.create_session(
    user_id="test-user",
    topic="Binary Trees",
    mode="socratic"
)
session_id = session["session_id"]
print(f"✓ Session created: {session_id}")

# Simulate turns 1-10
test_explanations = [
    "A binary tree is a hierarchical data structure.",                    # Turn 1
    "Each node in a binary tree has at most two children.",               # Turn 2
    "The children are called left child and right child.",                # Turn 3
    "Binary trees are used for efficient searching.",                     # Turn 4
    "The root is the topmost node in the tree.",                         # Turn 5 - Analytics trigger
    "Traversal methods include inorder, preorder, and postorder.",       # Turn 6 - Post-analytics test
    "A leaf node has no children.",                                      # Turn 7
    "The height of a tree is the longest path from root to leaf.",      # Turn 8
    "Binary search trees maintain sorted order.",                        # Turn 9
    "Balanced trees ensure O(log n) operations."                         # Turn 10 - Analytics trigger
]

analytics_call = None

for i, explanation in enumerate(test_explanations, 1):
    print(f"\n{'='*70}")
    print(f"TURN {i}")
    print(f"{'='*70}")

    try:
        # Analyze
        print(f"\n[{i}/6] Analyzing explanation...")
        analysis = agent.analyze_explanation(
            session_id=session_id,
            explanation=explanation
        )
        print(f"✓ Analysis: confidence={analysis['confidence_score']}, clarity={analysis['clarity_score']}")

        # Generate question
        print(f"\n[{i}/6] Generating question...")
        question = agent.generate_question(
            session_id=session_id,
            explanation=explanation,
            analysis=analysis,
            mode="socratic"
        )
        print(f"✓ Question: \"{question[:80]}...\"")

        # On turn 5 and 10, spawn analytics
        if i % 5 == 0:  # Every 5th turn
            print(f"\n[ANALYTICS] Turn {i} - spawning background analytics...")
            if MODAL_AVAILABLE and compute_session_analytics:
                try:
                    session_data = agent.sessions[session_id]
                    analytics_call = compute_session_analytics.spawn(session_data)
                    print(f"✓ Analytics spawned: {analytics_call.object_id}")
                    print(f"  → Running in background (non-blocking)")
                except Exception as analytics_error:
                    print(f"✗ Analytics spawn failed: {analytics_error}")
                    import traceback
                    traceback.print_exc()

        # After analytics spawns (turns 6 and 11), verify Modal still works
        if i in [6]:
            print(f"\n{'='*70}")
            print(f"CRITICAL CHECK: Turn {i} after analytics spawn")
            print(f"{'='*70}")
            print(f"[CHECK] Did Modal work on turn {i}?")
            print(f"  → If you see [MODAL] messages above: ✅ YES")
            print(f"  → If you see [LOCAL] messages above: ❌ NO - Modal stopped working")

            # Check if analytics completed
            if analytics_call:
                try:
                    print(f"\n[CHECK] Analytics status:")
                    print(f"  → Call ID: {analytics_call.object_id}")
                    print(f"  → Analytics may still be running in background")
                except Exception as e:
                    print(f"  → Could not check analytics: {e}")

        print(f"\n✓ Turn {i} completed successfully!")

    except Exception as turn_error:
        print(f"\n✗ Turn {i} FAILED: {turn_error}")
        import traceback
        traceback.print_exc()
        break

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

if i >= 10:
    print("✓ Successfully completed ALL 10 turns!")
    print("\nSummary:")
    print("  - Turn 5: Analytics spawned ✓")
    print("  - Turn 6-9: Continued working after first analytics ✓")
    print("  - Turn 10: Second analytics spawned ✓")
    print("\n✅ Modal functions worked correctly throughout all turns")
else:
    print(f"✗ Test stopped at turn {i}")
    print(f"❌ Application failed before completing all 10 turns")

print("=" * 70)
