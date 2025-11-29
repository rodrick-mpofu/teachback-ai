"""
Test Modal connection and function lookup
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Modal Connection")
print("=" * 60)

# Check Modal credentials
modal_token_id = os.environ.get("MODAL_TOKEN_ID")
modal_token_secret = os.environ.get("MODAL_TOKEN_SECRET")

if modal_token_id and modal_token_secret:
    print(f"[OK] Modal Token ID found: {modal_token_id[:10]}...")
    print(f"[OK] Modal Token Secret found: {modal_token_secret[:10]}...")
else:
    print("[FAIL] Modal credentials not found in environment")
    exit(1)

# Test importing Modal
try:
    import modal
    print(f"[OK] Modal package imported successfully (version {modal.__version__})")
except ImportError as e:
    print(f"[FAIL] Failed to import Modal: {e}")
    exit(1)

# Test looking up deployed functions
print("\nAttempting to connect to deployed Modal functions...")

try:
    compute_session_analytics = modal.Function.from_name("teachback-ai", "compute_session_analytics")
    print(f"[OK] Found compute_session_analytics: {compute_session_analytics}")
except Exception as e:
    print(f"[FAIL] Failed to find compute_session_analytics: {e}")

try:
    parallel_analyze_and_question = modal.Function.from_name("teachback-ai", "parallel_analyze_and_question")
    print(f"[OK] Found parallel_analyze_and_question: {parallel_analyze_and_question}")
except Exception as e:
    print(f"[FAIL] Failed to find parallel_analyze_and_question: {e}")

# Test invoking a simple function (if found)
print("\nAttempting to invoke compute_session_analytics with test data...")
try:
    test_session = {
        "topic": "test",
        "mode": "socratic",
        "analyses": [
            {
                "confidence_score": 0.8,
                "clarity_score": 0.7,
                "knowledge_gaps": ["gap1"],
                "unexplained_jargon": ["jargon1"],
                "strengths": ["strength1"]
            }
        ]
    }

    result = compute_session_analytics.remote(test_session)
    print(f"[OK] Function invocation successful!")
    print(f"   Result: {result}")
except Exception as e:
    print(f"[FAIL] Function invocation failed: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
