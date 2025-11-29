"""
Test to reproduce the "stops after turn 5" issue
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
print("TURN 5 ISSUE DEBUGGING TEST")
print("=" * 70)

# Import the TeachingAgent
from src.agents.teaching_agent import TeachingAgent, MODAL_AVAILABLE, compute_session_analytics

print(f"\n[INFO] MODAL_AVAILABLE: {MODAL_AVAILABLE}")
print(f"[INFO] compute_session_analytics: {compute_session_analytics}")

# Create a teaching agent
print("\n[TEST] Creating TeachingAgent and simulating 6 turns...")
agent = TeachingAgent()

# Create a test session
session = agent.create_session(
    user_id="test-user",
    topic="Binary Trees",
    mode="socratic"
)
session_id = session["session_id"]
print(f"✓ Session created: {session_id}")

# Simulate 6 turns
test_explanations = [
    "A binary tree is a hierarchical data structure.",
    "Each node in a binary tree has at most two children.",
    "The children are called left child and right child.",
    "Binary trees are used for efficient searching.",
    "The root is the topmost node in the tree.",  # Turn 5 - analytics should trigger
    "Traversal methods include inorder, preorder, and postorder."  # Turn 6 - should this work?
]

for i, explanation in enumerate(test_explanations, 1):
    print(f"\n{'='*70}")
    print(f"TURN {i}")
    print(f"{'='*70}")

    try:
        # Step 1: Analyze
        print(f"\n[{i}/6] Analyzing explanation...")
        analysis = agent.analyze_explanation(
            session_id=session_id,
            explanation=explanation
        )
        print(f"✓ Analysis complete: confidence={analysis['confidence_score']}, clarity={analysis['clarity_score']}")

        # Step 2: Generate question
        print(f"\n[{i}/6] Generating question...")
        question = agent.generate_question(
            session_id=session_id,
            explanation=explanation,
            analysis=analysis,
            mode="socratic"
        )
        print(f"✓ Question generated: \"{question[:80]}...\"")

        # Step 3: On turn 5, trigger background analytics
        if i == 5:
            print(f"\n[ANALYTICS] Turn 5 detected - triggering background analytics...")
            if MODAL_AVAILABLE and compute_session_analytics:
                try:
                    session_data = agent.sessions[session_id]
                    print(f"  → Session has {len(session_data['analyses'])} analyses")
                    print(f"  → Session has {len(session_data['conversation_history'])} conversation turns")

                    call = compute_session_analytics.spawn(session_data)
                    print(f"  ✓ Analytics spawned successfully (call_id: {call.object_id})")
                    print(f"  → Analytics running in background (not blocking)")

                except Exception as analytics_error:
                    print(f"  ✗ Analytics failed: {analytics_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  ⊘ Modal not available for analytics")

        print(f"\n✓ Turn {i} completed successfully!")

    except Exception as turn_error:
        print(f"\n✗ Turn {i} FAILED with error: {turn_error}")
        import traceback
        traceback.print_exc()
        print(f"\n⚠️  Application stopped at turn {i}")
        break

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

if i == 6:
    print("✓ All 6 turns completed successfully!")
    print("  The application should NOT stop after turn 5.")
else:
    print(f"✗ Application stopped at turn {i}")
    print("  This indicates an issue that needs to be fixed.")

print("=" * 70)
