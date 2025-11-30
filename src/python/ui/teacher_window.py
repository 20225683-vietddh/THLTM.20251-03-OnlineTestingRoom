"""
Teacher Window UI Component
Displays dashboard with all student results and room management
"""
import customtkinter as ctk
from tkinter import messagebox

class TeacherWindow:
    """Teacher dashboard UI component"""
    
    def __init__(self, parent, callbacks):
        """
        Initialize teacher window
        
        Args:
            parent: Parent frame to pack widgets into
            callbacks: Dict with callback functions
                - on_logout: callback()
                - on_create_room: callback(room_name, num_questions, duration)
                - on_start_room: callback(room_id)
                - on_end_room: callback(room_id)
                - on_refresh_rooms: callback()
        """
        self.parent = parent
        self.callbacks = callbacks
        self.frame = None
        self.rooms_data = []
        
    def show_dashboard(self, full_name, results, rooms=None):
        """
        Show teacher dashboard with results and room management
        
        Args:
            full_name: Teacher's full name
            results: List of test results
            rooms: List of test rooms (optional)
        """
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.rooms_data = rooms or []
        
        dashboard_frame = ctk.CTkFrame(self.parent)
        dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(dashboard_frame)
        header_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text=f"👨‍🏫 Teacher Dashboard",
            font=("Arial", 22, "bold")
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            header_frame,
            text=f"Welcome, {full_name}!",
            font=("Arial", 14)
        ).pack(side="left", padx=10)
        
        # Logout button
        ctk.CTkButton(
            header_frame,
            text="Logout",
            command=self._handle_logout,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="right", padx=20)
        
        # Statistics Frame
        stats_frame = ctk.CTkFrame(dashboard_frame)
        stats_frame.pack(fill="x", pady=10, padx=10)
        
        self._show_statistics(stats_frame, results)
        
        # Tabview for Results and Rooms
        tabview = ctk.CTkTabview(dashboard_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results Tab
        results_tab = tabview.add("📊 Test Results")
        self._show_results_tab(results_tab, results)
        
        # Rooms Tab
        rooms_tab = tabview.add("🏫 Test Rooms")
        self._show_rooms_tab(rooms_tab)
        
        # Questions Tab
        questions_tab = tabview.add("📝 Manage Questions")
        self._show_questions_tab(questions_tab)
    
    def _show_results_tab(self, parent, results):
        """Show results in tab"""
        # Results table
        results_text = ctk.CTkTextbox(parent, font=("Courier New", 11))
        results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        results_text.insert("end", 
            f"{'Student Name':<25} {'Username':<15} {'Score':<10} {'Percentage':<12} {'Date':<20}\n"
        )
        results_text.insert("end", "=" * 90 + "\n")
        
        # Results data
        if results:
            for r in results:
                results_text.insert("end",
                    f"{r['full_name']:<25} "
                    f"{r['username']:<15} "
                    f"{r['score']}/{r['total_questions']:<7} "
                    f"{r['percentage']:<11.2f}% "
                    f"{r['test_date']:<20}\n"
                )
        else:
            results_text.insert("end", "\nNo test results yet.\n")
        
        results_text.configure(state="disabled")
    
    def _show_rooms_tab(self, parent):
        """Show room management tab"""
        # Create Room Section
        create_frame = ctk.CTkFrame(parent)
        create_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            create_frame,
            text="➕ Create New Test Room",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Input form
        form_frame = ctk.CTkFrame(create_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Room name
        ctk.CTkLabel(form_frame, text="Room Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.room_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Enter room name...")
        self.room_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Number of questions
        ctk.CTkLabel(form_frame, text="Number of Questions:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.num_questions_entry = ctk.CTkEntry(form_frame, width=150, placeholder_text="10")
        self.num_questions_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.num_questions_entry.insert(0, "10")
        
        # Duration
        ctk.CTkLabel(form_frame, text="Duration (minutes):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.duration_entry = ctk.CTkEntry(form_frame, width=150, placeholder_text="30")
        self.duration_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.duration_entry.insert(0, "30")
        
        # Create button
        ctk.CTkButton(
            form_frame,
            text="Create Room",
            command=self._handle_create_room,
            fg_color="green",
            hover_color="darkgreen"
        ).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Rooms List Section
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text="📋 My Test Rooms",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self._handle_refresh_rooms,
            width=100
        ).pack(side="right", padx=10)
        
        # Rooms table
        self.rooms_text = ctk.CTkTextbox(list_frame, font=("Courier New", 10))
        self.rooms_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ctk.CTkFrame(list_frame)
        control_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(
            control_frame,
            text="🎮 Room Control:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(control_frame, text="Room Code:").pack(side="left", padx=5)
        self.control_room_code_entry = ctk.CTkEntry(control_frame, width=100, placeholder_text="ABC123")
        self.control_room_code_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="▶️ Start Test",
            command=self._handle_start_test,
            fg_color="#00AA00",
            hover_color="#008800",
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="⏹️ End Test",
            command=self._handle_end_test,
            fg_color="#CC0000",
            hover_color="#AA0000",
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        self._update_rooms_list()
    
    def _update_rooms_list(self):
        """Update rooms list display with timestamps"""
        self.rooms_text.configure(state="normal")
        self.rooms_text.delete("1.0", "end")
        
        # Header with better formatting
        self.rooms_text.insert("end",
            f"{'Room Name':<25} {'Code':<8} {'Q#':<4} {'Mins':<5} {'Status':<10} {'👥':<4} {'⏰ Timeline':<40}\n"
        )
        self.rooms_text.insert("end", "=" * 110 + "\n")
        
        # Rooms data
        if self.rooms_data:
            for room in self.rooms_data:
                # Status with icon
                if room['status'] == 'waiting':
                    status_display = "⏳ Waiting"
                elif room['status'] == 'active':
                    status_display = "▶️ Active"
                else:
                    status_display = "✅ Ended"
                
                # Format timestamps
                timeline = self._format_timeline(room)
                
                self.rooms_text.insert("end",
                    f"{room['room_name']:<25} "
                    f"{room['room_code']:<8} "
                    f"{room['num_questions']:<4} "
                    f"{room['duration_minutes']:<5} "
                    f"{status_display:<10} "
                    f"{room.get('participant_count', 0):<4} "
                    f"{timeline:<40}\n"
                )
        else:
            self.rooms_text.insert("end", "\nNo rooms created yet. Create your first room above!\n")
        
        self.rooms_text.configure(state="disabled")
    
    def _format_timeline(self, room):
        """Format start/end time for display"""
        from datetime import datetime
        
        start_time = room.get('start_time')
        end_time = room.get('end_time')
        created_at = room.get('created_at')
        
        if room['status'] == 'waiting':
            # Show created time
            if created_at:
                try:
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at)
                    else:
                        dt = created_at
                    return f"Created: {dt.strftime('%m/%d %H:%M')}"
                except:
                    return "Not started yet"
            return "Not started yet"
            
        elif room['status'] == 'active':
            # Show start time
            if start_time:
                try:
                    if isinstance(start_time, str):
                        dt = datetime.fromisoformat(start_time)
                    else:
                        dt = start_time
                    return f"Started: {dt.strftime('%m/%d %H:%M')}"
                except:
                    return "Active (no timestamp)"
            return "Active (no timestamp)"
            
        else:  # ended
            # Show start and end time
            timeline_parts = []
            if start_time:
                try:
                    if isinstance(start_time, str):
                        dt = datetime.fromisoformat(start_time)
                    else:
                        dt = start_time
                    timeline_parts.append(f"Start: {dt.strftime('%H:%M')}")
                except:
                    pass
            
            if end_time:
                try:
                    if isinstance(end_time, str):
                        dt = datetime.fromisoformat(end_time)
                    else:
                        dt = end_time
                    timeline_parts.append(f"End: {dt.strftime('%H:%M')}")
                except:
                    pass
            
            if timeline_parts:
                return " → ".join(timeline_parts)
            return "Ended (no timestamp)"
    
    def update_rooms(self, rooms):
        """Update rooms data and refresh display"""
        self.rooms_data = rooms
        if hasattr(self, 'rooms_text'):
            self._update_rooms_list()
        
        # Update room dropdown in Questions tab
        if hasattr(self, 'room_dropdown'):
            self._update_room_dropdown()
    
    def _handle_create_room(self):
        """Handle create room button"""
        room_name = self.room_name_entry.get().strip()
        
        try:
            num_questions = int(self.num_questions_entry.get())
            duration = int(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for questions and duration")
            return
        
        if not room_name:
            messagebox.showerror("Invalid Input", "Please enter a room name")
            return
        
        if num_questions < 1 or num_questions > 50:
            messagebox.showerror("Invalid Input", "Number of questions must be between 1 and 50")
            return
        
        if duration < 5 or duration > 180:
            messagebox.showerror("Invalid Input", "Duration must be between 5 and 180 minutes")
            return
        
        if self.callbacks.get('on_create_room'):
            self.callbacks['on_create_room'](room_name, num_questions, duration)
    
    def _handle_refresh_rooms(self):
        """Handle refresh rooms button"""
        if self.callbacks.get('on_refresh_rooms'):
            self.callbacks['on_refresh_rooms']()
    
    def show_room_created(self, room_code):
        """Show room created success message"""
        messagebox.showinfo(
            "Room Created Successfully! ✅",
            f"Test room created!\n\n"
            f"📋 Room Code: {room_code}\n\n"
            f"Next steps:\n"
            f"1. Go to 'Manage Questions' tab\n"
            f"2. Click '🔄 Refresh Rooms'\n"
            f"3. Select your room and add questions\n"
            f"4. Share code '{room_code}' with students"
        )
        # Clear form
        self.room_name_entry.delete(0, "end")
        self.num_questions_entry.delete(0, "end")
        self.num_questions_entry.insert(0, "10")
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, "30")
    
    def _show_statistics(self, parent, results):
        """Show statistics summary"""
        if not results:
            ctk.CTkLabel(
                parent,
                text="No data available yet",
                font=("Arial", 12)
            ).pack(pady=10)
            return
        
        # Calculate statistics
        total_attempts = len(results)
        avg_score = sum(r['percentage'] for r in results) / total_attempts
        max_score = max(r['percentage'] for r in results)
        min_score = min(r['percentage'] for r in results)
        
        # Display in grid
        stats_data = [
            ("Total Attempts", f"{total_attempts}"),
            ("Average Score", f"{avg_score:.2f}%"),
            ("Highest Score", f"{max_score:.2f}%"),
            ("Lowest Score", f"{min_score:.2f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            stat_frame = ctk.CTkFrame(parent)
            stat_frame.grid(row=0, column=i, padx=10, pady=10)
            
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 11)
            ).pack(pady=2)
            
            ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Arial", 18, "bold"),
                text_color="green"
            ).pack(pady=2)
    
    def _show_questions_tab(self, parent):
        """Show question management tab with scrollbar"""
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Room selection
        select_frame = ctk.CTkFrame(scrollable_frame)
        select_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            select_frame,
            text="📝 Manage Questions for Room",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Room dropdown
        room_select_frame = ctk.CTkFrame(select_frame)
        room_select_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(room_select_frame, text="Select Room:").pack(side="left", padx=10)
        
        self.room_codes = [f"{r['room_name']} ({r['room_code']})" for r in self.rooms_data] if self.rooms_data else ["No rooms"]
        self.selected_room_var = ctk.StringVar(value=self.room_codes[0] if self.room_codes else "No rooms")
        
        self.room_dropdown = ctk.CTkOptionMenu(
            room_select_frame,
            variable=self.selected_room_var,
            values=self.room_codes,
            command=self._on_room_selected,
            width=300
        )
        self.room_dropdown.pack(side="left", padx=10)
        
        ctk.CTkButton(
            room_select_frame,
            text="🔄 Refresh",
            command=self._refresh_room_dropdown,
            width=100,
            height=35
        ).pack(side="left", padx=5)
        
        # Question list - IMPROVED with better styling
        list_frame = ctk.CTkFrame(scrollable_frame)
        list_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        questions_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        questions_header.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(
            questions_header,
            text="📋 Questions List",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)
        
        self.question_count_label = ctk.CTkLabel(
            questions_header,
            text="(0 questions)",
            font=("Arial", 12, "bold"),
            text_color="#00AA00"
        )
        self.question_count_label.pack(side="left", padx=5)
        
        # Hint label
        ctk.CTkLabel(
            questions_header,
            text="💡 Questions auto-load when you select a room",
            font=("Arial", 9, "italic"),
            text_color="#0066CC"
        ).pack(side="right", padx=10)
        
        self.questions_text = ctk.CTkTextbox(
            list_frame, 
            font=("Consolas", 10),
            height=250,
            wrap="word"
        )
        self.questions_text.pack(fill="x", padx=5, pady=5)
        
        # Add question section - IMPROVED COMPACT LAYOUT
        add_frame = ctk.CTkFrame(scrollable_frame, border_width=2, border_color="#00AA00")
        add_frame.pack(fill="x", padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text="➕ Add New Question",
            font=("Arial", 14, "bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="🗑️ Clear Form",
            command=self._clear_question_form,
            fg_color="gray",
            hover_color="darkgray",
            width=100,
            height=28
        ).pack(side="right", padx=5)
        
        form_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=10)
        
        # Question text - Full width with better styling
        q_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        q_frame.pack(fill="x", padx=5, pady=8)
        
        ctk.CTkLabel(
            q_frame, 
            text="❓ Question:", 
            font=("Arial", 12, "bold"),
            text_color="#0066CC",
            width=100
        ).pack(side="left", padx=5)
        self.question_entry = ctk.CTkEntry(
            q_frame, 
            placeholder_text="Type your question here...",
            height=38,
            font=("Arial", 11),
            border_width=2
        )
        self.question_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Options label
        ctk.CTkLabel(
            form_frame,
            text="📝 Answer Options:",
            font=("Arial", 12, "bold"),
            text_color="#0066CC"
        ).pack(anchor="w", padx=10, pady=(8, 5))
        
        # Options in 2x2 grid - More compact with better styling
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=5, pady=5)
        
        # Row 1: A and B
        row1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row1.pack(fill="x", pady=3)
        
        ctk.CTkLabel(row1, text="A)", font=("Arial", 11, "bold"), width=35, text_color="#00AA00").pack(side="left", padx=5)
        self.option_a_entry = ctk.CTkEntry(row1, placeholder_text="First option", height=35, font=("Arial", 10))
        self.option_a_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(row1, text="B)", font=("Arial", 11, "bold"), width=35, text_color="#00AA00").pack(side="left", padx=5)
        self.option_b_entry = ctk.CTkEntry(row1, placeholder_text="Second option", height=35, font=("Arial", 10))
        self.option_b_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Row 2: C and D
        row2 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row2.pack(fill="x", pady=3)
        
        ctk.CTkLabel(row2, text="C)", font=("Arial", 11, "bold"), width=35, text_color="#00AA00").pack(side="left", padx=5)
        self.option_c_entry = ctk.CTkEntry(row2, placeholder_text="Third option", height=35, font=("Arial", 10))
        self.option_c_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(row2, text="D)", font=("Arial", 11, "bold"), width=35, text_color="#00AA00").pack(side="left", padx=5)
        self.option_d_entry = ctk.CTkEntry(row2, placeholder_text="Fourth option", height=35, font=("Arial", 10))
        self.option_d_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Separator
        ctk.CTkLabel(form_frame, text="", height=5).pack()
        
        # Bottom row: Correct answer + Add button
        bottom_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=5, pady=12)
        
        # Left side: Correct answer
        left_side = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        left_side.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            left_side, 
            text="✓ Correct Answer:", 
            font=("Arial", 12, "bold"),
            text_color="#FF6600"
        ).pack(side="left", padx=5)
        
        self.correct_answer_var = ctk.StringVar(value="A")
        ctk.CTkOptionMenu(
            left_side,
            variable=self.correct_answer_var,
            values=["A", "B", "C", "D"],
            width=90,
            height=38,
            font=("Arial", 13, "bold"),
            fg_color="#FF6600",
            button_color="#FF8800",
            button_hover_color="#FF5500"
        ).pack(side="left", padx=10)
        
        # Right side: Big Add button
        ctk.CTkButton(
            bottom_frame,
            text="✚  ADD QUESTION",
            command=self._handle_add_question,
            fg_color="#00AA00",
            hover_color="#008800",
            width=220,
            height=45,
            font=("Arial", 13, "bold"),
            corner_radius=10
        ).pack(side="right", padx=15)
        
        self.current_room_id = None
        self.questions_data = []
    
    def _update_room_dropdown(self):
        """Update room dropdown options"""
        if self.rooms_data:
            self.room_codes = [f"{r['room_name']} ({r['room_code']})" for r in self.rooms_data]
            self.room_dropdown.configure(values=self.room_codes)
            if self.room_codes:
                self.selected_room_var.set(self.room_codes[0])
        else:
            self.room_codes = ["No rooms"]
            self.room_dropdown.configure(values=self.room_codes)
            self.selected_room_var.set("No rooms")
    
    def _refresh_room_dropdown(self):
        """Refresh room list and update dropdown"""
        if self.callbacks.get('on_refresh_rooms'):
            self.callbacks['on_refresh_rooms']()
        # Dropdown will be updated via update_rooms() callback
    
    def _on_room_selected(self, choice):
        """Called when room selection changes"""
        # Auto-set current_room_id when room is selected
        if choice and choice != "No rooms" and '(' in choice and ')' in choice:
            room_code = choice.split('(')[1].split(')')[0]
            
            # Find room by code
            for room in self.rooms_data:
                if room['room_code'] == room_code:
                    self.current_room_id = room['id']
                    print(f"[DEBUG] Room selected: {room['room_name']} (ID: {self.current_room_id})")
                    # Auto-load questions
                    if self.callbacks.get('on_load_questions'):
                        self.callbacks['on_load_questions'](room['id'])
                    break
        else:
            self.current_room_id = None
    
    def _load_questions(self):
        """Load questions for selected room"""
        if not self.rooms_data or self.selected_room_var.get() == "No rooms":
            return
        
        # Extract room code from selection (format: "Room Name (CODE)")
        selected = self.selected_room_var.get()
        if '(' in selected and ')' in selected:
            room_code = selected.split('(')[1].split(')')[0]
            
            # Find room by code
            for room in self.rooms_data:
                if room['room_code'] == room_code:
                    self.current_room_id = room['id']
                    
                    # Call callback to load questions
                    if self.callbacks.get('on_load_questions'):
                        self.callbacks['on_load_questions'](room['id'])
                    break
    
    def _handle_add_question(self):
        """Handle add question button"""
        if not self.current_room_id:
            from tkinter import messagebox
            messagebox.showwarning("No Room Selected", "Please select a room first!")
            return
        
        question_text = self.question_entry.get().strip()
        option_a = self.option_a_entry.get().strip()
        option_b = self.option_b_entry.get().strip()
        option_c = self.option_c_entry.get().strip()
        option_d = self.option_d_entry.get().strip()
        correct_answer = self.correct_answer_var.get()
        
        # Validate
        if not question_text:
            from tkinter import messagebox
            messagebox.showwarning("Invalid Input", "Question text cannot be empty!")
            return
        
        if not all([option_a, option_b, option_c, option_d]):
            from tkinter import messagebox
            messagebox.showwarning("Invalid Input", "All options must be filled!")
            return
        
        # Convert correct answer letter to number (A=0, B=1, C=2, D=3)
        correct_answer_num = ord(correct_answer) - ord('A')
        
        # Call callback
        if self.callbacks.get('on_add_question'):
            self.callbacks['on_add_question'](
                self.current_room_id,
                question_text,
                option_a, option_b, option_c, option_d,
                correct_answer_num
            )
    
    def _clear_question_form(self):
        """Clear question form"""
        self.question_entry.delete(0, 'end')
        self.option_a_entry.delete(0, 'end')
        self.option_b_entry.delete(0, 'end')
        self.option_c_entry.delete(0, 'end')
        self.option_d_entry.delete(0, 'end')
        self.correct_answer_var.set("A")
    
    def update_questions(self, questions):
        """Update questions display"""
        self.questions_data = questions
        
        # Update count label
        if hasattr(self, 'question_count_label'):
            count = len(questions) if questions else 0
            self.question_count_label.configure(text=f"({count} question{'s' if count != 1 else ''})")
        
        if hasattr(self, 'questions_text'):
            self.questions_text.configure(state="normal")
            self.questions_text.delete("1.0", "end")
            
            if questions:
                for i, q in enumerate(questions, 1):
                    correct_letter = chr(ord('A') + q['correct_answer'])
                    self.questions_text.insert("end", 
                        f"Q{i}. {q['question_text']}\n"
                        f"   A) {q['option_a']}\n"
                        f"   B) {q['option_b']}\n"
                        f"   C) {q['option_c']}\n"
                        f"   D) {q['option_d']}\n"
                        f"   ✓ Correct: {correct_letter}\n\n"
                    )
            else:
                self.questions_text.insert("end", "\nNo questions added yet. Add your first question below!\n")
            
            self.questions_text.configure(state="disabled")
    
    def _handle_start_test(self):
        """Handle start test button"""
        room_code = self.control_room_code_entry.get().strip()
        
        if not room_code:
            from tkinter import messagebox
            messagebox.showwarning("No Room Code", "Please enter a room code!")
            return
        
        # Find room by code
        room_id = None
        for room in self.rooms_data:
            if room['room_code'] == room_code:
                room_id = room['id']
                
                if room['status'] != 'waiting':
                    messagebox.showwarning(
                        "Invalid Status",
                        f"Room is already {room['status']}!\nCan only start rooms in 'waiting' status."
                    )
                    return
                break
        
        if not room_id:
            from tkinter import messagebox
            messagebox.showerror("Room Not Found", f"No room with code '{room_code}' found!")
            return
        
        # Call callback
        if self.callbacks.get('on_start_room'):
            self.callbacks['on_start_room'](room_id)
    
    def _handle_end_test(self):
        """Handle end test button"""
        room_code = self.control_room_code_entry.get().strip()
        
        if not room_code:
            from tkinter import messagebox
            messagebox.showwarning("No Room Code", "Please enter a room code!")
            return
        
        # Find room by code
        room_id = None
        for room in self.rooms_data:
            if room['room_code'] == room_code:
                room_id = room['id']
                
                if room['status'] != 'active':
                    messagebox.showwarning(
                        "Invalid Status",
                        f"Room is {room['status']}!\nCan only end rooms that are 'active'."
                    )
                    return
                break
        
        if not room_id:
            from tkinter import messagebox
            messagebox.showerror("Room Not Found", f"No room with code '{room_code}' found!")
            return
        
        # Call callback
        if self.callbacks.get('on_end_room'):
            self.callbacks['on_end_room'](room_id)
    
    def _handle_logout(self):
        """Handle logout button"""
        if self.callbacks.get('on_logout'):
            self.callbacks['on_logout']()

