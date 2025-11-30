"""
User Repository
Handles all user-related database operations
"""
import sqlite3


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, db_connection_getter):
        """
        Initialize repository
        
        Args:
            db_connection_getter: Function that returns database connection
        """
        self.get_connection = db_connection_getter
    
    def create_user(self, username, password_hash, role, full_name, email=None):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, full_name, email))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return user_id
        except sqlite3.IntegrityError:
            return None  # Username already exists
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, full_name, email, created_at
            FROM users
            WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password_hash': row[2],
                'role': row[3],
                'full_name': row[4],
                'email': row[5],
                'created_at': str(row[6]) if row[6] else None
            }
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, full_name, email, created_at
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password_hash': row[2],
                'role': row[3],
                'full_name': row[4],
                'email': row[5],
                'created_at': str(row[6]) if row[6] else None
            }
        return None

