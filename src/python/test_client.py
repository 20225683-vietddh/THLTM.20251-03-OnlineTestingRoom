"""
Multiple Choice Test Client GUI using CustomTkinter
Client cho học sinh làm bài thi trắc nghiệm
"""
import customtkinter as ctk
from network_wrapper import NetworkWrapper
import threading
import json
from datetime import datetime, timedelta

class TestClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize network wrapper
        self.network = NetworkWrapper()
        self.network.init_network()
        self.socket = None
        self.connected = False
        
        # Test data
        self.questions = []
        self.current_question = 0
        self.answers = []  # List of selected answers
        self.test_duration = 30
        self.start_time = None
        self.timer_running = False
        
        # Configure window
        self.title("Test Client - Network Programming")
        self.geometry("800x700")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create UI
        self.create_widgets()
        self.show_connection_screen()
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """Create UI widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def show_connection_screen(self):
        """Show connection screen"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Connection Frame
        connection_frame = ctk.CTkFrame(self.main_frame)
        connection_frame.pack(expand=True)
        
        ctk.CTkLabel(
            connection_frame,
            text="📝 Online Multiple Choice Test",
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        # Student name
        ctk.CTkLabel(connection_frame, text="Your Name:", font=("Arial", 14)).pack(pady=5)
        self.name_entry = ctk.CTkEntry(connection_frame, width=300, height=40)
        self.name_entry.pack(pady=5)
        
        # Host
        ctk.CTkLabel(connection_frame, text="Server Host:", font=("Arial", 14)).pack(pady=5)
        self.host_entry = ctk.CTkEntry(connection_frame, width=300, height=40)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(pady=5)
        
        # Port
        ctk.CTkLabel(connection_frame, text="Server Port:", font=("Arial", 14)).pack(pady=5)
        self.port_entry = ctk.CTkEntry(connection_frame, width=300, height=40)
        self.port_entry.insert(0, "5000")
        self.port_entry.pack(pady=5)
        
        # Connect button
        self.connect_button = ctk.CTkButton(
            connection_frame,
            text="Connect to Test Server",
            command=self.connect_to_server,
            height=50,
            font=("Arial", 16, "bold")
        )
        self.connect_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            connection_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
    def connect_to_server(self):
        """Connect to test server"""
        student_name = self.name_entry.get().strip()
        if not student_name:
            self.status_label.configure(text="⚠ Please enter your name", text_color="red")
            return
            
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            self.status_label.configure(text="Connecting...", text_color="yellow")
            self.socket = self.network.connect_to_server(host, port)
            self.connected = True
            
            # Send student name
            self.network.send_message(self.socket, f"NAME:{student_name}")
            
            # Receive test configuration
            config_msg = self.network.receive_message(self.socket)
            if config_msg.startswith("CONFIG:"):
                config = json.loads(config_msg.split("CONFIG:")[1])
                self.test_duration = config["duration"]
                
                # Show ready screen
                self.show_ready_screen(config)
            
        except Exception as e:
            self.status_label.configure(text=f"✗ Connection failed: {str(e)}", text_color="red")
            
    def show_ready_screen(self, config):
        """Show ready screen before test starts"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        ready_frame = ctk.CTkFrame(self.main_frame)
        ready_frame.pack(expand=True)
        
        ctk.CTkLabel(
            ready_frame,
            text="✓ Connected to Test Server",
            font=("Arial", 20, "bold"),
            text_color="green"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            ready_frame,
            text="Test Information",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        info_text = f"""
        Number of Questions: {config['num_questions']}
        Duration: {config['duration']} minutes
        
        Instructions:
        • Read each question carefully
        • Select one answer for each question
        • You can navigate between questions
        • Submit your answers before time runs out
        """
        
        ctk.CTkLabel(
            ready_frame,
            text=info_text,
            font=("Arial", 14),
            justify="left"
        ).pack(pady=20)
        
        ctk.CTkButton(
            ready_frame,
            text="Start Test",
            command=self.start_test,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(pady=20)
        
    def start_test(self):
        """Start the test"""
        try:
            # Request test questions
            self.network.send_message(self.socket, "START")
            
            # Receive questions
            questions_msg = self.network.receive_message(self.socket)
            if questions_msg.startswith("QUESTIONS:"):
                questions_data = json.loads(questions_msg.split("QUESTIONS:")[1])
                self.questions = questions_data["questions"]
                
                # Initialize answers list
                self.answers = [{"question_id": q["id"], "selected": -1} for q in self.questions]
                
                # Start timer
                self.start_time = datetime.now()
                self.timer_running = True
                
                # Show test screen
                self.show_test_screen()
                
                # Start timer update (from main thread)
                self.after(1000, self.update_timer)
                
        except Exception as e:
            print(f"Error starting test: {e}")
            
    def show_test_screen(self):
        """Show test screen with questions"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Top bar with timer
        top_bar = ctk.CTkFrame(self.main_frame)
        top_bar.pack(fill="x", pady=10)
        
        self.timer_label = ctk.CTkLabel(
            top_bar,
            text="Time Remaining: 00:00",
            font=("Arial", 16, "bold"),
            text_color="green"
        )
        self.timer_label.pack(side="left", padx=20)
        
        self.progress_label = ctk.CTkLabel(
            top_bar,
            text=f"Question 1/{len(self.questions)}",
            font=("Arial", 14)
        )
        self.progress_label.pack(side="right", padx=20)
        
        # Question frame
        self.question_frame = ctk.CTkFrame(self.main_frame)
        self.question_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        # Navigation frame
        nav_frame = ctk.CTkFrame(self.main_frame)
        nav_frame.pack(fill="x", pady=10)
        
        self.prev_button = ctk.CTkButton(
            nav_frame,
            text="← Previous",
            command=self.previous_question,
            state="disabled"
        )
        self.prev_button.pack(side="left", padx=20)
        
        self.submit_button = ctk.CTkButton(
            nav_frame,
            text="Submit Test",
            command=self.submit_test,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.submit_button.pack(side="right", padx=20)
        
        self.next_button = ctk.CTkButton(
            nav_frame,
            text="Next →",
            command=self.next_question
        )
        self.next_button.pack(side="right")
        
        # Display first question
        self.display_question()
        
    def display_question(self):
        """Display current question"""
        # Clear question frame
        for widget in self.question_frame.winfo_children():
            widget.destroy()
            
        question = self.questions[self.current_question]
        
        # Question text
        ctk.CTkLabel(
            self.question_frame,
            text=f"Question {self.current_question + 1}",
            font=("Arial", 16, "bold")
        ).pack(pady=10, anchor="w")
        
        ctk.CTkLabel(
            self.question_frame,
            text=question["question"],
            font=("Arial", 14),
            wraplength=700,
            justify="left"
        ).pack(pady=10, anchor="w")
        
        # Options
        self.option_var = ctk.IntVar(value=self.answers[self.current_question]["selected"])
        
        for i, option in enumerate(question["options"]):
            radio = ctk.CTkRadioButton(
                self.question_frame,
                text=option,
                variable=self.option_var,
                value=i,
                font=("Arial", 13),
                command=lambda: self.save_answer(self.option_var.get())
            )
            radio.pack(pady=8, anchor="w", padx=20)
        
        # Update progress
        self.progress_label.configure(text=f"Question {self.current_question + 1}/{len(self.questions)}")
        
        # Update navigation buttons
        self.prev_button.configure(state="normal" if self.current_question > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_question < len(self.questions) - 1 else "disabled")
        
    def save_answer(self, selected):
        """Save the selected answer"""
        self.answers[self.current_question]["selected"] = selected
        
    def previous_question(self):
        """Go to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            self.display_question()
            
    def next_question(self):
        """Go to next question"""
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.display_question()
            
    def update_timer(self):
        """Update timer display (called from main thread using after())"""
        if not self.timer_running:
            return
            
        elapsed = datetime.now() - self.start_time
        remaining = timedelta(minutes=self.test_duration) - elapsed
        
        if remaining.total_seconds() <= 0:
            self.timer_running = False
            self.timer_label.configure(text="Time's Up!", text_color="red")
            self.submit_test()
            return
            
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        
        color = "green" if minutes >= 5 else "orange" if minutes >= 2 else "red"
        self.timer_label.configure(
            text=f"Time Remaining: {minutes:02d}:{seconds:02d}",
            text_color=color
        )
        
        # Schedule next update (Tkinter-safe way)
        self.after(1000, self.update_timer)
            
    def submit_test(self):
        """Submit test answers"""
        self.timer_running = False
        
        try:
            # Send answers to server
            answers_json = json.dumps(self.answers)
            self.network.send_message(self.socket, f"ANSWERS:{answers_json}")
            
            # Receive result
            result_msg = self.network.receive_message(self.socket)
            if result_msg.startswith("RESULT:"):
                result = json.loads(result_msg.split("RESULT:")[1])
                self.show_result_screen(result)
                
        except Exception as e:
            print(f"Error submitting test: {e}")
            
    def show_result_screen(self, result):
        """Show test result"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(expand=True)
        
        ctk.CTkLabel(
            result_frame,
            text="🎉 Test Completed!",
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            result_frame,
            text="Your Score",
            font=("Arial", 18)
        ).pack(pady=10)
        
        score_text = f"{result['score']}/{result['total']}"
        percentage = result['percentage']
        
        color = "green" if percentage >= 70 else "orange" if percentage >= 50 else "red"
        
        ctk.CTkLabel(
            result_frame,
            text=score_text,
            font=("Arial", 48, "bold"),
            text_color=color
        ).pack(pady=10)
        
        ctk.CTkLabel(
            result_frame,
            text=f"{percentage}%",
            font=("Arial", 32),
            text_color=color
        ).pack(pady=10)
        
        # Grade
        if percentage >= 90:
            grade = "Excellent! 🌟"
        elif percentage >= 70:
            grade = "Good Job! 👍"
        elif percentage >= 50:
            grade = "Passed ✓"
        else:
            grade = "Need Improvement 📚"
            
        ctk.CTkLabel(
            result_frame,
            text=grade,
            font=("Arial", 20)
        ).pack(pady=20)
        
        ctk.CTkButton(
            result_frame,
            text="Close",
            command=self.on_closing,
            height=40
        ).pack(pady=20)
        
    def on_closing(self):
        """Handle window close"""
        self.timer_running = False
        if self.connected and self.socket:
            self.network.close_socket(self.socket)
        self.network.cleanup_network()
        self.destroy()


if __name__ == "__main__":
    app = TestClient()
    app.mainloop()

