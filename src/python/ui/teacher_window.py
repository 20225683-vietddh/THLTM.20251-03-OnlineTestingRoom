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
        
        self._update_rooms_list()
    
    def _update_rooms_list(self):
        """Update rooms list display"""
        self.rooms_text.configure(state="normal")
        self.rooms_text.delete("1.0", "end")
        
        # Header
        self.rooms_text.insert("end",
            f"{'Room Name':<25} {'Code':<8} {'Questions':<10} {'Duration':<10} {'Status':<10} {'Students':<10}\n"
        )
        self.rooms_text.insert("end", "=" * 85 + "\n")
        
        # Rooms data
        if self.rooms_data:
            for room in self.rooms_data:
                status_icon = "⏳" if room['status'] == 'waiting' else ("▶️" if room['status'] == 'active' else "✅")
                self.rooms_text.insert("end",
                    f"{room['room_name']:<25} "
                    f"{room['room_code']:<8} "
                    f"{room['num_questions']:<10} "
                    f"{room['duration_minutes']}min{'':<5} "
                    f"{status_icon} {room['status']:<8} "
                    f"{room.get('participant_count', 0):<10}\n"
                )
        else:
            self.rooms_text.insert("end", "\nNo rooms created yet. Create your first room above!\n")
        
        self.rooms_text.configure(state="disabled")
    
    def update_rooms(self, rooms):
        """Update rooms data and refresh display"""
        self.rooms_data = rooms
        if hasattr(self, 'rooms_text'):
            self._update_rooms_list()
    
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
            "Room Created!",
            f"Test room created successfully!\n\nRoom Code: {room_code}\n\nStudents can use this code to join the room."
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
    
    def _handle_logout(self):
        """Handle logout button"""
        if self.callbacks.get('on_logout'):
            self.callbacks['on_logout']()

