"""
Server Application Package
Django-style modular architecture with clean separation of concerns

Entry point: python -m server.main
"""
from .server_gui import TestServerGUI
from .handlers import RequestHandlers
from .room_manager import RoomManager
from .client_handler import ClientHandler

__version__ = '2.0.0'
__all__ = [
    'TestServerGUI',
    'RequestHandlers',
    'RoomManager',
    'ClientHandler',
]

