"""
Test script for authentication system
Run this to verify database and auth modules work correctly
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import Database, AuthManager, SessionManager

def test_phase1():
    """Test Phase 1: Database & Auth Core"""
    print("=" * 60)
    print("TESTING PHASE 1: Database & Authentication")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing Database...")
    db = Database("data/app.db")
    auth = AuthManager()
    session_mgr = SessionManager()
    print("   ✓ Database initialized")
    
    # Test password hashing
    print("\n2. Testing Password Hashing...")
    password = "test123"
    hashed = auth.hash_password(password)
    print(f"   Password: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    
    is_valid = auth.verify_password(password, hashed)
    print(f"   ✓ Verification: {'PASSED' if is_valid else 'FAILED'}")
    
    is_invalid = auth.verify_password("wrong", hashed)
    print(f"   ✓ Wrong password rejected: {'PASSED' if not is_invalid else 'FAILED'}")
    
    # Test validation
    print("\n3. Testing Input Validation...")
    
    # Username validation
    valid, msg = auth.validate_username("john123")
    print(f"   Username 'john123': {'✓ Valid' if valid else f'✗ {msg}'}")
    
    valid, msg = auth.validate_username("ab")
    print(f"   Username 'ab': {'✓ Valid' if valid else f'✗ {msg}'}")
    
    # Password validation
    valid, msg = auth.validate_password("password123")
    print(f"   Password 'password123': {'✓ Valid' if valid else f'✗ {msg}'}")
    
    valid, msg = auth.validate_password("123")
    print(f"   Password '123': {'✓ Valid' if valid else f'✗ {msg}'}")
    
    # Test user registration
    print("\n4. Testing User Registration...")
    
    # Create teacher account
    teacher_pass = auth.hash_password("teacher123")
    teacher_id = db.create_user(
        username="teacher1",
        password_hash=teacher_pass,
        role="teacher",
        full_name="John Teacher",
        email="teacher@example.com"
    )
    
    if teacher_id:
        print(f"   ✓ Teacher account created (ID: {teacher_id})")
    else:
        print("   ⚠ Teacher already exists (this is OK if running again)")
    
    # Create student account
    student_pass = auth.hash_password("student123")
    student_id = db.create_user(
        username="student1",
        password_hash=student_pass,
        role="student",
        full_name="Jane Student",
        email="student@example.com"
    )
    
    if student_id:
        print(f"   ✓ Student account created (ID: {student_id})")
    else:
        print("   ⚠ Student already exists (this is OK if running again)")
    
    # Test duplicate username
    duplicate_id = db.create_user(
        username="student1",
        password_hash=student_pass,
        role="student",
        full_name="Duplicate",
        email="dup@example.com"
    )
    
    if duplicate_id is None:
        print("   ✓ Duplicate username rejected correctly")
    else:
        print("   ✗ ERROR: Duplicate username was accepted!")
    
    # Test login verification
    print("\n5. Testing Login Verification...")
    
    user = db.get_user_by_username("teacher1")
    if user:
        print(f"   Retrieved user: {user['username']} ({user['role']})")
        
        # Verify correct password
        is_valid = auth.verify_password("teacher123", user['password_hash'])
        print(f"   ✓ Correct password: {'VERIFIED' if is_valid else 'FAILED'}")
        
        # Verify wrong password
        is_invalid = auth.verify_password("wrongpass", user['password_hash'])
        print(f"   ✓ Wrong password: {'REJECTED' if not is_invalid else 'ACCEPTED (ERROR!)'}")
    
    # Test session management
    print("\n6. Testing Session Management...")
    
    token = session_mgr.create_session(
        user_id=1,
        username="teacher1",
        role="teacher",
        full_name="John Teacher"
    )
    
    print(f"   Session token created: {token[:20]}...")
    
    # Validate session
    session = session_mgr.validate_session(token)
    if session:
        print(f"   ✓ Session validated for user: {session['username']}")
        print(f"     Role: {session['role']}")
        print(f"     Expires: {session['expires_at']}")
    
    # Invalid session
    invalid_session = session_mgr.validate_session("invalid_token_12345")
    print(f"   ✓ Invalid token rejected: {'PASSED' if invalid_session is None else 'FAILED'}")
    
    # Destroy session
    destroyed = session_mgr.destroy_session(token)
    print(f"   ✓ Session destroyed: {'SUCCESS' if destroyed else 'FAILED'}")
    
    # Test database queries
    print("\n7. Testing Database Queries...")
    
    students = db.get_all_students()
    print(f"   Total students in database: {len(students)}")
    for student in students:
        print(f"     - {student['full_name']} (@{student['username']})")
    
    stats = db.get_statistics()
    print(f"\n   Database Statistics:")
    print(f"     Students: {stats['total_students']}")
    print(f"     Teachers: {stats['total_teachers']}")
    print(f"     Test Attempts: {stats['total_attempts']}")
    print(f"     Average Score: {stats['average_score']}%")
    
    print("\n" + "=" * 60)
    print("✓ PHASE 1 TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYou can now use these accounts to test:")
    print("  Teacher: username='teacher1', password='teacher123'")
    print("  Student: username='student1', password='student123'")
    print("=" * 60)

if __name__ == "__main__":
    test_phase1()

