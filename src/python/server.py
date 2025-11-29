"""
Test Application Server
Server with authentication, test management, and role-based access using TAP Protocol v1.0
"""
import customtkinter as ctk
from protocol_wrapper import (
    ProtocolWrapper,
    MSG_REGISTER_REQ, MSG_REGISTER_RES,
    MSG_LOGIN_REQ, MSG_LOGIN_RES,
    MSG_TEST_CONFIG, MSG_TEST_START_REQ, MSG_TEST_START_RES,
    MSG_TEST_QUESTIONS, MSG_TEST_SUBMIT, MSG_TEST_RESULT,
    MSG_TEACHER_DATA_REQ, MSG_TEACHER_DATA_RES,
    MSG_ERROR,
    ERR_SUCCESS, ERR_BAD_REQUEST, ERR_INVALID_JSON, ERR_INVALID_CREDS,
    ERR_USERNAME_EXISTS, ERR_UNAUTHORIZED, ERR_INTERNAL, ERR_WRONG_ROLE
)
from auth import Database, AuthManager, SessionManager
import threading
import json
from datetime import datetime
import os

class TestServer(ctk.CTk):
    """Test Application Server with TAP Protocol v1.0"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize protocol wrapper
        self.proto = ProtocolWrapper()
        self.proto.init_network()
        self.server_socket = None
        self.clients = {}  # {socket: {"user_id": int, "username": str, "role": str, "status": str}}
        self.running = False
        self.accept_thread = None
        
        # Initialize authentication system
        self.db = Database("data/app.db")
        self.auth = AuthManager()
        self.session_mgr = SessionManager()
        
        # Test configuration
        self.questions = []
        self.test_duration = 30  # minutes
        
        # Configure window
        self.title("Test Server - Network Programming")
        self.geometry("1000x750")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Load questions
        self.load_questions()
        
        # Create UI
        self.create_widgets()
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_questions(self):
        """Load questions from JSON file"""
        questions_file = os.path.join(os.path.dirname(__file__), "questions.json")
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data.get("questions", [])
                self.test_duration = data.get("duration", 30)
        except FileNotFoundError:
            self.append_log("⚠ Warning: questions.json not found.")
            
    def create_widgets(self):
        """Create UI widgets"""
        # Left Panel - Server Control
        self.left_panel = ctk.CTkFrame(self, width=350)
        self.left_panel.pack(side="left", fill="both", padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.left_panel, 
            text="🖥️ TEST SERVER",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Server Control Frame
        self.control_frame = ctk.CTkFrame(self.left_panel)
        self.control_frame.pack(pady=10, padx=10, fill="x")
        
        # Port input
        self.port_label = ctk.CTkLabel(self.control_frame, text="Port:")
        self.port_label.pack(pady=5)
        
        self.port_entry = ctk.CTkEntry(self.control_frame, width=200)
        self.port_entry.insert(0, "5000")
        self.port_entry.pack(pady=5)
        
        # Start/Stop button
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="Start Server",
            command=self.toggle_server,
            height=40
        )
        self.start_button.pack(pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.control_frame,
            text="● Server Stopped",
            text_color="red",
            font=("Arial", 14)
        )
        self.status_label.pack(pady=5)
        
        # Statistics Frame
        self.stats_frame = ctk.CTkFrame(self.left_panel)
        self.stats_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(
            self.stats_frame,
            text="📊 Statistics",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.stats_text = ctk.CTkTextbox(self.stats_frame, height=100, state="disabled")
        self.stats_text.pack(pady=5, padx=5, fill="x")
        self.update_statistics()
        
        # Connected Users Frame
        self.users_frame = ctk.CTkFrame(self.left_panel)
        self.users_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            self.users_frame,
            text="👥 Connected Users",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.users_list = ctk.CTkTextbox(self.users_frame, state="disabled")
        self.users_list.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Right Panel - Logs
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            self.right_panel,
            text="📋 Server Logs",
            font=("Arial", 16, "bold")
        ).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(self.right_panel, state="disabled")
        self.log_text.pack(pady=5, padx=5, fill="both", expand=True)
        
    def toggle_server(self):
        """Start or stop server"""
        if not self.running:
            self.start_server()
        else:
            self.stop_server()
            
    def start_server(self):
        """Start server"""
        try:
            port = int(self.port_entry.get())
            self.server_socket = self.proto.create_server(port)
            self.running = True
            
            # Update UI
            self.start_button.configure(text="Stop Server")
            self.status_label.configure(text="● Server Running", text_color="green")
            self.port_entry.configure(state="disabled")
            
            # Start accept thread
            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()
            
            self.append_log(f"✓ Server started on port {port} (TAP Protocol v1.0)")
            
        except Exception as e:
            self.append_log(f"✗ Failed to start server: {str(e)}")
            
    def stop_server(self):
        """Stop server"""
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                self.proto.close_socket(client_socket)
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.proto.close_socket(self.server_socket)
            except:
                pass
        
        # Update UI
        self.start_button.configure(text="Start Server")
        self.status_label.configure(text="● Server Stopped", text_color="red")
        self.port_entry.configure(state="normal")
        self.update_students_list()
        
        self.append_log("✓ Server stopped")
        
    def accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket = self.proto.accept_client(self.server_socket)
                self.append_log(f"✓ New connection from client")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.append_log(f"✗ Accept error: {str(e)}")
                break
                
    def handle_client(self, client_socket):
        """Handle client communication with TAP Protocol"""
        try:
            # Wait for authentication (REGISTER or LOGIN)
            request = self.proto.receive_message(client_socket)
            msg_type = request['message_type']
            
            if msg_type == MSG_REGISTER_REQ:
                self.handle_register(client_socket, request)
                
            elif msg_type == MSG_LOGIN_REQ:
                session_token = self.handle_login(client_socket, request)
                
                if session_token:
                    # Get session info
                    session = self.session_mgr.validate_session(session_token)
                    
                    # Handle based on role
                    if session['role'] == 'student':
                        self.handle_student(client_socket, session)
                    else:
                        self.handle_teacher(client_socket, session)
            else:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Invalid request")
                
        except Exception as e:
            self.append_log(f"✗ Client error: {str(e)}")
        finally:
            # Cleanup
            if client_socket in self.clients:
                user = self.clients[client_socket]
                self.append_log(f"✗ {user['username']} disconnected")
                del self.clients[client_socket]
                self.update_students_list()
            try:
                self.proto.close_socket(client_socket)
            except:
                pass
                
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
            
            # Hash password
            password_hash = self.auth.hash_password(password)
            
            # Create user
            user_id = self.db.create_user(username, password_hash, role, full_name, email)
            
            if user_id:
                self.append_log(f"✓ User registered: {username} ({role})")
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Registration successful',
                    'data': {
                        'user_id': user_id,
                        'username': username,
                        'role': role
                    }
                })
                self.update_statistics()
            else:
                self.append_log(f"✗ Registration failed: Username '{username}' exists")
                self.send_response(client_socket, MSG_REGISTER_RES, {
                    'code': ERR_USERNAME_EXISTS,
                    'message': 'Username already exists'
                })
                
        except Exception as e:
            self.append_log(f"✗ Registration error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_login(self, client_socket, request):
        """Handle login request, returns session_token or None"""
        try:
            payload = request['payload']
            username = payload.get('username', '')
            password = payload.get('password', '')
            role = payload.get('role', '')
            
            # Get user from database
            user = self.db.get_user_by_username(username)
            
            if not user:
                self.append_log(f"✗ Login failed: User '{username}' not found")
                self.send_response(client_socket, MSG_LOGIN_RES, {
                    'code': ERR_INVALID_CREDS,
                    'message': 'Invalid credentials'
                })
                return None
            
            # Verify password
            if not self.auth.verify_password(password, user['password_hash']):
                self.append_log(f"✗ Login failed: Invalid password for '{username}'")
                self.send_response(client_socket, MSG_LOGIN_RES, {
                    'code': ERR_INVALID_CREDS,
                    'message': 'Invalid credentials'
                })
                return None
            
            # Check role
            if user['role'] != role:
                self.append_log(f"✗ Login failed: Role mismatch for '{username}'")
                self.send_response(client_socket, MSG_LOGIN_RES, {
                    'code': ERR_WRONG_ROLE,
                    'message': 'Invalid role'
                })
                return None
            
            # Create session
            session_token = self.session_mgr.create_session(
                user_id=user['id'],
                username=user['username'],
                role=user['role'],
                full_name=user['full_name']
            )
            
            # Store client info
            self.clients[client_socket] = {
                "user_id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "status": "authenticated"
            }
            
            self.append_log(f"✓ {username} logged in ({role})")
            self.update_students_list()
            
            # Send success response
            self.send_response(client_socket, MSG_LOGIN_RES, {
                'code': ERR_SUCCESS,
                'message': 'Login successful',
                'data': {
                    'session_token': session_token,
                    'user_id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'full_name': user['full_name']
                }
            })
            
            return session_token
            
        except Exception as e:
            self.append_log(f"✗ Login error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
            return None
    
    def handle_student(self, client_socket, session):
        """Handle student operations"""
        try:
            # Send test config
            self.send_response(client_socket, MSG_TEST_CONFIG, {
                "num_questions": len(self.questions),
                "duration": self.test_duration
            })
            
            # Wait for START request
            request = self.proto.receive_message(client_socket)
            if request['message_type'] == MSG_TEST_START_REQ:
                self.clients[client_socket]["status"] = "testing"
                self.update_students_list()
                
                # Send start confirmation
                self.send_response(client_socket, MSG_TEST_START_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Test started',
                    'start_time': self.proto.lib.py_get_unix_timestamp()
                })
                
                # Send questions
                self.append_log(f"✓ {session['username']} started test")
                self.send_response(client_socket, MSG_TEST_QUESTIONS, {
                    "questions": self.questions
                })
            
            # Receive answers
            submit_request = self.proto.receive_message(client_socket)
            if submit_request['message_type'] == MSG_TEST_SUBMIT:
                answers_data = submit_request['payload']
                answers = answers_data.get('answers', [])
                
                # Calculate score
                score = 0
                for answer in answers:
                    q_id = answer.get('question_id')
                    selected = answer.get('selected')
                    
                    # Find correct answer
                    for q in self.questions:
                        if q['id'] == q_id and q.get('answer') == selected:
                            score += 1
                            break
                
                # Save result
                self.db.save_test_result(
                    student_id=session['user_id'],
                    score=score,
                    total_questions=len(self.questions),
                    answers_json=json.dumps(answers),
                    duration_seconds=0  # TODO: Calculate from start_time
                )
                
                # Send result
                result = {
                    "score": score,
                    "total": len(self.questions),
                    "percentage": round(score / len(self.questions) * 100, 2)
                }
                
                self.send_response(client_socket, MSG_TEST_RESULT, {
                    'code': ERR_SUCCESS,
                    'message': 'Test completed',
                    'data': result
                })
                
                self.append_log(f"✅ {session['username']} completed: {score}/{len(self.questions)} ({result['percentage']}%)")
                self.update_statistics()
                
        except Exception as e:
            self.append_log(f"✗ Student handling error: {str(e)}")
    
    def handle_teacher(self, client_socket, session):
        """Handle teacher operations"""
        try:
            # Send all test results
            results = self.db.get_all_results()
            stats = self.db.get_statistics()
            
            self.send_response(client_socket, MSG_TEACHER_DATA_RES, {
                'code': ERR_SUCCESS,
                'message': 'Teacher data loaded',
                'data': {
                    'results': results,
                    'statistics': stats
                }
            })
            
            self.append_log(f"✓ {session['username']} accessed teacher dashboard")
            
        except Exception as e:
            self.append_log(f"✗ Teacher handling error: {str(e)}")
    
    def send_response(self, client_socket, msg_type, payload):
        """Send protocol response"""
        try:
            self.proto.send_message(client_socket, msg_type, payload, use_session=False)
        except Exception as e:
            self.append_log(f"✗ Send error: {str(e)}")
    
    def send_error(self, client_socket, error_code, message):
        """Send error response"""
        self.send_response(client_socket, MSG_ERROR, {
            'code': error_code,
            'message': message
        })
    
    def append_log(self, message):
        """Append log message (thread-safe)"""
        def _update():
            self.log_text.configure(state="normal")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{timestamp}] {message}\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        
        self.after(0, _update)
    
    def update_students_list(self):
        """Update connected users list (thread-safe)"""
        def _update():
            self.users_list.configure(state="normal")
            self.users_list.delete("1.0", "end")
            
            if self.clients:
                for client_info in self.clients.values():
                    status_icon = "📝" if client_info['status'] == "testing" else "✓"
                    role_icon = "👨‍🎓" if client_info['role'] == "student" else "👨‍🏫"
                    self.users_list.insert("end", 
                        f"{status_icon} {role_icon} {client_info['username']} ({client_info['status']})\n"
                    )
            else:
                self.users_list.insert("end", "No connected users")
            
            self.users_list.configure(state="disabled")
        
        self.after(0, _update)
    
    def update_statistics(self):
        """Update statistics display (thread-safe)"""
        def _update():
            stats = self.db.get_statistics()
            
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            
            total_users = stats['total_students'] + stats['total_teachers']
            self.stats_text.insert("end", f"Total Users: {total_users}\n")
            self.stats_text.insert("end", f"Students: {stats['total_students']}\n")
            self.stats_text.insert("end", f"Teachers: {stats['total_teachers']}\n")
            self.stats_text.insert("end", f"Tests Taken: {stats['total_attempts']}\n")
            
            if stats['average_score'] > 0:
                self.stats_text.insert("end", f"Avg Score: {stats['average_score']:.1f}%\n")
            
            self.stats_text.configure(state="disabled")
        
        self.after(0, _update)
    
    def on_closing(self):
        """Handle window close"""
        if self.running:
            self.stop_server()
        self.proto.cleanup_network()
        self.destroy()


if __name__ == "__main__":
    app = TestServer()
    app.mainloop()

