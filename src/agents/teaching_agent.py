"""
TeachingAgent - Manages interactive teaching sessions with AI students.

This module provides a TeachingAgent class that creates and manages teaching sessions
where users explain topics and receive feedback from AI students with different personalities.
"""

import os
import uuid
from typing import Dict, List, Optional
from anthropic import Anthropic


class TeachingAgent:
    """
    Manages teaching sessions where users explain topics to AI students.

    The agent maintains session state, analyzes explanations using Claude AI,
    and generates contextual questions based on different AI student modes.
    """

    def __init__(self):
        """Initialize the TeachingAgent with API client and session storage."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-opus-20240229"
        self.sessions: Dict[str, Dict] = {}

    def create_session(self, user_id: str, topic: str, mode: str) -> dict:
        """
        Create a new teaching session.

        Args:
            user_id: Unique identifier for the user
            topic: The topic to be taught
            mode: AI student personality mode (socratic, contrarian, five-year-old, anxious)

        Returns:
            Dictionary containing session_id and welcome_message

        Raises:
            ValueError: If mode is not recognized
        """
        valid_modes = ["socratic", "contrarian", "five-year-old", "anxious"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

        session_id = str(uuid.uuid4())

        # Mode-specific welcome messages
        welcome_messages = {
            "socratic": f"Welcome! I'm here to learn about {topic} through thoughtful questioning. "
                       f"I'll ask probing questions to help deepen your understanding. Let's begin!",
            "contrarian": f"Interesting topic - {topic}. I tend to be skeptical and challenge assumptions. "
                         f"I'll question your claims to make sure you've thought things through. Ready?",
            "five-year-old": f"Yay! I want to learn about {topic}! But I'm only five, so you need to explain "
                            f"things really simply. I'll ask 'why' a lot. Can we start?",
            "anxious": f"Oh, we're learning about {topic}? I worry about edge cases and what could go wrong. "
                      f"I hope you can help me understand the risks and failure scenarios. Shall we begin?"
        }

        self.sessions[session_id] = {
            "user_id": user_id,
            "topic": topic,
            "mode": mode,
            "conversation_history": [],
            "analyses": [],
            "created_at": None  # Could add timestamp if needed
        }

        return {
            "session_id": session_id,
            "welcome_message": welcome_messages[mode]
        }

    def analyze_explanation(self, session_id: str, explanation: str) -> dict:
        """
        Analyze a user's explanation using Claude AI.

        Args:
            session_id: The session identifier
            explanation: The user's explanation text

        Returns:
            Dictionary containing:
                - confidence_score: 0-1 indicating speaker's confidence
                - clarity_score: 0-1 indicating explanation clarity
                - knowledge_gaps: List of identified gaps
                - unexplained_jargon: List of technical terms not explained
                - strengths: List of strong points in the explanation

        Raises:
            KeyError: If session_id doesn't exist
            Exception: If API call fails
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        topic = session["topic"]

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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,  # Reduced for faster response
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )

            # Extract JSON from response
            import json
            analysis_text = response.content[0].text
            analysis = json.loads(analysis_text)

            # Store analysis in session
            session["analyses"].append(analysis)

            return analysis

        except Exception as e:
            raise Exception(f"Failed to analyze explanation: {str(e)}")

    def generate_question(
        self,
        session_id: str,
        explanation: str,
        analysis: dict,
        mode: str
    ) -> str:
        """
        Generate a contextual question from the AI student.

        Args:
            session_id: The session identifier
            explanation: The user's latest explanation
            analysis: Analysis results from analyze_explanation
            mode: AI student mode (socratic, contrarian, five-year-old, anxious)

        Returns:
            The AI student's next question as a string

        Raises:
            KeyError: If session_id doesn't exist
            ValueError: If mode is invalid
            Exception: If API call fails
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        topic = session["topic"]
        history = session["conversation_history"]

        # Build context from conversation history
        history_context = ""
        if history:
            history_context = "\n\nPrevious conversation:\n"
            for turn in history[-3:]:  # Last 3 turns for context
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

        if mode not in mode_prompts:
            raise ValueError(f"Invalid mode: {mode}")

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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                system=mode_prompts[mode],
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            question = response.content[0].text.strip()

            # Store in conversation history
            session["conversation_history"].append({
                "explanation": explanation,
                "analysis": analysis,
                "question": question
            })

            return question

        except Exception as e:
            raise Exception(f"Failed to generate question: {str(e)}")

    def get_session_summary(self, session_id: str) -> dict:
        """
        Get a comprehensive summary of the teaching session.

        Args:
            session_id: The session identifier

        Returns:
            Dictionary containing:
                - topic: The session topic
                - mode: The AI student mode
                - total_turns: Number of conversation turns
                - average_confidence: Mean confidence score across all turns
                - average_clarity: Mean clarity score across all turns
                - persistent_gaps: Knowledge gaps that appear multiple times
                - conversation_history: Full conversation history

        Raises:
            KeyError: If session_id doesn't exist
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        analyses = session["analyses"]

        # Calculate averages
        total_turns = len(analyses)
        average_confidence = 0.0
        average_clarity = 0.0

        if total_turns > 0:
            average_confidence = sum(a["confidence_score"] for a in analyses) / total_turns
            average_clarity = sum(a["clarity_score"] for a in analyses) / total_turns

        # Find persistent gaps (appearing in multiple analyses)
        all_gaps = []
        for analysis in analyses:
            all_gaps.extend(analysis.get("knowledge_gaps", []))

        gap_counts = {}
        for gap in all_gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1

        persistent_gaps = [gap for gap, count in gap_counts.items() if count > 1]

        return {
            "topic": session["topic"],
            "mode": session["mode"],
            "total_turns": total_turns,
            "average_confidence": round(average_confidence, 2),
            "average_clarity": round(average_clarity, 2),
            "persistent_gaps": persistent_gaps,
            "conversation_history": session["conversation_history"]
        }
