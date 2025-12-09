"""
Client Handlers
Handles teacher and student interface logic
"""
from protocol_wrapper import (
    MSG_TEACHER_DATA_RES, MSG_TEST_CONFIG, MSG_TEST_START_REQ,
    MSG_TEST_START_RES, MSG_TEST_QUESTIONS, MSG_TEST_SUBMIT,
    MSG_TEST_RESULT, MSG_ERROR,
    MSG_CREATE_ROOM_REQ, MSG_CREATE_ROOM_RES,
    MSG_GET_ROOMS_REQ, MSG_GET_ROOMS_RES,
    MSG_START_ROOM_REQ, MSG_START_ROOM_RES,
    MSG_END_ROOM_REQ, MSG_END_ROOM_RES,
    MSG_ADD_QUESTION_REQ, MSG_ADD_QUESTION_RES,
    MSG_GET_QUESTIONS_REQ, MSG_GET_QUESTIONS_RES,
    MSG_DELETE_QUESTION_REQ, MSG_DELETE_QUESTION_RES,
    MSG_JOIN_ROOM_REQ, MSG_JOIN_ROOM_RES,
    MSG_GET_STUDENT_ROOMS_REQ, MSG_GET_STUDENT_ROOMS_RES,
    MSG_GET_AVAILABLE_ROOMS_REQ, MSG_GET_AVAILABLE_ROOMS_RES,
    MSG_START_ROOM_TEST_REQ, MSG_START_ROOM_TEST_RES,
    MSG_SUBMIT_ROOM_TEST_REQ, MSG_SUBMIT_ROOM_TEST_RES,
    MSG_AUTO_SAVE_REQ, MSG_AUTO_SAVE_RES
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
    
    def create_room(self, room_name, num_questions, duration_minutes):
        """Create a new test room"""
        try:
            # Send create room request
            self.conn.send_message(MSG_CREATE_ROOM_REQ, {
                'room_name': room_name,
                'num_questions': num_questions,
                'duration_minutes': duration_minutes
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_CREATE_ROOM_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return {
                        'success': True,
                        'room_id': data.get('room_id'),
                        'room_code': data.get('room_code')
                    }
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to create room: {str(e)}")
    
    def refresh_rooms(self):
        """Refresh room list"""
        try:
            # Send get rooms request
            self.conn.send_message(MSG_GET_ROOMS_REQ, {})
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_GET_ROOMS_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return data.get('rooms', [])
                else:
                    raise ValueError(payload.get('message', 'Failed to get rooms'))
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to refresh rooms: {str(e)}")
    
    def start_room(self, room_id):
        """Start test in a room"""
        try:
            # Send start room request
            self.conn.send_message(MSG_START_ROOM_REQ, {
                'room_id': room_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_START_ROOM_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    return {'success': True}
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to start room: {str(e)}")
    
    def end_room(self, room_id):
        """End test in a room"""
        try:
            # Send end room request
            self.conn.send_message(MSG_END_ROOM_REQ, {
                'room_id': room_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_END_ROOM_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    return {'success': True}
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to end room: {str(e)}")
    
    def add_question(self, room_id, question_text, option_a, option_b, option_c, option_d, correct_answer):
        """Add a question to a room"""
        try:
            # Send add question request
            self.conn.send_message(MSG_ADD_QUESTION_REQ, {
                'room_id': room_id,
                'question_text': question_text,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'correct_answer': correct_answer
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_ADD_QUESTION_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    return {'success': True, 'question_id': payload.get('data', {}).get('question_id')}
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to add question: {str(e)}")
    
    def get_questions(self, room_id):
        """Get questions for a room"""
        try:
            # Send get questions request
            self.conn.send_message(MSG_GET_QUESTIONS_REQ, {
                'room_id': room_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_GET_QUESTIONS_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return data.get('questions', [])
                else:
                    raise ValueError(payload.get('message', 'Failed to get questions'))
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to get questions: {str(e)}")
    
    def delete_question(self, question_id):
        """Delete a question"""
        try:
            # Send delete question request
            self.conn.send_message(MSG_DELETE_QUESTION_REQ, {
                'question_id': question_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_DELETE_QUESTION_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    return {'success': True}
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to delete question: {str(e)}")


class StudentHandler:
    """Handles student test interface"""
    
    def __init__(self, connection, ui_callbacks):
        self.conn = connection
        self.ui = ui_callbacks
        self.questions = []
        self.auto_save_in_progress = False  # Track auto-save state
        
    def join_room(self, room_id):
        """Join a test room by room ID"""
        try:
            # Send join room request
            self.conn.send_message(MSG_JOIN_ROOM_REQ, {
                'room_id': room_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_JOIN_ROOM_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return {
                        'success': True,
                        'room_name': data.get('room_name'),
                        'room_id': data.get('room_id')
                    }
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to join room: {str(e)}")
    
    def refresh_rooms(self):
        """Get list of rooms student has joined"""
        try:
            # Send get student rooms request
            self.conn.send_message(MSG_GET_STUDENT_ROOMS_REQ, {})
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_GET_STUDENT_ROOMS_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return data.get('rooms', [])
                else:
                    raise ValueError(payload.get('message', 'Failed to get rooms'))
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to refresh rooms: {str(e)}")
    
    def get_available_rooms(self):
        """Get list of available rooms to join"""
        try:
            # Send get available rooms request
            self.conn.send_message(MSG_GET_AVAILABLE_ROOMS_REQ, {})
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_GET_AVAILABLE_ROOMS_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    return data.get('rooms', [])
                else:
                    raise ValueError(payload.get('message', 'Failed to get available rooms'))
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to get available rooms: {str(e)}")
    
    def start_room_test(self, room_id, cached_data=None):
        """Start test for a specific room (optionally resume from cache)"""
        try:
            # Send start room test request
            self.conn.send_message(MSG_START_ROOM_TEST_REQ, {
                'room_id': room_id
            })
            
            # Receive response
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_START_ROOM_TEST_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    data = payload.get('data', {})
                    questions = data.get('questions', [])
                    duration = data.get('duration_minutes', 30)
                    room_name = data.get('room_name', 'Test Room')
                    
                    # Show test screen via UI callback (with cached data if resuming)
                    self.questions = questions
                    self.ui['show_test'](questions, duration, room_id, cached_data)
                    
                    return {
                        'success': True,
                        'questions': questions,
                        'duration': duration,
                        'room_name': room_name
                    }
                else:
                    return {'success': False, 'message': payload.get('message')}
            
            raise ValueError("Unexpected response")
            
        except Exception as e:
            raise Exception(f"Failed to start room test: {str(e)}")
    
    def submit_room_test(self, room_id, answers):
        """Submit test answers for a room"""
        try:
            # Wait for any ongoing auto-save to complete
            import time
            max_wait = 3  # Max 3 seconds
            waited = 0
            while self.auto_save_in_progress and waited < max_wait:
                print(f"[SUBMIT] Waiting for auto-save to complete... ({waited}s)")
                time.sleep(0.5)
                waited += 0.5
            
            if self.auto_save_in_progress:
                print("⚠️ [SUBMIT] Auto-save still in progress, proceeding anyway...")
            
            # Send submit request
            self.conn.send_message(MSG_SUBMIT_ROOM_TEST_REQ, {
                'room_id': room_id,
                'answers': answers
            })
            
            # Receive result
            response = self.conn.receive_message()
            
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            if response['message_type'] == MSG_SUBMIT_ROOM_TEST_RES:
                payload = response['payload']
                if payload.get('code') == 1000:  # ERR_SUCCESS
                    result = payload.get('data', {})
                    
                    # Show result via UI callback
                    self.ui['show_result'](result)
                    return True
                else:
                    raise ValueError(payload.get('message', 'Failed to submit test'))
            
            raise ValueError("Failed to receive result")
            
        except Exception as e:
            raise Exception(f"Failed to submit test: {str(e)}")
        
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
    
    def auto_save(self, room_id, answers, is_final=False):
        """Auto-save test progress to server"""
        if self.auto_save_in_progress:
            print("⚠️ Auto-save already in progress, skipping...")
            return False
        
        try:
            self.auto_save_in_progress = True
            
            # Send auto-save request
            self.conn.send_message(MSG_AUTO_SAVE_REQ, {
                'room_id': room_id,
                'answers': answers,
                'is_final': is_final
            })
            
            # Try to consume response (non-blocking, best effort)
            # Note: socket is an int (C file descriptor), not Python socket object
            try:
                response = self.conn.receive_message()
                
                if response['message_type'] == MSG_AUTO_SAVE_RES:
                    print("[AUTO-SAVE] Server acknowledged")
                    return True
            except Exception as e:
                # Auto-save is non-critical, just log and continue
                print(f"⚠️ Auto-save ACK error (non-critical): {e}")
                return False
            finally:
                self.auto_save_in_progress = False
            
            return False
            
        except Exception as e:
            print(f"⚠️ Auto-save error: {e}")
            self.auto_save_in_progress = False
            return False

