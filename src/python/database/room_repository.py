"""
Room Repository
Handles test room and participant database operations
"""
import sqlite3
import random
import string
from datetime import datetime


class RoomRepository:
    """Repository for room operations"""
    
    def __init__(self, db_connection_getter):
        """
        Initialize repository
        
        Args:
            db_connection_getter: Function that returns database connection
        """
        self.get_connection = db_connection_getter
    
    def create_test_room(self, room_name, teacher_id, num_questions, duration_minutes):
        """Create new test room"""
        # Generate room code
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_rooms (room_name, room_code, teacher_id, num_questions, duration_minutes, status)
                VALUES (?, ?, ?, ?, ?, 'waiting')
            ''', (room_name, room_code, teacher_id, num_questions, duration_minutes))
            
            room_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'room_id': room_id, 'room_code': room_code}
        except sqlite3.IntegrityError:
            # If room_code collision, retry
            return self.create_test_room(room_name, teacher_id, num_questions, duration_minutes)
    
    def get_room_by_id(self, room_id):
        """Get room by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.room_name, r.room_code, r.teacher_id, u.full_name,
                   r.num_questions, r.duration_minutes, r.status, r.created_at,
                   r.start_time, r.end_time
            FROM test_rooms r
            JOIN users u ON r.teacher_id = u.id
            WHERE r.id = ?
        ''', (room_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'room_name': row[1],
                'room_code': row[2],
                'teacher_id': row[3],
                'teacher_name': row[4],
                'num_questions': row[5],
                'duration_minutes': row[6],
                'status': row[7],
                'created_at': str(row[8]) if row[8] else None,
                'start_time': str(row[9]) if row[9] else None,
                'end_time': str(row[10]) if row[10] else None
            }
        return None
    
    def get_room_by_code(self, room_code):
        """Get room by code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.room_name, r.room_code, r.teacher_id, u.full_name,
                   r.num_questions, r.duration_minutes, r.status, r.created_at,
                   r.start_time, r.end_time
            FROM test_rooms r
            JOIN users u ON r.teacher_id = u.id
            WHERE r.room_code = ?
        ''', (room_code,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'room_name': row[1],
                'room_code': row[2],
                'teacher_id': row[3],
                'teacher_name': row[4],
                'num_questions': row[5],
                'duration_minutes': row[6],
                'status': row[7],
                'created_at': str(row[8]) if row[8] else None,
                'start_time': str(row[9]) if row[9] else None,
                'end_time': str(row[10]) if row[10] else None
            }
        return None
    
    def get_teacher_rooms(self, teacher_id):
        """Get list of rooms for a teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.room_name, r.room_code, r.num_questions, r.duration_minutes,
                   r.status, r.created_at, r.start_time, r.end_time,
                   COUNT(DISTINCT p.student_id) as participant_count
            FROM test_rooms r
            LEFT JOIN room_participants p ON r.id = p.room_id
            WHERE r.teacher_id = ?
            GROUP BY r.id
            ORDER BY r.created_at DESC
        ''', (teacher_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        rooms = []
        for row in rows:
            rooms.append({
                'id': row[0],
                'room_name': row[1],
                'room_code': row[2],
                'num_questions': row[3],
                'duration_minutes': row[4],
                'status': row[5],
                'created_at': str(row[6]) if row[6] else None,
                'start_time': str(row[7]) if row[7] else None,
                'end_time': str(row[8]) if row[8] else None,
                'participant_count': row[9]
            })
        return rooms
    
    def start_test_room(self, room_id):
        """Start test in room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE test_rooms
            SET status = 'active', start_time = ?
            WHERE id = ? AND status = 'waiting'
        ''', (datetime.now().isoformat(), room_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def end_test_room(self, room_id):
        """
        End test in room
        
        Returns:
            dict: {'success': bool, 'message': str, 'error': str (optional)}
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get room info to validate timing
        cursor.execute('''
            SELECT status, start_time, duration_minutes
            FROM test_rooms
            WHERE id = ?
        ''', (room_id,))
        
        room = cursor.fetchone()
        
        if not room:
            conn.close()
            return {'success': False, 'error': 'Room not found'}
        
        status, start_time_str, duration_minutes = room
        
        if status != 'active':
            conn.close()
            return {'success': False, 'error': f'Room is not active (status: {status})'}
        
        # Validate timing
        if not start_time_str:
            conn.close()
            return {'success': False, 'error': 'Room has no start time'}
        
        from datetime import timedelta
        start_time = datetime.fromisoformat(start_time_str)
        min_end_time = start_time + timedelta(minutes=duration_minutes)
        now = datetime.now()
        
        if now < min_end_time:
            remaining = min_end_time - now
            remaining_minutes = int(remaining.total_seconds() / 60)
            conn.close()
            return {
                'success': False,
                'error': f'Cannot end test yet. Students need {remaining_minutes} more minutes to finish.'
            }
        
        # All checks passed, end the room
        cursor.execute('''
            UPDATE test_rooms
            SET status = 'ended', end_time = ?
            WHERE id = ?
        ''', (now.isoformat(), room_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Room ended successfully'}
    
    def join_room(self, room_code, student_id):
        """Student joins a room"""
        room = self.get_room_by_code(room_code)
        if not room:
            return {'success': False, 'error': 'Room not found'}
        
        if room['status'] == 'ended':
            return {'success': False, 'error': 'Test has ended'}
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO room_participants (room_id, student_id, status)
                VALUES (?, ?, 'joined')
            ''', (room['id'], student_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'room': room}
        except sqlite3.IntegrityError:
            # Already joined
            return {'success': True, 'room': room, 'already_joined': True}
    
    def get_room_participants(self, room_id):
        """Get participants in a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.student_id, u.username, u.full_name, p.joined_at,
                   p.status, p.test_result_id
            FROM room_participants p
            JOIN users u ON p.student_id = u.id
            WHERE p.room_id = ?
            ORDER BY p.joined_at
        ''', (room_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        participants = []
        for row in rows:
            participants.append({
                'id': row[0],
                'student_id': row[1],
                'username': row[2],
                'full_name': row[3],
                'joined_at': str(row[4]) if row[4] else None,
                'status': row[5],
                'test_result_id': row[6]
            })
        return participants
    
    def update_participant_status(self, room_id, student_id, status):
        """Update participant status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE room_participants
            SET status = ?
            WHERE room_id = ? AND student_id = ?
        ''', (status, room_id, student_id))
        
        conn.commit()
        conn.close()
    
    def get_student_rooms(self, student_id):
        """Get list of rooms student has joined"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.room_name, r.room_code, u.full_name as teacher_name,
                   r.num_questions, r.duration_minutes, r.status, p.joined_at, p.status as participant_status
            FROM room_participants p
            JOIN test_rooms r ON p.room_id = r.id
            JOIN users u ON r.teacher_id = u.id
            WHERE p.student_id = ?
            ORDER BY p.joined_at DESC
        ''', (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        rooms = []
        for row in rows:
            rooms.append({
                'id': row[0],
                'room_name': row[1],
                'room_code': row[2],
                'teacher_name': row[3],
                'num_questions': row[4],
                'duration_minutes': row[5],
                'room_status': row[6],
                'joined_at': str(row[7]) if row[7] else None,
                'participant_status': row[8]
            })
        return rooms
    
    def get_available_rooms(self, student_id=None):
        """Get list of available rooms (optionally filter out already joined by student)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if student_id:
            # Get rooms NOT joined by this student
            cursor.execute('''
                SELECT r.id, r.room_name, r.room_code, u.full_name as teacher_name,
                       r.num_questions, r.duration_minutes, r.status, r.created_at
                FROM test_rooms r
                JOIN users u ON r.teacher_id = u.id
                WHERE r.id NOT IN (
                    SELECT room_id FROM room_participants WHERE student_id = ?
                )
                AND r.status IN ('waiting', 'active')
                ORDER BY r.created_at DESC
            ''', (student_id,))
        else:
            # Get all non-ended rooms
            cursor.execute('''
                SELECT r.id, r.room_name, r.room_code, u.full_name as teacher_name,
                       r.num_questions, r.duration_minutes, r.status, r.created_at
                FROM test_rooms r
                JOIN users u ON r.teacher_id = u.id
                WHERE r.status IN ('waiting', 'active')
                ORDER BY r.created_at DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        rooms = []
        for row in rows:
            rooms.append({
                'id': row[0],
                'room_name': row[1],
                'room_code': row[2],
                'teacher_name': row[3],
                'num_questions': row[4],
                'duration_minutes': row[5],
                'status': row[6],
                'created_at': str(row[7]) if row[7] else None
            })
        return rooms
    
    def add_room_question(self, room_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_order=0):
        """Add a question to a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO room_questions 
            (room_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (room_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_order))
        conn.commit()
        return cursor.lastrowid
    
    def get_room_questions(self, room_id):
        """Get all questions for a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, question_text, option_a, option_b, option_c, option_d, 
                   correct_answer, question_order
            FROM room_questions
            WHERE room_id = ?
            ORDER BY question_order, id
        ''', (room_id,))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'question_text': row[1],
                'option_a': row[2],
                'option_b': row[3],
                'option_c': row[4],
                'option_d': row[5],
                'correct_answer': row[6],
                'question_order': row[7]
            })
        return questions
    
    def update_room_question(self, question_id, question_text, option_a, option_b, option_c, option_d, correct_answer):
        """Update a room question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE room_questions
            SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, 
                option_d = ?, correct_answer = ?
            WHERE id = ?
        ''', (question_text, option_a, option_b, option_c, option_d, correct_answer, question_id))
        conn.commit()
    
    def get_question_by_id(self, question_id):
        """Get a question by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, room_id, question_text, option_a, option_b, option_c, option_d, 
                   correct_answer, question_order
            FROM room_questions 
            WHERE id = ?
        ''', (question_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'room_id': row[1],
                'question_text': row[2],
                'option_a': row[3],
                'option_b': row[4],
                'option_c': row[5],
                'option_d': row[6],
                'correct_answer': row[7],
                'question_order': row[8]
            }
        return None
    
    def delete_room_question(self, question_id):
        """Delete a room question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM room_questions WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()
    
    def delete_all_room_questions(self, room_id):
        """Delete all questions for a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM room_questions WHERE room_id = ?', (room_id,))
        conn.commit()
    
    def get_room_question_count(self, room_id):
        """Get count of questions in a room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM room_questions WHERE room_id = ?', (room_id,))
        return cursor.fetchone()[0]

