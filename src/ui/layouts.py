"""
TeachBack AI - UI Layouts
Main layout definitions for the Gradio interface
"""

import gradio as gr
from typing import Dict, Tuple
from .components import (
    STUDENT_MODES,
    create_initial_state,
    get_analysis_panel,
    create_header,
    create_sidebar,
    create_footer
)


def create_session_setup_layout() -> Tuple:
    """Create the session setup section and return its components"""
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

    return topic_input, mode_dropdown, mode_description, voice_checkbox, start_button, session_status


def create_teaching_interface_layout() -> Tuple:
    """Create the teaching interface section and return its components"""
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

    return explanation_input, submit_button, student_response_output, audio_output


def create_analysis_panel_layout() -> Tuple:
    """Create the analysis panel section and return its components"""
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

    return confidence_slider, clarity_slider, analysis_output


def create_main_layout(mcp_client) -> Tuple:
    """
    Create the complete main layout and return all interactive components

    Returns:
        Tuple containing all components needed for event handlers
    """
    # Header
    create_header()

    with gr.Row(equal_height=False):
        # LEFT COLUMN - Sidebar
        create_sidebar(mcp_client)

        # RIGHT COLUMN - Main Content
        with gr.Column(scale=4, min_width=600):
            # Session Setup
            topic_input, mode_dropdown, mode_description, voice_checkbox, start_button, session_status = create_session_setup_layout()

            # Teaching Interface + Analysis Panel
            with gr.Row():
                with gr.Column(scale=2):
                    explanation_input, submit_button, student_response_output, audio_output = create_teaching_interface_layout()

                # Analysis Panel
                confidence_slider, clarity_slider, analysis_output = create_analysis_panel_layout()

    # Footer
    create_footer(mcp_client)

    # Session State
    session_state_component = gr.State(create_initial_state())

    return (
        topic_input,
        mode_dropdown,
        mode_description,
        voice_checkbox,
        start_button,
        session_status,
        explanation_input,
        submit_button,
        student_response_output,
        audio_output,
        confidence_slider,
        clarity_slider,
        analysis_output,
        session_state_component
    )
