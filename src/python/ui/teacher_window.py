"""
Teacher Window UI Component
Displays dashboard with all student results
"""
import customtkinter as ctk

class TeacherWindow:
    """Teacher dashboard UI component"""
    
    def __init__(self, parent, callbacks):
        """
        Initialize teacher window
        
        Args:
            parent: Parent frame to pack widgets into
            callbacks: Dict with callback functions
                - on_logout: callback()
        """
        self.parent = parent
        self.callbacks = callbacks
        self.frame = None
        
    def show_dashboard(self, full_name, results):
        """
        Show teacher dashboard with results
        
        Args:
            full_name: Teacher's full name
            results: List of test results
        """
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
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
        
        # Results Frame
        results_title = ctk.CTkLabel(
            dashboard_frame,
            text=f"📊 All Test Results ({len(results)} attempts)",
            font=("Arial", 16, "bold")
        )
        results_title.pack(pady=10)
        
        # Results table
        results_frame = ctk.CTkFrame(dashboard_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollable textbox for results
        results_text = ctk.CTkTextbox(results_frame, font=("Courier New", 11))
        results_text.pack(fill="both", expand=True)
        
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

