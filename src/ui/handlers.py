"""
TeachBack AI - Event Handlers
Event handling functions for UI interactions
"""

import os
from typing import Optional, Dict, Tuple
from src.mcp.client_wrapper import MCPClientWrapper
from src.utils.elevenlabs_client import text_to_speech_file
from src.database.db_manager import DatabaseManager
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.spaced_repetition import SpacedRepetitionService
from .components import get_analysis_panel, create_initial_state, STUDENT_MODES

# Initialize database and services (singleton pattern)
_db_manager = None
_kg_service = None
_sr_service = None


def get_db_manager():
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager("teachback.db")
    return _db_manager


def get_kg_service():
    """Get or create knowledge graph service singleton"""
    global _kg_service
    if _kg_service is None:
        _kg_service = KnowledgeGraphService()
    return _kg_service


def get_sr_service():
    """Get or create spaced repetition service singleton"""
    global _sr_service
    if _sr_service is None:
        _sr_service = SpacedRepetitionService(get_db_manager())
    return _sr_service


def is_modal_enabled():
    """Check if Modal is enabled via environment variable"""
    return os.environ.get("USE_MODAL", "false").lower() == "true"


def start_teaching_session(
    topic: str,
    mode: str,
    voice_enabled: bool,
    state: Dict,
    mcp_client: MCPClientWrapper
) -> Tuple[str, str, str, int, int, Dict]:
    """Initialize a new teaching session using MCP"""

    if not topic or not topic.strip():
        return "⚠️ Please enter a topic to teach!", "", get_analysis_panel(state), 0, 0, state

    # Reset session state
    state = create_initial_state()
    state["topic"] = topic
    state["mode"] = mode
    state["voice_enabled"] = voice_enabled

    try:
        # Convert mode to MCP format (remove emoji prefix)
        mode_map = {
            "🤔 Socratic Student": "socratic",
            "😈 Contrarian Student": "contrarian",
            "👶 Five-Year-Old Student": "five-year-old",
            "😰 Anxious Student": "anxious"
        }
        mcp_mode = mode_map.get(mode, "socratic")

        # Call MCP to create session
        if not mcp_client:
            mcp_client = MCPClientWrapper(timeout=120)

        result = mcp_client.create_teaching_session(
            user_id=state["user_id"],
            topic=topic,
            mode=mcp_mode
        )

        # Store session ID and welcome message
        state["session_id"] = result["session_id"]
        initial_question = result["welcome_message"]

        state["conversation_history"].append({"role": "student", "content": initial_question})

        # Save to database
        try:
            db = get_db_manager()
            # Ensure user exists
            db.get_or_create_user(state["user_id"], "default_user")
            # Create session in database
            db.create_session(
                session_id=state["session_id"],
                user_id=state["user_id"],
                topic=topic,
                mode=mcp_mode,
                voice_enabled=voice_enabled,
                max_turns=state["max_turns"]
            )
            # Add initial conversation
            db.add_conversation_turn(
                session_id=state["session_id"],
                turn_number=0,
                role="student",
                content=initial_question
            )
        except Exception as db_error:
            print(f"Database error: {db_error}")
            # Continue even if database fails

        status_msg = f"✅ Session started via MCP! Teaching: **{topic}** | Mode: **{mode}** | Session ID: `{state['session_id'][:8]}...`"

        return status_msg, initial_question, get_analysis_panel(state), 0, 0, state

    except Exception as e:
        # Fallback to local session if MCP fails
        error_msg = f"⚠️ MCP connection issue: {str(e)}\nStarting local session..."
        print(f"MCP Error: {e}")

        # Generate fallback initial question
        initial_questions = {
            "🤔 Socratic Student": f"I'm interested in learning about {topic}. What's the core idea behind it, and why should I care?",
            "😈 Contrarian Student": f"Okay, {topic}... I've heard it's overrated. Why should I believe it's actually important?",
            "👶 Five-Year-Old Student": f"What's {topic}? Can you explain it like I'm five?",
            "😰 Anxious Student": f"I'm worried about learning {topic}... What if I don't understand it? Where do I even start?"
        }
        initial_question = initial_questions.get(mode, f"Tell me about {topic}. What is it?")
        state["conversation_history"].append({"role": "student", "content": initial_question})

        return error_msg, initial_question, get_analysis_panel(state), 0, 0, state


