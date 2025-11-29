"""
TeachBack AI - Learn by Teaching, Not Faking
Main Gradio Application
"""

import gradio as gr
import os
import atexit
from dotenv import load_dotenv
from src.mcp.client_wrapper import MCPClientWrapper
from src.ui import (
    CUSTOM_CSS,
    create_main_layout,
    start_teaching_session,
    submit_explanation,
    update_mode_description,
    create_advanced_features_interface
)
from src.ui.components import create_footer

# Load environment variables
load_dotenv()

# Initialize MCP Client
mcp_client = None
try:
    mcp_client = MCPClientWrapper(timeout=300)  # Increased to 300 seconds for Claude API calls
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


# Build Gradio Interface
with gr.Blocks(css=CUSTOM_CSS, title="🎓 TeachBack AI", theme='shivi/calm_seafoam') as app:

    # Create tabbed interface
    with gr.Tabs() as tabs:
        # Main Teaching Tab
        with gr.Tab("🎓 Teach"):
            # Create all UI components and get references
            (
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
            ) = create_main_layout(mcp_client)

            # Event Handlers for main teaching tab
            mode_dropdown.change(
                fn=update_mode_description,
                inputs=[mode_dropdown],
                outputs=[mode_description]
            )

            start_button.click(
                fn=lambda topic, mode, voice, state: start_teaching_session(topic, mode, voice, state, mcp_client),
                inputs=[topic_input, mode_dropdown, voice_checkbox, session_state_component],
                outputs=[session_status, student_response_output, analysis_output, confidence_slider, clarity_slider, session_state_component]
            )

            submit_button.click(
                fn=lambda explanation, state: submit_explanation(explanation, state, mcp_client),
                inputs=[explanation_input, session_state_component],
                outputs=[student_response_output, audio_output, analysis_output, confidence_slider, clarity_slider, explanation_input, session_state_component]
            )

            explanation_input.submit(
                fn=lambda explanation, state: submit_explanation(explanation, state, mcp_client),
                inputs=[explanation_input, session_state_component],
                outputs=[student_response_output, audio_output, analysis_output, confidence_slider, clarity_slider, explanation_input, session_state_component]
            )

        # Advanced Features Tabs
        create_advanced_features_interface(default_user_id="default_user")

    # Footer at the bottom of the entire page
    create_footer(mcp_client)


# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
