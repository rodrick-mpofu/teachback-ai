"""
Test script for TeachBack AI advanced features
Run this to verify all features are working correctly
"""

import sys
from datetime import datetime

def test_database():
    """Test database operations"""
    print("\n=== Testing Database ===")
    try:
        from src.database.db_manager import DatabaseManager

        db = DatabaseManager("test_teachback.db")
        print("✓ Database initialized")

        # Create user
        user = db.get_or_create_user("test_user", "Test User")
        print(f"✓ User created: {user.username}")

        # Create session
        session = db.create_session(
            session_id="test_session_001",
            user_id="test_user",
            topic="Python Recursion",
            mode="socratic",
            voice_enabled=False
        )
        print(f"✓ Session created: {session.topic}")

        # Add conversation
        conv = db.add_conversation_turn(
            session_id="test_session_001",
            turn_number=1,
            role="teacher",
            content="Recursion is when a function calls itself."
        )
        print(f"✓ Conversation added: Turn {conv.turn_number}")

        # Add analysis
        analysis = db.add_analysis(
            session_id="test_session_001",
            turn_number=1,
            confidence_score=0.75,
            clarity_score=0.80,
            knowledge_gaps=["Base case explanation"],
            unexplained_jargon=["stack frame"],
            strengths=["Simple definition"]
        )
        print(f"✓ Analysis added: Confidence {analysis.confidence_score}")

        # Get user stats
        stats = db.get_user_stats("test_user")
        print(f"✓ User stats retrieved: {stats['total_sessions']} sessions")

        # Cleanup
        db.cleanup()
        print("✓ Database cleanup successful")

        import os
        if os.path.exists("test_teachback.db"):
            os.remove("test_teachback.db")
            print("✓ Test database removed")

        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_graph():
    """Test knowledge graph service"""
    print("\n=== Testing Knowledge Graph ===")
    try:
        from src.services.knowledge_graph import KnowledgeGraphService
        from src.database.db_manager import DatabaseManager

        kg = KnowledgeGraphService()
        print("✓ Knowledge graph service initialized")

        db = DatabaseManager("test_teachback.db")
        db.get_or_create_user("test_user", "Test User")

        # Create knowledge node
        node = db.create_or_update_knowledge_node(
            user_id="test_user",
            topic="Machine Learning",
            confidence=0.7,
            clarity=0.8,
            related_concepts=["Neural Networks", "Deep Learning"],
            gaps=["Gradient descent"]
        )
        print(f"✓ Knowledge node created: {node.topic}")

        # Get graph data
        graph_data = db.get_user_knowledge_graph("test_user")
        print(f"✓ Graph data retrieved: {len(graph_data['nodes'])} nodes")

        # Generate HTML
        html = kg.generate_graph_html(graph_data)
        print(f"✓ Graph HTML generated: {len(html)} characters")

        # Cleanup
        db.cleanup()
        import os
        if os.path.exists("test_teachback.db"):
            os.remove("test_teachback.db")
            print("✓ Test database removed")

        return True

    except Exception as e:
        print(f"✗ Knowledge graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_spaced_repetition():
    """Test spaced repetition service"""
    print("\n=== Testing Spaced Repetition ===")
    try:
        from src.services.spaced_repetition import SpacedRepetitionService
        from src.database.db_manager import DatabaseManager

        db = DatabaseManager("test_teachback.db")
        db.get_or_create_user("test_user", "Test User")

        sr = SpacedRepetitionService(db)
        print("✓ Spaced repetition service initialized")

        # Add topic for review
        sr.add_topic_for_review("test_user", "Quantum Physics")
        print("✓ Topic added for review")

        # Get due reviews
        due = sr.get_due_reviews("test_user")
        print(f"✓ Due reviews retrieved: {len(due)} items")

        if due:
            # Record a review
            result = sr.record_review(due[0]["id"], quality=4)
            print(f"✓ Review recorded: Next review in {result['interval_days']} days")

        # Get statistics
        stats = sr.get_review_statistics("test_user")
        print(f"✓ Review stats: {stats['items_due_now']} due now")

        # Calculate quality from performance
        quality = sr.calculate_quality_from_performance(
            confidence=0.85,
            clarity=0.90,
            had_gaps=False
        )
        print(f"✓ Quality calculation: {quality}/5")

        # Cleanup
        db.cleanup()
        import os
        if os.path.exists("test_teachback.db"):
            os.remove("test_teachback.db")
            print("✓ Test database removed")

        return True

    except Exception as e:
        print(f"✗ Spaced repetition test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_handlers():
    """Test UI handler functions"""
    print("\n=== Testing UI Handlers ===")
    try:
        from src.ui.advanced_handlers import (
            view_session_history,
            view_progress_chart,
            view_knowledge_graph,
            view_spaced_repetition
        )
        from src.database.db_manager import DatabaseManager

        db = DatabaseManager("test_teachback.db")
        user = db.get_or_create_user("test_user", "Test User")

        # Create a test session
        session = db.create_session(
            session_id="ui_test_session",
            user_id="test_user",
            topic="Test Topic",
            mode="socratic"
        )
        db.complete_session("ui_test_session", 0.75, 0.80)
        db.update_progress_metrics("test_user")

        print("✓ Test data created")

        # Test history view
        table, stats = view_session_history("test_user")
        print(f"✓ Session history: {len(table)} chars")

        # Test progress chart
        chart = view_progress_chart("test_user", 7)
        print(f"✓ Progress chart: {len(chart)} chars")

        # Test knowledge graph view
        graph = view_knowledge_graph("test_user")
        print(f"✓ Knowledge graph view: {len(graph)} chars")

        # Test spaced repetition view
        due, schedule = view_spaced_repetition("test_user")
        print(f"✓ Spaced repetition view: {len(due)} chars")

        # Cleanup
        db.cleanup()
        import os
        if os.path.exists("test_teachback.db"):
            os.remove("test_teachback.db")
            print("✓ Test database removed")

        return True

    except Exception as e:
        print(f"✗ UI handlers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("TeachBack AI - Feature Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Database Operations", test_database()))
    results.append(("Knowledge Graph", test_knowledge_graph()))
    results.append(("Spaced Repetition", test_spaced_repetition()))
    results.append(("UI Handlers", test_ui_handlers()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")

        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"Total: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("-" * 60)

    if failed == 0:
        print("\n🎉 All tests passed! Your TeachBack AI features are ready to use.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
