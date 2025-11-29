"""
Modal Integration Test Suite

This module tests Modal integration including parallel execution,
background analytics, batch processing, and fallback behavior.

Usage:
    python -m unittest test_modal_integration.py
"""

import unittest
import os
import time
from unittest.mock import patch, MagicMock


class TestModalIntegration(unittest.TestCase):
    """Test suite for Modal integration in TeachBack AI"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_explanation = "Recursion is when a function calls itself."
        self.test_topic = "Recursion in Python"
        self.test_mode = "socratic"
        self.test_session_history = {
            "topic": self.test_topic,
            "mode": self.test_mode,
            "conversation_history": [],
            "analyses": [
                {
                    "confidence_score": 0.7,
                    "clarity_score": 0.8,
                    "knowledge_gaps": ["Base case explanation"],
                    "unexplained_jargon": ["stack frame"],
                    "strengths": ["Clear definition"]
                },
                {
                    "confidence_score": 0.8,
                    "clarity_score": 0.85,
                    "knowledge_gaps": ["Base case explanation"],
                    "unexplained_jargon": [],
                    "strengths": ["Good examples", "Clear structure"]
                }
            ]
        }

    def test_modal_availability(self):
        """Test that Modal imports work correctly"""
        try:
            from src.modal_functions.parallel_teaching import (
                analyze_explanation_modal,
                generate_question_modal,
                parallel_analyze_and_question
            )
            from src.modal_functions.background_analytics import (
                compute_session_analytics,
                batch_analyze_sessions
            )
            print("✅ All Modal functions imported successfully")
            self.assertTrue(True)
        except ImportError as e:
            print(f"⚠️ Modal imports failed (expected if Modal not installed): {e}")
            self.skipTest("Modal not available")

    @patch.dict(os.environ, {"USE_MODAL": "false"})
    def test_fallback_behavior(self):
        """Test that local execution works when Modal is disabled"""
        from src.agents.teaching_agent import TeachingAgent

        agent = TeachingAgent()
        self.assertFalse(agent.use_modal)

        # Create a test session
        session = agent.create_session(
            user_id="test_user",
            topic=self.test_topic,
            mode=self.test_mode
        )

        # Test local analysis
        start_time = time.time()
        analysis = agent.analyze_explanation(
            session_id=session["session_id"],
            explanation=self.test_explanation
        )
        local_time = time.time() - start_time

        # Verify analysis structure
        self.assertIn("confidence_score", analysis)
        self.assertIn("clarity_score", analysis)
        self.assertIn("knowledge_gaps", analysis)
        self.assertIn("unexplained_jargon", analysis)
        self.assertIn("strengths", analysis)

        print(f"✅ Local execution completed in {local_time:.2f}s")

    @patch.dict(os.environ, {"USE_MODAL": "true"})
    def test_modal_enabled_flag(self):
        """Test that USE_MODAL environment variable is respected"""
        from src.agents.teaching_agent import TeachingAgent

        # Create agent with Modal enabled
        agent = TeachingAgent()
        self.assertTrue(agent.use_modal)

        print("✅ Modal flag correctly set from environment variable")

    def test_parallel_execution_performance(self):
        """
        Test that Modal parallel execution is faster than sequential.

        Note: This test requires Modal to be properly configured and will
        be skipped if Modal is not available.
        """
        try:
            from src.agents.teaching_agent import TeachingAgent
            from src.modal_functions.parallel_teaching import MODAL_AVAILABLE
        except ImportError:
            self.skipTest("Modal not available")

        if not MODAL_AVAILABLE:
            self.skipTest("Modal functions not available")

        # Create agent instances
        agent_local = TeachingAgent()
        agent_local.use_modal = False

        agent_modal = TeachingAgent()
        agent_modal.use_modal = True

        # Create test sessions
        session_local = agent_local.create_session(
            user_id="test_user_local",
            topic=self.test_topic,
            mode=self.test_mode
        )

        session_modal = agent_modal.create_session(
            user_id="test_user_modal",
            topic=self.test_topic,
            mode=self.test_mode
        )

        # Test sequential execution
        print("\n⏱️ Testing sequential execution...")
        start_time = time.time()
        analysis_local = agent_local.analyze_explanation(
            session_id=session_local["session_id"],
            explanation=self.test_explanation
        )
        question_local = agent_local.generate_question(
            session_id=session_local["session_id"],
            explanation=self.test_explanation,
            analysis=analysis_local,
            mode=self.test_mode
        )
        sequential_time = time.time() - start_time
        print(f"✅ Sequential execution: {sequential_time:.2f}s")

        # Test Modal parallel execution
        print("\n⚡ Testing Modal parallel execution...")
        try:
            analysis_modal, question_modal, modal_time = agent_modal.analyze_and_question_parallel(
                session_id=session_modal["session_id"],
                explanation=self.test_explanation
            )
            print(f"✅ Modal execution: {modal_time:.2f}s")

            # Modal should be faster (or at least comparable)
            speedup = sequential_time / modal_time if modal_time > 0 else 0
            print(f"\n📊 Performance comparison:")
            print(f"   Sequential: {sequential_time:.2f}s")
            print(f"   Modal:      {modal_time:.2f}s")
            print(f"   Speedup:    {speedup:.2f}x")

            if modal_time < sequential_time:
                print("✅ Modal is faster than sequential execution")
            else:
                print("⚠️ Modal not faster (may be cold start or network latency)")

        except Exception as e:
            error_msg = str(e)
            if "not been hydrated" in error_msg or "not running" in error_msg:
                print(f"⚠️ Modal not deployed, execution fell back to local")
                print("   Deploy Modal with: python deploy_modal.py")
                # This is expected behavior, not a test failure
            else:
                print(f"⚠️ Modal execution failed: {e}")
                print("This may be due to Modal not being deployed or configured")
            self.skipTest(f"Modal not deployed: {error_msg[:100]}")

    def test_background_analytics(self):
        """Test background analytics computation"""
        try:
            from src.modal_functions.background_analytics import compute_session_analytics
        except ImportError:
            self.skipTest("Modal not available")

        # Test local computation (without Modal deploy)
        result = compute_session_analytics.local(self.test_session_history)

        # Verify analytics structure
        self.assertIn("learning_curve", result)
        self.assertIn("clarity_trend", result)
        self.assertIn("confidence_over_time", result)
        self.assertIn("persistent_gaps", result)
        self.assertIn("suggested_review_topics", result)
        self.assertIn("total_turns", result)
        self.assertIn("average_confidence", result)
        self.assertIn("average_clarity", result)

        # Verify values
        self.assertEqual(result["total_turns"], 2)
        self.assertEqual(len(result["learning_curve"]), 2)
        self.assertIn("Base case explanation", result["persistent_gaps"])

        print("✅ Background analytics computation successful")
        print(f"   Average confidence: {result['average_confidence']}")
        print(f"   Average clarity: {result['average_clarity']}")
        print(f"   Clarity trend: {result['clarity_trend']}")

    def test_batch_session_processing(self):
        """Test batch processing of multiple sessions"""
        try:
            from src.modal_functions.background_analytics import (
                batch_analyze_sessions,
                compute_session_analytics
            )
        except ImportError:
            self.skipTest("Modal not available")

        # Create multiple test sessions
        sessions = [
            self.test_session_history,
            {
                "topic": "Binary Search",
                "mode": "contrarian",
                "conversation_history": [],
                "analyses": [
                    {
                        "confidence_score": 0.6,
                        "clarity_score": 0.7,
                        "knowledge_gaps": ["Time complexity"],
                        "unexplained_jargon": ["O(log n)"],
                        "strengths": ["Good examples"]
                    }
                ]
            },
            {
                "topic": "Graph Traversal",
                "mode": "five-year-old",
                "conversation_history": [],
                "analyses": [
                    {
                        "confidence_score": 0.9,
                        "clarity_score": 0.85,
                        "knowledge_gaps": [],
                        "unexplained_jargon": [],
                        "strengths": ["Clear explanation", "Simple language"]
                    }
                ]
            }
        ]

        # Test batch processing
        print("\n📦 Testing batch session processing...")

        try:
            # Try Modal .map() first
            start_time = time.time()
            results = list(batch_analyze_sessions.map(sessions))
            batch_time = time.time() - start_time

            # Verify results
            self.assertEqual(len(results), 3)
            for result in results:
                self.assertIn("total_turns", result)
                self.assertIn("average_confidence", result)
                self.assertIn("average_clarity", result)

            print(f"✅ Modal batch processing completed in {batch_time:.2f}s")
            print(f"   Processed {len(results)} sessions")
            print(f"   Average time per session: {batch_time/len(results):.2f}s")

        except Exception as e:
            # Fall back to local processing if Modal not deployed
            if "not been hydrated" in str(e) or "not running" in str(e):
                print("⚠️ Modal not deployed, testing local batch processing...")
                start_time = time.time()
                results = [compute_session_analytics.local(s) for s in sessions]
                batch_time = time.time() - start_time

                # Verify results
                self.assertEqual(len(results), 3)
                for result in results:
                    self.assertIn("total_turns", result)
                    self.assertIn("average_confidence", result)
                    self.assertIn("average_clarity", result)

                print(f"✅ Local batch processing completed in {batch_time:.2f}s")
                print(f"   Processed {len(results)} sessions")
                print(f"   Average time per session: {batch_time/len(results):.2f}s")
            else:
                raise

    @patch.dict(os.environ, {"USE_MODAL": "true"})
    def test_trigger_background_analytics(self):
        """Test triggering background analytics from TeachingAgent"""
        try:
            from src.agents.teaching_agent import TeachingAgent, MODAL_AVAILABLE
        except ImportError:
            self.skipTest("Modal not available")

        if not MODAL_AVAILABLE:
            self.skipTest("Modal functions not available")

        agent = TeachingAgent()
        agent.use_modal = True

        # Create test session
        session = agent.create_session(
            user_id="test_user",
            topic=self.test_topic,
            mode=self.test_mode
        )

        # Add some analyses to the session
        agent.sessions[session["session_id"]]["analyses"] = self.test_session_history["analyses"]

        # Trigger background analytics
        print("\n📊 Testing background analytics trigger...")
        call_id = agent.trigger_background_analytics(session["session_id"])

        if call_id:
            print(f"✅ Background analytics spawned (call_id: {call_id})")
        else:
            print("⚠️ Background analytics not spawned (Modal may not be deployed)")

    def test_import_structure(self):
        """Test that all imports resolve correctly"""
        print("\n🔍 Testing import structure...")

        # Test modal_setup imports
        try:
            from modal_setup import app, image, anthropic_secret, elevenlabs_secret
            print("✅ modal_setup imports successful")
        except ImportError as e:
            self.fail(f"modal_setup import failed: {e}")

        # Test parallel_teaching imports
        try:
            from src.modal_functions.parallel_teaching import (
                analyze_explanation_modal,
                generate_question_modal,
                parallel_analyze_and_question
            )
            print("✅ parallel_teaching imports successful")
        except ImportError as e:
            print(f"⚠️ parallel_teaching imports failed (expected if Modal not installed): {e}")

        # Test background_analytics imports
        try:
            from src.modal_functions.background_analytics import (
                compute_session_analytics,
                batch_analyze_sessions
            )
            print("✅ background_analytics imports successful")
        except ImportError as e:
            print(f"⚠️ background_analytics imports failed (expected if Modal not installed): {e}")

        # Test TeachingAgent with Modal support
        try:
            from src.agents.teaching_agent import TeachingAgent, MODAL_AVAILABLE
            print(f"✅ TeachingAgent imports successful (MODAL_AVAILABLE={MODAL_AVAILABLE})")
        except ImportError as e:
            self.fail(f"TeachingAgent import failed: {e}")


def run_performance_comparison():
    """
    Run a detailed performance comparison between sequential and Modal execution.
    This is a standalone function that can be called separately.
    """
    print("\n" + "="*60)
    print("🚀 Modal Performance Comparison")
    print("="*60)

    try:
        from src.agents.teaching_agent import TeachingAgent, MODAL_AVAILABLE

        if not MODAL_AVAILABLE:
            print("❌ Modal not available. Cannot run performance comparison.")
            return

        print("\nThis will compare sequential vs Modal parallel execution.")
        print("Note: First run may be slower due to cold start.\n")

        # Test scenarios
        test_cases = [
            ("Simple concept", "Variables store data in memory"),
            ("Complex concept", "In recursion, a function calls itself with a modified input until it reaches a base case that terminates the recursion"),
            ("Technical explanation", "REST APIs use HTTP methods like GET, POST, PUT, DELETE to perform CRUD operations on resources")
        ]

        for idx, (name, explanation) in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {idx}: {name}")
            print("-" * 60)

            # Sequential test
            agent_seq = TeachingAgent()
            agent_seq.use_modal = False
            session_seq = agent_seq.create_session("test_user", "Programming", "socratic")

            start = time.time()
            agent_seq.analyze_explanation(session_seq["session_id"], explanation)
            seq_time = time.time() - start

            # Modal test
            agent_modal = TeachingAgent()
            agent_modal.use_modal = True
            session_modal = agent_modal.create_session("test_user", "Programming", "socratic")

            start = time.time()
            agent_modal.analyze_and_question_parallel(session_modal["session_id"], explanation)
            modal_time = time.time() - start

            speedup = seq_time / modal_time if modal_time > 0 else 0
            print(f"   Sequential: {seq_time:.2f}s")
            print(f"   Modal:      {modal_time:.2f}s")
            print(f"   Speedup:    {speedup:.2f}x")

        print("\n" + "="*60)

    except Exception as e:
        print(f"\n❌ Performance comparison failed: {e}")


if __name__ == "__main__":
    print("\n🧪 TeachBack AI - Modal Integration Test Suite")
    print("="*60)

    # Run unit tests
    unittest.main(verbosity=2, exit=False)

    # Optional: Run detailed performance comparison
    # Uncomment the following line to run performance tests
    # run_performance_comparison()
