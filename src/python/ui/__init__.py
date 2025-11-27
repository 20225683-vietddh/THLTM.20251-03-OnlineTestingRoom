"""
UI Module - Separate UI components for clean architecture
"""

from .login_window import LoginWindow
from .register_window import RegisterWindow
from .student_window import StudentWindow
from .teacher_window import TeacherWindow

__all__ = ['LoginWindow', 'RegisterWindow', 'StudentWindow', 'TeacherWindow']

