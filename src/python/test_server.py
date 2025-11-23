"""
Multiple Choice Test Server GUI using CustomTkinter
Server quản lý bài thi, câu hỏi, và theo dõi học sinh làm bài
"""
import customtkinter as ctk
from network_wrapper import NetworkWrapper
import threading
import json
from datetime import datetime
import os

class TestServer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize network wrapper
        self.network = NetworkWrapper()
        self.network.init_network()
        self.server_socket = None
        self.clients = {}  # {socket: {"name": str, "score": int, "status": str}}
        self.running = False
        self.accept_thread = None
        
        # Test configuration
        self.questions = []
        self.test_duration = 30  # minutes
        
        # Configure window
        self.title("Test Server - Network Programming")
        self.geometry("900x700")
        
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
            self.append_log("⚠ Warning: questions.json not found. Using sample questions.")
            self.create_sample_questions()
            
    def create_sample_questions(self):
        """Create sample questions if file not found"""
        self.questions = [
            {
                "id": 1,
                "question": "What does TCP stand for?",
                "options": ["Transmission Control Protocol", "Transfer Control Protocol", 
                           "Transport Communication Protocol", "Telecommunication Control Protocol"],
                "answer": 0
            },
            {
                "id": 2,
                "question": "Which layer of OSI model does IP protocol belong to?",
                "options": ["Application Layer", "Transport Layer", "Network Layer", "Data Link Layer"],
                "answer": 2
            }
        ]
        
    def create_widgets(self):
        """Create UI widgets"""
        # Left Panel - Server Control
        self.left_panel = ctk.CTkFrame(self, width=300)
        self.left_panel.pack(side="left", fill="both", padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.left_panel, 
            text="TEST SERVER",
            font=("Arial", 20, "bold")
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
        
        # Test Info Frame
        self.info_frame = ctk.CTkFrame(self.left_panel)
        self.info_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(
            self.info_frame,
            text="Test Information",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.questions_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Total Questions: {len(self.questions)}"
        )
        self.questions_label.pack(pady=2)
        
        self.duration_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Duration: {self.test_duration} minutes"
        )
        self.duration_label.pack(pady=2)
        
        # Connected Students Frame
        self.students_frame = ctk.CTkFrame(self.left_panel)
        self.students_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            self.students_frame,
            text="Connected Students",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.students_list = ctk.CTkTextbox(self.students_frame, state="disabled")
        self.students_list.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Right Panel - Logs
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            self.right_panel,
            text="Server Logs",
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
        
        # Schedule on main thread if called from worker thread
        self.after(0, _append)
        
    def update_students_list(self):
        """Update the connected students list (thread-safe)"""
        def _update():
            self.students_list.configure(state="normal")
            self.students_list.delete("1.0", "end")
            
            for socket, info in self.clients.items():
                status_icon = "📝" if info["status"] == "testing" else "✅" if info["status"] == "completed" else "⏳"
                self.students_list.insert("end", 
                    f"{status_icon} {info['name']}\n"
                    f"   Score: {info['score']}/{len(self.questions)}\n"
                    f"   Status: {info['status']}\n\n"
                )
            
            self.students_list.configure(state="disabled")
        
        # Schedule on main thread if called from worker thread
        self.after(0, _update)
        
    def toggle_server(self):
        """Start or stop the server"""
        if self.running:
            self.stop_server()
        else:
            self.start_server()
            
    def start_server(self):
        """Start the test server"""
        try:
            port = int(self.port_entry.get())
            self.server_socket = self.network.create_server(port)
            self.running = True
            
            self.append_log(f"✓ Test server started on port {port}")
            self.append_log(f"⏳ Waiting for students to connect...")
            
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
        """Stop the test server"""
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
        self.update_students_list()
        
    def accept_clients(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket = self.network.accept_client(self.server_socket)
                
                # Initialize client info
                self.clients[client_socket] = {
                    "name": f"Student_{len(self.clients) + 1}",
                    "score": 0,
                    "status": "connected"
                }
                
                self.append_log(f"✓ New student connected!")
                self.update_students_list()
                
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
        """Handle communication with a client"""
        try:
            # Receive student name
            name_msg = self.network.receive_message(client_socket)
            if name_msg.startswith("NAME:"):
                student_name = name_msg.split("NAME:")[1]
                self.clients[client_socket]["name"] = student_name
                self.append_log(f"📝 {student_name} registered")
                self.update_students_list()
            
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
                self.append_log(f"📝 {self.clients[client_socket]['name']} started the test")
                self.update_students_list()
                
                # Send all questions
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
                
                self.clients[client_socket]["score"] = score
                self.clients[client_socket]["status"] = "completed"
                
                # Send result
                result = {
                    "score": score,
                    "total": len(self.questions),
                    "percentage": round(score / len(self.questions) * 100, 2)
                }
                self.network.send_message(client_socket, f"RESULT:{json.dumps(result)}")
                
                self.append_log(
                    f"✅ {self.clients[client_socket]['name']} completed: "
                    f"{score}/{len(self.questions)} ({result['percentage']}%)"
                )
                self.update_students_list()
                
        except Exception as e:
            if self.running:
                self.append_log(f"✗ Client handler error: {str(e)}")
        finally:
            # Keep connection open to show results
            pass
            
    def calculate_score(self, answers):
        """Calculate student's score"""
        score = 0
        for answer in answers:
            question_id = answer["question_id"]
            selected = answer["selected"]
            
            # Find correct answer
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
    app = TestServer()
    app.mainloop()

