"""
Modal App - Unified Modal deployment for TeachBack AI

This module contains all Modal functions for the TeachBack AI project.
Deploy this file to Modal to enable cloud-based parallel processing.
"""

import os
import json
from typing import Dict, List
import modal

# Define Modal app
app = modal.App("teachback-ai")

# Define secrets
anthropic_secret = modal.Secret.from_name("anthropic-api-key")

# Define base image with required dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("anthropic>=0.39.0", "python-dotenv")
)


# ============================================================================
# ANALYSIS & QUESTION GENERATION FUNCTIONS
# ============================================================================

@app.function(image=image, secrets=[anthropic_secret])
def analyze_explanation_modal(explanation: str, topic: str) -> dict:
    """
    Analyze a user's explanation using Claude AI via Modal.

    Args:
        explanation: The user's explanation text
        topic: The topic being taught

    Returns:
        Dictionary containing:
            - confidence_score: 0-1 indicating speaker's confidence
            - clarity_score: 0-1 indicating explanation clarity
            - knowledge_gaps: List of identified gaps
            - unexplained_jargon: List of technical terms not explained
            - strengths: List of strong points in the explanation
    """
    from anthropic import Anthropic

    # Initialize Anthropic client with secret from Modal
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = "claude-sonnet-4-5-20250929"

    # Construct analysis prompt
    analysis_prompt = f"""Analyze this explanation about {topic}. Provide a detailed assessment in the following JSON format:

{{
    "confidence_score": <float 0-1>,
    "clarity_score": <float 0-1>,
    "knowledge_gaps": [<list of strings>],
    "unexplained_jargon": [<list of technical terms not explained>],
    "strengths": [<list of strong points>]
}}

Explanation to analyze:
{explanation}

Guidelines:
- confidence_score: How confident does the speaker seem? (0=very uncertain, 1=very confident)
- clarity_score: How clear and well-structured is the explanation? (0=confusing, 1=crystal clear)
- knowledge_gaps: Specific areas where understanding seems incomplete or incorrect
- unexplained_jargon: Technical terms used without definition or context
- strengths: What the speaker explained well

Respond ONLY with valid JSON, no additional text."""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": analysis_prompt
            }]
        )

        # Extract JSON from response
        import re
        analysis_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if analysis_text.startswith("```"):
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', analysis_text, re.DOTALL)
            if match:
                analysis_text = match.group(1).strip()

        analysis = json.loads(analysis_text)
        return analysis

    except Exception as e:
        return {
            "confidence_score": 0.0,
            "clarity_score": 0.0,
            "knowledge_gaps": [f"Analysis failed: {str(e)}"],
            "unexplained_jargon": [],
            "strengths": []
        }


@app.function(image=image, secrets=[anthropic_secret])
def generate_question_modal(
    explanation: str,
    mode: str,
    analysis: dict,
    topic: str,
    conversation_history: list
) -> str:
    """
    Generate a contextual question from the AI student via Modal.

    Args:
        explanation: The user's latest explanation
        mode: AI student mode (socratic, contrarian, five-year-old, anxious)
        analysis: Analysis results from analyze_explanation_modal
        topic: The topic being taught
        conversation_history: Previous conversation turns

    Returns:
        The AI student's next question as a string
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = "claude-sonnet-4-5-20250929"

    # Build context from conversation history
    history_context = ""
    if conversation_history:
        history_context = "\n\nPrevious conversation:\n"
        for turn in conversation_history[-3:]:
            history_context += f"Student: {turn.get('question', '')}\n"
            history_context += f"Teacher: {turn.get('explanation', '')}\n"

    # Mode-specific system prompts
    mode_prompts = {
        "socratic": f"""You are a Socratic AI student learning about {topic}. Your goal is to ask probing,
