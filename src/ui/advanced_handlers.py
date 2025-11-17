"""
Advanced UI Handlers for TeachBack AI
Handles session history, progress tracking, knowledge graphs, and spaced repetition
"""

from typing import Tuple, List, Dict
import gradio as gr
from .handlers import get_db_manager, get_kg_service, get_sr_service


def view_session_history(user_id: str) -> Tuple[str, str]:
    """
    View session history for a user

    Returns:
        Tuple of (sessions_table_html, stats_markdown)
    """
    try:
        db = get_db_manager()

        # Get user stats
        stats = db.get_user_stats(user_id)

        # Get recent sessions
        sessions = db.get_user_sessions(user_id, limit=20)

        # Build stats markdown
        stats_md = f"""
## 📊 Your Learning Stats

- **Total Sessions:** {stats['total_sessions']}
- **Completed Sessions:** {stats['completed_sessions']}
- **Total Turns:** {stats['total_turns']}
- **Average Confidence:** {stats['average_confidence']*100:.0f}%
- **Average Clarity:** {stats['average_clarity']*100:.0f}%
- **Unique Topics:** {stats['unique_topics']}
- **Current Streak:** {stats['current_streak']} days 🔥
"""

        # Build sessions table
        if not sessions:
            table_html = "<p>No sessions found. Start teaching to build your history!</p>"
        else:
            table_html = """
<table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
<thead>
    <tr style="background: #f0f0f0; border-bottom: 2px solid #ddd;">
        <th style="padding: 10px; text-align: left;">Topic</th>
        <th style="padding: 10px; text-align: left;">Mode</th>
        <th style="padding: 10px; text-align: center;">Turns</th>
        <th style="padding: 10px; text-align: center;">Confidence</th>
        <th style="padding: 10px; text-align: center;">Clarity</th>
        <th style="padding: 10px; text-align: left;">Date</th>
        <th style="padding: 10px; text-align: center;">Status</th>
    </tr>
</thead>
<tbody>
"""
            for session in sessions:
                status = "✅ Complete" if session.completed_at else "⏸️ In Progress"
                status_color = "#28a745" if session.completed_at else "#ffc107"

                conf = session.final_confidence or session.average_confidence
                clar = session.final_clarity or session.average_clarity

                table_html += f"""
    <tr style="border-bottom: 1px solid #eee;">
        <td style="padding: 10px;"><strong>{session.topic}</strong></td>
        <td style="padding: 10px;">{session.mode}</td>
        <td style="padding: 10px; text-align: center;">{session.turn_count}</td>
        <td style="padding: 10px; text-align: center;">{conf*100:.0f}%</td>
        <td style="padding: 10px; text-align: center;">{clar*100:.0f}%</td>
        <td style="padding: 10px;">{session.created_at.strftime("%Y-%m-%d %H:%M")}</td>
        <td style="padding: 10px; text-align: center; color: {status_color};">{status}</td>
    </tr>
"""
            table_html += "</tbody></table>"

        return table_html, stats_md

    except Exception as e:
        error_msg = f"Error loading history: {str(e)}"
        return f"<p style='color: red;'>{error_msg}</p>", "## Error\nCould not load stats."


def view_progress_chart(user_id: str, days: int = 30) -> str:
    """
    View progress chart for the last N days

    Returns:
        HTML string with progress visualization
    """
    try:
        db = get_db_manager()
        progress = db.get_progress_history(user_id, days=days)

        if not progress:
            return "<p>No progress data available yet. Complete some sessions to see your progress!</p>"

        # Build simple HTML chart
        chart_html = f"""
<div style="padding: 20px; background: #f9f9f9; border-radius: 8px;">
    <h3>📈 Progress Over Last {days} Days</h3>
    <div style="margin-top: 20px;">
"""

        for metric in progress:
            date_str = metric.date.strftime("%m/%d")
            sessions = metric.sessions_completed
            confidence = metric.average_confidence * 100 if metric.average_confidence else 0
            clarity = metric.average_clarity * 100 if metric.average_clarity else 0

            # Create bar visualization
            conf_bar = f'<div style="background: #4CAF50; width: {confidence}%; height: 20px; border-radius: 4px;"></div>'
            clar_bar = f'<div style="background: #2196F3; width: {clarity}%; height: 20px; border-radius: 4px;"></div>'

            chart_html += f"""
    <div style="margin-bottom: 20px; padding: 10px; background: white; border-radius: 5px;">
        <div style="font-weight: bold; margin-bottom: 5px;">{date_str} - {sessions} session(s)</div>
        <div style="margin-bottom: 5px;">
            <span style="font-size: 12px;">Confidence: {confidence:.0f}%</span>
            {conf_bar}
        </div>
        <div>
            <span style="font-size: 12px;">Clarity: {clarity:.0f}%</span>
            {clar_bar}
        </div>
    </div>
"""

        chart_html += """
    </div>
</div>
"""
        return chart_html

    except Exception as e:
        return f"<p style='color: red;'>Error loading progress: {str(e)}</p>"


def view_knowledge_graph(user_id: str) -> str:
    """
    View knowledge graph visualization

    Returns:
        HTML string with interactive graph
    """
    try:
        db = get_db_manager()
        kg_service = get_kg_service()

        # Get graph data from database
        graph_data = db.get_user_knowledge_graph(user_id)

        if not graph_data["nodes"]:
            return "<p>No knowledge graph yet. Complete some sessions to build your graph!</p>"

        # Generate interactive visualization
        html = kg_service.generate_graph_html(graph_data)

        return html

    except Exception as e:
        return f"<p style='color: red;'>Error loading knowledge graph: {str(e)}</p>"


