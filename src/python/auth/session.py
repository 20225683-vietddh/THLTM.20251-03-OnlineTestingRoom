"""
Session Management
Handles user sessions and authentication tokens
"""
import secrets
from datetime import datetime, timedelta

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, session_duration_hours=24):
        """
        Initialize session manager
        
        Args:
            session_duration_hours (int): Session expiration time in hours
        """
        self.sessions = {}  # {token: session_data}
        self.session_duration = timedelta(hours=session_duration_hours)
    
    def create_session(self, user_id, username, role, full_name):
        """
        Create a new session for user
        
        Args:
            user_id (int): User ID
            username (str): Username
            role (str): User role (student/teacher)
            full_name (str): User's full name
            
        Returns:
            str: Session token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Store session data
        self.sessions[token] = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'full_name': full_name,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.session_duration,
            'last_activity': datetime.now()
        }
        
        return token
    
    def validate_session(self, token):
        """
        Validate session token
        
        Args:
            token (str): Session token
            
        Returns:
            dict or None: Session data if valid, None if invalid
        """
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        # Check if session expired
        if datetime.now() > session['expires_at']:
            # Remove expired session
            del self.sessions[token]
            return None
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return session
    
    def get_session(self, token):
        """
        Get session data without validation
        
        Args:
            token (str): Session token
            
        Returns:
            dict or None: Session data if exists
        """
        return self.sessions.get(token)
    
    def destroy_session(self, token):
        """
        Destroy a session (logout)
        
        Args:
            token (str): Session token
            
        Returns:
            bool: True if session was destroyed
        """
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def get_user_sessions(self, user_id):
        """
        Get all sessions for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of session tokens
        """
        tokens = []
        for token, session in self.sessions.items():
            if session['user_id'] == user_id:
                tokens.append(token)
        return tokens
    
    def destroy_user_sessions(self, user_id):
        """
        Destroy all sessions for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            int: Number of sessions destroyed
        """
        tokens = self.get_user_sessions(user_id)
        for token in tokens:
            del self.sessions[token]
        return len(tokens)
    
    def cleanup_expired_sessions(self):
        """
        Remove all expired sessions
        
        Returns:
            int: Number of sessions removed
        """
        now = datetime.now()
        expired_tokens = []
        
        for token, session in self.sessions.items():
            if now > session['expires_at']:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.sessions[token]
        
        return len(expired_tokens)
    
    def get_all_active_sessions(self):
        """
        Get all active sessions
        
        Returns:
            dict: All active sessions
        """
        return self.sessions.copy()
    
    def get_session_count(self):
        """
        Get number of active sessions
        
        Returns:
            int: Number of active sessions
        """
        return len(self.sessions)
    
    def extend_session(self, token, hours=24):
        """
        Extend session expiration time
        
        Args:
            token (str): Session token
            hours (int): Hours to extend
            
        Returns:
            bool: True if successful
        """
        if token in self.sessions:
            self.sessions[token]['expires_at'] = datetime.now() + timedelta(hours=hours)
            return True
        return False

