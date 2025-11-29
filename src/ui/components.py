"""
TeachBack AI - UI Components
Reusable Gradio components and helpers
"""

import gradio as gr
from typing import Dict

# AI Student Personalities
STUDENT_MODES = {
    "🤔 Socratic Student": "Asks 'why?' to help you discover gaps. Patient and thoughtful, guides you toward deeper understanding.",
    "😈 Contrarian Student": "Challenges every claim you make. Provides counterexamples and plays devil's advocate.",
    "👶 Five-Year-Old Student": "Asks 'why?' until you can explain it simply. Takes everything literally, forces clear explanations.",
    "😰 Anxious Student": "Worries about edge cases and failure scenarios. Asks 'what if...?' constantly."
}


def create_initial_state() -> Dict:
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
        "last_analysis": None,
        "all_analyses": []  # Track all analyses for Modal background analytics
    }


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


def create_header() -> gr.HTML:
    """Create the main header component"""
    return gr.HTML("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5em;">🎓 TeachBack AI</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; font-style: italic;">"Learn by Teaching, Not Faking"</p>
        </div>
    """)


def create_sidebar(mcp_client) -> gr.Column:
    """Create the sidebar component"""
    mcp_status_icon = "🟢" if mcp_client else "🔴"
    mcp_status_text = "MCP Connected" if mcp_client else "MCP Offline"

    with gr.Column(scale=1, min_width=250, elem_classes="sidebar") as sidebar:
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

    return sidebar


def create_footer(mcp_client) -> gr.Markdown:
    """Create the footer component"""
    mcp_status = "🟢 MCP Server Active" if mcp_client else "🔴 MCP Server Offline"
    return gr.Markdown(f"""
---
**Built for MCP's 1st Birthday Hackathon** | Track: MCP in Action - Consumer

{mcp_status} | Powered by Anthropic Claude, Gradio, MCP & ElevenLabs

[LinkedIn](https://www.linkedin.com/in/rodrick-mpofu/) | [GitHub](https://github.com/rodrick-mpofu)
    """)


# Simple, clean CSS that works with Gradio
CUSTOM_CSS = """
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
    background: rgba(22, 33, 62, 0.30) !important;
    backdrop-filter: blur(22px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(180%) !important;

    border-radius: 12px !important;
    padding: 20px !important;

    border: 2px solid transparent !important;
    background-image:
        linear-gradient(rgba(22, 33, 62, 0.30), rgba(22, 33, 62, 0.30)),
        linear-gradient(180deg, #1a1a2e, #16213e) !important;
    background-origin: border-box !important;
    background-clip: padding-box, border-box !important;

    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;

    min-height: 80vh !important;
    margin-right: 20px !important;
}

.sidebar * {
    color: white !important;
}

/* Main header */
.main-header {
    background: linear-gradient(to right, #5433ff, #20bdff, #a5fecb);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(15px) saturate(180%);

    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 12px;

    padding: 30px;
    margin-bottom: 20px;
    text-align: center;
    color: white;

    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
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

/* Text color - ensure all text is dark/black */
.analysis-panel,
.analysis-panel *,
.analysis-panel h3,
.analysis-panel p,
.analysis-panel strong,
.analysis-panel label,
.analysis-panel .label,
.analysis-panel span,
.analysis-panel div {
    color: #000000 !important;
}

/* Slider styling within analysis panel */
.analysis-panel input[type="range"] {
    background: transparent !important;
}
"""
