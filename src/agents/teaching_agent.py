"""
TeachingAgent - Manages interactive teaching sessions with AI students.

This module provides a TeachingAgent class that creates and manages teaching sessions
where users explain topics and receive feedback from AI students with different personalities.
"""

import os
import uuid
import time
import logging
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic

# Set up logger for this module
logger = logging.getLogger(__name__)

# Load Modal credentials from environment if available
if os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET"):
    os.environ["MODAL_TOKEN_ID"] = os.environ.get("MODAL_TOKEN_ID")
    os.environ["MODAL_TOKEN_SECRET"] = os.environ.get("MODAL_TOKEN_SECRET")

# Optional Modal imports for parallel processing
MODAL_AVAILABLE = False
parallel_analyze_and_question = None
compute_session_analytics = None
analyze_explanation_modal = None
generate_question_modal = None

try:
    import modal
    # Try to reference deployed functions from Modal
    try:
        compute_session_analytics = modal.Function.from_name("teachback-ai", "compute_session_analytics")
        parallel_analyze_and_question = modal.Function.from_name("teachback-ai", "parallel_analyze_and_question")
        analyze_explanation_modal = modal.Function.from_name("teachback-ai", "analyze_explanation_modal")
        generate_question_modal = modal.Function.from_name("teachback-ai", "generate_question_modal")
        MODAL_AVAILABLE = True
        logger.info("[OK] Connected to deployed Modal functions")
    except Exception as lookup_error:
        logger.warning(f"Could not reference deployed Modal functions: {lookup_error}")
        logger.warning("   Make sure you've deployed with: python deploy_modal.py")
        MODAL_AVAILABLE = False
except ImportError:
    logger.warning("Modal package not installed")
    MODAL_AVAILABLE = False


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
        self.model = "claude-sonnet-4-5-20250929"  # Faster than Opus, still very capable
        self.sessions: Dict[str, Dict] = {}
        self.use_modal = os.environ.get("USE_MODAL", "false").lower() == "true"

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

        Uses Modal's analyze_explanation_modal when available for faster execution,
        falls back to local API call if Modal is not available.

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

        # Try to use Modal first if available
        if MODAL_AVAILABLE and analyze_explanation_modal:
            try:
                logger.info("[MODAL] Using Modal for explanation analysis...")
                analysis = analyze_explanation_modal.remote(
                    explanation=explanation,
                    topic=topic
                )

                # Store analysis in session
                session["analyses"].append(analysis)
                logger.info("[MODAL] Analysis completed successfully")
                return analysis

            except Exception as modal_error:
                import traceback
                logger.warning(f"Modal analysis failed: {modal_error}")
                logger.warning(f"Traceback: {traceback.format_exc()}")
                logger.warning("Falling back to local execution")
                # Fall through to local execution

        # Local execution fallback
        logger.info("[LOCAL] Using local Claude API for explanation analysis...")

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
            import re
            analysis_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if analysis_text.startswith("```"):
                # Extract content between ``` markers
                match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', analysis_text, re.DOTALL)
                if match:
                    analysis_text = match.group(1).strip()

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

        Uses Modal's generate_question_modal when available for faster execution,
        falls back to local API call if Modal is not available.

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

        # Try to use Modal first if available
        if MODAL_AVAILABLE and generate_question_modal:
            try:
                logger.info("[MODAL] Using Modal for question generation...")
                question = generate_question_modal.remote(
                    explanation=explanation,
                    mode=mode,
                    analysis=analysis,
                    topic=topic,
                    conversation_history=history
                )

                # Store in conversation history
                session["conversation_history"].append({
                    "explanation": explanation,
                    "analysis": analysis,
                    "question": question
                })

                logger.info("[MODAL] Question generated successfully")
                return question

            except Exception as modal_error:
                import traceback
                logger.warning(f"Modal question generation failed: {modal_error}")
                logger.warning(f"Traceback: {traceback.format_exc()}")
                logger.warning("Falling back to local execution")
                # Fall through to local execution

        # Local execution fallback
        logger.info("[LOCAL] Using local Claude API for question generation...")

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

    def analyze_and_question_parallel(
        self,
        session_id: str,
        explanation: str
    ) -> Tuple[dict, str, float]:
        """
        Analyze explanation and generate question using Modal parallel processing.

        This method uses Modal to run analysis and question generation in parallel
        when USE_MODAL environment variable is set to true. Falls back to sequential
        execution if Modal is not available.

        Args:
            session_id: The session identifier
            explanation: The user's explanation text

        Returns:
            Tuple of (analysis_dict, question_string, execution_time_seconds)

        Raises:
            KeyError: If session_id doesn't exist
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        topic = session["topic"]
        mode = session["mode"]
        conversation_history = session["conversation_history"]

        start_time = time.time()

        # Use Modal if available and enabled
        if self.use_modal and MODAL_AVAILABLE:
            try:
                print("[MODAL] Using Modal for parallel execution...")
                analysis, question = parallel_analyze_and_question.remote(
                    explanation=explanation,
                    mode=mode,
                    topic=topic,
                    conversation_history=conversation_history
                )

                # Store in session
                session["analyses"].append(analysis)
                session["conversation_history"].append({
                    "explanation": explanation,
                    "analysis": analysis,
                    "question": question
                })

                execution_time = time.time() - start_time
                print(f"[MODAL] Modal execution completed in {execution_time:.2f}s")
                return (analysis, question, execution_time)

            except Exception as e:
                print(f"[WARNING] Modal execution failed: {e}, falling back to local execution")
                # Fall through to local execution

        # Fallback to local sequential execution
        print("[LOCAL] Using local sequential execution...")
        analysis = self.analyze_explanation(session_id, explanation)
        question = self.generate_question(session_id, explanation, analysis, mode)

        execution_time = time.time() - start_time
        print(f"[LOCAL] Local execution completed in {execution_time:.2f}s")
        return (analysis, question, execution_time)

    def trigger_background_analytics(self, session_id: str) -> Optional[str]:
        """
        Trigger background analytics computation using Modal.

        This method spawns a non-blocking Modal task to compute session analytics.
        The task runs in the background and doesn't block the main thread.

        Args:
            session_id: The session identifier

        Returns:
            Call ID for the spawned task if Modal is available, None otherwise

        Raises:
            KeyError: If session_id doesn't exist
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Use Modal if available and enabled
        if self.use_modal and MODAL_AVAILABLE:
            try:
                print("[ANALYTICS] Triggering background analytics computation...")
                # Spawn non-blocking analytics task
                call = compute_session_analytics.spawn(session)
                print(f"[ANALYTICS] Analytics task spawned (call_id: {call.object_id})")
                return call.object_id

            except Exception as e:
                print(f"[WARNING] Failed to spawn analytics task: {e}")
                return None

        print("[INFO] Modal not available, skipping background analytics")
        return None
