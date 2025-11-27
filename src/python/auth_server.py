"""
Authenticated Test Server with Login/Register Support
Server với authentication, role-based access, và session management
"""
import customtkinter as ctk
from network_wrapper import NetworkWrapper
from auth import Database, AuthManager, SessionManager
import threading
import json
from datetime import datetime
import os

class AuthTestServer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize network wrapper
        self.network = NetworkWrapper()
        self.network.init_network()
        self.server_socket = None
        self.clients = {}  # {socket: {"user_id": int, "username": str, "role": str, "status": str}}
        self.running = False
        self.accept_thread = None
        
        # Initialize authentication system
        self.db = Database("data/users.db")
        self.auth = AuthManager()
        self.session_mgr = SessionManager()
        
        # Test configuration
        self.questions = []
        self.test_duration = 30  # minutes
        
        # Configure window
        self.title("Auth Test Server - Network Programming")
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
            text="🔐 AUTH TEST SERVER",
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
        ).pack(pady=10)
        
        self.log_display = ctk.CTkTextbox(self.right_panel, state="disabled")
        self.log_display.pack(pady=5, padx=5, fill="both", expand=True)
        
    def append_log(self, message):
        """Append message to log display (thread-safe)"""
        def _append():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_display.configure(state="normal")
            self.log_display.insert("end", f"[{timestamp}] {message}\n")
            self.log_display.configure(state="disabled")
            self.log_display.see("end")
        
        self.after(0, _append)
        
    def update_users_list(self):
        """Update the connected users list (thread-safe)"""
        def _update():
            self.users_list.configure(state="normal")
            self.users_list.delete("1.0", "end")
            
            for socket, info in self.clients.items():
                role_icon = "👨‍🏫" if info.get("role") == "teacher" else "👨‍🎓"
                status_icon = "📝" if info.get("status") == "testing" else "✅" if info.get("status") == "completed" else "⏳"
                
                self.users_list.insert("end", 
                    f"{role_icon} {status_icon} {info.get('username', 'Unknown')}\n"
                    f"   Role: {info.get('role', 'N/A')}\n"
                    f"   Status: {info.get('status', 'connected')}\n\n"
                )
            
            self.users_list.configure(state="disabled")
        
        self.after(0, _update)
    
    def update_statistics(self):
        """Update database statistics"""
        def _update():
            stats = self.db.get_statistics()
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("end", 
                f"Students: {stats['total_students']}\n"
                f"Teachers: {stats['total_teachers']}\n"
                f"Test Attempts: {stats['total_attempts']}\n"
                f"Avg Score: {stats['average_score']}%"
            )
            self.stats_text.configure(state="disabled")
        
        self.after(0, _update)
        
    def toggle_server(self):
        """Start or stop the server"""
        if self.running:
            self.stop_server()
        else:
            self.start_server()
            
    def start_server(self):
        """Start the authentication server"""
        try:
            port = int(self.port_entry.get())
            self.server_socket = self.network.create_server(port)
            self.running = True
            
            self.append_log(f"✓ Authentication server started on port {port}")
            self.append_log(f"⏳ Waiting for clients to connect...")
            
            # Update UI
            self.start_button.configure(text="Stop Server")
            self.status_label.configure(text="● Server Running", text_color="green")
            self.port_entry.configure(state="disabled")
            
            # Start accept thread
            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()
            
        except Exception as e:
            self.append_log(f"✗ Failed to start server: {str(e)}")
            
    def stop_server(self):
        """Stop the authentication server"""
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                self.network.close_socket(client_socket)
            except:
                pass
        self.clients.clear()
        
        if self.server_socket:
            self.network.close_socket(self.server_socket)
            self.server_socket = None
            
        self.append_log("✗ Server stopped")
        
        # Update UI
        self.start_button.configure(text="Start Server")
        self.status_label.configure(text="● Server Stopped", text_color="red")
        self.port_entry.configure(state="normal")
        self.update_users_list()
        
    def accept_clients(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket = self.network.accept_client(self.server_socket)
                
                # Initialize client info (not authenticated yet)
                self.clients[client_socket] = {
                    "authenticated": False,
                    "username": "Guest",
                    "role": None,
                    "status": "connected"
                }
                
                self.append_log(f"✓ New client connected (awaiting authentication)")
                self.update_users_list()
                
                # Start handling this client in a new thread
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
        """Handle communication with a client (with authentication)"""
        try:
            # Wait for authentication
            auth_msg = self.network.receive_message(client_socket)
            
            if auth_msg.startswith("REGISTER:"):
                self.handle_registration(client_socket, auth_msg)
                return
                
            elif auth_msg.startswith("LOGIN:"):
                # Handle login
                session_token = self.handle_login(client_socket, auth_msg)
                if not session_token:
                    return  # Authentication failed
                
                # Get session info
                session = self.session_mgr.validate_session(session_token)
                if not session:
                    return
                
                # Update client info
                self.clients[client_socket] = {
                    "authenticated": True,
                    "user_id": session['user_id'],
                    "username": session['username'],
                    "role": session['role'],
                    "session_token": session_token,
                    "status": "authenticated"
                }
                
                self.append_log(f"🔐 {session['username']} ({session['role']}) authenticated successfully")
                self.update_users_list()
                self.update_statistics()
                
                # Handle role-specific requests
                if session['role'] == 'student':
                    self.handle_student(client_socket, session)
                elif session['role'] == 'teacher':
                    self.handle_teacher(client_socket, session)
            else:
                self.network.send_message(client_socket, "ERROR:Invalid authentication request")
                
        except Exception as e:
            self.append_log(f"✗ Client handler error: {str(e)}")
        finally:
            if client_socket in self.clients:
                del self.clients[client_socket]
            self.update_users_list()
    
    def handle_registration(self, client_socket, auth_msg):
        """Handle user registration"""
        try:
            # Parse: REGISTER:role:{"username":"...", "password":"...", "full_name":"...", "email":"..."}
            parts = auth_msg.split(":", 2)
            role = parts[1]
            data = json.loads(parts[2])
            
            username = data['username']
            password = data['password']
            full_name = data['full_name']
            email = data.get('email', '')
            
            # Validate inputs
            valid, msg = self.auth.validate_username(username)
            if not valid:
                self.network.send_message(client_socket, f"REGISTER_FAILED:{json.dumps({'error': msg})}")
                return
            
            valid, msg = self.auth.validate_password(password)
            if not valid:
                self.network.send_message(client_socket, f"REGISTER_FAILED:{json.dumps({'error': msg})}")
                return
            
            valid, msg = self.auth.validate_full_name(full_name)
            if not valid:
                self.network.send_message(client_socket, f"REGISTER_FAILED:{json.dumps({'error': msg})}")
                return
            
            # Hash password
            password_hash = self.auth.hash_password(password)
            
            # Create user in database
            user_id = self.db.create_user(username, password_hash, role, full_name, email)
            
            if user_id:
                self.append_log(f"✓ New {role} registered: {username} ({full_name})")
                response = json.dumps({
                    'user_id': user_id,
                    'username': username,
                    'role': role
                })
                self.network.send_message(client_socket, f"REGISTER_SUCCESS:{response}")
                self.update_statistics()
            else:
                self.append_log(f"✗ Registration failed: Username '{username}' already exists")
                self.network.send_message(client_socket, f"REGISTER_FAILED:{json.dumps({'error': 'Username already exists'})}")
                
        except Exception as e:
            self.append_log(f"✗ Registration error: {str(e)}")
            self.network.send_message(client_socket, f"REGISTER_FAILED:{json.dumps({'error': str(e)})}")
    
    def handle_login(self, client_socket, auth_msg):
        """Handle user login - Returns session token if successful"""
        try:
            # Parse: LOGIN:role:{"username":"...", "password":"..."}
            parts = auth_msg.split(":", 2)
            role = parts[1]
            data = json.loads(parts[2])
            
            username = data['username']
            password = data['password']
            
            # Get user from database
            user = self.db.get_user_by_username(username)
            
            if not user:
                self.append_log(f"✗ Login failed: User '{username}' not found")
                self.network.send_message(client_socket, f"AUTH_FAILED:{json.dumps({'error': 'Invalid credentials'})}")
                return None
            
            # Verify password
            if not self.auth.verify_password(password, user['password_hash']):
                self.append_log(f"✗ Login failed: Invalid password for '{username}'")
                self.network.send_message(client_socket, f"AUTH_FAILED:{json.dumps({'error': 'Invalid credentials'})}")
                return None
            
            # Check role match
            if user['role'] != role:
                self.append_log(f"✗ Login failed: Role mismatch for '{username}'")
                self.network.send_message(client_socket, f"AUTH_FAILED:{json.dumps({'error': 'Invalid role'})}")
                return None
            
            # Create session
            session_token = self.session_mgr.create_session(
                user_id=user['id'],
                username=user['username'],
                role=user['role'],
                full_name=user['full_name']
            )
            
            # Send success response
            response = json.dumps({
                'session_token': session_token,
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name']
            })
            self.network.send_message(client_socket, f"AUTH_SUCCESS:{response}")
            
            return session_token
            
        except Exception as e:
            self.append_log(f"✗ Login error: {str(e)}")
            self.network.send_message(client_socket, f"AUTH_FAILED:{json.dumps({'error': str(e)})}")
            return None
    
    def handle_student(self, client_socket, session):
        """Handle student-specific requests"""
        try:
            # Send test configuration
            config = {
                "num_questions": len(self.questions),
                "duration": self.test_duration
            }
            self.network.send_message(client_socket, f"CONFIG:{json.dumps(config)}")
            
            # Wait for START request
            start_msg = self.network.receive_message(client_socket)
            if start_msg == "START":
                self.clients[client_socket]["status"] = "testing"
                self.append_log(f"📝 {session['username']} started the test")
                self.update_users_list()
                
                # Send questions
                questions_data = {
                    "questions": [
                        {
                            "id": q["id"],
                            "question": q["question"],
                            "options": q["options"]
                        }
                        for q in self.questions
                    ]
                }
                self.network.send_message(client_socket, f"QUESTIONS:{json.dumps(questions_data)}")
            
            # Receive answers
            answers_msg = self.network.receive_message(client_socket)
            if answers_msg.startswith("ANSWERS:"):
                answers_data = json.loads(answers_msg.split("ANSWERS:")[1])
                score = self.calculate_score(answers_data)
                
                # Save to database
                self.db.save_test_result(
                    student_id=session['user_id'],
                    score=score,
                    total_questions=len(self.questions),
                    answers_json=json.dumps(answers_data),
                    duration_seconds=self.test_duration * 60
                )
                
                self.clients[client_socket]["status"] = "completed"
                
                # Send result
                result = {
                    "score": score,
                    "total": len(self.questions),
                    "percentage": round(score / len(self.questions) * 100, 2)
                }
                self.network.send_message(client_socket, f"RESULT:{json.dumps(result)}")
                
                self.append_log(f"✅ {session['username']} completed: {score}/{len(self.questions)} ({result['percentage']}%)")
                self.update_users_list()
                self.update_statistics()
                
        except Exception as e:
            self.append_log(f"✗ Student handler error: {str(e)}")
    
    def handle_teacher(self, client_socket, session):
        """Handle teacher-specific requests"""
        try:
            # Teachers can view all results
            self.append_log(f"👨‍🏫 Teacher {session['username']} connected")
            
            # Send all results
            results = self.db.get_all_results()
            response = json.dumps({"results": results})
            self.network.send_message(client_socket, f"TEACHER_DATA:{response}")
            
        except Exception as e:
            self.append_log(f"✗ Teacher handler error: {str(e)}")
    
    def calculate_score(self, answers):
        """Calculate student's score"""
        score = 0
        for answer in answers:
            question_id = answer["question_id"]
            selected = answer["selected"]
            
            for q in self.questions:
                if q["id"] == question_id:
                    if selected == q["answer"]:
                        score += 1
                    break
        return score
        
    def on_closing(self):
        """Handle window close"""
        if self.running:
            self.stop_server()
        self.network.cleanup_network()
        self.destroy()


if __name__ == "__main__":
    app = AuthTestServer()
    app.mainloop()

