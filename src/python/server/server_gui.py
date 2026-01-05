"""
Server GUI Module
Provides the graphical interface for the test server
"""
import customtkinter as ctk
import threading
import ctypes
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol_wrapper import (
    ProtocolWrapper, ClientContext, ServerContext, 
    ClientHandlerFunc, socket_type
)
from auth import AuthManager, SessionManager
from database import Database
from server.handlers import RequestHandlers
from server.room_manager import RoomManager
from server.client_handler import ClientHandler


class TestServerGUI(ctk.CTk):
    """Test Application Server GUI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.proto = ProtocolWrapper()
        self.proto.init_network()
        
        self.db = Database("data/app.db")
        self.auth = AuthManager()
        self.session_mgr = SessionManager()
        
        # Server state
        self.server_socket = None
        self.server_running = False
        self.clients = {}
        self.server_context = None
        self.server_thread = None
        self.broadcast_manager = None  # Will be initialized in start_server if needed
        
        # Setup GUI FIRST (so append_log works)
        self.setup_gui()
        
        # NOW initialize handlers (they can use append_log)
        self.handlers = RequestHandlers(
            self.proto, self.db, self.auth,
            self.session_mgr, self.append_log
        )
        self.handlers.load_questions()
        
        # Initialize room manager
        self.room_mgr = RoomManager(self.proto, self.db, self.append_log)
        
        # Initialize client handler
        self.client_handler = ClientHandler(
            self.proto, self.session_mgr, self.handlers,
            self.room_mgr, self.append_log, self.clients,
            {
                'students_list': self.update_students_list,
                'statistics': self.update_statistics
            }
        )
        
        # Set window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start server automatically
        self.after(100, lambda: self.start_server(5555))
        
    def setup_gui(self):
        """Setup the GUI layout"""
        self.title("Test Application Server (TAP Protocol v1.0)")
        self.geometry("1000x700")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="🖥️ Test Application Server",
            font=("Arial", 24, "bold")
        ).pack(side="left", padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(
            header,
            text="⚫ Server Stopped",
            font=("Arial", 14),
            text_color="red"
        )
        self.status_label.pack(side="right", padx=20)
        
        # Left panel - Server Log
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(
            left_panel,
            text="📋 Server Log",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        self.log_text = ctk.CTkTextbox(left_panel, font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text.configure(state="disabled")
        
        # Right panel - Stats and Users
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Statistics
        stats_frame = ctk.CTkFrame(right_panel)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Statistics",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.stats_text = ctk.CTkTextbox(stats_frame, height=120, font=("Arial", 11))
        self.stats_text.pack(fill="x", padx=10, pady=5)
        self.stats_text.configure(state="disabled")
        
        # Connected Users
        users_frame = ctk.CTkFrame(right_panel)
        users_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            users_frame,
            text="👥 Connected Users",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.users_list = ctk.CTkTextbox(users_frame, font=("Arial", 11))
        self.users_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.users_list.configure(state="disabled")
        
        # Bottom controls
        controls = ctk.CTkFrame(self, height=60)
        controls.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkButton(
            controls,
            text="🔄 Refresh Stats",
            command=self.update_statistics,
            height=40,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            controls,
            text="🗑️ Clear Log",
            command=self.clear_log,
            height=40,
            width=150,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=10, pady=10)
        
        # Initialize displays
        self.update_statistics()
        self.update_students_list()
    
    def start_server(self, port=5555):
        """Start the server using C accept loop"""
        if self.server_running:
            return
        
        try:
            # Create server socket
            self.server_socket = self.proto.create_server(port)
            self.server_running = True
            
            # Create C callback for client handler
            @ClientHandlerFunc
            def c_client_handler(ctx_ptr):
                """C callback wrapper for Python client handler"""
                try:
                    # Extract client socket from context
                    ctx = ctx_ptr.contents
                    client_socket = ctx.client_socket
                    
                    # Call Python handler
                    self.client_handler.handle_client(client_socket)
                    
                except Exception as e:
                    self.append_log(f"✗ Handler error: {str(e)}")
                
                return None
            
            # Keep reference to prevent garbage collection
            self._c_handler_ref = c_client_handler
            
            # Initialize C server context
            self.server_context = ServerContext()
            result = self.proto.lib.py_server_context_init(
                ctypes.byref(self.server_context),
                self.server_socket,
                c_client_handler,
                None  # user_data
            )
            
            if result != 0:
                raise RuntimeError("Failed to initialize server context")
            
            # Start C accept loop in Python thread
            # (C will spawn C threads for each client)
            self.server_thread = threading.Thread(
                target=self._run_c_accept_loop,
                daemon=True
            )
            self.server_thread.start()
            
            self.status_label.configure(
                text=f"🟢 Server Running on Port {port}",
                text_color="green"
            )
            
            self.append_log(f"[OK] Server started on port {port} (TAP Protocol v1.0)")
            self.append_log(f"[OK] Using C accept loop with pthread per client")
            
        except Exception as e:
            self.append_log(f"✗ Failed to start server: {str(e)}")
            self.server_running = False
    
    def _run_c_accept_loop(self):
        """Run C accept loop (blocks until server stops)"""
        try:
            self.proto.lib.py_server_accept_loop(
                ctypes.byref(self.server_context)
            )
        except Exception as e:
            self.append_log(f"✗ Accept loop error: {str(e)}")
    
    def append_log(self, message):
        """Append message to log (thread-safe)"""
        def _update():
            self.log_text.configure(state="normal")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{timestamp}] {message}\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        
        self.after(0, _update)
    
    def update_students_list(self):
        """Update connected users list (thread-safe)"""
        def _update():
            # Clean up dead connections using C health check
            dead_sockets = []
            for socket in list(self.clients.keys()):
                if not self.proto.is_connection_alive(socket):
                    dead_sockets.append(socket)
            
            for socket in dead_sockets:
                user = self.clients[socket]
                self.append_log(f"⚠️ {user['username']} connection lost (auto cleanup)")
                del self.clients[socket]
            
            self.users_list.configure(state="normal")
            self.users_list.delete("1.0", "end")
            
            if self.clients:
                for socket, client_info in self.clients.items():
                    status_icon = "📝" if client_info.get('status') == "testing" else "[OK]"
                    role_icon = "👨‍🎓" if client_info['role'] == "student" else "👨‍🏫"
                    ip = client_info.get('ip_address', 'unknown')
                    self.users_list.insert("end", 
                        f"{status_icon} {role_icon} {client_info['username']} ({ip})\n"
                    )
            else:
                self.users_list.insert("end", "No connected users")
            
            self.users_list.configure(state="disabled")
        
        self.after(0, _update)
    
    def update_statistics(self):
        """Update statistics display (thread-safe)"""
        def _update():
            stats = self.db.get_statistics()
            
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            
            total_users = stats['total_students'] + stats['total_teachers']
            self.stats_text.insert("end", f"Total Users: {total_users}\n")
            self.stats_text.insert("end", f"Students: {stats['total_students']}\n")
            self.stats_text.insert("end", f"Teachers: {stats['total_teachers']}\n")
            self.stats_text.insert("end", f"Test Attempts: {stats['total_attempts']}\n")
            self.stats_text.insert("end", f"Average Score: {stats['average_score']:.2f}%\n")
            
            self.stats_text.configure(state="disabled")
        
        self.after(0, _update)
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
    
    def on_closing(self):
        """Handle window close"""
        self.server_running = False
        
        # Stop C server context (socket will be closed inside)
        if hasattr(self, 'server_context') and self.server_context:
            self.server_context.running = 0
            try:
                self.proto.lib.py_server_context_destroy(
                    ctypes.byref(self.server_context)
                )
            except Exception as e:
                print(f"Error destroying server context: {e}")
        
        # Cleanup broadcast manager (if exists)
        if hasattr(self, 'broadcast_manager') and self.broadcast_manager:
            try:
                self.proto.lib.py_broadcast_manager_destroy(
                    ctypes.byref(self.broadcast_manager)
                )
            except Exception as e:
                print(f"Error destroying broadcast manager: {e}")
        
        # Cleanup network
        try:
            self.proto.cleanup_network()
        except Exception as e:
            print(f"Error cleaning up network: {e}")
        
        self.destroy()
