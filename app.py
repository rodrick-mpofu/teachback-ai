"""
TeachBack AI - Learn by Teaching, Not Faking
Main Gradio Application
"""

import gradio as gr
import os
import atexit
from dotenv import load_dotenv
from typing import Optional, Dict, List, Tuple
from src.mcp.client_wrapper import MCPClientWrapper
from src.utils.elevenlabs_client import text_to_speech_file

# Load environment variables
load_dotenv()

# Initialize MCP Client
mcp_client = None
try:
    mcp_client = MCPClientWrapper(timeout=60)  # Increased to 60 seconds for Claude API calls
    print("✅ MCP Client initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize MCP Client: {e}")
    print("The app will attempt to connect when needed.")

# Register cleanup on exit
def cleanup_mcp():
    """Cleanup MCP client on app shutdown"""
    global mcp_client
    if mcp_client:
        try:
            mcp_client.cleanup()
            print("✅ MCP Client cleaned up")
        except Exception as e:
            print(f"Warning: MCP cleanup error: {e}")

atexit.register(cleanup_mcp)

# AI Student Personalities
STUDENT_MODES = {
    "🤔 Socratic Student": "Asks 'why?' to help you discover gaps. Patient and thoughtful, guides you toward deeper understanding.",
    "😈 Contrarian Student": "Challenges every claim you make. Provides counterexamples and plays devil's advocate.",
    "👶 Five-Year-Old Student": "Asks 'why?' until you can explain it simply. Takes everything literally, forces clear explanations.",
    "😰 Anxious Student": "Worries about edge cases and failure scenarios. Asks 'what if...?' constantly."
}

def create_initial_state():
    """Create initial session state"""
    return {
        "session_id": None,
        "user_id": "default_user",
        "topic": None,
        "mode": None,
        "voice_enabled": False,
        "turn_count": 0,
        "max_turns": 10,
        "conversation_history": [],
        "knowledge_gaps": [],
        "confidence_score": 0,
        "clarity_score": 0,
        "last_analysis": None
    }


def start_teaching_session(topic: str, mode: str, voice_enabled: bool, state: Dict) -> Tuple[str, str, str, int, int, Dict]:
    """Initialize a new teaching session using MCP"""
    global mcp_client

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


def submit_explanation(explanation: str, state: Dict) -> Tuple[str, Optional[str], str, int, int, str, Dict]:
    """Process user's explanation and generate AI student response using MCP"""
    global mcp_client

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


def get_analysis_panel(state: Dict) -> str:
    """Generate the analysis panel as markdown with MCP analysis details"""
    gaps = state.get("knowledge_gaps", [])
    turn = state.get("turn_count", 0)
    max_turn = state.get("max_turns", 10)
    last_analysis = state.get("last_analysis")

    # Format knowledge gaps
    gaps_text = "\n".join([f"• {gap}" for gap in gaps]) if gaps else "None detected yet"

    # Add detailed analysis if available
    detailed_analysis = ""
    if last_analysis:
        unexplained = last_analysis.get("unexplained_jargon", [])
        strengths = last_analysis.get("strengths", [])

        if unexplained:
            detailed_analysis += "\n\n### ⚠️ Unexplained Jargon:\n"
            detailed_analysis += "\n".join([f"• {term}" for term in unexplained])

        if strengths:
            detailed_analysis += "\n\n### ✅ Strengths:\n"
            detailed_analysis += "\n".join([f"• {strength}" for strength in strengths])

    analysis_md = f"""
### 🎯 Knowledge Gaps Found:
{gaps_text}
{detailed_analysis}

---

**Turn:** {turn}/{max_turn}
"""
    return analysis_md


def create_progress_bar(percentage: int, length: int = 10) -> str:
    """Create a text-based progress bar"""
    filled = int((percentage / 100) * length)
    bar = "▓" * filled + "░" * (length - filled)
    return f"[{bar}]"


# Simple, clean CSS that works with Gradio
custom_css = """
/* Full width container */
.gradio-container {
    max-width: 100% !important;
    padding: 20px !important;
}

/* Remove default gaps */
.app {
    gap: 0 !important;
}

/* Sidebar styling */
.sidebar {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    min-height: 80vh !important;
    margin-right: 20px !important;
}

.sidebar * {
    color: white !important;
}

/* Main header */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 20px;
    text-align: center;
}

/* Analysis panel - target the column itself */
.analysis-panel {
    background: linear-gradient(135deg, #fff9e6 0%, #fff4d4 100%) !important;
    border: 3px solid #ffd700 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3) !important;
}

/* All children should have transparent backgrounds */
.analysis-panel > *,
.analysis-panel .block,
.analysis-panel .form {
    background: transparent !important;
    border: none !important;
}

/* Text color */
.analysis-panel h3,
.analysis-panel p,
.analysis-panel strong,
.analysis-panel label {
    color: #1a1a2e !important;
}

/* Slider styling within analysis panel */
.analysis-panel input[type="range"] {
    background: transparent !important;
}
"""


