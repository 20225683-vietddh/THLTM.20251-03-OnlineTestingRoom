"""
Authentication Manager
Handles password hashing, verification, and user authentication
"""
import hashlib
import secrets

class AuthManager:
    """Manage authentication operations"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using PBKDF2-HMAC-SHA256 with salt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Salt + hash in format "salt$hash"
        """
        # Generate random salt (32 characters)
        salt = secrets.token_hex(16)
        
        # Hash password with salt using PBKDF2
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',                    # Hash algorithm
            password.encode('utf-8'),    # Password to hash
            salt.encode('utf-8'),        # Salt
            100000                       # Number of iterations
        )
        
        # Return salt and hash separated by $
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password, hash_with_salt):
        """
        Verify password against stored hash
        
        Args:
            password (str): Plain text password to verify
            hash_with_salt (str): Stored hash in format "salt$hash"
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            # Split salt and hash
            salt, stored_hash = hash_with_salt.split('$')
            
            # Hash the input password with the same salt
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # Compare hashes
            return new_hash.hex() == stored_hash
            
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def validate_username(username):
        """
        Validate username format
        
        Args:
            username (str): Username to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        
        if not username.isalnum():
            return False, "Username must contain only letters and numbers"
        
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if len(password) > 50:
            return False, "Password is too long"
        
        # Optional: Add more requirements
        # has_digit = any(c.isdigit() for c in password)
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """
        Simple email validation
        
        Args:
            email (str): Email to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email:
            return True, ""  # Email is optional
        
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_full_name(full_name):
        """
        Validate full name
        
        Args:
            full_name (str): Full name to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not full_name:
            return False, "Full name cannot be empty"
        
        if len(full_name) < 2:
            return False, "Full name must be at least 2 characters"
        
        if len(full_name) > 50:
            return False, "Full name is too long"
        
        return True, ""

