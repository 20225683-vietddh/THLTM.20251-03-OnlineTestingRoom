"""
Python wrapper for C network functions using ctypes
"""
import ctypes
import os
import platform
from pathlib import Path

class NetworkWrapper:
    def __init__(self):
        self.lib = None
        self._load_library()
        
    def _load_library(self):
        """Load the compiled C library"""
        # Determine library name based on platform
        system = platform.system()
        if system == "Windows":
            lib_name = "network.dll"
        elif system == "Darwin":
            lib_name = "libnetwork.dylib"
        else:
            lib_name = "libnetwork.so"
        
        # Try to find the library
        lib_path = Path(__file__).parent.parent.parent / "lib" / lib_name
        
        if not lib_path.exists():
            raise FileNotFoundError(
                f"Network library not found at {lib_path}.\n"
                f"Please compile the C library first using the build script."
            )
        
        # Load the library
        self.lib = ctypes.CDLL(str(lib_path))
        
        # Define function signatures
        self._define_functions()
        
    def _define_functions(self):
        """Define C function signatures for ctypes"""
        # py_init_network() -> int
        self.lib.py_init_network.argtypes = []
        self.lib.py_init_network.restype = ctypes.c_int
        
        # py_cleanup_network() -> void
        self.lib.py_cleanup_network.argtypes = []
        self.lib.py_cleanup_network.restype = None
        
        # py_create_server(int port) -> socket_t
        self.lib.py_create_server.argtypes = [ctypes.c_int]
        self.lib.py_create_server.restype = ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int
        
        # py_accept_client(socket_t) -> socket_t
        self.lib.py_accept_client.argtypes = [ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int]
        self.lib.py_accept_client.restype = ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int
        
        # py_connect_to_server(const char*, int) -> socket_t
        self.lib.py_connect_to_server.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.py_connect_to_server.restype = ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int
        
        # py_send_message(socket_t, const char*) -> int
        self.lib.py_send_message.argtypes = [
            ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int,
            ctypes.c_char_p
        ]
        self.lib.py_send_message.restype = ctypes.c_int
        
        # py_receive_message(socket_t, char*, int) -> int
        self.lib.py_receive_message.argtypes = [
            ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int
        ]
        self.lib.py_receive_message.restype = ctypes.c_int
        
        # py_close_socket(socket_t) -> void
        self.lib.py_close_socket.argtypes = [ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int]
        self.lib.py_close_socket.restype = None
        
    def init_network(self):
        """Initialize network (required for Windows)"""
        result = self.lib.py_init_network()
        if result != 0:
            raise RuntimeError("Failed to initialize network")
        
    def cleanup_network(self):
        """Cleanup network"""
        self.lib.py_cleanup_network()
        
    def create_server(self, port):
        """Create a server socket"""
        socket = self.lib.py_create_server(port)
        if socket == -1:
            raise RuntimeError(f"Failed to create server on port {port}")
        return socket
        
    def accept_client(self, server_socket):
        """Accept a client connection"""
        client_socket = self.lib.py_accept_client(server_socket)
        if client_socket == -1:
            raise RuntimeError("Failed to accept client")
        return client_socket
        
    def connect_to_server(self, host, port):
        """Connect to a server (client side)"""
        socket = self.lib.py_connect_to_server(host.encode('utf-8'), port)
        if socket == -1:
            raise RuntimeError(f"Failed to connect to {host}:{port}")
        return socket
        
    def send_message(self, socket, message):
        """Send a message through socket"""
        result = self.lib.py_send_message(socket, message.encode('utf-8'))
        if result == -1:
            raise RuntimeError("Failed to send message")
        return result
        
    def receive_message(self, socket, buffer_size=8192):
        """Receive a message from socket"""
        buffer = ctypes.create_string_buffer(buffer_size)
        result = self.lib.py_receive_message(socket, buffer, buffer_size)
        if result == -1:
            raise RuntimeError("Failed to receive message")
        return buffer.value.decode('utf-8')
        
    def close_socket(self, socket):
        """Close a socket"""
        self.lib.py_close_socket(socket)