# Build Gradio Interface
with gr.Blocks(css=custom_css, title="🎓 TeachBack AI", theme=gr.themes.Soft()) as app:

    # Header
    gr.HTML("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5em;">🎓 TeachBack AI</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; font-style: italic;">"Learn by Teaching, Not Faking"</p>
        </div>
    """)

    with gr.Row(equal_height=False):
        # LEFT COLUMN - Sidebar
        with gr.Column(scale=1, min_width=250, elem_classes="sidebar"):
            mcp_status_icon = "🟢" if mcp_client else "🔴"
            mcp_status_text = "MCP Connected" if mcp_client else "MCP Offline"
            gr.Markdown(f"""
## 📚 Navigation

**Dashboard** ← You are here
My Sessions
Progress
Settings

---

## 🔌 System Status

{mcp_status_icon} **{mcp_status_text}**
Using MCP Server for AI

---

## 👤 Profile

**Rodrick**
Student
            """)

        # RIGHT COLUMN - Main Content
        with gr.Column(scale=4, min_width=600):

            # Session Setup
            with gr.Group():
                gr.Markdown("## 🚀 Start New Teaching Session")

                topic_input = gr.Textbox(
                    label="📚 What topic do you want to teach?",
                    placeholder="e.g., Recursion in Python, Photosynthesis, Blockchain..."
                )

                mode_dropdown = gr.Dropdown(
                    choices=list(STUDENT_MODES.keys()),
                    value="🤔 Socratic Student",
                    label="🎭 Select AI Student Mode"
                )

                mode_description = gr.Markdown(STUDENT_MODES["🤔 Socratic Student"])

                voice_checkbox = gr.Checkbox(
                    label="🎤 Enable Voice Mode",
                    value=False,
                    interactive=True,
                    info="AI student will speak responses with personality-matched voices"
                )

                start_button = gr.Button("🚀 Start Teaching Session", variant="primary", size="lg")
                session_status = gr.Markdown("")

            # Teaching Interface
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Group():
                        gr.Markdown("## 💬 Teaching Interface")

                        explanation_input = gr.Textbox(
                            label="Your Explanation:",
                            placeholder="Explain the concept as if you're teaching a real student...",
                            lines=5
                        )

                        submit_button = gr.Button("📤 Submit Explanation", variant="primary")

                        student_response_output = gr.Markdown(
                            "*Start a session to begin teaching...*"
                        )

                        audio_output = gr.Audio(
                            label="🔊 Student Voice Response",
                            visible=True,
                            autoplay=True
                        )

                # Analysis Panel
                with gr.Column(scale=1, elem_classes="analysis-panel"):
                    gr.Markdown("### 📊 Your Progress")

                    confidence_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=0,
                        label="Confidence Score",
                        interactive=False,
                        info="Based on certainty of explanations"
                    )

                    clarity_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=0,
                        label="Clarity Score",
                        interactive=False,
                        info="Based on structure and simplicity"
                    )

                    analysis_output = gr.Markdown(
                        get_analysis_panel(create_initial_state())
                    )

    # Footer
    mcp_status = "🟢 MCP Server Active" if mcp_client else "🔴 MCP Server Offline"
    gr.Markdown(f"""
---
**Built for MCP's 1st Birthday Hackathon** | Track: MCP in Action - Consumer

{mcp_status} | Powered by Anthropic Claude, Gradio, MCP & ElevenLabs

[LinkedIn](https://www.linkedin.com/in/rodrick-mpofu/) | [GitHub](https://github.com/rodrick-mpofu)
    """)

    # Session State - using gr.State()
    session_state_component = gr.State(create_initial_state())

    # Event Handlers
    mode_dropdown.change(
        fn=lambda mode: STUDENT_MODES.get(mode, ""),
        inputs=[mode_dropdown],
        outputs=[mode_description]
    )

    start_button.click(
        fn=start_teaching_session,
        inputs=[topic_input, mode_dropdown, voice_checkbox, session_state_component],
        outputs=[session_status, student_response_output, analysis_output, confidence_slider, clarity_slider, session_state_component]
    )

    submit_button.click(
        fn=submit_explanation,
        inputs=[explanation_input, session_state_component],
        outputs=[student_response_output, audio_output, analysis_output, confidence_slider, clarity_slider, explanation_input, session_state_component]
    )

    explanation_input.submit(
        fn=submit_explanation,
        inputs=[explanation_input, session_state_component],
        outputs=[student_response_output, audio_output, analysis_output, confidence_slider, clarity_slider, explanation_input, session_state_component]
    )


# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
