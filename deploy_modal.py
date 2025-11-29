"""
Modal Deployment Script for TeachBack AI

This script deploys all Modal functions to the Modal cloud platform.
Run this script to deploy or update your Modal functions.

Usage:
    python deploy_modal.py
"""

import sys
from modal_app import app


def print_deployment_info():
    """Print deployment information and instructions"""
    print("\n" + "="*60)
    print("🚀 TeachBack AI Modal Deployment")
    print("="*60)
    print("\n📦 Deployed Functions:")
    print("  1. analyze_explanation_modal")
    print("     - Analyzes user explanations via Claude API")
    print("     - Resource: Default container")
    print()
    print("  2. generate_question_modal")
    print("     - Generates AI student questions")
    print("     - Resource: Default container")
    print()
    print("  3. parallel_analyze_and_question")
    print("     - Runs analysis and question generation in parallel")
    print("     - Resource: Default container")
    print()
    print("  4. compute_session_analytics")
    print("     - Computes session analytics with 2 CPUs, 4GB memory")
    print("     - Resource: Enhanced container")
    print()
    print("  5. batch_analyze_sessions")
    print("     - Batch processes multiple sessions in parallel")
    print("     - Resource: Default container")
    print()
    print("="*60)
    print("⚙️  Configuration:")
    print("  - Cold start time: ~2-5 seconds (first call)")
    print("  - Warm latency: <500ms (subsequent calls)")
    print("  - Timeout: 300 seconds for analytics")
    print()
    print("="*60)
    print("📞 How to Call Functions:")
    print()
    print("  Remote (from your app):")
    print("    from src.modal_functions.parallel_teaching import parallel_analyze_and_question")
    print("    result = parallel_analyze_and_question.remote(explanation, mode, topic, history)")
    print()
    print("  Spawn (non-blocking):")
    print("    from src.modal_functions.background_analytics import compute_session_analytics")
    print("    call = compute_session_analytics.spawn(session_data)")
    print("    # Later: result = call.get()")
    print()
    print("="*60)
    print("🔒 Required Secrets:")
    print("  - anthropic-api-key (required)")
    print("  - elevenlabs-api-key (optional)")
    print()
    print("  To create secrets in Modal:")
    print("    modal secret create anthropic-api-key ANTHROPIC_API_KEY=<your-key>")
    print("    modal secret create elevenlabs-api-key ELEVENLABS_API_KEY=<your-key>")
    print()
    print("="*60)
    print("✅ Next Steps:")
    print("  1. Set USE_MODAL=true in your .env file")
    print("  2. Restart your application")
    print("  3. Modal functions will be used automatically")
    print()
    print("="*60)
    print()


if __name__ == "__main__":
    try:
        print("Starting Modal deployment...")
        print("This may take a few minutes on first deployment...")
        print()

        # Deploy the unified app
        app.deploy()

        print("\nDeployment completed successfully!")
        print_deployment_info()

    except Exception as e:
        print(f"\nDeployment failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Modal is installed: pip install modal")
        print("  2. Authenticate with Modal: modal token new")
        print("  3. Check that secrets are created in Modal dashboard")
        print("  4. Verify modal_app.py is present")
        sys.exit(1)
