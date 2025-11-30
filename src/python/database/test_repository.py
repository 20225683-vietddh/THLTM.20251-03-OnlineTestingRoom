"""
Test Repository
Handles test results and test-related database operations
"""


class TestRepository:
    """Repository for test operations"""
    
    def __init__(self, db_connection_getter):
        """
        Initialize repository
        
        Args:
            db_connection_getter: Function that returns database connection
        """
        self.get_connection = db_connection_getter
    
    def save_test_result(self, student_id, score, total_questions, answers_json, duration_seconds=0):
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
    
    def get_user_results(self, user_id):
        """Get test results for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, test_date, score, total_questions, duration_seconds
            FROM test_results
            WHERE student_id = ?
            ORDER BY test_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'test_date': str(row[1]) if row[1] else None,
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
                'test_date': str(row[3]) if row[3] else None,
                'score': row[4],
                'total_questions': row[5],
                'duration_seconds': row[6],
                'percentage': round(row[4] / row[5] * 100, 2) if row[5] > 0 else 0
            })
        return results

