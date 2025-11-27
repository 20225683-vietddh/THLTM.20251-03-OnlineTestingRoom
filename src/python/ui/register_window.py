"""
Register Window UI Component
"""
import customtkinter as ctk

class RegisterWindow:
    """Registration screen UI component"""
    
    def __init__(self, parent, callbacks):
        """
        Initialize register window
        
        Args:
            parent: Parent frame to pack widgets into
            callbacks: Dict with callback functions
                - on_register: callback(username, password, full_name, email, role)
                - on_back: callback()
        """
        self.parent = parent
        self.callbacks = callbacks
        self.frame = None
        
    def show(self):
        """Display registration window"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create main frame
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(expand=True)
        
        # Title
        ctk.CTkLabel(
            self.frame,
            text="📝 Register New Account",
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        # Role selection
        ctk.CTkLabel(
            self.frame, 
            text="I am a:", 
            font=("Arial", 14)
        ).pack(pady=5)
        
        self.role_var = ctk.StringVar(value="student")
        
        role_frame = ctk.CTkFrame(self.frame)
        role_frame.pack(pady=10)
        
        ctk.CTkRadioButton(
            role_frame,
            text="👨‍🎓 Student",
            variable=self.role_var,
            value="student",
            font=("Arial", 13)
        ).pack(side="left", padx=20)
        
        ctk.CTkRadioButton(
            role_frame,
            text="👨‍🏫 Teacher",
            variable=self.role_var,
            value="teacher",
            font=("Arial", 13)
        ).pack(side="left", padx=20)
        
        # Full name
        ctk.CTkLabel(
            self.frame, 
            text="Full Name:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.fullname_entry = ctk.CTkEntry(self.frame, width=300, height=35)
        self.fullname_entry.pack(pady=5)
        self.fullname_entry.focus()
        
        # Username
        ctk.CTkLabel(
            self.frame, 
            text="Username:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.username_entry = ctk.CTkEntry(self.frame, width=300, height=35)
        self.username_entry.pack(pady=5)
        
        # Email (optional)
        ctk.CTkLabel(
            self.frame, 
            text="Email (optional):", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.email_entry = ctk.CTkEntry(self.frame, width=300, height=35)
        self.email_entry.pack(pady=5)
        
        # Password
        ctk.CTkLabel(
            self.frame, 
            text="Password:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.password_entry = ctk.CTkEntry(self.frame, width=300, height=35, show="*")
        self.password_entry.pack(pady=5)
        
        # Confirm password
        ctk.CTkLabel(
            self.frame, 
            text="Confirm Password:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.confirm_entry = ctk.CTkEntry(self.frame, width=300, height=35, show="*")
        self.confirm_entry.pack(pady=5)
        
        # Register button
        ctk.CTkButton(
            self.frame,
            text="Register",
            command=self._handle_register,
            width=300,
            height=45,
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Back button
        ctk.CTkButton(
            self.frame,
            text="← Back",
            command=self._handle_back,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
    
    def _handle_register(self):
        """Handle register button click"""
        full_name = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_var.get()
        
        # Validate
        if not full_name or not username or not password:
            self.show_status("⚠ Please fill in required fields", "red")
            return
        
        if password != confirm:
            self.show_status("⚠ Passwords do not match", "red")
            return
        
        if self.callbacks.get('on_register'):
            self.callbacks['on_register'](username, password, full_name, email, role)
    
    def _handle_back(self):
        """Handle back button click"""
        if self.callbacks.get('on_back'):
            self.callbacks['on_back']()
    
    def show_status(self, message, color="yellow"):
        """Show status message"""
        self.status_label.configure(text=message, text_color=color)

