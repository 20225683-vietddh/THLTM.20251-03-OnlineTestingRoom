"""
Test Client Application
Clean modular architecture matching server structure
"""
import customtkinter as ctk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui import LoginWindow, RegisterWindow, StudentWindow, TeacherWindow
from auth import AuthManager
from client.connection import ConnectionManager
from client.handlers import TeacherHandler, StudentHandler


class TestClientApp(ctk.CTk):
    """Test Client Application"""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("Test Application Client")
        self.geometry("900x600 ")
        
        # Initialize components
        self.auth = AuthManager()
        self.conn = ConnectionManager()
        self.conn.init_network()
        
        # UI state
        self.current_user = None
        self.current_role = None
        self.login_window = None
        self.register_window = None
        self.teacher_window = None
        self.student_window = None
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Show login screen
        self.show_login()
    
    def show_login(self):
        """Show login screen"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.login_window = LoginWindow(self.main_frame, {
            'on_login': self.handle_login,
            'on_register': self.show_register
        })
        self.login_window.show()
    
    def show_register(self):
        """Show register screen"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.register_window = RegisterWindow(self.main_frame, {
            'on_back': self.show_login,
            'on_register': self.handle_register
        })
        self.register_window.show()
    
    def handle_login(self, username, password, role):
        """Handle login attempt"""
        try:
            # Connect to server
            if not self.conn.connected:
                self.conn.connect()
            
            # Login
            result = self.conn.login(username, password, role)
            
            if result['success']:
                self.current_user = username
                self.current_role = result['role']
                full_name = result['full_name']
                
                # Show interface based on role
                if self.current_role == 'teacher':
                    self.show_teacher_dashboard(full_name)
                else:
                    self.show_student_test(full_name)
                    
                return True
            else:
                if self.login_window:
                    self.login_window.show_status(f"✗ {result['message']}", "red")
                return False
                
        except Exception as e:
            if self.login_window:
                self.login_window.show_status(f"✗ Error: {str(e)}", "red")
            return False
    
    def handle_register(self, username, password, role, full_name, email):
        """Handle registration (not implemented - use server's register)"""
        if self.register_window:
            self.register_window.show_status("Registration not implemented in client", "orange")
    
    def show_teacher_dashboard(self, full_name):
        """Show teacher dashboard"""
        try:
            # Clear UI
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            # Create handler first (need it for callbacks)
            self.teacher_handler = TeacherHandler(self.conn, {
                'show_dashboard': lambda fn, results, rooms: self.teacher_window.show_dashboard(fn, results, rooms)
            })
            
            # Create teacher window with callbacks
            self.teacher_window = TeacherWindow(self.main_frame, {
                'on_logout': self.handle_logout,
                'on_create_room': self.handle_create_room,
                'on_refresh_rooms': self.handle_refresh_rooms,
                'on_start_room': self.handle_start_room,
                'on_end_room': self.handle_end_room,
                'on_add_question': self.handle_add_question,
                'on_load_questions': self.handle_load_questions
            })
            
            # Update handler UI callback reference (now that teacher_window exists)
            self.teacher_handler.ui = {
                'show_dashboard': lambda fn, results, rooms: self.teacher_window.show_dashboard(fn, results, rooms)
            }
            
            # Load dashboard
            self.teacher_handler.load_dashboard(full_name)
            
        except Exception as e:
            self.show_error("Teacher Dashboard Error", str(e))
            self.show_login()
    
    def show_student_test(self, full_name):
        """Show student test"""
        try:
            # Clear UI
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            # Create student window
            self.student_window = StudentWindow(self.main_frame, {
                'on_start_test': self.handle_start_test,
                'on_submit_test': self.handle_submit_test
            })
            
            # Create handler
            self.student_handler = StudentHandler(self.conn, {
                'show_ready': lambda fn, nq, d: self.student_window.show_ready_screen(fn, nq, d),
                'show_test': lambda q, d: self.student_window.show_test_screen(q, d),
                'show_result': lambda r: self.student_window.show_result_screen(r, full_name)
            })
            
            # Load test config
            self.student_handler.load_test_config(full_name)
            
        except Exception as e:
            self.show_error("Student Test Error", str(e))
            self.show_login()
    
    def handle_start_test(self):
        """Handle start test"""
        try:
            self.student_handler.start_test()
        except Exception as e:
            self.show_error("Start Test Error", str(e))
    
    def handle_submit_test(self, answers):
        """Handle submit test"""
        try:
            self.student_handler.submit_test(answers)
        except Exception as e:
            self.show_error("Submit Test Error", str(e))
    
    def handle_create_room(self, room_name, num_questions, duration_minutes):
        """Handle create room"""
        try:
            result = self.teacher_handler.create_room(room_name, num_questions, duration_minutes)
            
            if result['success']:
                # Show success message with room code
                self.teacher_window.show_room_created(result['room_code'])
                # Refresh rooms list
                self.handle_refresh_rooms()
            else:
                self.show_error("Create Room Error", result.get('message', 'Unknown error'))
        except Exception as e:
            self.show_error("Create Room Error", str(e))
    
    def handle_refresh_rooms(self):
        """Handle refresh rooms"""
        try:
            rooms = self.teacher_handler.refresh_rooms()
            # Update UI with new rooms
            if hasattr(self.teacher_window, 'update_rooms'):
                self.teacher_window.update_rooms(rooms)
        except Exception as e:
            self.show_error("Refresh Rooms Error", str(e))
    
    def handle_start_room(self, room_id):
        """Handle start room"""
        try:
            result = self.teacher_handler.start_room(room_id)
            
            if result['success']:
                from tkinter import messagebox
                messagebox.showinfo("Success", "Test started successfully!")
                # Refresh rooms to update status
                self.handle_refresh_rooms()
            else:
                self.show_error("Start Room Error", result.get('message', 'Unknown error'))
        except Exception as e:
            self.show_error("Start Room Error", str(e))
    
    def handle_end_room(self, room_id):
        """Handle end room"""
        try:
            result = self.teacher_handler.end_room(room_id)
            
            if result['success']:
                from tkinter import messagebox
                messagebox.showinfo("Success", "Test ended successfully!")
                # Refresh rooms to update status
                self.handle_refresh_rooms()
            else:
                self.show_error("End Room Error", result.get('message', 'Unknown error'))
        except Exception as e:
            self.show_error("End Room Error", str(e))
    
    def handle_add_question(self, room_id, question_text, option_a, option_b, option_c, option_d, correct_answer):
        """Handle add question"""
        try:
            result = self.teacher_handler.add_question(
                room_id, question_text, option_a, option_b, option_c, option_d, correct_answer
            )
            
            if result['success']:
                from tkinter import messagebox
                messagebox.showinfo("Success", "Question added successfully!")
                # Clear form and reload questions
                self.teacher_window._clear_question_form()
                self.handle_load_questions(room_id)
            else:
                self.show_error("Add Question Error", result.get('message', 'Unknown error'))
        except Exception as e:
            self.show_error("Add Question Error", str(e))
    
    def handle_load_questions(self, room_id):
        """Handle load questions"""
        try:
            questions = self.teacher_handler.get_questions(room_id)
            # Update UI with questions
            if hasattr(self.teacher_window, 'update_questions'):
                self.teacher_window.update_questions(questions)
        except Exception as e:
            self.show_error("Load Questions Error", str(e))
    
    def handle_logout(self):
        """Handle logout"""
        self.conn.disconnect()
        self.current_user = None
        self.current_role = None
        self.show_login()
    
    def show_error(self, title, message):
        """Show error dialog"""
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    def on_closing(self):
        """Handle window close"""
        self.conn.cleanup()
        self.destroy()


def main():
    """Main entry point"""
    app = TestClientApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
