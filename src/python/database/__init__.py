"""
Database Package
Clean repository pattern for database operations

Usage:
    from database import DatabaseManager as Database
    db = Database("data/app.db")
    db.users.create_user(...)  # Access repositories
    db.create_user(...)         # Or use facade methods
"""
from .database_manager import DatabaseManager
from .connection import Database as DBConnection
from .user_repository import UserRepository
from .test_repository import TestRepository
from .room_repository import RoomRepository
from .stats_repository import StatsRepository

# For backward compatibility
Database = DatabaseManager

__version__ = '2.0.0'
__all__ = [
    'Database',
    'DatabaseManager',
    'DBConnection',
    'UserRepository',
    'TestRepository', 
    'RoomRepository',
    'StatsRepository'
]


