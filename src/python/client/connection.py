"""
Connection Manager
Handles server connection and protocol communication
"""
from protocol_wrapper import ProtocolWrapper, MSG_LOGIN_REQ, MSG_LOGIN_RES, MSG_ERROR


class ConnectionManager:
    """Manages connection to server"""
    
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.proto = ProtocolWrapper()
        self.socket = None
        self.connected = False
        self.session_token = None
        
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
    
    def login(self, username, password, role):
        """Login to server"""
        if not self.connected:
            raise ConnectionError("Not connected to server")
        
        # Send login request
        self.proto.send_message(self.socket, MSG_LOGIN_REQ, {
            'username': username,
            'password': password,
            'role': role
        }, use_session=False)
        
        # Receive response
        response = self.proto.receive_message(self.socket)
        
        # Check for error
        if response['message_type'] == MSG_ERROR:
            error_msg = response['payload'].get('message', 'Unknown error')
            raise ValueError(error_msg)
        
        # Check login success
        if response['message_type'] == MSG_LOGIN_RES:
            payload = response['payload']
            code = payload.get('code')
            
            if code == 1000:  # ERR_SUCCESS
                self.session_token = payload.get('session_token')
                self.proto.set_session_token(self.session_token)
                return {
                    'success': True,
                    'role': payload.get('role'),
                    'full_name': payload.get('full_name'),
                    'session_token': self.session_token
                }
            else:
                return {'success': False, 'message': payload.get('message', 'Login failed')}
        
        return {'success': False, 'message': 'Unexpected response'}
    
    def receive_message(self):
        """Receive message from server"""
        return self.proto.receive_message(self.socket)
    
    def send_message(self, msg_type, payload, use_session=True):
        """Send message to server"""
        self.proto.send_message(self.socket, msg_type, payload, use_session)
    
    def disconnect(self):
        """Disconnect from server"""
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

