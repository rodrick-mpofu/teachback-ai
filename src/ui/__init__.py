"""
TeachBack AI - UI Module
Exports UI components, layouts, and handlers
"""

from .components import (
    STUDENT_MODES,
    create_initial_state,
    get_analysis_panel,
    create_progress_bar,
    CUSTOM_CSS
)

from .layouts import create_main_layout

from .handlers import (
    start_teaching_session,
    submit_explanation,
    update_mode_description
)

__all__ = [
    'STUDENT_MODES',
    'create_initial_state',
    'get_analysis_panel',
    'create_progress_bar',
    'CUSTOM_CSS',
    'create_main_layout',
    'start_teaching_session',
    'submit_explanation',
    'update_mode_description'
]
