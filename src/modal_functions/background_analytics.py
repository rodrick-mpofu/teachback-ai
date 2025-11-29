"""
Background Analytics - Modal-powered analytics computation.

This module provides Modal functions for computing session analytics in the
background without blocking the main UI thread.
"""

from typing import Dict, List
import modal

# Define Modal app and image directly in this module
app = modal.App("teachback-ai")

# Define base image with required dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("anthropic>=0.39.0", "python-dotenv")
)


@app.function(image=image, cpu=2, memory=4096, timeout=300)
def compute_session_analytics(session_history: dict) -> dict:
    """
    Compute comprehensive analytics for a teaching session.

    This function runs with enhanced resources (2 CPUs, 4GB memory) to handle
    complex analytics computations efficiently.

    Args:
        session_history: Dictionary containing session data including:
            - conversation_history: List of conversation turns
            - analyses: List of analysis results
            - topic: The session topic
            - mode: The AI student mode

    Returns:
        Dictionary containing:
            - learning_curve: List of clarity scores over time
            - clarity_trend: Overall trend (improving/stable/declining)
            - confidence_over_time: List of confidence scores over time
            - persistent_gaps: Knowledge gaps appearing multiple times
            - suggested_review_topics: Topics that need review
            - total_turns: Number of conversation turns
            - average_confidence: Mean confidence score
            - average_clarity: Mean clarity score
    """
    analyses = session_history.get("analyses", [])

    if not analyses:
        return {
            "learning_curve": [],
            "clarity_trend": "no_data",
            "confidence_over_time": [],
            "persistent_gaps": [],
            "suggested_review_topics": [],
            "total_turns": 0,
            "average_confidence": 0.0,
            "average_clarity": 0.0
        }

    # Extract learning curve and confidence over time
    learning_curve = [a.get("clarity_score", 0.0) for a in analyses]
    confidence_over_time = [a.get("confidence_score", 0.0) for a in analyses]

    # Calculate averages
    total_turns = len(analyses)
    average_confidence = sum(confidence_over_time) / total_turns if total_turns > 0 else 0.0
    average_clarity = sum(learning_curve) / total_turns if total_turns > 0 else 0.0

    # Determine clarity trend
    clarity_trend = "stable"
    if len(learning_curve) >= 3:
        first_third = sum(learning_curve[:len(learning_curve)//3]) / (len(learning_curve)//3)
        last_third = sum(learning_curve[-len(learning_curve)//3:]) / (len(learning_curve)//3)

        if last_third > first_third + 0.1:
            clarity_trend = "improving"
        elif last_third < first_third - 0.1:
            clarity_trend = "declining"

    # Find persistent gaps (appearing in multiple analyses)
    all_gaps = []
    for analysis in analyses:
        all_gaps.extend(analysis.get("knowledge_gaps", []))

    gap_counts = {}
    for gap in all_gaps:
        gap_counts[gap] = gap_counts.get(gap, 0) + 1

    persistent_gaps = [gap for gap, count in gap_counts.items() if count > 1]

    # Suggested review topics (from unexplained jargon and persistent gaps)
    all_jargon = []
    for analysis in analyses:
        all_jargon.extend(analysis.get("unexplained_jargon", []))

    suggested_review_topics = list(set(persistent_gaps + all_jargon))[:5]  # Top 5

    return {
        "learning_curve": learning_curve,
        "clarity_trend": clarity_trend,
        "confidence_over_time": confidence_over_time,
        "persistent_gaps": persistent_gaps,
        "suggested_review_topics": suggested_review_topics,
        "total_turns": total_turns,
        "average_confidence": round(average_confidence, 2),
        "average_clarity": round(average_clarity, 2)
    }


@app.function(image=image)
def batch_analyze_sessions(sessions: List[dict]) -> List[dict]:
    """
    Analyze multiple sessions in parallel using Modal's .map() functionality.

    This function processes multiple teaching sessions concurrently, making it
    ideal for batch analytics or dashboard generation.

    Args:
        sessions: List of session history dictionaries

    Returns:
        List of analytics dictionaries, one per session
    """
    # Use Modal's .map() to run compute_session_analytics in parallel
    # across all sessions
    results = list(compute_session_analytics.map(sessions))
    return results
