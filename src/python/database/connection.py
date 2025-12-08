"""
Database Connection & Initialization
Core database setup and connection management
"""
import sqlite3
import os


class Database:
    """Database connection manager"""
    
    def __init__(self, db_path="data/app.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create directory if not exists
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create if there's a directory
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database tables
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
                full_name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers TEXT,
                duration_seconds INTEGER,
                FOREIGN KEY (student_id) REFERENCES users(id)
            )
        ''')
        
        # Tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                description TEXT,
                duration_minutes INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer INTEGER NOT NULL CHECK(correct_answer BETWEEN 0 AND 3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )
        ''')
        
        # Test rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                room_code TEXT UNIQUE NOT NULL,
                teacher_id INTEGER NOT NULL,
                num_questions INTEGER NOT NULL,
                duration_minutes INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'waiting' CHECK(status IN ('waiting', 'active', 'ended')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            )
        ''')
        
        # Room participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'joined' CHECK(status IN ('joined', 'testing', 'submitted')),
                test_result_id INTEGER,
                FOREIGN KEY (room_id) REFERENCES test_rooms(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (test_result_id) REFERENCES test_results(id),
                UNIQUE(room_id, student_id)
            )
        ''')
        
        # Room questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer INTEGER NOT NULL CHECK(correct_answer BETWEEN 0 AND 3),
                question_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES test_rooms(id) ON DELETE CASCADE
            )
        ''')
        
        # Test progress table (for auto-save)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_final BOOLEAN DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES test_rooms(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                UNIQUE(room_id, student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Database initialized at: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        pass  # Using context manager, connection auto-closes

