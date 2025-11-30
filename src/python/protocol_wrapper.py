"""
Protocol Wrapper for TAP (Test Application Protocol) v1.0
Python wrapper for C protocol functions with proper headers
"""
import ctypes
import json
import platform
import struct
import os
from pathlib import Path

# Protocol constants
PROTOCOL_MAGIC = 0x54415031  # "TAP1"
PROTOCOL_VERSION = 0x0100    # v1.0

# Message Types
MSG_REGISTER_REQ = 0x0001
MSG_REGISTER_RES = 0x0002
MSG_LOGIN_REQ = 0x0003
MSG_LOGIN_RES = 0x0004
MSG_LOGOUT_REQ = 0x0005
MSG_LOGOUT_RES = 0x0006
MSG_TEST_CONFIG = 0x0010
MSG_TEST_START_REQ = 0x0011
MSG_TEST_START_RES = 0x0012
MSG_TEST_QUESTIONS = 0x0013
MSG_TEST_SUBMIT = 0x0014
MSG_TEST_RESULT = 0x0015
MSG_TEACHER_DATA_REQ = 0x0020
MSG_TEACHER_DATA_RES = 0x0021
# Test Room Management
MSG_CREATE_ROOM_REQ = 0x0030
MSG_CREATE_ROOM_RES = 0x0031
MSG_JOIN_ROOM_REQ = 0x0032
MSG_JOIN_ROOM_RES = 0x0033
MSG_START_ROOM_REQ = 0x0034
MSG_START_ROOM_RES = 0x0035
MSG_END_ROOM_REQ = 0x0036
MSG_END_ROOM_RES = 0x0037
MSG_GET_ROOMS_REQ = 0x0038
MSG_GET_ROOMS_RES = 0x0039
MSG_ADD_QUESTION_REQ = 0x0040
MSG_ADD_QUESTION_RES = 0x0041
MSG_GET_QUESTIONS_REQ = 0x0042
MSG_GET_QUESTIONS_RES = 0x0043
MSG_DELETE_QUESTION_REQ = 0x0044
MSG_DELETE_QUESTION_RES = 0x0045
MSG_GET_STUDENT_ROOMS_REQ = 0x0046
MSG_GET_STUDENT_ROOMS_RES = 0x0047
MSG_GET_AVAILABLE_ROOMS_REQ = 0x0048
MSG_GET_AVAILABLE_ROOMS_RES = 0x0049
MSG_START_ROOM_TEST_REQ = 0x004A
MSG_START_ROOM_TEST_RES = 0x004B
MSG_SUBMIT_ROOM_TEST_REQ = 0x004C
MSG_SUBMIT_ROOM_TEST_RES = 0x004D
MSG_ROOM_STATUS = 0x003A
MSG_ERROR = 0x00FF
MSG_HEARTBEAT = 0x00FE

# Error Codes
ERR_SUCCESS = 1000
ERR_BAD_REQUEST = 2000
ERR_INVALID_JSON = 2001
ERR_UNAUTHORIZED = 3000
ERR_INVALID_CREDS = 3001
ERR_SESSION_EXPIRED = 3002
ERR_FORBIDDEN = 4000
ERR_WRONG_ROLE = 4001
ERR_CONFLICT = 5000
ERR_USERNAME_EXISTS = 5001
ERR_INTERNAL = 6000

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
        # Determine socket type (platform-specific)
        socket_type = ctypes.c_int64 if platform.system() == "Windows" else ctypes.c_int
        
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
    MSG_ROOM_STATUS: "ROOM_STATUS",
    MSG_ERROR: "ERROR",
    MSG_HEARTBEAT: "HEARTBEAT"
}

def get_message_type_name(msg_type):
    """Get human-readable message type name"""
    return MESSAGE_TYPE_NAMES.get(msg_type, f"UNKNOWN_0x{msg_type:04X}")
