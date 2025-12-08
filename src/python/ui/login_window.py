"""
Login Window UI Component
"""
import customtkinter as ctk
import json

class LoginWindow:
    """Login screen UI component"""
    
    def __init__(self, parent, callbacks):
        """
        Initialize login window
        
        Args:
            parent: Parent frame to pack widgets into
            callbacks: Dict with callback functions
                - on_login: callback(username, password, role)
                - on_register: callback()
                - on_status: callback(message, color)
        """
        self.parent = parent
        self.callbacks = callbacks
        self.frame = None
        
    def show(self):
        """Display login window"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create main frame
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(expand=True)
        
        # Title
        ctk.CTkLabel(
            self.frame,
            text="🔐 Login",
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        # Role selection
        ctk.CTkLabel(
            self.frame, 
            text="I am a:", 
            font=("Arial", 14)
        ).pack(pady=10)
        
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
        
        # Username
        ctk.CTkLabel(
            self.frame, 
            text="Username:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.username_entry = ctk.CTkEntry(self.frame, width=300, height=35)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        
        # Password
        ctk.CTkLabel(
            self.frame, 
            text="Password:", 
            font=("Arial", 13)
        ).pack(pady=5)
        
        self.password_entry = ctk.CTkEntry(self.frame, width=300, height=35, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        # Login button
        ctk.CTkButton(
            self.frame,
            text="Login",
            command=self._handle_login,
            width=300,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(pady=20)
        
        # Register button
        ctk.CTkButton(
            self.frame,
            text="📝 Create New Account",
            command=self._handle_register,
            width=300,
            height=35,
            font=("Arial", 13),
            fg_color="blue",
            hover_color="darkblue"
        ).pack(pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
    
    def _handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            self.show_status("⚠ Please fill in all fields", "red")
            return
        
        if self.callbacks.get('on_login'):
            self.callbacks['on_login'](username, password, role)
    
    def _handle_register(self):
        """Handle register button click"""
        if self.callbacks.get('on_register'):
            self.callbacks['on_register']()
    
    def show_status(self, message, color="yellow"):
        """Show status message"""
        self.status_label.configure(text=message, text_color=color)

