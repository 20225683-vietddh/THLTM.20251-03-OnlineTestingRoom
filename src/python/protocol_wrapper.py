"""
Protocol Wrapper for TAP (Test Application Protocol) v1.0
Python wrapper for C protocol functions with proper headers
"""
import ctypes
import json
import platform
import struct
import os
import re
from pathlib import Path

# ==================== AUTO-LOAD CONSTANTS FROM C HEADER ====================

def _load_protocol_constants():
    """
    Parse protocol.h and load all constants at import time.
    Source of truth: src/network/core/protocol.h
    """
    # Locate protocol.h
    current_file = Path(__file__)
    protocol_header = current_file.parent.parent.parent / "src" / "network" / "core" / "protocol.h"
    
    if not protocol_header.exists():
        raise FileNotFoundError(f"protocol.h not found at {protocol_header}")
    
    constants = {}
    header_content = protocol_header.read_text(encoding='utf-8')
    
    # Pattern: #define CONSTANT_NAME 0x1234 or #define CONSTANT_NAME 1234
    pattern = re.compile(r'^\s*#define\s+((?:MSG_|ERR_|PROTOCOL_|MAX_)\w+)\s+(0x[0-9A-Fa-f]+|\d+)', re.MULTILINE)
    
    for match in pattern.finditer(header_content):
        name = match.group(1)
        value_str = match.group(2)
        # Convert hex or decimal to int
        value = int(value_str, 0)
        constants[name] = value
    
    return constants

# Load all constants into module globals
globals().update(_load_protocol_constants())

# Determine socket type based on platform
socket_type = ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int

# Protocol Header Structure (matches C struct)
class ProtocolHeader(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("version", ctypes.c_uint16),
        ("message_type", ctypes.c_uint16),
        ("length", ctypes.c_uint32),
        ("message_id", ctypes.c_char * 16),
        ("timestamp", ctypes.c_int64),
        ("session_token", ctypes.c_char * 32),
        ("reserved", ctypes.c_char * 12)
    ]

# Client Context Structure (matches C struct)
class ClientContext(ctypes.Structure):
    _fields_ = [
        ("client_socket", socket_type),
        ("thread_id", ctypes.c_int),
        ("user_data", ctypes.c_void_p)
    ]

# Server Context Structure (matches C struct)
class ServerContext(ctypes.Structure):
    _fields_ = [
        ("server_socket", socket_type),
        ("handler", ctypes.c_void_p),  # Function pointer
        ("running", ctypes.c_int),
        ("clients_mutex", ctypes.c_void_p),  # Opaque mutex
        ("active_clients", ctypes.c_int),
        ("user_data", ctypes.c_void_p)
    ]

# Broadcast Client Structure (matches C struct)
class BroadcastClient(ctypes.Structure):
    _fields_ = [
        ("socket", socket_type),
        ("room_id", ctypes.c_int),
        ("username", ctypes.c_char * 32),
        ("active", ctypes.c_int)
    ]

# Client handler function type
ClientHandlerFunc = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ClientContext))