thoughtful questions that expose gaps in understanding and encourage deeper thinking.
Focus on 'why', 'how', and questions about underlying principles and assumptions.
Be respectful but intellectually challenging.""",

        "contrarian": f"""You are a contrarian AI student learning about {topic}. You tend to be skeptical
and challenge claims with counterarguments and alternative viewpoints.
Point out potential flaws, ask about exceptions, and question assumptions.
Be provocative but constructive.""",

        "five-year-old": f"""You are a curious five-year-old child learning about {topic}. You ask 'why'
repeatedly and need simple, concrete explanations without jargon.
If something isn't explained simply enough, you don't understand it.
Be innocent, enthusiastic, and persistently curious.""",

        "anxious": f"""You are an anxious AI student learning about {topic}. You worry about edge cases,
failure scenarios, and what could go wrong.
Ask about risks, potential problems, and situations where things might not work as expected.
Be concerned and detail-oriented about safety and reliability."""
    }

    # Construct question generation prompt
    user_prompt = f"""Based on this explanation and analysis, generate your next question.

Topic: {topic}

Latest explanation:
{explanation}

Analysis:
- Confidence: {analysis['confidence_score']}
- Clarity: {analysis['clarity_score']}
- Knowledge gaps: {', '.join(analysis['knowledge_gaps']) if analysis['knowledge_gaps'] else 'None identified'}
- Unexplained jargon: {', '.join(analysis['unexplained_jargon']) if analysis['unexplained_jargon'] else 'None'}
- Strengths: {', '.join(analysis['strengths']) if analysis['strengths'] else 'None'}
{history_context}

Generate a single, natural question that fits your personality and helps the teacher improve their explanation.
Respond with ONLY the question, no additional formatting or explanation."""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=256,
            system=mode_prompts.get(mode, mode_prompts["socratic"]),
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        question = response.content[0].text.strip()
        return question

    except Exception as e:
        return f"I'm having trouble generating a question right now. Could you explain more about {topic}?"


@app.function(image=image)
def parallel_analyze_and_question(
    explanation: str,
    mode: str,
    topic: str,
    conversation_history: list = None
) -> tuple:
    """
    Run analysis and question generation in parallel using Modal.

    Args:
        explanation: The user's explanation text
        mode: AI student mode
        topic: The topic being taught
        conversation_history: Previous conversation turns (optional)

    Returns:
        Tuple of (analysis_dict, question_string)
    """
    if conversation_history is None:
        conversation_history = []

    # Spawn analysis
    analysis_call = analyze_explanation_modal.spawn(explanation, topic)
    analysis = analysis_call.get()

    # Generate question with the analysis
    question = generate_question_modal.remote(
        explanation=explanation,
        mode=mode,
        analysis=analysis,
        topic=topic,
        conversation_history=conversation_history
    )

    return (analysis, question)


# ============================================================================
# BACKGROUND ANALYTICS FUNCTIONS
# ============================================================================

@app.function(image=image, cpu=2, memory=4096, timeout=300)
def compute_session_analytics(session_history: dict) -> dict:
    """
    Compute comprehensive analytics for a teaching session.

    Args:
        session_history: Dictionary containing session data

    Returns:
        Dictionary containing analytics results
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

    # Extract metrics
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

    # Find persistent gaps
    all_gaps = []
    for analysis in analyses:
        all_gaps.extend(analysis.get("knowledge_gaps", []))

    gap_counts = {}
    for gap in all_gaps:
        gap_counts[gap] = gap_counts.get(gap, 0) + 1

    persistent_gaps = [gap for gap, count in gap_counts.items() if count > 1]

    # Suggested review topics
    all_jargon = []
    for analysis in analyses:
        all_jargon.extend(analysis.get("unexplained_jargon", []))

    suggested_review_topics = list(set(persistent_gaps + all_jargon))[:5]

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

    Args:
        sessions: List of session history dictionaries

    Returns:
        List of analytics dictionaries, one per session
    """
    results = list(compute_session_analytics.map(sessions))
    return results
