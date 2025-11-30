"""
Statistics Repository
Handles statistics and analytics operations
"""


class StatsRepository:
    """Repository for statistics operations"""
    
    def __init__(self, db_connection_getter):
        """
        Initialize repository
        
        Args:
            db_connection_getter: Function that returns database connection
        """
        self.get_connection = db_connection_getter
    
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

