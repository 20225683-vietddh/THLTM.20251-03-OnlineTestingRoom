"""
Database management using SQLite
Handles users, test results, and questions
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="data/app.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
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
        
        # Tests table (for multiple tests support)
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
        
        # Questions table (better than JSON file)
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
        
        conn.commit()
        conn.close()
        
        print(f"✓ Database initialized at: {self.db_path}")
    
    # ==================== USER OPERATIONS ====================
    
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
            FROM users WHERE username = ?
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
                'created_at': row[6]
            }
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, full_name, email, created_at
            FROM users WHERE id = ?
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
                'created_at': row[6]
            }
        return None
    
    def get_all_students(self):
        """Get all students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, full_name, email, created_at
            FROM users WHERE role = 'student'
            ORDER BY full_name
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            students.append({
                'id': row[0],
                'username': row[1],
                'full_name': row[2],
                'email': row[3],
                'created_at': row[4]
            })
        return students
    
    # ==================== TEST RESULTS OPERATIONS ====================
    
    def save_test_result(self, student_id, score, total_questions, answers_json, duration_seconds):
        """Save test result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO test_results (student_id, score, total_questions, answers, duration_seconds)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, score, total_questions, answers_json, duration_seconds))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_student_results(self, student_id):
        """Get all test results for a student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, test_date, score, total_questions, duration_seconds
            FROM test_results
            WHERE student_id = ?
            ORDER BY test_date DESC
        ''', (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'test_date': row[1],
                'score': row[2],
                'total_questions': row[3],
                'duration_seconds': row[4],
                'percentage': round(row[2] / row[3] * 100, 2)
            })
        return results
    
    def get_all_results(self):
        """Get all test results (for teachers)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, u.username, u.full_name, r.test_date, 
                   r.score, r.total_questions, r.duration_seconds
            FROM test_results r
            JOIN users u ON r.student_id = u.id
            ORDER BY r.test_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'username': row[1],
                'full_name': row[2],
                'test_date': row[3],
                'score': row[4],
                'total_questions': row[5],
                'duration_seconds': row[6],
                'percentage': round(row[4] / row[5] * 100, 2)
            })
        return results
    
    def get_statistics(self):
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total students
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
        total_students = cursor.fetchone()[0]
        
        # Total teachers
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "teacher"')
        total_teachers = cursor.fetchone()[0]
        
        # Total test attempts
        cursor.execute('SELECT COUNT(*) FROM test_results')
        total_attempts = cursor.fetchone()[0]
        
        # Average score
        cursor.execute('''
            SELECT AVG(CAST(score AS FLOAT) / total_questions * 100)
            FROM test_results
        ''')
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_attempts': total_attempts,
            'average_score': round(avg_score, 2)
        }
    
    # ==================== UTILITY ====================
    
    def close(self):
        """Close database connection"""
        pass  # Using context manager, connection auto-closes

