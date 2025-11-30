"""
Client Application Package
Clean modular architecture matching server structure
"""
from .client_app import TestClientApp
from .connection import ConnectionManager
from .handlers import TeacherHandler, StudentHandler

__version__ = '2.0.0'
__all__ = ['TestClientApp', 'ConnectionManager', 'TeacherHandler', 'StudentHandler']

