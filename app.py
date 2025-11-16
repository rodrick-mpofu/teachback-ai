"""
TeachBack AI - Learn by Teaching, Not Faking
Main Gradio Application
"""

import gradio as gr
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List, Tuple
from src.utils.claude_client import generate_ai_student_response, analyze_explanation_with_claude
from src.utils.elevenlabs_client import text_to_speech_file

# Load environment variables
load_dotenv()

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
        "topic": None,
        "mode": None,
        "voice_enabled": False,
        "turn_count": 0,
        "max_turns": 10,
        "conversation_history": [],
        "knowledge_gaps": [],
        "confidence_score": 0,
        "clarity_score": 0
    }


def start_teaching_session(topic: str, mode: str, voice_enabled: bool, state: Dict) -> Tuple[str, str, str, int, int, Dict]:
    """Initialize a new teaching session"""
    if not topic or not topic.strip():
        return "⚠️ Please enter a topic to teach!", "", get_analysis_panel(state), 0, 0, state

    # Reset session state
    state = create_initial_state()
    state["topic"] = topic
    state["mode"] = mode
    state["voice_enabled"] = voice_enabled

    # Generate initial question based on mode
    initial_questions = {
        "🤔 Socratic Student": f"I'm interested in learning about {topic}. What's the core idea behind it, and why should I care?",
        "😈 Contrarian Student": f"Okay, {topic}... I've heard it's overrated. Why should I believe it's actually important?",
        "👶 Five-Year-Old Student": f"What's {topic}? Can you explain it like I'm five?",
        "😰 Anxious Student": f"I'm worried about learning {topic}... What if I don't understand it? Where do I even start?"
    }

    initial_question = initial_questions.get(mode, f"Tell me about {topic}. What is it?")
    state["conversation_history"].append({"role": "student", "content": initial_question})

    status_msg = f"✅ Session started! Teaching: **{topic}** | Mode: **{mode}**"

    return status_msg, initial_question, get_analysis_panel(state), 0, 0, state


def submit_explanation(explanation: str, state: Dict) -> Tuple[str, Optional[str], str, int, int, str, Dict]:
    """Process user's explanation and generate AI student response"""
    if not explanation or not explanation.strip():
        return "⚠️ Please provide an explanation!", None, get_analysis_panel(state), state["confidence_score"], state["clarity_score"], explanation, state

    if not state["topic"]:
        return "⚠️ Please start a teaching session first!", None, get_analysis_panel(state), 0, 0, explanation, state

    # Increment turn count
    state["turn_count"] += 1

    # Add user explanation to history
    state["conversation_history"].append({"role": "teacher", "content": explanation})

    # Generate student response using Claude API
    student_response = generate_ai_student_response(
        topic=state["topic"],
        mode=state["mode"],
        conversation_history=state["conversation_history"],
        turn_count=state["turn_count"]
    )

    # Add student response to history
    state["conversation_history"].append({"role": "student", "content": student_response})

    # Analyze explanation
    state = analyze_user_explanation(explanation, state)

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


def generate_student_response_fallback(explanation: str, mode: str) -> str:
    """Fallback student response if Claude API fails"""
    responses = {
        "🤔 Socratic Student": "That's interesting. But why does that work? Can you break down the underlying principle?",
        "😈 Contrarian Student": "I disagree. What about the cases where that doesn't work? Give me a counterexample.",
        "👶 Five-Year-Old Student": "But why? I don't understand those big words. Can you explain simpler?",
        "😰 Anxious Student": "Wait, what if something goes wrong? What are the edge cases I should worry about?"
    }
    return responses.get(mode, "Can you explain that in more detail?")


def analyze_user_explanation(explanation: str, state: Dict) -> Dict:
    """Analyze user's explanation using Claude API for confidence, clarity, and knowledge gaps"""
    try:
        # Use Claude API for real analysis
        analysis = analyze_explanation_with_claude(
            topic=state["topic"],
            explanation=explanation,
            conversation_history=state["conversation_history"]
        )

        # Update state with Claude's analysis
        state["confidence_score"] = analysis["confidence_score"]
        state["clarity_score"] = analysis["clarity_score"]

        # Add new knowledge gaps (avoid duplicates)
        for gap in analysis["knowledge_gaps"]:
            if gap not in state["knowledge_gaps"]:
                state["knowledge_gaps"].append(gap)

        return state

    except Exception as e:
        # Fallback to simple analysis if Claude API fails
        print(f"Analysis error: {e}")
        import random

        # Simple score updates
        state["confidence_score"] = min(100, state["confidence_score"] + random.randint(5, 15))
        state["clarity_score"] = min(100, state["clarity_score"] + random.randint(5, 15))

        # Detect hedging language
        hedging_words = ["i think", "maybe", "probably", "kind of", "sort of", "i guess"]
        if any(word in explanation.lower() for word in hedging_words):
            state["confidence_score"] = max(0, state["confidence_score"] - 10)

        return state


def get_analysis_panel(state: Dict) -> str:
    """Generate the analysis panel as markdown"""
    gaps = state.get("knowledge_gaps", [])
    turn = state.get("turn_count", 0)
    max_turn = state.get("max_turns", 10)

    # Format knowledge gaps
    gaps_text = "\n".join([f"• {gap}" for gap in gaps]) if gaps else "None detected yet"

    analysis_md = f"""
### 🎯 Knowledge Gaps Found:
{gaps_text}

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
            gr.Markdown("""
## 📚 Navigation

**Dashboard** ← You are here
My Sessions
Progress
Settings

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
    gr.Markdown("""
---
**Built for MCP's 1st Birthday Hackathon** | Track: MCP in Action - Consumer
Powered by Anthropic Claude, Gradio, MCP & ElevenLabs

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
