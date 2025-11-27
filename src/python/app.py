"""
Main Application - Online Multiple Choice Test System
Clean architecture with modular UI components
"""
import customtkinter as ctk
from network_wrapper import NetworkWrapper
from auth import AuthManager
from ui import LoginWindow, RegisterWindow, StudentWindow, TeacherWindow
import json

class TestApplication(ctk.CTk):
    """Main application orchestrator"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.network = NetworkWrapper()
        self.network.init_network()
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
            
            print(f"Connecting to {self.server_host}:{self.server_port}...")
            self.socket = self.network.connect_to_server(self.server_host, self.server_port)
            self.connected = True
            print("✓ Connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
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
            # Send login request
            login_data = json.dumps({
                'username': username,
                'password': password
            })
            self.network.send_message(self.socket, f"LOGIN:{role}:{login_data}")
            
            # Receive response
            response = self.network.receive_message(self.socket)
            
            if response.startswith("AUTH_SUCCESS"):
                session_data = json.loads(response.split("AUTH_SUCCESS:")[1])
                
                # Store session
                self.session_token = session_data['session_token']
                self.user_id = session_data['user_id']
                self.username = session_data['username']
                self.role = session_data['role']
                self.full_name = session_data['full_name']
                
                print(f"✓ Logged in as {self.username} ({self.role})")
                
                # Navigate based on role
                if self.role == 'student':
                    self.show_student_interface()
                else:
                    self.show_teacher_interface()
                    
            else:
                error_data = json.loads(response.split("AUTH_FAILED:")[1])
                if self.login_window:
                    self.login_window.show_status(f"✗ {error_data['error']}", "red")
                    
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
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
            # Send registration request
            reg_data = json.dumps({
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email
            })
            self.network.send_message(self.socket, f"REGISTER:{role}:{reg_data}")
            
            # Receive response
            response = self.network.receive_message(self.socket)
            
            if response.startswith("REGISTER_SUCCESS"):
                if self.register_window:
                    self.register_window.show_status(
                        "✓ Registration successful! Please login.",
                        "green"
                    )
                # Auto-switch to login after 2 seconds
                self.after(2000, self.show_login)
            else:
                error_data = json.loads(response.split("REGISTER_FAILED:")[1])
                if self.register_window:
                    self.register_window.show_status(f"✗ {error_data['error']}", "red")
                    
        except Exception as e:
            print(f"✗ Registration error: {str(e)}")
            if self.register_window:
                self.register_window.show_status(f"✗ Error: {str(e)}", "red")
    
    # ==================== STUDENT INTERFACE ====================
    
    def show_student_interface(self):
        """Show student interface"""
        # Receive config
        try:
            config_msg = self.network.receive_message(self.socket)
            if config_msg.startswith("CONFIG:"):
                config = json.loads(config_msg.split("CONFIG:")[1])
                
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
            print(f"✗ Error showing student interface: {str(e)}")
    
    def handle_start_test(self):
        """Handle start test"""
        try:
            # Request questions
            self.network.send_message(self.socket, "START")
            
            # Receive questions
            questions_msg = self.network.receive_message(self.socket)
            if questions_msg.startswith("QUESTIONS:"):
                questions_data = json.loads(questions_msg.split("QUESTIONS:")[1])
                questions = questions_data["questions"]
                
                # Show test screen
                if self.student_window:
                    # Get duration from previous config or default
                    duration = getattr(self.student_window, 'test_duration', 30)
                    self.student_window.show_test_screen(questions, duration)
                    
        except Exception as e:
            print(f"✗ Error starting test: {str(e)}")
    
    def handle_submit_test(self, answers):
        """Handle submit test"""
        try:
            # Send answers
            answers_json = json.dumps(answers)
            self.network.send_message(self.socket, f"ANSWERS:{answers_json}")
            
            # Receive result
            result_msg = self.network.receive_message(self.socket)
            if result_msg.startswith("RESULT:"):
                result = json.loads(result_msg.split("RESULT:")[1])
                
                # Show result
                if self.student_window:
                    self.student_window.show_result_screen(result, self.full_name)
                    
        except Exception as e:
            print(f"✗ Error submitting test: {str(e)}")
    
    # ==================== TEACHER INTERFACE ====================
    
    def show_teacher_interface(self):
        """Show teacher interface"""
        try:
            # Receive teacher data
            teacher_data_msg = self.network.receive_message(self.socket)
            if teacher_data_msg.startswith("TEACHER_DATA:"):
                data = json.loads(teacher_data_msg.split("TEACHER_DATA:")[1])
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
            print(f"✗ Error showing teacher interface: {str(e)}")
    
    # ==================== CLEANUP ====================
    
    def on_closing(self):
        """Handle window close"""
        if hasattr(self.student_window, 'timer_running'):
            self.student_window.timer_running = False
        if self.connected and self.socket:
            try:
                self.network.close_socket(self.socket)
            except:
                pass
        self.network.cleanup_network()
        self.destroy()


if __name__ == "__main__":
    app = TestApplication()
    app.mainloop()

