"""
Advanced UI Layouts for TeachBack AI
Layouts for session history, progress, knowledge graph, and spaced repetition
"""

import gradio as gr
from .advanced_handlers import (
    view_session_history,
    view_progress_chart,
    view_knowledge_graph,
    view_spaced_repetition,
    conduct_review,
    get_session_details
)


def create_history_tab(default_user_id: str = "default_user"):
    """Create the Session History tab"""
    with gr.Tab("📚 Session History"):
        gr.Markdown("## Your Teaching Journey")

        user_id = gr.State(default_user_id)

        refresh_btn = gr.Button("🔄 Refresh History", variant="secondary")

        with gr.Row():
            with gr.Column(scale=3):
                sessions_table = gr.HTML("<p>Loading sessions...</p>")

            with gr.Column(scale=1):
                stats_display = gr.Markdown("Loading stats...")

        # Refresh on button click
        refresh_btn.click(
            fn=lambda uid: view_session_history(uid),
            inputs=[user_id],
            outputs=[sessions_table, stats_display]
        )

    return user_id


def create_progress_tab(default_user_id: str = "default_user"):
    """Create the Progress Tracking tab"""
    with gr.Tab("📈 Progress Tracker"):
        gr.Markdown("## Track Your Learning Progress")

        user_id = gr.State(default_user_id)

        days_slider = gr.Slider(
            minimum=7,
            maximum=90,
            value=30,
            step=1,
            label="Days to Display"
        )

        refresh_btn = gr.Button("🔄 Refresh Progress", variant="secondary")

        progress_chart = gr.HTML("<p>Loading progress...</p>")

        # Update on button click
        refresh_btn.click(
            fn=lambda uid, days: view_progress_chart(uid, days),
            inputs=[user_id, days_slider],
            outputs=[progress_chart]
        )

        # Update on slider change
        days_slider.change(
            fn=lambda uid, days: view_progress_chart(uid, days),
            inputs=[user_id, days_slider],
            outputs=[progress_chart]
        )

    return user_id


def create_knowledge_graph_tab(default_user_id: str = "default_user"):
    """Create the Knowledge Graph tab"""
    with gr.Tab("🕸️ Knowledge Graph"):
        gr.Markdown("""
## Your Knowledge Network

This interactive graph shows all the topics you've taught and how they relate to each other.

- **Node Size:** How many times you've taught this topic
- **Node Color:** Your confidence level (Green = High, Yellow = Medium, Blue = Low)
- **Hover:** View detailed stats
- **Drag:** Move nodes around
- **Scroll:** Zoom in/out
""")

        user_id = gr.State(default_user_id)

        refresh_btn = gr.Button("🔄 Refresh Graph", variant="secondary")

        graph_display = gr.HTML("<p>Loading knowledge graph...</p>")

        # Update on button click
        refresh_btn.click(
            fn=lambda uid: view_knowledge_graph(uid),
            inputs=[user_id],
            outputs=[graph_display]
        )

    return user_id


def create_spaced_repetition_tab(default_user_id: str = "default_user"):
    """Create the Spaced Repetition tab"""
    with gr.Tab("🔁 Review Schedule"):
        gr.Markdown("""
## Spaced Repetition System

Based on the **SM-2 algorithm**, this system helps you retain knowledge by scheduling reviews at optimal intervals.

**How it works:**
1. After each session, topics are added to your review queue
2. Review topics when they're due
3. Rate your recall quality (0-5)
4. The algorithm adjusts future review intervals based on your performance
""")

        user_id = gr.State(default_user_id)

        refresh_btn = gr.Button("🔄 Refresh Schedule", variant="secondary")

        due_reviews = gr.HTML("<p>Loading reviews...</p>")
        upcoming_schedule = gr.HTML("<p>Loading schedule...</p>")

        # Manual review section
        with gr.Accordion("✏️ Record a Review", open=False):
            gr.Markdown("Record a manual review for a topic:")

            review_id_input = gr.Number(label="Review Item ID", precision=0)
            quality_slider = gr.Slider(
                minimum=0,
                maximum=5,
                value=3,
                step=1,
                label="Recall Quality",
                info="0=Complete forget, 3=Correct with difficulty, 5=Perfect recall"
            )

            record_btn = gr.Button("✅ Record Review")
            review_result = gr.Markdown("")

            record_btn.click(
                fn=lambda uid, rid, q: conduct_review(uid, int(rid), int(q)),
                inputs=[user_id, review_id_input, quality_slider],
                outputs=[review_result]
            )

        # Refresh functionality
        refresh_btn.click(
            fn=lambda uid: view_spaced_repetition(uid),
            inputs=[user_id],
            outputs=[due_reviews, upcoming_schedule]
        )

    return user_id


def create_advanced_features_interface(default_user_id: str = "default_user"):
    """
    Create a complete interface with all advanced features as tabs

    This can be added to the main app or used as a separate page
    """
    with gr.Tabs() as tabs:
        create_history_tab(default_user_id)
        create_progress_tab(default_user_id)
        create_knowledge_graph_tab(default_user_id)
        create_spaced_repetition_tab(default_user_id)

    return tabs
