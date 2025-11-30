"""
Client Handlers
Handles teacher and student interface logic
"""
from protocol_wrapper import (
    MSG_TEACHER_DATA_RES, MSG_TEST_CONFIG, MSG_TEST_START_REQ,
    MSG_TEST_START_RES, MSG_TEST_QUESTIONS, MSG_TEST_SUBMIT,
    MSG_TEST_RESULT, MSG_ERROR
)


class TeacherHandler:
    """Handles teacher interface"""
    
    def __init__(self, connection, ui_callbacks):
        self.conn = connection
        self.ui = ui_callbacks
        
    def load_dashboard(self, full_name):
        """Load teacher dashboard"""
        try:
            # Receive data from server (auto-sent after login)
            response = self.conn.receive_message()
            
            # Check for error
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(f"Server error: {error_msg}")
            
            # Process teacher data
            if response['message_type'] == MSG_TEACHER_DATA_RES:
                payload = response.get('payload', {})
                
                if 'data' not in payload:
                    raise ValueError("Server response missing data")
                
                data = payload['data']
                results = data.get('results', [])
                rooms = data.get('rooms', [])
                
                # Show dashboard via UI callback
                self.ui['show_dashboard'](full_name, results, rooms)
                return True
            
            raise ValueError("Unexpected response from server")
            
        except Exception as e:
            raise Exception(f"Failed to load teacher dashboard: {str(e)}")


class StudentHandler:
    """Handles student test interface"""
    
    def __init__(self, connection, ui_callbacks):
        self.conn = connection
        self.ui = ui_callbacks
        self.questions = []
        
    def load_test_config(self, full_name):
        """Load test configuration"""
        try:
            # Receive test config from server
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_TEST_CONFIG:
                config = response['payload']
                num_questions = config.get('num_questions', 0)
                duration = config.get('duration', 30)
                
                # Show ready screen via UI callback
                self.ui['show_ready'](full_name, num_questions, duration)
                return True
            
            raise ValueError("Expected test config from server")
            
        except Exception as e:
            raise Exception(f"Failed to load test: {str(e)}")
    
    def start_test(self):
        """Start the test"""
        try:
            # Send start request
            self.conn.send_message(MSG_TEST_START_REQ, {'ready': True})
            
            # Receive start confirmation
            response = self.conn.receive_message()
            if response['message_type'] != MSG_TEST_START_RES:
                raise ValueError("Failed to start test")
            
            # Receive questions
            response = self.conn.receive_message()
            if response['message_type'] == MSG_TEST_QUESTIONS:
                self.questions = response['payload'].get('questions', [])
                
                # Show test screen via UI callback
                duration = response['payload'].get('duration', 30)
                self.ui['show_test'](self.questions, duration)
                return True
            
            raise ValueError("Failed to receive questions")
            
        except Exception as e:
            raise Exception(f"Failed to start test: {str(e)}")
    
    def submit_test(self, answers):
        """Submit test answers"""
        try:
            # Send answers
            self.conn.send_message(MSG_TEST_SUBMIT, {'answers': answers})
            
            # Receive result
            response = self.conn.receive_message()
            if response['message_type'] == MSG_TEST_RESULT:
                result = response['payload'].get('data', {})
                
                # Show result via UI callback
                self.ui['show_result'](result)
                return True
            
            raise ValueError("Failed to receive result")
            
        except Exception as e:
            raise Exception(f"Failed to submit test: {str(e)}")