def submit_explanation(
    explanation: str,
    state: Dict,
    mcp_client: MCPClientWrapper
) -> Tuple[str, Optional[str], str, int, int, str, Dict]:
    """Process user's explanation and generate AI student response using MCP"""

    if not explanation or not explanation.strip():
        return "⚠️ Please provide an explanation!", None, get_analysis_panel(state), state["confidence_score"], state["clarity_score"], explanation, state

    if not state["topic"] or not state.get("session_id"):
        return "⚠️ Please start a teaching session first!", None, get_analysis_panel(state), 0, 0, explanation, state

    # Increment turn count
    state["turn_count"] += 1

    # Add user explanation to history
    state["conversation_history"].append({"role": "teacher", "content": explanation})

    try:
        # Convert mode to MCP format
        mode_map = {
            "🤔 Socratic Student": "socratic",
            "😈 Contrarian Student": "contrarian",
            "👶 Five-Year-Old Student": "five-year-old",
            "😰 Anxious Student": "anxious"
        }
        mcp_mode = mode_map.get(state["mode"], "socratic")

        # Step 1: Analyze explanation using MCP
        if not mcp_client:
            mcp_client = MCPClientWrapper(timeout=120)

        analysis = mcp_client.analyze_explanation(
            session_id=state["session_id"],
            explanation=explanation
        )

        # Update state with analysis results
        state["confidence_score"] = int(analysis["confidence_score"] * 100)  # Convert 0-1 to 0-100
        state["clarity_score"] = int(analysis["clarity_score"] * 100)
        state["last_analysis"] = analysis

        # Track all analyses for Modal background analytics
        if "all_analyses" not in state:
            state["all_analyses"] = []
        state["all_analyses"].append(analysis)

        # Update knowledge gaps (avoid duplicates)
        for gap in analysis.get("knowledge_gaps", []):
            if gap not in state["knowledge_gaps"]:
                state["knowledge_gaps"].append(gap)

        # Step 2: Generate student question using MCP
        student_response = mcp_client.generate_question(
            session_id=state["session_id"],
            explanation=explanation,
            analysis=analysis,
            mode=mcp_mode
        )

        # Add student response to history
        state["conversation_history"].append({"role": "student", "content": student_response})

        # Trigger background analytics every 5 interactions if Modal is enabled
        if is_modal_enabled() and state["turn_count"] % 5 == 0:
            try:
                # Import the deployed Modal function directly
                from src.agents.teaching_agent import compute_session_analytics, MODAL_AVAILABLE

                if MODAL_AVAILABLE and compute_session_analytics:
                    # Build session history with all analyses
                    session_data = {
                        "topic": state["topic"],
                        "mode": mcp_mode,
                        "conversation_history": state["conversation_history"],
                        "analyses": state.get("all_analyses", [])
                    }

                    print(f"[ANALYTICS] Triggering background analytics computation (turn {state['turn_count']})...")
                    print(f"[ANALYTICS] Session data: {len(session_data['analyses'])} analyses")
                    call = compute_session_analytics.spawn(session_data)
                    print(f"[ANALYTICS] Analytics task spawned (call_id: {call.object_id})")
                    student_response = "\n[Computing analytics in background...]\n\n" + student_response
                else:
                    print("[INFO] Modal not available for background analytics")
            except Exception as bg_error:
                print(f"[WARNING] Background analytics error: {bg_error}")

        # Save to database
        try:
            db = get_db_manager()

            # Save conversation turns
            db.add_conversation_turn(
                session_id=state["session_id"],
                turn_number=state["turn_count"],
                role="teacher",
                content=explanation
            )
            db.add_conversation_turn(
                session_id=state["session_id"],
                turn_number=state["turn_count"],
                role="student",
                content=student_response
            )

            # Save analysis
            db.add_analysis(
                session_id=state["session_id"],
                turn_number=state["turn_count"],
                confidence_score=analysis["confidence_score"],
                clarity_score=analysis["clarity_score"],
                knowledge_gaps=analysis.get("knowledge_gaps", []),
                unexplained_jargon=analysis.get("unexplained_jargon", []),
                strengths=analysis.get("strengths", [])
            )

            # Update session metrics
            db.update_session_metrics(
                session_id=state["session_id"],
                turn_count=state["turn_count"],
                average_confidence=state["confidence_score"] / 100,
                average_clarity=state["clarity_score"] / 100
            )

            # Update knowledge graph (with timeout protection)
            # TEMPORARILY DISABLED for debugging
            try:
                print("[DEBUG] Skipping knowledge graph extraction (temporarily disabled)")
                related_concepts = []  # Skip KG extraction
                # kg_service = get_kg_service()
                # related_concepts = kg_service.extract_related_concepts(
                #     state["topic"],
                #     state["conversation_history"]
                # )

                db.create_or_update_knowledge_node(
                    user_id=state["user_id"],
                    topic=state["topic"],
                    confidence=state["confidence_score"] / 100,
                    clarity=state["clarity_score"] / 100,
                    related_concepts=related_concepts,
                    gaps=analysis.get("knowledge_gaps", [])
                )

                # Create edges for related concepts
                for related in related_concepts:
                    db.create_or_update_knowledge_node(
                        user_id=state["user_id"],
                        topic=related,
                        confidence=0.5,
                        clarity=0.5,
                        related_concepts=[state["topic"]],
                        gaps=[]
                    )
                    db.create_knowledge_edge(
                        from_topic=state["topic"],
                        to_topic=related,
                        user_id=state["user_id"],
                        relationship_type="related_to"
                    )
            except Exception as kg_error:
                print(f"[WARNING] Knowledge graph update failed: {kg_error}")
                # Continue without knowledge graph - don't block the conversation

        except Exception as db_error:
            print(f"Database error: {db_error}")
            # Continue even if database fails

        # Generate voice response if enabled
        audio_path = None
        if state["voice_enabled"]:
            try:
                audio_path = text_to_speech_file(
                    text=student_response,
                    mode=state["mode"],
                    output_filename=f"response_{state['turn_count']}.mp3"
                )
            except Exception as e:
                print(f"Voice generation error: {e}")
                # Continue without voice if error occurs

        # Check if session should end
        if state["turn_count"] >= state["max_turns"]:
            student_response += f"\n\n---\n**Session complete!** You've completed {state['turn_count']} turns. Great teaching!"

            # Mark session as complete and update spaced repetition
            try:
                db = get_db_manager()
                db.complete_session(
                    session_id=state["session_id"],
                    final_confidence=state["confidence_score"] / 100,
                    final_clarity=state["clarity_score"] / 100
                )

                # Update progress metrics
                db.update_progress_metrics(state["user_id"])

                # Auto-create spaced repetition review
                sr_service = get_sr_service()
                sr_service.auto_create_review_from_session(
                    user_id=state["user_id"],
                    topic=state["topic"],
                    confidence=state["confidence_score"] / 100,
                    clarity=state["clarity_score"] / 100,
                    knowledge_gaps=state["knowledge_gaps"]
                )
            except Exception as db_error:
                print(f"Session completion error: {db_error}")

        return student_response, audio_path, get_analysis_panel(state), state["confidence_score"], state["clarity_score"], "", state

    except Exception as e:
        # Fallback error handling
        error_msg = f"⚠️ Error processing via MCP: {str(e)}\n\nPlease try again or restart the session."
        print(f"MCP Error in submit_explanation: {e}")

        # Return error without updating state much
        return error_msg, None, get_analysis_panel(state), state["confidence_score"], state["clarity_score"], explanation, state


def generate_student_response_fallback(explanation: str, mode: str) -> str:
    """Fallback student response if Claude API fails"""
    responses = {
        "🤔 Socratic Student": "That's interesting. But why does that work? Can you break down the underlying principle?",
        "😈 Contrarian Student": "I disagree. What about the cases where that doesn't work? Give me a counterexample.",
        "👶 Five-Year-Old Student": "But why? I don't understand those big words. Can you explain simpler?",
        "😰 Anxious Student": "Wait, what if something goes wrong? What are the edge cases I should worry about?"
    }
    return responses.get(mode, "Can you explain that in more detail?")


def update_mode_description(mode: str) -> str:
    """Update the mode description when dropdown changes"""
    return STUDENT_MODES.get(mode, "")
