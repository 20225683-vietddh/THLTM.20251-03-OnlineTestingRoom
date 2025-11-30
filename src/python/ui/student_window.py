"""
Student Window UI Component
Handles student test interface with timer and questions
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox

class StudentWindow:
    """Student test interface UI component"""
    
    def __init__(self, parent, callbacks):
        """
        Initialize student window
        
        Args:
            parent: Parent frame to pack widgets into
            callbacks: Dict with callback functions
                - on_start_test: callback()
                - on_submit_test: callback(answers)
                - on_answer_change: callback(question_idx, selected)
                - on_join_room: callback(room_code)
                - on_refresh_rooms: callback()
        """
        self.parent = parent
        self.callbacks = callbacks
        self.frame = None
        
        # Test state
        self.questions = []
        self.current_question = 0
        self.answers = []
        self.test_duration = 30
        self.start_time = None
        self.timer_running = False
        
        # UI components
        self.timer_label = None
        self.progress_label = None
        self.question_frame = None
        self.prev_button = None
        self.next_button = None
        self.submit_button = None
        
        # Room data
        self.rooms_data = []
    
    def show_room_lobby(self, full_name):
        """Show room lobby where student can join a test room"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        lobby_frame = ctk.CTkFrame(self.parent)
        lobby_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(
            lobby_frame,
            text=f"Welcome, {full_name}!",
            font=("Arial", 22, "bold")
        ).pack(pady=20)
        
        # Join Room Section
        join_frame = ctk.CTkFrame(lobby_frame)
        join_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            join_frame,
            text="🔐 Enter Room Code",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            join_frame,
            text="Enter the 6-character code provided by your teacher:",
            font=("Arial", 12)
        ).pack(pady=5)
        
        # Room code entry
        code_frame = ctk.CTkFrame(join_frame)
        code_frame.pack(pady=10)
        
        self.room_code_entry = ctk.CTkEntry(
            code_frame,
            width=250,
            height=45,
            font=("Arial", 20, "bold"),
            placeholder_text="ABC123",
            justify="center"
        )
        self.room_code_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            code_frame,
            text="Join Room",
            command=self._handle_join_room,
            height=45,
            width=120,
            font=("Arial", 14, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left")
        
        # Or divider
        ctk.CTkLabel(
            lobby_frame,
            text="— OR —",
            font=("Arial", 12)
        ).pack(pady=10)
        
        # My Rooms Section
        rooms_frame = ctk.CTkFrame(lobby_frame)
        rooms_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        header_frame = ctk.CTkFrame(rooms_frame)
        header_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="📚 My Joined Rooms",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self._handle_refresh_rooms,
            width=100
        ).pack(side="right", padx=10)
        
        # Rooms list
        self.rooms_text = ctk.CTkTextbox(rooms_frame, font=("Courier New", 11))
        self.rooms_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._update_rooms_lobby()
    
    def _update_rooms_lobby(self):
        """Update rooms list in lobby"""
        self.rooms_text.configure(state="normal")
        self.rooms_text.delete("1.0", "end")
        
        # Header
        self.rooms_text.insert("end",
            f"{'Room Name':<30} {'Teacher':<20} {'Status':<15} {'Duration':<10}\n"
        )
        self.rooms_text.insert("end", "=" * 80 + "\n")
        
        # Rooms data
        if self.rooms_data:
            for room in self.rooms_data:
                status_icon = "⏳" if room['room_status'] == 'waiting' else ("▶️" if room['room_status'] == 'active' else "✅")
                self.rooms_text.insert("end",
                    f"{room['room_name']:<30} "
                    f"{room['teacher_name']:<20} "
                    f"{status_icon} {room['room_status']:<13} "
                    f"{room['duration_minutes']}min\n"
                )
        else:
            self.rooms_text.insert("end", "\nNo rooms joined yet. Enter a room code above to join!\n")
        
        self.rooms_text.configure(state="disabled")
    
    def update_rooms(self, rooms):
        """Update rooms data and refresh display"""
        self.rooms_data = rooms
        if hasattr(self, 'rooms_text'):
            self._update_rooms_lobby()
    
    def _handle_join_room(self):
        """Handle join room button"""
        room_code = self.room_code_entry.get().strip().upper()
        
        if not room_code:
            messagebox.showerror("Invalid Input", "Please enter a room code")
            return
        
        if len(room_code) != 6:
            messagebox.showerror("Invalid Input", "Room code must be 6 characters")
            return
        
        if self.callbacks.get('on_join_room'):
            self.callbacks['on_join_room'](room_code)
    
    def _handle_refresh_rooms(self):
        """Handle refresh rooms button"""
        if self.callbacks.get('on_refresh_rooms'):
            self.callbacks['on_refresh_rooms']()
    
    def show_room_joined(self, room_name):
        """Show success message after joining room"""
        messagebox.showinfo(
            "Joined Successfully!",
            f"You have joined the room: {room_name}\n\nWait for the teacher to start the test."
        )
        self.room_code_entry.delete(0, "end")
        
    def show_ready_screen(self, full_name, num_questions, duration):
        """Show ready screen before test starts"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        ready_frame = ctk.CTkFrame(self.parent)
        ready_frame.pack(expand=True)
        
        ctk.CTkLabel(
            ready_frame,
            text=f"✓ Welcome, {full_name}!",
            font=("Arial", 20, "bold"),
            text_color="green"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            ready_frame,
            text="Test Information",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        info_text = f"""
        Number of Questions: {num_questions}
        Duration: {duration} minutes
        
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
            command=self._handle_start_test,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(pady=20)
    
    def show_test_screen(self, questions, duration):
        """Show test screen with questions"""
        self.questions = questions
        self.test_duration = duration
        self.answers = [{"question_id": q["id"], "selected": -1} for q in questions]
        self.start_time = datetime.now()
        self.timer_running = True
        
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Top bar with timer
        top_bar = ctk.CTkFrame(self.parent)
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
        self.question_frame = ctk.CTkFrame(self.parent)
        self.question_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        # Navigation frame
        nav_frame = ctk.CTkFrame(self.parent)
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
            command=self._handle_submit,
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
        
        # Start timer
        self._update_timer()
    
    def display_question(self):
        """Display current question"""
        # Clear question frame
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        question = self.questions[self.current_question]
        
        # Question number
        ctk.CTkLabel(
            self.question_frame,
            text=f"Question {self.current_question + 1}",
            font=("Arial", 16, "bold")
        ).pack(pady=10, anchor="w")
        
        # Question text
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
                command=lambda: self._save_answer(self.option_var.get())
            )
            radio.pack(pady=8, anchor="w", padx=20)
        
        # Update navigation
        self.progress_label.configure(
            text=f"Question {self.current_question + 1}/{len(self.questions)}"
        )
        self.prev_button.configure(
            state="normal" if self.current_question > 0 else "disabled"
        )
        self.next_button.configure(
            state="normal" if self.current_question < len(self.questions) - 1 else "disabled"
        )
    
    def _save_answer(self, selected):
        """Save selected answer"""
        self.answers[self.current_question]["selected"] = selected
        if self.callbacks.get('on_answer_change'):
            self.callbacks['on_answer_change'](self.current_question, selected)
    
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
    
    def _update_timer(self):
        """Update timer display (recursive with after)"""
        if not self.timer_running:
            return
        
        elapsed = datetime.now() - self.start_time
        remaining = timedelta(minutes=self.test_duration) - elapsed
        
        if remaining.total_seconds() <= 0:
            self.timer_running = False
            self.timer_label.configure(text="Time's Up!", text_color="red")
            self._handle_submit()
            return
        
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        
        color = "green" if minutes >= 5 else "orange" if minutes >= 2 else "red"
        self.timer_label.configure(
            text=f"Time Remaining: {minutes:02d}:{seconds:02d}",
            text_color=color
        )
        
        # Schedule next update
        self.parent.after(1000, self._update_timer)
    
    def _handle_start_test(self):
        """Handle start test button"""
        if self.callbacks.get('on_start_test'):
            self.callbacks['on_start_test']()
    
    def _handle_submit(self):
        """Handle submit test button"""
        self.timer_running = False
        if self.callbacks.get('on_submit_test'):
            self.callbacks['on_submit_test'](self.answers)
    
    def show_result_screen(self, result, full_name):
        """Show test result"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        result_frame = ctk.CTkFrame(self.parent)
        result_frame.pack(expand=True)
        
        ctk.CTkLabel(
            result_frame,
            text="🎉 Test Completed!",
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            result_frame,
            text=f"Hello, {full_name}",
            font=("Arial", 16)
        ).pack(pady=10)
        
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
            command=self.parent.quit,
            height=40
        ).pack(pady=20)