class ProtocolWrapper:
    """Enhanced wrapper with protocol support"""
    
    def __init__(self):
        # Load C network library directly
        self.lib = None
        self._load_library()
        
        # Define protocol function signatures
        self._define_protocol_functions()
        
        # Session token (stored locally after login)
        self.session_token = None
    
    def _load_library(self):
        """Load the C network library"""
        # Get the project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        
        # Determine library name based on platform
        if platform.system() == "Windows":
            lib_name = "network.dll"
        elif platform.system() == "Darwin":
            lib_name = "libnetwork.dylib"
        else:
            lib_name = "libnetwork.so"
        
        lib_path = project_root / "lib" / lib_name
        
        if not lib_path.exists():
            raise FileNotFoundError(f"Network library not found: {lib_path}")
        
        # Load the library
        self.lib = ctypes.CDLL(str(lib_path))
        
    def _define_protocol_functions(self):
        """Define C protocol function signatures"""
        
        # === Basic Socket Functions ===
        # py_init_network() -> int
        self.lib.py_init_network.argtypes = []
        self.lib.py_init_network.restype = ctypes.c_int
        
        # py_cleanup_network() -> void
        self.lib.py_cleanup_network.argtypes = []
        self.lib.py_cleanup_network.restype = None
        
        # py_create_server(int port) -> socket_t
        self.lib.py_create_server.argtypes = [ctypes.c_int]
        self.lib.py_create_server.restype = socket_type
        
        # py_accept_client(socket_t) -> socket_t
        self.lib.py_accept_client.argtypes = [socket_type]
        self.lib.py_accept_client.restype = socket_type
        
        # py_connect_to_server(const char*, int) -> socket_t
        self.lib.py_connect_to_server.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.py_connect_to_server.restype = socket_type
        
        # py_close_socket(socket_t) -> void
        self.lib.py_close_socket.argtypes = [socket_type]
        self.lib.py_close_socket.restype = None
        
        # === Protocol Functions ===
        # py_send_protocol_message
        self.lib.py_send_protocol_message.argtypes = [
            socket_type,      # socket
            ctypes.c_uint16,  # msg_type
            ctypes.c_char_p,  # payload
            ctypes.c_char_p   # session_token
        ]
        self.lib.py_send_protocol_message.restype = ctypes.c_int
        
        # py_receive_protocol_message
        self.lib.py_receive_protocol_message.argtypes = [
            socket_type,      # socket
            ctypes.POINTER(ProtocolHeader),  # header
            ctypes.c_char_p,  # payload
            ctypes.c_int      # max_payload_size
        ]
        self.lib.py_receive_protocol_message.restype = ctypes.c_int
        
        # === Utility Functions ===
        # py_generate_message_id
        self.lib.py_generate_message_id.argtypes = [ctypes.c_char_p]
        self.lib.py_generate_message_id.restype = None
        
        # py_get_unix_timestamp
        self.lib.py_get_unix_timestamp.argtypes = []
        self.lib.py_get_unix_timestamp.restype = ctypes.c_int64
        
        # === Socket Timeout Functions ===
        # py_socket_set_recv_timeout
        self.lib.py_socket_set_recv_timeout.argtypes = [socket_type, ctypes.c_int]
        self.lib.py_socket_set_recv_timeout.restype = ctypes.c_int
        
        # py_socket_set_send_timeout
        self.lib.py_socket_set_send_timeout.argtypes = [socket_type, ctypes.c_int]
        self.lib.py_socket_set_send_timeout.restype = ctypes.c_int
        
        # py_socket_set_timeout
        self.lib.py_socket_set_timeout.argtypes = [socket_type, ctypes.c_int]
        self.lib.py_socket_set_timeout.restype = ctypes.c_int
        
        # === Threading Functions ===
        # py_server_accept_loop
        self.lib.py_server_accept_loop.argtypes = [ctypes.c_void_p]
        self.lib.py_server_accept_loop.restype = ctypes.c_void_p
        
        # py_server_context_init
        self.lib.py_server_context_init.argtypes = [
            ctypes.POINTER(ServerContext),
            socket_type,
            ClientHandlerFunc,
            ctypes.c_void_p
        ]
        self.lib.py_server_context_init.restype = ctypes.c_int
        
        # py_server_context_destroy
        self.lib.py_server_context_destroy.argtypes = [ctypes.POINTER(ServerContext)]
        self.lib.py_server_context_destroy.restype = None
        
        # py_thread_create_client_handler
        self.lib.py_thread_create_client_handler.argtypes = [
            ClientHandlerFunc,
            ctypes.POINTER(ClientContext)
        ]
        self.lib.py_thread_create_client_handler.restype = ctypes.c_int
    
    def send_message(self, socket, msg_type, payload_dict=None, use_session=True):
        """
        Send protocol message with header
        
        Args:
            socket: Socket descriptor
            msg_type: Message type code (e.g., MSG_LOGIN_REQ)
            payload_dict: Python dict to convert to JSON
            use_session: Whether to include session token
            
        Returns:
            int: Bytes sent, or negative on error
        """
        # Convert payload dict to JSON string
        if payload_dict:
            payload = json.dumps(payload_dict).encode('utf-8')
        else:
            payload = b''
        
        # Get session token if needed
        session_token_bytes = None
        if use_session and self.session_token:
            session_token_bytes = self.session_token.encode('utf-8')
        
        # Send via C function
        result = self.lib.py_send_protocol_message(
            socket,
            msg_type,
            payload if payload else None,
            session_token_bytes if session_token_bytes else None
        )
        
        if result < 0:
            raise RuntimeError(f"Failed to send protocol message (error: {result})")
        
        return result
    
    def receive_message(self, socket, max_size=65536):
        """
        Receive protocol message with header
        
        Args:
            socket: Socket descriptor
            max_size: Maximum payload size
            
        Returns:
            tuple: (header, payload_dict)
        """
        # Prepare header and payload buffers
        header = ProtocolHeader()
        payload_buffer = ctypes.create_string_buffer(max_size)
        
        # Receive via C function
        result = self.lib.py_receive_protocol_message(
            socket,
            ctypes.byref(header),
            payload_buffer,
            max_size
        )
        
        if result < 0:
            error_messages = {
                -1: "Header receive failed",
                -2: "Invalid protocol magic",
                -3: "Version mismatch",
                -4: "Payload too large",
                -5: "Payload receive failed"
            }
            raise RuntimeError(error_messages.get(result, f"Receive error: {result}"))
        
        # Parse JSON payload
        payload_dict = {}
        if result > 0:
            try:
                payload_dict = json.loads(payload_buffer.value.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON payload: {e}")
        
        # Return header info and payload
        # C code uses htons() which converts to network byte order (big-endian)
        # But ctypes reads as native byte order, so we need to swap on little-endian systems
        msg_type_raw = header.message_type
        if platform.system() == "Windows":  # Little-endian
            # Swap bytes: 0xFF00 -> 0x00FF
            msg_type = ((msg_type_raw & 0xFF) << 8) | ((msg_type_raw >> 8) & 0xFF)
        else:
            msg_type = msg_type_raw
        
        return {
            'message_type': msg_type,
            'message_id': header.message_id.decode('utf-8', errors='ignore'),
            'timestamp': header.timestamp,
            'session_token': header.session_token.decode('utf-8', errors='ignore').rstrip('\x00'),
            'payload': payload_dict
        }
    
    def set_session_token(self, token):
        """Store session token for future requests"""
        self.session_token = token
    
    def clear_session_token(self):
        """Clear stored session token"""
        self.session_token = None
    
    # Delegate basic socket operations to C library
    def init_network(self):
        """Initialize network subsystem (required for Windows)"""
        result = self.lib.py_init_network()
        if result != 0:
            raise RuntimeError(f"Failed to initialize network: {result}")
        return result
    
    def cleanup_network(self):
        """Cleanup network subsystem"""
        self.lib.py_cleanup_network()
    
    def create_server(self, port):
        """Create TCP server socket"""
        return self.lib.py_create_server(port)
    
    def accept_client(self, server_socket):
        """Accept incoming client connection"""
        return self.lib.py_accept_client(server_socket)
    
    def connect_to_server(self, host, port):
        """Connect to server as client"""
        return self.lib.py_connect_to_server(host.encode('utf-8'), port)
    
    def close_socket(self, socket):
        """Close socket connection"""
        self.lib.py_close_socket(socket)
    
    def is_connection_alive(self, socket):
        """
        Check if socket connection is still alive
        
        Args:
            socket: Socket descriptor
            
        Returns:
            bool: True if connection alive, False otherwise
        """
        result = self.lib.py_socket_is_alive(socket)
        return result == 1
    
    def get_client_ip(self, socket):
        """
        Get client IP address from socket
        
        Args:
            socket: Client socket descriptor
            
        Returns:
            str: IP address string, or "unknown" if failed
        """
        ip_buffer = ctypes.create_string_buffer(16)
        result = self.lib.py_socket_get_client_ip(socket, ip_buffer)
        if result == 0:
            return ip_buffer.value.decode('utf-8')
        return "unknown"
    
    def set_recv_timeout(self, socket, seconds):
        """
        Set receive timeout for socket
        
        Args:
            socket: Socket descriptor
            seconds: Timeout in seconds (0 = disable)
            
        Returns:
            bool: True on success, False on error
        """
        result = self.lib.py_socket_set_recv_timeout(socket, seconds)
        return result == 0
    
    def set_send_timeout(self, socket, seconds):
        """
        Set send timeout for socket
        
        Args:
            socket: Socket descriptor
            seconds: Timeout in seconds (0 = disable)
            
        Returns:
            bool: True on success, False on error
        """
        result = self.lib.py_socket_set_send_timeout(socket, seconds)
        return result == 0
    
    def set_timeout(self, socket, seconds):
        """
        Set both recv and send timeout for socket
        
        Args:
            socket: Socket descriptor
            seconds: Timeout in seconds (0 = disable)
            
        Returns:
            bool: True on success, False on error
        """
        result = self.lib.py_socket_set_timeout(socket, seconds)
        return result == 0


# Message Type Names (for debugging)
MESSAGE_TYPE_NAMES = {
    MSG_REGISTER_REQ: "REGISTER_REQ",
    MSG_REGISTER_RES: "REGISTER_RES",
    MSG_LOGIN_REQ: "LOGIN_REQ",
    MSG_LOGIN_RES: "LOGIN_RES",
    MSG_LOGOUT_REQ: "LOGOUT_REQ",
    MSG_LOGOUT_RES: "LOGOUT_RES",
    MSG_TEST_CONFIG: "TEST_CONFIG",
    MSG_TEST_START_REQ: "TEST_START_REQ",
    MSG_TEST_START_RES: "TEST_START_RES",
    MSG_TEST_QUESTIONS: "TEST_QUESTIONS",
    MSG_TEST_SUBMIT: "TEST_SUBMIT",
    MSG_TEST_RESULT: "TEST_RESULT",
    MSG_TEACHER_DATA_REQ: "TEACHER_DATA_REQ",
    MSG_TEACHER_DATA_RES: "TEACHER_DATA_RES",
    MSG_CREATE_ROOM_REQ: "CREATE_ROOM_REQ",
    MSG_CREATE_ROOM_RES: "CREATE_ROOM_RES",
    MSG_JOIN_ROOM_REQ: "JOIN_ROOM_REQ",
    MSG_JOIN_ROOM_RES: "JOIN_ROOM_RES",
    MSG_START_ROOM_REQ: "START_ROOM_REQ",
    MSG_START_ROOM_RES: "START_ROOM_RES",
    MSG_END_ROOM_REQ: "END_ROOM_REQ",
    MSG_END_ROOM_RES: "END_ROOM_RES",
    MSG_GET_ROOMS_REQ: "GET_ROOMS_REQ",
    MSG_GET_ROOMS_RES: "GET_ROOMS_RES",
    MSG_ADD_QUESTION_REQ: "ADD_QUESTION_REQ",
    MSG_ADD_QUESTION_RES: "ADD_QUESTION_RES",
    MSG_GET_QUESTIONS_REQ: "GET_QUESTIONS_REQ",
    MSG_GET_QUESTIONS_RES: "GET_QUESTIONS_RES",
    MSG_DELETE_QUESTION_REQ: "DELETE_QUESTION_REQ",
    MSG_DELETE_QUESTION_RES: "DELETE_QUESTION_RES",
    MSG_GET_STUDENT_ROOMS_REQ: "GET_STUDENT_ROOMS_REQ",
    MSG_GET_STUDENT_ROOMS_RES: "GET_STUDENT_ROOMS_RES",
    MSG_GET_AVAILABLE_ROOMS_REQ: "GET_AVAILABLE_ROOMS_REQ",
    MSG_GET_AVAILABLE_ROOMS_RES: "GET_AVAILABLE_ROOMS_RES",
    MSG_START_ROOM_TEST_REQ: "START_ROOM_TEST_REQ",
    MSG_START_ROOM_TEST_RES: "START_ROOM_TEST_RES",
    MSG_SUBMIT_ROOM_TEST_REQ: "SUBMIT_ROOM_TEST_REQ",
    MSG_SUBMIT_ROOM_TEST_RES: "SUBMIT_ROOM_TEST_RES",
    MSG_AUTO_SAVE_REQ: "AUTO_SAVE_REQ",
    MSG_AUTO_SAVE_RES: "AUTO_SAVE_RES",
    MSG_ROOM_STATUS: "ROOM_STATUS",
    MSG_ERROR: "ERROR",
    MSG_HEARTBEAT: "HEARTBEAT"
}

def get_message_type_name(msg_type):
    """Get human-readable message type name"""
    return MESSAGE_TYPE_NAMES.get(msg_type, f"UNKNOWN_0x{msg_type:04X}")
