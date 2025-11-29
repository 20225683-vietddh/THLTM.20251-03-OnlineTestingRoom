"""
Main Application - Online Multiple Choice Test System
Clean architecture with modular UI components
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
    ERR_SUCCESS, ERR_INVALID_CREDS, ERR_USERNAME_EXISTS
)
from auth import AuthManager
from ui import LoginWindow, RegisterWindow, StudentWindow, TeacherWindow
import json

class TestApplication(ctk.CTk):
    """Main application orchestrator"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.proto = ProtocolWrapper()
        self.proto.init_network()
        self.auth = AuthManager()
        
        # Connection state
        self.socket = None
        self.connected = False
        self.server_host = "127.0.0.1"
        self.server_port = 5000
        
        # Session state
        self.session_token = None
        self.user_id = None
        self.username = None
        self.role = None
        self.full_name = None
        
        # Configure window
        self.title("Test System - Network Programming")
        self.geometry("800x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize UI components
        self.login_window = None
        self.register_window = None
        self.student_window = None
        self.teacher_window = None
        
        # Show start screen
        self.show_start_screen()
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ==================== NAVIGATION ====================
    
    def show_start_screen(self):
        """Show initial welcome screen with connection settings"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        start_frame = ctk.CTkFrame(self.main_frame)
        start_frame.pack(expand=True)
        
        ctk.CTkLabel(
            start_frame,
            text="📝 Online Test System",
            font=("Arial", 28, "bold")
        ).pack(pady=30)
        
        ctk.CTkLabel(
            start_frame,
            text="Welcome! Please login or register to continue",
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Connection settings
        conn_frame = ctk.CTkFrame(start_frame)
        conn_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(conn_frame, text="Server Host:", font=("Arial", 12)).pack(pady=5)
        self.host_entry = ctk.CTkEntry(conn_frame, width=300)
        self.host_entry.insert(0, self.server_host)
        self.host_entry.pack(pady=5)
        
        ctk.CTkLabel(conn_frame, text="Server Port:", font=("Arial", 12)).pack(pady=5)
        self.port_entry = ctk.CTkEntry(conn_frame, width=300)
        self.port_entry.insert(0, str(self.server_port))
        self.port_entry.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(start_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Login",
            command=self.show_login,
            width=150,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Register",
            command=self.show_register,
            width=150,
            height=50,
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
    
    def show_login(self):
        """Show login screen"""
        # Save connection settings
        try:
            self.server_host = self.host_entry.get()
            self.server_port = int(self.port_entry.get())
        except:
            pass
        
        # Create and show login window
        self.login_window = LoginWindow(self.main_frame, {
            'on_login': self.handle_login,
            'on_back': self.show_start_screen
        })
        self.login_window.show()
    
    def show_register(self):
        """Show register screen"""
        # Save connection settings
        try:
            self.server_host = self.host_entry.get()
            self.server_port = int(self.port_entry.get())
        except:
            pass
        
        # Create and show register window
        self.register_window = RegisterWindow(self.main_frame, {
            'on_register': self.handle_register,
            'on_back': self.show_start_screen
        })
        self.register_window.show()
    
    # ==================== AUTHENTICATION ====================
    
    def connect_to_server(self):
        """Connect to server"""
        try:
            if self.connected:
                return True
            
            self.socket = self.proto.connect_to_server(self.server_host, self.server_port)
            self.connected = True
            return True
        except Exception as e:
            return False
    
    def handle_login(self, username, password, role):
        """Handle login request"""
        # Show status
        if self.login_window:
            self.login_window.show_status("Connecting...", "yellow")
        
        # Connect
        if not self.connect_to_server():
            if self.login_window:
                self.login_window.show_status("✗ Connection failed", "red")
            return
        
        try:
            # Send login request with protocol
            self.proto.send_message(self.socket, MSG_LOGIN_REQ, {
                'username': username,
                'password': password,
                'role': role
            }, use_session=False)
            
            # Receive response
            response = self.proto.receive_message(self.socket)
            
            if response['message_type'] == MSG_LOGIN_RES:
                payload = response['payload']
                
                if payload['code'] == ERR_SUCCESS:
                    session_data = payload['data']
                    
                    # Store session
                    self.session_token = session_data['session_token']
                    self.user_id = session_data['user_id']
                    self.username = session_data['username']
                    self.role = session_data['role']
                    self.full_name = session_data['full_name']
                    
                    # Set session token in protocol wrapper
                    self.proto.set_session_token(self.session_token)
                    
                    # Navigate based on role
                    if self.role == 'student':
                        self.show_student_interface()
                    else:
                        self.show_teacher_interface()
                else:
                    # Login failed
                    error_msg = payload.get('message', 'Login failed')
                    if self.login_window:
                        self.login_window.show_status(f"✗ {error_msg}", "red")
            elif response['message_type'] == MSG_ERROR:
                # Server sent error
                error_msg = response['payload'].get('message', 'Unknown error')
                if self.login_window:
                    self.login_window.show_status(f"✗ {error_msg}", "red")
            else:
                # Unexpected message type
                if self.login_window:
                    self.login_window.show_status("✗ Unexpected response", "red")
                    
        except Exception as e:
            if self.login_window:
                self.login_window.show_status(f"✗ Error: {str(e)}", "red")
    
    def handle_register(self, username, password, full_name, email, role):
        """Handle registration request"""
        # Validate
        valid, msg = self.auth.validate_username(username)
        if not valid:
            if self.register_window:
                self.register_window.show_status(f"⚠ {msg}", "red")
            return
        
        valid, msg = self.auth.validate_password(password)
        if not valid:
            if self.register_window:
                self.register_window.show_status(f"⚠ {msg}", "red")
            return
        
        # Connect
        if self.register_window:
            self.register_window.show_status("Connecting...", "yellow")
        
        if not self.connect_to_server():
            if self.register_window:
                self.register_window.show_status("✗ Connection failed", "red")
            return
        
        try:
            # Send registration request with protocol
            self.proto.send_message(self.socket, MSG_REGISTER_REQ, {
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email,
                'role': role
            }, use_session=False)
            
            # Receive response
            response = self.proto.receive_message(self.socket)
            
            if response['message_type'] == MSG_REGISTER_RES:
                payload = response['payload']
                
                if payload['code'] == ERR_SUCCESS:
                    if self.register_window:
                        self.register_window.show_status(
                            "✓ Registration successful! Please login.",
                            "green"
                        )
                    # Auto-switch to login after 2 seconds
                    self.after(2000, self.show_login)
                else:
                    error_msg = payload.get('message', 'Registration failed')
                    if self.register_window:
                        self.register_window.show_status(f"✗ {error_msg}", "red")
                    
        except Exception as e:
            if self.register_window:
                self.register_window.show_status(f"✗ Error: {str(e)}", "red")
    
    # ==================== STUDENT INTERFACE ====================
    
    def show_student_interface(self):
        """Show student interface"""
        # Receive config (auto-sent by server)
        try:
            response = self.proto.receive_message(self.socket)
            if response['message_type'] == MSG_TEST_CONFIG:
                config = response['payload']
                
                # Create student window
                self.student_window = StudentWindow(self.main_frame, {
                    'on_start_test': self.handle_start_test,
                    'on_submit_test': self.handle_submit_test
                })
                
                # Show ready screen
                self.student_window.show_ready_screen(
                    full_name=self.full_name,
                    num_questions=config['num_questions'],
                    duration=config['duration']
                )
        except Exception as e:
            pass
    
    def handle_start_test(self):
        """Handle start test"""
        try:
            # Send start request
            self.proto.send_message(self.socket, MSG_TEST_START_REQ, {'ready': True})
            
            # Receive start confirmation
            response = self.proto.receive_message(self.socket)
            
            # Receive questions
            questions_response = self.proto.receive_message(self.socket)
            if questions_response['message_type'] == MSG_TEST_QUESTIONS:
                questions = questions_response['payload']['questions']
                
                # Show test screen
                if self.student_window:
                    # Get duration from previous config or default
                    duration = getattr(self.student_window, 'test_duration', 30)
                    self.student_window.show_test_screen(questions, duration)
                    
        except Exception as e:
            pass
    
    def handle_submit_test(self, answers):
        """Handle submit test"""
        try:
            # Send answers with protocol
            self.proto.send_message(self.socket, MSG_TEST_SUBMIT, {
                'answers': answers,
                'end_time': self.proto.lib.py_get_unix_timestamp()
            })
            
            # Receive result
            response = self.proto.receive_message(self.socket)
            if response['message_type'] == MSG_TEST_RESULT:
                result = response['payload']['data']
                
                # Show result
                if self.student_window:
                    self.student_window.show_result_screen(result, self.full_name)
                    
        except Exception as e:
            pass
    
    # ==================== TEACHER INTERFACE ====================
    
    def show_teacher_interface(self):
        """Show teacher interface"""
        try:
            # Request teacher data (auto-sent by server, or request manually)
            # Server should auto-send after login, but we can also request
            # self.proto.send_message(self.socket, MSG_TEACHER_DATA_REQ, {})
            
            # Receive teacher data
            response = self.proto.receive_message(self.socket)
            if response['message_type'] == MSG_TEACHER_DATA_RES:
                data = response['payload']['data']
                results = data.get("results", [])
                
                # Create teacher window
                self.teacher_window = TeacherWindow(self.main_frame, {
                    'on_logout': self.on_closing
                })
                
                # Show dashboard
                self.teacher_window.show_dashboard(
                    full_name=self.full_name,
                    results=results
                )
        except Exception as e:
            pass
    
    # ==================== CLEANUP ====================
    
    def on_closing(self):
        """Handle window close"""
        if hasattr(self.student_window, 'timer_running'):
            self.student_window.timer_running = False
        if self.connected and self.socket:
            try:
                self.proto.close_socket(self.socket)
            except:
                pass
        self.proto.cleanup_network()
        self.destroy()


if __name__ == "__main__":
    app = TestApplication()
    app.mainloop()

