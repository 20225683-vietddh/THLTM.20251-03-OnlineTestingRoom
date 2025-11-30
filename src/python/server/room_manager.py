"""
Room Management Module
Handles test room creation, control, and participant management
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocol_wrapper import (
    MSG_CREATE_ROOM_RES, MSG_JOIN_ROOM_RES, MSG_START_ROOM_RES,
    MSG_END_ROOM_RES, MSG_GET_ROOMS_RES, MSG_ERROR,
    ERR_SUCCESS, ERR_BAD_REQUEST, ERR_INTERNAL
)


class RoomManager:
    """Manages test rooms and their lifecycle"""
    
    def __init__(self, proto, db, logger):
        """
        Initialize room manager
        
        Args:
            proto: ProtocolWrapper instance
            db: Database instance
            logger: Callback function for logging
        """
        self.proto = proto
        self.db = db
        self.log = logger
    
    def send_response(self, client_socket, msg_type, payload):
        """Send protocol response"""
        try:
            self.proto.send_message(client_socket, msg_type, payload, use_session=False)
        except Exception as e:
            self.log(f"✗ Send error: {str(e)}")
    
    def send_error(self, client_socket, error_code, message):
        """Send error response"""
        self.send_response(client_socket, MSG_ERROR, {
            'code': error_code,
            'message': message
        })
    
    def handle_create_room(self, client_socket, session, request):
        """Create a new test room"""
        try:
            payload = request['payload']
            room_name = payload.get('room_name', '')
            num_questions = payload.get('num_questions', 10)
            duration_minutes = payload.get('duration_minutes', 30)
            
            if not room_name:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Room name is required")
                return
            
            # Create room in database
            result = self.db.create_test_room(
                room_name=room_name,
                teacher_id=session['user_id'],
                num_questions=num_questions,
                duration_minutes=duration_minutes
            )
            
            self.send_response(client_socket, MSG_CREATE_ROOM_RES, {
                'code': ERR_SUCCESS,
                'message': 'Room created successfully',
                'data': {
                    'room_id': result['room_id'],
                    'room_code': result['room_code']
                }
            })
            
            self.log(f"[OK] {session['username']} created room '{room_name}' (Code: {result['room_code']})")
            
        except Exception as e:
            self.log(f"✗ Create room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_get_rooms(self, client_socket, session):
        """Get list of rooms for teacher"""
        try:
            rooms = self.db.get_teacher_rooms(session['user_id'])
            
            self.send_response(client_socket, MSG_GET_ROOMS_RES, {
                'code': ERR_SUCCESS,
                'message': 'Rooms retrieved successfully',
                'data': {'rooms': rooms}
            })
            
        except Exception as e:
            self.log(f"✗ Get rooms error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_start_room(self, client_socket, request):
        """Start test in a room"""
        try:
            payload = request['payload']
            room_id = payload.get('room_id')
            
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Room ID is required")
                return
            
            success = self.db.start_test_room(room_id)
            
            if success:
                self.send_response(client_socket, MSG_START_ROOM_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Test started successfully'
                })
                self.log(f"[OK] Test room {room_id} started")
            else:
                self.send_error(client_socket, ERR_BAD_REQUEST, 
                              "Cannot start test (already started or not found)")
                
        except Exception as e:
            self.log(f"✗ Start room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_end_room(self, client_socket, request):
        """End test in a room"""
        try:
            payload = request['payload']
            room_id = payload.get('room_id')
            
            if not room_id:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Room ID is required")
                return
            
            success = self.db.end_test_room(room_id)
            
            if success:
                self.send_response(client_socket, MSG_END_ROOM_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Test ended successfully'
                })
                self.log(f"[OK] Test room {room_id} ended")
            else:
                self.send_error(client_socket, ERR_BAD_REQUEST,
                              "Cannot end test (not active or not found)")
                
        except Exception as e:
            self.log(f"✗ End room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_join_room(self, client_socket, session, request):
        """Student joins a room"""
        try:
            payload = request['payload']
            room_code = payload.get('room_code', '').strip().upper()
            
            if not room_code:
                self.send_error(client_socket, ERR_BAD_REQUEST, "Room code is required")
                return
            
            result = self.db.join_room(room_code, session['user_id'])
            
            if result['success']:
                room = result['room']
                self.send_response(client_socket, MSG_JOIN_ROOM_RES, {
                    'code': ERR_SUCCESS,
                    'message': 'Joined room successfully',
                    'data': {'room': room}
                })
                self.log(f"[OK] {session['username']} joined room '{room['room_name']}' ({room_code})")
            else:
                self.send_error(client_socket, ERR_BAD_REQUEST, result['error'])
                
        except Exception as e:
            self.log(f"✗ Join room error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))
    
    def handle_get_student_rooms(self, client_socket, session):
        """Get list of rooms student has joined"""
        try:
            rooms = self.db.get_student_rooms(session['user_id'])
            
            self.send_response(client_socket, MSG_GET_ROOMS_RES, {
                'code': ERR_SUCCESS,
                'message': 'Rooms retrieved successfully',
                'data': {'rooms': rooms}
            })
            
        except Exception as e:
            self.log(f"✗ Get student rooms error: {str(e)}")
            self.send_error(client_socket, ERR_INTERNAL, str(e))

