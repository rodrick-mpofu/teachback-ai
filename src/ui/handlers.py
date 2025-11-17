"""
TeachBack AI - Event Handlers
Event handling functions for UI interactions
"""

from typing import Optional, Dict, Tuple
from src.mcp.client_wrapper import MCPClientWrapper
from src.utils.elevenlabs_client import text_to_speech_file
from .components import get_analysis_panel, create_initial_state, STUDENT_MODES


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
            mcp_client = MCPClientWrapper(timeout=60)

        result = mcp_client.create_teaching_session(
            user_id=state["user_id"],
            topic=topic,
            mode=mcp_mode
        )

        # Store session ID and welcome message
        state["session_id"] = result["session_id"]
        initial_question = result["welcome_message"]

        state["conversation_history"].append({"role": "student", "content": initial_question})

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
            mcp_client = MCPClientWrapper(timeout=60)

        analysis = mcp_client.analyze_explanation(
            session_id=state["session_id"],
            explanation=explanation
        )

        # Update state with analysis results
        state["confidence_score"] = int(analysis["confidence_score"] * 100)  # Convert 0-1 to 0-100
        state["clarity_score"] = int(analysis["clarity_score"] * 100)
        state["last_analysis"] = analysis

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
