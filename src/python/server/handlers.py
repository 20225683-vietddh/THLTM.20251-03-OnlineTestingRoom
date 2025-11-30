"""
Protocol Message Handlers
Handles registration, login, and test-related requests
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol_wrapper import (
    MSG_REGISTER_RES, MSG_LOGIN_RES, MSG_TEST_CONFIG,
    MSG_TEST_START_RES, MSG_TEST_QUESTIONS, MSG_TEST_RESULT,
    MSG_TEACHER_DATA_RES, MSG_ERROR,
    ERR_SUCCESS, ERR_BAD_REQUEST, ERR_INVALID_CREDS,
    ERR_USERNAME_EXISTS, ERR_INTERNAL
)
import json


class RequestHandlers:
    """Handles all protocol message requests"""
    
    def __init__(self, proto, db, auth, session_mgr, logger):
        """
        Initialize handlers
        
        Args:
            proto: ProtocolWrapper instance
            db: Database instance
            auth: AuthManager instance
            session_mgr: SessionManager instance
            logger: Callback function for logging
        """
        self.proto = proto
        self.db = db
        self.auth = auth
        self.session_mgr = session_mgr
        self.log = logger
        self.questions = []
        self.test_duration = 30
    
    def load_questions(self, questions_file='src/python/questions.json'):
        """Load questions from JSON file"""
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            self.log(f"[OK] Loaded {len(self.questions)} questions")
        except Exception as e:
            self.log(f"✗ Failed to load questions: {str(e)}")
            self.questions = []
    
    def send_response(self, client_socket, msg_type, payload):
        """Send protocol response"""
        try:
            self.proto.send_message(client_socket, msg_type, payload, use_session=False)
        except Exception as e:
            self.log(f"✗ Send error: {str(e)}")
            raise  # Re-raise so caller knows send failed
    
    def send_error(self, client_socket, error_code, message):
        """Send error response"""
        self.send_response(client_socket, MSG_ERROR, {
            'code': error_code,
            'message': message
        })
    
    def handle_register(self, client_socket, request):
        """Handle registration request"""
        try:
            payload = request['payload']
            username = payload.get('username', '')
            password = payload.get('password', '')
            role = payload.get('role', '')
            full_name = payload.get('full_name', '')
            email = payload.get('email', '')
            
            # Validate inputs
            valid, msg = self.auth.validate_username(username)
            if not valid:
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_BAD_REQUEST,
                    'message': msg
                })
                return
            
            valid, msg = self.auth.validate_password(password)
            if not valid:
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_BAD_REQUEST,
                    'message': msg
                })
                return
            
            valid, msg = self.auth.validate_full_name(full_name)
            if not valid:
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_BAD_REQUEST,
                    'message': msg
                })
                return
            
            # Hash password and create user
            password_hash = self.auth.hash_password(password)
            user_id = self.db.create_user(username, password_hash, role, full_name, email)
            
            if user_id:
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Registration successful'
                })
                self.log(f"[OK] User registered: {username} ({role})")
            else:
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_USERNAME_EXISTS,
                    'message': 'Username already exists'
                })
                
        except Exception as e:
            self.log(f"✗ Registration error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, "Registration failed")
    
    def handle_login(self, client_socket, request):
        """Handle login request, returns session_token or None"""
        try:
            payload = request['payload']
            username = payload.get('username', '')
            password = payload.get('password', '')
            
            # Get user from database
            user = self.db.get_user_by_username(username)
            
            if not user:
                self.send_response(client_socket, MSG_LOGIN_RES, {
                    'code': ERR_INVALID_CREDS,
                    'message': 'Invalid username or password'
                })
                return None
            
            # Verify password
            if not self.auth.verify_password(password, user['password_hash']):
                self.send_response(client_socket, MSG_LOGIN_RES, {
                    'code': ERR_INVALID_CREDS,
                    'message': 'Invalid username or password'
                })
                return None
            
            # Create session
            session_token = self.session_mgr.create_session(
                user_id=user['id'],
                username=user['username'],
                role=user['role'],
                full_name=user['full_name']
            )
            
            # Send success response
            self.send_response(client_socket, MSG_LOGIN_RES, {
                'code': ERR_SUCCESS,
                'message': 'Login successful',
                'session_token': session_token,
                'role': user['role'],
                'full_name': user['full_name']
            })
            
            self.log(f"[OK] {username} logged in ({user['role']})")
            return session_token
            
        except Exception as e:
            self.log(f"✗ Login error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, "Login failed")
            return None
    
    def handle_student_test(self, client_socket, session):
        """Handle student test flow"""
        try:
            # Send test config
            self.send_response(client_socket, MSG_TEST_CONFIG, {
                "num_questions": len(self.questions),
                "duration": self.test_duration
            })
            
            # Wait for START request
            request = self.proto.receive_message(client_socket)
            if request['message_type'] != MSG_TEST_START_REQ:
                return
            
            # Send start confirmation
            self.send_response(client_socket, MSG_TEST_START_RES, {
                'code': ERR_SUCCESS,
                'message': 'Test started',
                'start_time': self.proto.lib.py_get_unix_timestamp()
            })
            
            # Send questions
            self.log(f"[OK] {session['username']} started test")
            self.send_response(client_socket, MSG_TEST_QUESTIONS, {
                "questions": self.questions
            })
            
            # Receive and grade answers
            submit_request = self.proto.receive_message(client_socket)
            if submit_request['message_type'] == MSG_TEST_SUBMIT:
                answers_data = submit_request['payload']
                answers = answers_data.get('answers', [])
                
                # Calculate score
                score = sum(1 for answer in answers 
                           for q in self.questions 
                           if q['id'] == answer.get('question_id') and 
                              q.get('answer') == answer.get('selected'))
                
                # Save result
                self.db.save_test_result(
                    student_id=session['user_id'],
                    score=score,
                    total_questions=len(self.questions),
                    answers_json=json.dumps(answers),
                    duration_seconds=0
                )
                
                # Send result
                percentage = round(score / len(self.questions) * 100, 2)
                self.send_response(client_socket, MSG_TEST_RESULT, {
                    'code': ERR_SUCCESS,
                    'message': 'Test completed',
                    'data': {
                        "score": score,
                        "total": len(self.questions),
                        "percentage": percentage
                    }
                })
                
                self.log(f"✅ {session['username']} completed: {score}/{len(self.questions)} ({percentage}%)")
                
        except Exception as e:
            self.log(f"✗ Student test error: {str(e)}")
    
    def handle_teacher_data(self, client_socket, session):
        """Handle teacher data request"""
        try:
            # Get all results and stats
            results = self.db.get_all_results()
            stats = self.db.get_statistics()
            
            # Get rooms with error handling
            try:
                rooms = self.db.get_teacher_rooms(session['user_id'])
                self.log(f"  Loaded {len(rooms)} rooms for teacher")
            except Exception as room_err:
                import traceback
                self.log(f"⚠ Warning: Could not load rooms: {str(room_err)}")
                self.log(f"  Traceback: {traceback.format_exc()}")
                rooms = []
            
            # Try to send with rooms first
            try:
                self.send_response(client_socket, MSG_TEACHER_DATA_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Teacher data loaded',
                    'data': {
                        'results': results,
                        'statistics': stats,
                        'rooms': rooms
                    }
                })
                self.log(f"[OK] {session['username']} accessed teacher dashboard (with {len(rooms)} rooms)")
            except Exception as send_err:
                # If sending with rooms failed, try without rooms
                self.log(f"⚠ Failed to send with rooms: {str(send_err)}")
                self.log(f"  Retrying without rooms data...")
                try:
                    self.send_response(client_socket, MSG_TEACHER_DATA_RES, {
                        'code': ERR_SUCCESS,
                        'message': 'Teacher data loaded (rooms unavailable)',
                        'data': {
                            'results': results,
                            'statistics': stats,
                            'rooms': []
                        }
                    })
                    self.log(f"[OK] {session['username']} accessed teacher dashboard (without rooms)")
                except Exception as retry_err:
                    self.log(f"✗ Complete failure: {str(retry_err)}")
                    try:
                        self.send_error(client_socket, ERR_INTERNAL, "Failed to send teacher data")
                    except:
                        pass
            
        except Exception as e:
            import traceback
            self.log(f"✗ Teacher data error: {str(e)}")
            self.log(f"  Traceback: {traceback.format_exc()}")
            try:
                self.send_error(client_socket, ERR_INTERNAL, str(e))
            except:
                pass

