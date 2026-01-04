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
                - on_join_room: callback(room_id)
                - on_refresh_rooms: callback()
                - on_refresh_available: callback()
                - on_logout: callback()
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
        self.room_id = None
        
        # Auto-save state
        self.auto_save_interval = 10  # seconds (save every 10s)
        self.last_save_time = None
        self.auto_save_running = False
        self.auto_save_task_id = None  # Store scheduled task ID
        self.is_submitting = False  # Flag to prevent auto-save during submit
        
        # UI components
        self.timer_label = None
        self.progress_label = None
        self.question_frame = None
        self.prev_button = None
        self.next_button = None
        self.submit_button = None
        
        # Room data
        self.joined_rooms_data = []
        self.available_rooms_data = []
    
    def show_room_lobby(self, full_name):
        """Show room lobby where student can join a test room"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top bar with welcome and logout
        top_bar = ctk.CTkFrame(main_frame)
        top_bar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            top_bar,
            text=f"👋 Welcome, {full_name}!",
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            top_bar,
            text="🚪 Logout",
            command=self._handle_logout,
            width=100,
            height=35,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="right", padx=10)
        
        # Create two-column layout
        columns_frame = ctk.CTkFrame(main_frame)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left column: Available Rooms
        left_frame = ctk.CTkFrame(columns_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        left_header = ctk.CTkFrame(left_frame)
        left_header.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            left_header,
            text="🏫 Available Rooms",
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            left_header,
            text="🔄",
            command=self._handle_refresh_available,
            width=40,
            height=30
        ).pack(side="right")
        
        # Available rooms list (scrollable with buttons)
        self.available_scroll = ctk.CTkScrollableFrame(left_frame, height=400)
        self.available_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Right column: My Joined Rooms
        right_frame = ctk.CTkFrame(columns_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        right_header = ctk.CTkFrame(right_frame)
        right_header.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            right_header,
            text="📚 My Joined Rooms",
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            right_header,
            text="🔄",
            command=self._handle_refresh_rooms,
            width=40,
            height=30
        ).pack(side="right")
        
        # Joined rooms list (scrollable with cards)
        self.joined_scroll = ctk.CTkScrollableFrame(right_frame, height=400)
        self.joined_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial update
        self._update_available_rooms()
        self._update_joined_rooms()
    
    def _update_available_rooms(self):
        """Update available rooms display"""
        # Clear existing widgets
        for widget in self.available_scroll.winfo_children():
            widget.destroy()
        
        if not self.available_rooms_data:
            ctk.CTkLabel(
                self.available_scroll,
                text="No available rooms at the moment.\nCheck back later!",
                font=("Arial", 12),
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Display each available room as a card with join button
        for room in self.available_rooms_data:
            room_card = ctk.CTkFrame(self.available_scroll)
            room_card.pack(fill="x", pady=5, padx=5)
            
            # Room info
            info_frame = ctk.CTkFrame(room_card)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            # Room name
            ctk.CTkLabel(
                info_frame,
                text=room['room_name'],
                font=("Arial", 14, "bold")
            ).pack(anchor="w")
            
            # Teacher and details
            details_text = f"👨‍🏫 {room['teacher_name']} | ⏱ {room['duration_minutes']} min | 📝 {room['num_questions']} questions"
            ctk.CTkLabel(
                info_frame,
                text=details_text,
                font=("Arial", 10),
                text_color="gray"
            ).pack(anchor="w")
            
            # Status
            status_icon = "⏳ Waiting" if room['status'] == 'waiting' else ("▶️ Active" if room['status'] == 'active' else "✅ Ended")
            status_color = "orange" if room['status'] == 'waiting' else ("green" if room['status'] == 'active' else "gray")
            ctk.CTkLabel(
                info_frame,
                text=status_icon,
                font=("Arial", 10),
                text_color=status_color
            ).pack(anchor="w")
            
            # Join button
            if room['status'] in ['waiting', 'active']:
                ctk.CTkButton(
                    room_card,
                    text="Join",
                    command=lambda r=room: self._handle_join_room_by_id(r['id']),
                    width=80,
                    height=60,
                    fg_color="green",
                    hover_color="darkgreen"
                ).pack(side="right", padx=10, pady=10)
            else:
                ctk.CTkLabel(
                    room_card,
                    text="Ended",
                    text_color="gray",
                    width=80
                ).pack(side="right", padx=10, pady=10)
    
    def _update_joined_rooms(self):
        """Update joined rooms display"""
        # Clear existing widgets
        for widget in self.joined_scroll.winfo_children():
            widget.destroy()
        
        if not self.joined_rooms_data:
            ctk.CTkLabel(
                self.joined_scroll,
                text="No rooms joined yet.\nJoin a room from the left!",
                font=("Arial", 12),
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Display each joined room as a card with action button
        for room in self.joined_rooms_data:
            room_card = ctk.CTkFrame(self.joined_scroll)
            room_card.pack(fill="x", pady=5, padx=5)
            
            # Room info
            info_frame = ctk.CTkFrame(room_card)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            # Room name
            ctk.CTkLabel(
                info_frame,
                text=room['room_name'],
                font=("Arial", 14, "bold")
            ).pack(anchor="w")
            
            # Teacher and details
            details_text = f"👨‍🏫 {room['teacher_name']} | ⏱ {room['duration_minutes']} min"
            ctk.CTkLabel(
                info_frame,
                text=details_text,
                font=("Arial", 10),
                text_color="gray"
            ).pack(anchor="w")
            
            # Status
            status_icon = "⏳ Waiting" if room['room_status'] == 'waiting' else ("▶️ Active" if room['room_status'] == 'active' else "✅ Ended")
            status_color = "orange" if room['room_status'] == 'waiting' else ("green" if room['room_status'] == 'active' else "gray")
            ctk.CTkLabel(
                info_frame,
                text=status_icon,
                font=("Arial", 10, "bold"),
                text_color=status_color
            ).pack(anchor="w")
            
            # Action button based on status
            participant_status = room.get('participant_status', 'joined')
            
            if participant_status == 'submitted':
                # Student already completed this test
                ctk.CTkLabel(
                    room_card,
                    text="✅\nCompleted",
                    text_color="green",
                    font=("Arial", 11, "bold"),
                    width=80
                ).pack(side="right", padx=10, pady=10)
            elif room['room_status'] == 'waiting':
                ctk.CTkLabel(
                    room_card,
                    text="Waiting\nfor teacher",
                    text_color="gray",
                    font=("Arial", 9),
                    width=80
                ).pack(side="right", padx=10, pady=10)
            elif room['room_status'] == 'active':
                ctk.CTkButton(
                    room_card,
                    text="Enter\nTest",
                    command=lambda r=room: self._handle_enter_room(r['id']),
                    width=80,
                    height=60,
                    fg_color="green",
                    hover_color="darkgreen",
                    font=("Arial", 12, "bold")
                ).pack(side="right", padx=10, pady=10)
            else:  # ended
                ctk.CTkLabel(
                    room_card,
                    text="Test\nEnded",
                    text_color="gray",
                    font=("Arial", 11),
                    width=80
                ).pack(side="right", padx=10, pady=10)
    
    def update_available_rooms(self, rooms):
        """Update available rooms data and refresh display"""
        self.available_rooms_data = rooms
        if hasattr(self, 'available_scroll'):
            self._update_available_rooms()
    
    def update_joined_rooms(self, rooms):
        """Update joined rooms data and refresh display"""
        self.joined_rooms_data = rooms
        if hasattr(self, 'joined_scroll'):
            self._update_joined_rooms()
    
    def _handle_join_room_by_id(self, room_id):
        """Handle join room by room ID"""
        if self.callbacks.get('on_join_room'):
            self.callbacks['on_join_room'](room_id)
    
    def _handle_refresh_rooms(self):
        """Handle refresh joined rooms button"""
        if self.callbacks.get('on_refresh_rooms'):
            self.callbacks['on_refresh_rooms']()
    
    def _handle_refresh_available(self):
        """Handle refresh available rooms button"""
        if self.callbacks.get('on_refresh_available'):
            self.callbacks['on_refresh_available']()
    
    def _handle_enter_room(self, room_id):
        """Handle enter room to take test"""
        if self.callbacks.get('on_enter_room'):
            self.callbacks['on_enter_room'](room_id)
    
    def _handle_view_results(self, room_id):
        """Handle view results for completed test"""
        from tkinter import messagebox
        messagebox.showinfo("Results", "View results feature coming soon!")
    
    def _handle_logout(self):
        """Handle logout button"""
        if self.callbacks.get('on_logout'):
            self.callbacks['on_logout']()
    
    def _handle_back_to_lobby(self):
        """Handle back to lobby after test completion"""
        if self.callbacks.get('on_back_to_lobby'):
            self.callbacks['on_back_to_lobby']()
       
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
    
    def show_test_screen(self, questions, duration, room_id=None, cached_data=None, server_timestamp=None):
        """Show test screen with questions"""
        self.questions = questions
        self.test_duration = duration
        self.room_id = room_id
        self.server_timestamp = server_timestamp  # Store server timestamp
        
        # Check if resuming from cache
        if cached_data:
            cached_answers = cached_data.get('answers', [])
            
            # Rebuild answers array to match question order
            # Map cached answers by question_id
            cached_map = {a['question_id']: a['selected'] for a in cached_answers}
            
            # Create new answers array matching question order
            self.answers = []
            for q in questions:
                question_id = q['id']
                # Use cached value if exists, otherwise -1 (not answered)
                selected = cached_map.get(question_id, -1)
                self.answers.append({"question_id": question_id, "selected": selected})
            
            # Restore current question
            self.current_question = cached_data.get('current_question', 0)
            # Clamp to valid range
            if self.current_question >= len(questions):
                self.current_question = len(questions) - 1
            
            # Restore start time (to calculate remaining time correctly)
            cached_timestamp = cached_data.get('timestamp')
            if cached_timestamp:
                cached_time = datetime.fromisoformat(cached_timestamp)
                cached_unix = cached_time.timestamp()  # Convert to UNIX
                
                # Calculate elapsed time using synced time
                import time
                if server_timestamp:
                    # Use server time
                    current_unix = server_timestamp
                    self.time_offset = server_timestamp - time.time()
                else:
                    # Fallback to local time
                    current_unix = time.time()
                    self.time_offset = 0
                
                elapsed_from_cache = current_unix - cached_unix
                self.start_time = current_unix - elapsed_from_cache
                
                answered_count = len([a for a in self.answers if a.get('selected', -1) != -1])
                print(f"[RESUME] Restored {answered_count}/{len(questions)} answers")
                print(f"[RESUME] Current question: {self.current_question + 1}")
                print(f"[RESUME] Elapsed time: {elapsed_from_cache:.1f}s")
            else:
                # Fresh start with server time
                import time
                if server_timestamp:
                    self.start_time = server_timestamp
                    self.time_offset = server_timestamp - time.time()
                else:
                    self.start_time = time.time()
                    self.time_offset = 0
        else:
            # Fresh start
            self.answers = [{"question_id": q["id"], "selected": -1} for q in questions]
            self.current_question = 0
            
            # Initialize with server timestamp (synced time)
            import time
            if server_timestamp:
                self.start_time = server_timestamp  # Use server's time
                self.time_offset = server_timestamp - time.time()  # Calculate offset
            else:
                # Fallback to local time if server timestamp not available
                self.start_time = time.time()
                self.time_offset = 0
        
        self.timer_running = True
        self.auto_save_running = True
        
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
        
        # Start auto-save
        self._start_auto_save()
    
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
        
        # Save to local cache immediately (don't wait for auto-save)
        try:
            self._save_local_cache()
        except Exception as e:
            print(f"⚠️ Failed to save cache on answer change: {e}")
        
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
        """Update timer display (recursive with after) - Uses server-synced time"""
        if not self.timer_running:
            return
        
        # Get current time synced with server
        import time
        current_unix = time.time() + getattr(self, 'time_offset', 0)
        
        # Calculate elapsed and remaining time
        elapsed_seconds = current_unix - self.start_time
        remaining_seconds = (self.test_duration * 60) - elapsed_seconds
        
        if remaining_seconds <= 0:
            self.timer_running = False
            self.timer_label.configure(text="Time's Up!", text_color="red")
            self._handle_submit()
            return
        
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
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
        # Set submitting flag to prevent auto-save
        self.is_submitting = True
        
        # Stop timers first
        self.timer_running = False
        self.auto_save_running = False
        
        # Cancel any pending auto-save task
        if self.auto_save_task_id:
            try:
                self.parent.after_cancel(self.auto_save_task_id)
                self.auto_save_task_id = None
                print("[SUBMIT] Cancelled pending auto-save task")
            except:
                pass
        
        # Wait for any ongoing auto-save to complete
        import time
        max_wait = 3.0  # Max 3 seconds
        waited = 0
        check_interval = 0.1
        
        # Check if handler has auto_save_in_progress flag
        handler = self.callbacks.get('_student_handler')
        if handler:
            while waited < max_wait:
                if not handler.auto_save_in_progress:
                    break
                print(f"[SUBMIT] Waiting for auto-save... ({waited:.1f}s)")
                time.sleep(check_interval)
                waited += check_interval
            
            if handler.auto_save_in_progress:
                print("⚠️ [SUBMIT] Auto-save still in progress after 3s, proceeding anyway")
        else:
            # Fallback: just wait a bit
            time.sleep(0.5)
        
        # Now submit
        if self.callbacks.get('on_submit_test'):
            self.callbacks['on_submit_test'](self.answers)
    
    def _start_auto_save(self):
        """Start periodic auto-save"""
        if not self.room_id:
            return  # Only auto-save for room tests
        
        self.auto_save_running = True
        self._auto_save_task()
    
    def _auto_save_task(self):
        """Auto-save answers every 30s"""
        # Don't auto-save if already stopped or submitting
        if not self.auto_save_running or not self.timer_running or self.is_submitting:
            return
        
        # Don't auto-save in last 10 seconds (to avoid conflict with submit)
        if self.start_time:
            import time
            current_unix = time.time() + getattr(self, 'time_offset', 0)
            elapsed_seconds = current_unix - self.start_time
            remaining_seconds = (self.test_duration * 60) - elapsed_seconds
            if remaining_seconds < 10:
                print("[AUTO-SAVE] Skipped (less than 10s remaining, avoiding submit conflict)")
                return
        
        try:
            # Save to local cache first (always succeed)
            self._save_local_cache()
            
            answered = len([a for a in self.answers if a.get('selected', -1) != -1])
            print(f"[CACHE] Saved {answered}/{len(self.answers)} answers to local cache")
            
            # Try save to server (may fail if server down)
            if self.callbacks.get('on_auto_save'):
                try:
                    self.callbacks['on_auto_save'](
                        room_id=self.room_id,
                        answers=self.answers,
                        is_final=False
                    )
                    print("[AUTO-SAVE] Server acknowledged")
                except Exception as e:
                    print(f"⚠️ Server auto-save failed (server down?): {e}")
                    # Don't crash - local cache is still safe!
            
            import time
            self.last_save_time = time.time()
            
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
            # Don't crash auto-save loop
        
        # Schedule next save
        if self.auto_save_running:
            self.auto_save_task_id = self.parent.after(
                self.auto_save_interval * 1000, 
                self._auto_save_task
            )
    
    def _save_local_cache(self):
        """Save answers to local file (backup)"""
        if not self.room_id:
            return
        
        import json
        import os
        
        import time
        cache_data = {
            'room_id': self.room_id,
            'answers': self.answers,
            'timestamp': datetime.fromtimestamp(time.time()).isoformat(),
            'questions_count': len(self.questions),
            'current_question': self.current_question
        }
        
        cache_dir = 'cache'
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f'test_{self.room_id}.json')
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"[CACHE] Saved to {cache_file}")
    
    def clear_local_cache(self):
        """Clear local cache after successful submit"""
        if not self.room_id:
            return
        
        import os
        
        cache_file = os.path.join('cache', f'test_{self.room_id}.json')
        
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"[CACHE] Cleared {cache_file}")
        except Exception as e:
            print(f"⚠️ Failed to clear cache: {e}")
    
    def show_result_screen(self, result, full_name):
        """Show test result"""
        # Clear local cache (submit successful)
        self.clear_local_cache()
        
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
            text="← Back to Lobby",
            command=self._handle_back_to_lobby,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="blue",
            hover_color="darkblue"
        ).pack(pady=20)