def view_spaced_repetition(user_id: str) -> Tuple[str, str]:
    """
    View spaced repetition schedule

    Returns:
        Tuple of (due_reviews_html, upcoming_schedule_html)
    """
    try:
        sr_service = get_sr_service()

        # Get due reviews
        due_reviews = sr_service.get_due_reviews(user_id)

        # Get upcoming schedule
        schedule = sr_service.get_review_schedule(user_id, days=14)

        # Get statistics
        stats = sr_service.get_review_statistics(user_id)

        # Build due reviews HTML
        if not due_reviews:
            due_html = """
<div style="padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; color: #155724;">
    <h3>✅ All Caught Up!</h3>
    <p>No reviews due right now. Great job!</p>
</div>
"""
        else:
            due_html = f"""
<div style="padding: 20px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; color: #856404;">
    <h3>⏰ Reviews Due Now: {len(due_reviews)}</h3>
    <ul>
"""
            for review in due_reviews:
                overdue = review["days_overdue"]
                due_html += f"""
        <li style="margin: 10px 0;">
            <strong>{review['topic']}</strong>
            <br><span style="font-size: 12px; color: #666;">
                {overdue} days overdue | Reviewed {review['repetition_number']} times
            </span>
        </li>
"""
            due_html += "</ul></div>"

        # Build upcoming schedule HTML
        schedule_html = f"""
<div style="padding: 20px; background: #f9f9f9; border-radius: 8px; margin-top: 20px;">
    <h3>📅 Upcoming Reviews (Next 14 Days)</h3>
    <p><strong>Statistics:</strong></p>
    <ul>
        <li>Due now: {stats['items_due_now']}</li>
        <li>Next 7 days: {stats['items_next_7_days']}</li>
        <li>Next 30 days: {stats['items_next_30_days']}</li>
    </ul>
"""

        if "overdue" in schedule and schedule["overdue"]:
            schedule_html += f"<div style='background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            schedule_html += f"<strong>Overdue ({len(schedule['overdue'])})</strong></div>"

        for date_key in sorted([k for k in schedule.keys() if k != "overdue"]):
            items = schedule[date_key]
            schedule_html += f"""
    <div style="background: white; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #2196F3;">
        <strong>{date_key}</strong> ({len(items)} review(s))
        <ul style="margin: 5px 0 0 20px;">
"""
            for item in items:
                schedule_html += f"<li>{item['topic']}</li>"

            schedule_html += "</ul></div>"

        schedule_html += "</div>"

        return due_html, schedule_html

    except Exception as e:
        error = f"<p style='color: red;'>Error loading spaced repetition: {str(e)}</p>"
        return error, error


def conduct_review(user_id: str, review_id: int, quality: int) -> str:
    """
    Record a review

    Args:
        user_id: User ID
        review_id: Review item ID
        quality: Quality score (0-5)

    Returns:
        Result message
    """
    try:
        sr_service = get_sr_service()
        result = sr_service.record_review(review_id, quality)

        if "error" in result:
            return f"❌ {result['error']}"

        next_date = result['next_review'].strftime("%Y-%m-%d")

        return f"""
✅ Review recorded for **{result['topic']}**!

- Quality: {quality}/5
- Next review: {next_date} (in {result['interval_days']} days)
- Easiness Factor: {result['easiness_factor']}
- Repetition #: {result['repetition_number']}
"""

    except Exception as e:
        return f"❌ Error recording review: {str(e)}"


def get_session_details(session_id: str) -> Tuple[str, str]:
    """
    Get detailed view of a specific session

    Returns:
        Tuple of (conversation_html, analysis_summary)
    """
    try:
        db = get_db_manager()

        # Get session
        session = db.get_session(session_id)
        if not session:
            return "<p>Session not found</p>", "# Error\nSession not found"

        # Get conversations
        conversations = db.get_session_conversations(session_id)

        # Get analyses
        analyses = db.get_session_analyses(session_id)

        # Build conversation HTML
        conv_html = f"""
<div style="padding: 20px; background: #f9f9f9; border-radius: 8px;">
    <h2>Session: {session.topic}</h2>
    <p><strong>Mode:</strong> {session.mode} | <strong>Date:</strong> {session.created_at.strftime("%Y-%m-%d %H:%M")}</p>
    <hr>
"""

        for conv in conversations:
            role_color = "#E3F2FD" if conv.role == "student" else "#FFF9C4"
            role_icon = "🎓" if conv.role == "student" else "👨‍🏫"

            conv_html += f"""
    <div style="background: {role_color}; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #2196F3;">
        <strong>{role_icon} {conv.role.capitalize()}</strong>
        <p style="margin-top: 10px;">{conv.content}</p>
    </div>
"""

        conv_html += "</div>"

        # Build analysis summary
        analysis_md = f"""
# 📊 Analysis Summary

**Turns:** {session.turn_count}/{session.max_turns}

**Average Confidence:** {session.average_confidence*100:.0f}%

**Average Clarity:** {session.average_clarity*100:.0f}%

## Knowledge Gaps Identified:
"""

        all_gaps = []
        for analysis in analyses:
            all_gaps.extend(analysis.knowledge_gaps)

        unique_gaps = list(set(all_gaps))
        if unique_gaps:
            for gap in unique_gaps:
                analysis_md += f"- {gap}\n"
        else:
            analysis_md += "None identified\n"

        return conv_html, analysis_md

    except Exception as e:
        error = f"<p style='color: red;'>Error loading session: {str(e)}</p>"
        return error, f"# Error\n{str(e)}"
