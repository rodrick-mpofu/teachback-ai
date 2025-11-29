"""
Test Modal Analytics Trigger

This script tests if the background analytics trigger works correctly.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Modal Analytics Trigger")
print("=" * 60)

# Check if Modal is enabled
use_modal = os.environ.get("USE_MODAL", "false").lower() == "true"
print(f"\nUSE_MODAL environment variable: {use_modal}")

if not use_modal:
    print("\n[WARNING] Modal is not enabled. Set USE_MODAL=true in .env to test.")
    exit(0)

# Import the function
try:
    from src.agents.teaching_agent import compute_session_analytics, MODAL_AVAILABLE
    print(f"\n[OK] Imported Modal functions")
    print(f"     MODAL_AVAILABLE: {MODAL_AVAILABLE}")
    print(f"     compute_session_analytics: {compute_session_analytics}")
except ImportError as e:
    print(f"\n[FAIL] Failed to import Modal functions: {e}")
    exit(1)

if not MODAL_AVAILABLE:
    print("\n[FAIL] Modal is not available. Make sure you've deployed with: python deploy_modal.py")
    exit(1)

# Create test session data
test_session = {
    "topic": "Python async/await",
    "mode": "socratic",
    "conversation_history": [
        {"role": "student", "content": "What is async/await?"},
        {"role": "teacher", "content": "Async/await is a way to write asynchronous code..."},
    ],
    "analyses": [
        {
            "confidence_score": 0.7,
            "clarity_score": 0.6,
            "knowledge_gaps": ["Event loop understanding"],
            "unexplained_jargon": ["coroutine", "event loop"],
            "strengths": ["Clear introduction"]
        },
        {
            "confidence_score": 0.8,
            "clarity_score": 0.75,
            "knowledge_gaps": ["Concurrent execution"],
            "unexplained_jargon": ["await"],
            "strengths": ["Good examples"]
        },
        {
            "confidence_score": 0.85,
            "clarity_score": 0.8,
            "knowledge_gaps": [],
            "unexplained_jargon": [],
            "strengths": ["Complete explanation"]
        }
    ]
}

print("\n[TEST] Spawning background analytics task...")
print(f"       Session data: {len(test_session['analyses'])} analyses")

try:
    # Spawn the task (non-blocking)
    call = compute_session_analytics.spawn(test_session)
    print(f"\n[OK] Task spawned successfully!")
    print(f"     Call ID: {call.object_id}")

    print("\n[INFO] The task is running in the background on Modal.")
    print("       You can check the Modal dashboard for logs and results.")
    print("       Dashboard: https://modal.com/apps")

    print("\n[TEST] Optionally waiting for result (this may take a few seconds)...")
    result = call.get(timeout=30)

    print(f"\n[OK] Task completed successfully!")
    print(f"     Result:")
    print(f"     - Total turns: {result['total_turns']}")
    print(f"     - Average confidence: {result['average_confidence']}")
    print(f"     - Average clarity: {result['average_clarity']}")
    print(f"     - Clarity trend: {result['clarity_trend']}")
    print(f"     - Persistent gaps: {result['persistent_gaps']}")
    print(f"     - Suggested review topics: {result['suggested_review_topics']}")

except Exception as e:
    print(f"\n[FAIL] Task execution failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("Test Complete - Analytics trigger is working!")
print("=" * 60)
