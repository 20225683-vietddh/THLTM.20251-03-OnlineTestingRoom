"""
Client Connection Handler
Manages individual client connections and routes requests
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol_wrapper import (
    MSG_REGISTER_REQ, MSG_LOGIN_REQ,
    MSG_CREATE_ROOM_REQ, MSG_GET_ROOMS_REQ,
    MSG_START_ROOM_REQ, MSG_END_ROOM_REQ,
    MSG_ADD_QUESTION_REQ, MSG_GET_QUESTIONS_REQ, MSG_DELETE_QUESTION_REQ,
    MSG_JOIN_ROOM_REQ, MSG_GET_STUDENT_ROOMS_REQ, MSG_GET_AVAILABLE_ROOMS_REQ,
    MSG_START_ROOM_TEST_REQ, MSG_SUBMIT_ROOM_TEST_REQ,
    MSG_AUTO_SAVE_REQ
)


class ClientHandler:
    """Handles individual client connections"""
    
    def __init__(self, proto, session_mgr, handlers, room_mgr, logger, clients_dict, update_callbacks):
        """
        Initialize client handler
        
        Args:
            proto: ProtocolWrapper instance
            session_mgr: SessionManager instance
            handlers: RequestHandlers instance
            room_mgr: RoomManager instance
            logger: Callback function for logging
            clients_dict: Shared dictionary of connected clients
            update_callbacks: Dict of update callbacks (students_list, statistics)
        """
        self.proto = proto
        self.session_mgr = session_mgr
        self.handlers = handlers
        self.room_mgr = room_mgr
        self.log = logger
        self.clients = clients_dict
        self.update_callbacks = update_callbacks
    
    def handle_client(self, client_socket):
        """Handle client communication"""
        # Get client IP from C
        client_ip = self.proto.get_client_ip(client_socket)
        
        try:
            # Wait for authentication (REGISTER or LOGIN)
            request = self.proto.receive_message(client_socket)
            msg_type = request['message_type']
            
            if msg_type == MSG_REGISTER_REQ:
                self.handlers.handle_register(client_socket, request)
                
            elif msg_type == MSG_LOGIN_REQ:
                session_token = self.handlers.handle_login(client_socket, request)
                
                if session_token:
                    # Get session info
                    session = self.session_mgr.validate_session(session_token)
                    
                    # Register client
                    self.clients[client_socket] = {
                        'username': session['username'],
                        'role': session['role'],
                        'status': 'connected',
                        'ip_address': client_ip  # Store IP from C
                    }
                    self.update_callbacks['students_list']()
                    
                    # Log with IP address
                    self.log(f"[OK] {session['username']} ({session['role']}) logged in from {client_ip}")
                    
                    # Handle based on role
                    if session['role'] == 'student':
                        # Student: handle room-based workflow
                        self._handle_student_requests(client_socket, session)
                    else:
                        # Teacher: send initial data then handle room management
                        self.handlers.handle_teacher_data(client_socket, session)
                        self._handle_teacher_requests(client_socket, session)
                    
            else:
                self.handlers.send_error(client_socket, 2000, "Invalid request")
                
        except Exception as e:
            self.log(f"✗ Client error: {str(e)}")
        finally:
            # Cleanup
            if client_socket in self.clients:
                user = self.clients[client_socket]
                self.log(f"✗ {user['username']} disconnected")
                del self.clients[client_socket]
                self.update_callbacks['students_list']()
            try:
                self.proto.close_socket(client_socket)
            except:
                pass
    
    def _handle_student_requests(self, client_socket, session):
        """Handle ongoing student requests (join rooms, take tests)"""
        try:
            while True:
                # Receive next request
                request = self.proto.receive_message(client_socket)
                msg_type = request['message_type']
                
                # Route request
                if msg_type == MSG_JOIN_ROOM_REQ:
                    self.handlers.handle_join_room(client_socket, session, request)
                
                elif msg_type == MSG_GET_STUDENT_ROOMS_REQ:
                    self.handlers.handle_get_student_rooms(client_socket, session, request)
                
                elif msg_type == MSG_GET_AVAILABLE_ROOMS_REQ:
                    self.handlers.handle_get_available_rooms(client_socket, session, request)
                
                elif msg_type == MSG_START_ROOM_TEST_REQ:
                    self.handlers.handle_start_room_test(client_socket, session, request)
                
                elif msg_type == MSG_SUBMIT_ROOM_TEST_REQ:
                    self.handlers.handle_submit_room_test(client_socket, session, request)
                
                elif msg_type == MSG_AUTO_SAVE_REQ:
                    self.handlers.handle_auto_save(client_socket, session, request)
                
                else:
                    self.handlers.send_error(client_socket, 2000, "Invalid request type")
                    break
                    
        except Exception as e:
            # Graceful disconnect vs error
            error_msg = str(e)
            if "Header receive failed" in error_msg or "Connection" in error_msg:
                # Normal disconnect - use info icon
                self.log(f"[OK] {session['username']} disconnected")
            else:
                # Actual error
                self.log(f"✗ [Student {session['username']}] Error: {error_msg}")
    
    def _handle_teacher_requests(self, client_socket, session):
        """Handle ongoing teacher requests (room management)"""
        try:
            while True:
                # Receive next request
                request = self.proto.receive_message(client_socket)
                msg_type = request['message_type']
                
                # Route request
                if msg_type == MSG_CREATE_ROOM_REQ:
                    self.handlers.handle_create_room(client_socket, session, request)
                
                elif msg_type == MSG_GET_ROOMS_REQ:
                    self.handlers.handle_get_rooms(client_socket, session, request)
                
                elif msg_type == MSG_START_ROOM_REQ:
                    self.handlers.handle_start_room(client_socket, session, request)
                
                elif msg_type == MSG_END_ROOM_REQ:
                    self.handlers.handle_end_room(client_socket, session, request)
                
                elif msg_type == MSG_ADD_QUESTION_REQ:
                    self.handlers.handle_add_question(client_socket, session, request)
                
                elif msg_type == MSG_GET_QUESTIONS_REQ:
                    self.handlers.handle_get_questions(client_socket, session, request)
                
                elif msg_type == MSG_DELETE_QUESTION_REQ:
                    self.handlers.handle_delete_question(client_socket, session, request)
                
                else:
                    self.handlers.send_error(client_socket, 2000, "Invalid request type")
                    break
                    
        except Exception as e:
            # Graceful disconnect vs error
            error_msg = str(e)
            if "Header receive failed" in error_msg or "Connection" in error_msg:
                # Normal disconnect - use info icon
                self.log(f"[OK] {session['username']} disconnected")
            else:
                # Actual error
                self.log(f"✗ [Teacher {session['username']}] Error: {error_msg}")
