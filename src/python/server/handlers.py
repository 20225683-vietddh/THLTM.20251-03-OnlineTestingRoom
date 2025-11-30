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
    MSG_CREATE_ROOM_RES, MSG_GET_ROOMS_RES,
    MSG_START_ROOM_RES, MSG_END_ROOM_RES,
    MSG_ADD_QUESTION_RES, MSG_GET_QUESTIONS_RES, MSG_DELETE_QUESTION_RES,
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
    
    def handle_create_room(self, client_socket, session, request):
        """Handle create room request"""
        try:
            payload = request.get('payload', {})
            room_name = payload.get('room_name', '')
            num_questions = payload.get('num_questions', 10)
            duration_minutes = payload.get('duration_minutes', 30)
            
            # Validate
            if not room_name or len(room_name) < 3:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Room name too short (min 3 characters)")
                return
            
            if not (1 <= num_questions <= 50):
                self.send_error(client_socket, ERR_BAD_REQUEST, "Invalid number of questions (1-50)")
                return
            
            if not (5 <= duration_minutes <= 180):
                self.send_error(client_socket, ERR_BAD_REQUEST, "Invalid duration (5-180 minutes)")
                return
            
            # Get teacher user
            user = self.db.get_user_by_username(session['username'])
            if not user:
                self.send_error(client_socket, ERR_INTERNAL, "User not found")
                return
            
            # Create room
            room_id, room_code = self.db.create_test_room(
                room_name=room_name,
                teacher_id=user['id'],
                num_questions=num_questions,
                duration_minutes=duration_minutes
            )
            
            self.log(f"[OK] Room created: {room_name} ({room_code}) by {session['username']}")
            
            # Send success response
            self.send_response(client_socket, MSG_CREATE_ROOM_RES, {
                'code': ERR_SUCCESS,
                'message': 'Room created successfully',
                'data': {
                    'room_id': room_id,
                    'room_code': room_code
                }
            })
            
        except Exception as e:
            self.log(f"✗ Create room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_get_rooms(self, client_socket, session, request):
        """Handle get rooms request"""
        try:
            # Get teacher user
            user = self.db.get_user_by_username(session['username'])
            if not user:
                self.send_error(client_socket, ERR_INTERNAL, "User not found")
                return
            
            # Get teacher rooms
            rooms = self.db.get_teacher_rooms(user['id'])
            
            self.log(f"[OK] Loaded {len(rooms)} rooms for {session['username']}")
            
            # Send response
            self.send_response(client_socket, MSG_GET_ROOMS_RES, {
                'code': ERR_SUCCESS,
                'message': 'Rooms loaded',
                'data': {
                    'rooms': rooms
                }
            })
            
        except Exception as e:
            self.log(f"✗ Get rooms error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_start_room(self, client_socket, session, request):
        """Handle start room request"""
        try:
            payload = request.get('payload', {})
            room_id = payload.get('room_id')
            
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Missing room_id")
                return
            
            # Get teacher user
            user = self.db.get_user_by_username(session['username'])
            if not user:
                self.send_error(client_socket, ERR_INTERNAL, "User not found")
                return
            
            # Get room to verify ownership
            room = self.db.get_room_by_code('')  # Need to add get_room_by_id
            # For now, just update status
            self.db.start_test_room(room_id)
            
            self.log(f"[OK] Room {room_id} started by {session['username']}")
            
            # Send response
            self.send_response(client_socket, MSG_START_ROOM_RES, {
                'code': ERR_SUCCESS,
                'message': 'Room started successfully'
            })
            
        except Exception as e:
            self.log(f"✗ Start room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_end_room(self, client_socket, session, request):
        """Handle end room request"""
        try:
            payload = request.get('payload', {})
            room_id = payload.get('room_id')
            
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Missing room_id")
                return
            
            # Get teacher user
            user = self.db.get_user_by_username(session['username'])
            if not user:
                self.send_error(client_socket, ERR_INTERNAL, "User not found")
                return
            
            # End room
            self.db.end_test_room(room_id)
            
            self.log(f"[OK] Room {room_id} ended by {session['username']}")
            
            # Send response
            self.send_response(client_socket, MSG_END_ROOM_RES, {
                'code': ERR_SUCCESS,
                'message': 'Room ended successfully'
            })
            
        except Exception as e:
            self.log(f"✗ End room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_add_question(self, client_socket, session, request):
        """Handle add question request"""
        try:
            payload = request.get('payload', {})
            room_id = payload.get('room_id')
            question_text = payload.get('question_text', '')
            option_a = payload.get('option_a', '')
            option_b = payload.get('option_b', '')
            option_c = payload.get('option_c', '')
            option_d = payload.get('option_d', '')
            correct_answer = payload.get('correct_answer', 0)
            
            # Validate
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Missing room_id")
                return
            
            if not question_text or len(question_text) < 5:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Question text too short (min 5 characters)")
                return
            
            if not all([option_a, option_b, option_c, option_d]):
                self.send_error(client_socket, ERR_BAD_REQUEST, "All options must be provided")
                return
            
            if correct_answer not in [0, 1, 2, 3]:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Invalid correct answer (must be 0-3)")
                return
            
            # Add question to database
            question_id = self.db.add_room_question(
                room_id=room_id,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer
            )
            
            self.log(f"[OK] Question {question_id} added to room {room_id} by {session['username']}")
            
            # Send success response
            self.send_response(client_socket, MSG_ADD_QUESTION_RES, {
                'code': ERR_SUCCESS,
                'message': 'Question added successfully',
                'data': {
                    'question_id': question_id
                }
            })
            
        except Exception as e:
            self.log(f"✗ Add question error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_get_questions(self, client_socket, session, request):
        """Handle get questions request"""
        try:
            payload = request.get('payload', {})
            room_id = payload.get('room_id')
            
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Missing room_id")
                return
            
            # Get questions from database
            questions = self.db.get_room_questions(room_id)
            
            self.log(f"[OK] Loaded {len(questions)} questions for room {room_id}")
            
            # Send response
            self.send_response(client_socket, MSG_GET_QUESTIONS_RES, {
                'code': ERR_SUCCESS,
                'message': 'Questions loaded',
                'data': {
                    'questions': questions
                }
            })
            
        except Exception as e:
            self.log(f"✗ Get questions error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_delete_question(self, client_socket, session, request):
        """Handle delete question request"""
        try:
            payload = request.get('payload', {})
            question_id = payload.get('question_id')
            
            if not question_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Missing question_id")
                return
            
            # Delete question
            self.db.delete_room_question(question_id)
            
            self.log(f"[OK] Question {question_id} deleted by {session['username']}")
            
            # Send response
            self.send_response(client_socket, MSG_DELETE_QUESTION_RES, {
                'code': ERR_SUCCESS,
                'message': 'Question deleted successfully'
            })
            
        except Exception as e:
            self.log(f"✗ Delete question error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))

