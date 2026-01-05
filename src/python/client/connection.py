"""
Connection Manager
Handles server connection and protocol communication
"""
from protocol_wrapper import (
    ProtocolWrapper, 
    MSG_LOGIN_REQ, MSG_LOGIN_RES, 
    MSG_REGISTER_REQ, MSG_REGISTER_RES,
    MSG_ERROR
)


class ConnectionManager:
    """Manages connection to server"""
    
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.proto = ProtocolWrapper()
        self.socket = None
        self.connected = False
        self.session_token = None
        self.broadcast_callback = None
        self.select_loop_running = False
        
    def init_network(self):
        """Initialize network"""
        self.proto.init_network()
        
    def connect(self):
        """Connect to server"""
        try:
            self.socket = self.proto.connect_to_server(self.host, self.port)
            self.connected = True
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to server: {str(e)}")
    
    def register(self, username, password, full_name, email, role):
        """Register new account (uses direct send/recv, no select loop)"""
        if not self.connected:
            raise ConnectionError("Not connected to server")
        
        try:
            # Send register request (direct protocol, no select loop)
            self.proto.send_message(self.socket, MSG_REGISTER_REQ, {
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email if email else "",
                'role': role
            }, use_session=False)
            
            # Receive response (direct protocol)
            response = self.proto.receive_message(self.socket)
            
            # Check for error
            if response['message_type'] == MSG_ERROR:
                error_msg = response['payload'].get('message', 'Unknown error')
                raise ValueError(error_msg)
            
            # Check register success
            if response['message_type'] == MSG_REGISTER_RES:
                payload = response['payload']
                code = payload.get('code')
                
                if code == 1000:  # ERR_SUCCESS
                    return {
                        'success': True,
                        'message': payload.get('message', 'Registration successful'),
                        'user_id': payload.get('user_id')
                    }
                else:
                    return {
                        'success': False,
                        'message': payload.get('message', 'Registration failed')
                    }
            
            return {'success': False, 'message': 'Unexpected response'}
        finally:
            # Server closes connection after register
            self.disconnect()
    
    def login(self, username, password, role):
        """
        Login to server
        After successful login, starts C select loop for multiplexing
        """
        if not self.connected:
            raise ConnectionError("Not connected to server")
        
        # Send login request (direct protocol, before select loop starts)
        self.proto.send_message(self.socket, MSG_LOGIN_REQ, {
            'username': username,
            'password': password,
            'role': role
        }, use_session=False)
        
        # Receive response (direct protocol)
        response = self.proto.receive_message(self.socket)
        
        # Check for error
        if response['message_type'] == MSG_ERROR:
            error_msg = response['payload'].get('message', 'Unknown error')
            self.disconnect()
            raise ValueError(error_msg)
        
        # Check login success
        if response['message_type'] == MSG_LOGIN_RES:
            payload = response['payload']
            code = payload.get('code')
            
            if code == 1000:  # ERR_SUCCESS
                self.session_token = payload.get('session_token')
                self.proto.set_session_token(self.session_token)
                
                # Start C select loop for I/O multiplexing
                # From this point, all requests must use send_request()
                if self.broadcast_callback:
                    success = self.proto.client_select_loop_start(
                        self.socket, 
                        self.session_token,  # Pass session token to C
                        self.broadcast_callback
                    )
                    if success:
                        self.select_loop_running = True
                
                return {
                    'success': True,
                    'role': payload.get('role'),
                    'full_name': payload.get('full_name'),
                    'session_token': self.session_token
                }
            else:
                self.disconnect()
                return {'success': False, 'message': payload.get('message', 'Login failed')}
        
        self.disconnect()
        return {'success': False, 'message': 'Unexpected response'}
    
    def set_broadcast_callback(self, callback):
        """
        Set callback for broadcast messages (MSG_ROOM_STATUS)
        Must be called BEFORE login
        
        Args:
            callback: function(msg_type, json_str) to handle broadcasts
        """
        def wrapped_callback(msg_type, json_str):
            # C calls this with (int, char*), we parse JSON and call Python callback
            import json
            import traceback
            try:
                data = json.loads(json_str)
                callback(msg_type, data)
            except Exception as e:
                print(f"[ERROR] Broadcast callback error: {e}")
                traceback.print_exc()
        
        self.broadcast_callback = wrapped_callback
    
    def send_request(self, msg_type, payload):
        """
        Send request and wait for response
        Uses C select loop if running, otherwise falls back to direct protocol
        
        Args:
            msg_type: Protocol message type
            payload: Python dict (will be converted to JSON)
            
        Returns:
            Response payload as dict
        """
        try:
            if self.select_loop_running:
                # Use C select loop (thread-safe, multiplexed)
                response = self.proto.client_select_loop_send_request(msg_type, payload)
                return response
            else:
                # Fallback: direct protocol (for requests before login)
                self.proto.send_message(self.socket, msg_type, payload)
                response = self.proto.receive_message(self.socket)
                return response['payload']
        except Exception as e:
            print(f"[ERROR] send_request failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def receive_message(self):
        """
        Receive message from server (deprecated when select loop is running)
        Only use this before login or for special cases
        """
        return self.proto.receive_message(self.socket)
    
    def send_message(self, msg_type, payload, use_session=True):
        """
        Send message to server (deprecated when select loop is running)
        Only use this before login or for special cases
        """
        self.proto.send_message(self.socket, msg_type, payload, use_session)
    
    def disconnect(self):
        """Disconnect from server and stop select loop"""
        # Stop C select loop first
        if self.select_loop_running:
            self.proto.client_select_loop_stop()
            self.select_loop_running = False
        
        # Close socket
        if self.socket:
            try:
                self.proto.close_socket(self.socket)
            except:
                pass
        
        self.connected = False
        self.session_token = None
    
    def cleanup(self):
        """Cleanup network resources"""
        self.disconnect()
        self.proto.cleanup_network()

