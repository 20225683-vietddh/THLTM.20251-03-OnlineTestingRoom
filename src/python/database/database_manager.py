"""
Database Manager
Aggregates all repositories for easy access (Facade pattern)
"""
from .connection import Database as DBConnection
from .user_repository import UserRepository
from .test_repository import TestRepository
from .room_repository import RoomRepository
from .stats_repository import StatsRepository

class DatabaseManager:
    """
    Main database manager - Facade for all repositories
    Maintains backward compatibility with old Database class
    """
    
    def __init__(self, db_path="data/app.db"):
        """Initialize database manager with all repositories"""
        # Core connection
        self.db_conn = DBConnection(db_path)
        self.db_path = db_path
        
        # Initialize repositories
        self.users = UserRepository(self.db_conn.get_connection)
        self.tests = TestRepository(self.db_conn.get_connection)
        self.rooms = RoomRepository(self.db_conn.get_connection)
        self.stats = StatsRepository(self.db_conn.get_connection)
    
    def get_connection(self):
        """Get database connection"""
        return self.db_conn.get_connection()
    
    # ==================== USER OPERATIONS (Delegate to UserRepository) ====================
    
    def create_user(self, username, password_hash, role, full_name, email=None):
        """Create a new user"""
        return self.users.create_user(username, password_hash, role, full_name, email)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.users.get_user_by_username(username)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users.get_user_by_id(user_id)
    
    # ==================== TEST OPERATIONS (Delegate to TestRepository) ====================
    
    def save_test_result(self, student_id, score, total_questions, answers_json, duration_seconds=0):
        """Save test result"""
        return self.tests.save_test_result(student_id, score, total_questions, answers_json, duration_seconds)
    
    def get_user_results(self, user_id):
        """Get test results for a user"""
        return self.tests.get_user_results(user_id)
    
    def get_all_results(self):
        """Get all test results"""
        return self.tests.get_all_results()
    
    # ==================== ROOM OPERATIONS (Delegate to RoomRepository) ====================
    
    def create_test_room(self, room_name, teacher_id, num_questions, duration_minutes):
        """Create test room"""
        return self.rooms.create_test_room(room_name, teacher_id, num_questions, duration_minutes)
    
    def get_room_by_id(self, room_id):
        """Get room by ID"""
        return self.rooms.get_room_by_id(room_id)
    
    def get_room_by_code(self, room_code):
        """Get room by code"""
        return self.rooms.get_room_by_code(room_code)
    
    def get_teacher_rooms(self, teacher_id):
        """Get teacher's rooms"""
        return self.rooms.get_teacher_rooms(teacher_id)
    
    def start_test_room(self, room_id):
        """Start test in room"""
        return self.rooms.start_test_room(room_id)
    
    def end_test_room(self, room_id):
        """
        End test in room
        
        Returns:
            dict: {'success': bool, 'message': str, 'error': str (optional)}
        """
        return self.rooms.end_test_room(room_id)
    
    def join_room(self, room_code, student_id):
        """Student joins room"""
        return self.rooms.join_room(room_code, student_id)
    
    def get_room_participants(self, room_id):
        """Get room participants"""
        return self.rooms.get_room_participants(room_id)
    
    def update_participant_status(self, room_id, student_id, status):
        """Update participant status"""
        return self.rooms.update_participant_status(room_id, student_id, status)
    
    def get_student_rooms(self, student_id):
        """Get student's rooms"""
        return self.rooms.get_student_rooms(student_id)
    
    def get_available_rooms(self, student_id=None):
        """Get available rooms"""
        return self.rooms.get_available_rooms(student_id)
    
    # ==================== ROOM QUESTIONS (Delegate to RoomRepository) ====================
    
    def add_room_question(self, room_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_order=0):
        """Add question to room"""
        return self.rooms.add_room_question(room_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_order)
    
    def get_room_questions(self, room_id):
        """Get questions for a room"""
        return self.rooms.get_room_questions(room_id)
    
    def update_room_question(self, question_id, question_text, option_a, option_b, option_c, option_d, correct_answer):
        """Update room question"""
        return self.rooms.update_room_question(question_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
    
    def delete_room_question(self, question_id):
        """Delete room question"""
        return self.rooms.delete_room_question(question_id)
    
    def get_room_question_count(self, room_id):
        """Get question count for room"""
        return self.rooms.get_room_question_count(room_id)
    
    def get_question_by_id(self, question_id):
        """Get a question by ID"""
        return self.rooms.get_question_by_id(question_id)
    
    # ==================== STATISTICS (Delegate to StatsRepository) ====================
    
    def get_statistics(self):
        """Get overall statistics"""
        return self.stats.get_statistics()
    
    # ==================== UTILITY ====================
    
    def close(self):
        """Close database connection"""
        self.db_conn.close()

