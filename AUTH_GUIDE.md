# Authentication System Guide

## 🎉 Hoàn thành tất cả 4 Phases!

Hệ thống authentication với login/register và role-based access đã sẵn sàng!

---

## 📦 Files mới được tạo

### Authentication Core:
```
src/python/auth/
├── __init__.py          # Module exports
├── database.py          # SQLite database operations
├── auth.py              # Password hashing & validation
└── session.py           # Session management
```

### Application với Auth:
```
src/python/
├── auth_server.py       # 🆕 Server với authentication
├── auth_client.py       # 🆕 Client với login/register UI
└── test_auth.py         # Test script cho Phase 1
```

### Database:
```
data/
└── users.db            # SQLite database (tự động tạo)
```

---

## 🚀 Hướng dẫn sử dụng

### **Bước 1: Test Authentication Core**

```powershell
# Test database, password hashing, sessions
python src/python/test_auth.py
```

**Kết quả mong đợi:**
- ✓ Database initialized
- ✓ Password hashing works
- ✓ Validation works
- ✓ Session management works
- ✓ Tạo 2 tài khoản mẫu:
  - Teacher: `teacher1` / `teacher123`
  - Student: `student1` / `student123`

---

### **Bước 2: Chạy Server với Authentication**

```powershell
# Terminal 1 - Run auth server
python src/python/auth_server.py
```

**Server Features:**
- 🔐 Handle REGISTER & LOGIN requests
- 👥 Track connected users với role
- 📊 Show database statistics
- 📝 Students can take tests
- 👨‍🏫 Teachers can view all results
- 🔒 Session-based authentication

---

### **Bước 3: Chạy Client**

```powershell
# Terminal 2 - Run auth client
python src/python/auth_client.py
```

**Client Features:**
- 📝 Register new account
- 🔐 Login với username/password
- 👨‍🎓 Student UI - Take tests
- 👨‍🏫 Teacher UI - View results dashboard

---

## 📋 Protocol Messages

### **Registration**
```
CLIENT → SERVER:
REGISTER:student:{"username":"john","password":"abc123","full_name":"John Doe","email":"john@email.com"}

SERVER → CLIENT (Success):
REGISTER_SUCCESS:{"user_id":1,"username":"john","role":"student"}

SERVER → CLIENT (Failed):
REGISTER_FAILED:{"error":"Username already exists"}
```

### **Login**
```
CLIENT → SERVER:
LOGIN:student:{"username":"john","password":"abc123"}

SERVER → CLIENT (Success):
AUTH_SUCCESS:{"session_token":"abc123xyz...","user_id":1,"username":"john","role":"student","full_name":"John Doe"}

SERVER → CLIENT (Failed):
AUTH_FAILED:{"error":"Invalid credentials"}
```

### **Student Test Flow**
```
1. CLIENT → SERVER: LOGIN:student:{...}
2. SERVER → CLIENT: AUTH_SUCCESS:{...}
3. SERVER → CLIENT: CONFIG:{"num_questions":10,"duration":30}
4. CLIENT → SERVER: START
5. SERVER → CLIENT: QUESTIONS:{...}
6. CLIENT → SERVER: ANSWERS:[...]
7. SERVER → CLIENT: RESULT:{"score":8,"total":10,"percentage":80.0}
```

### **Teacher Dashboard**
```
1. CLIENT → SERVER: LOGIN:teacher:{...}
2. SERVER → CLIENT: AUTH_SUCCESS:{...}
3. SERVER → CLIENT: TEACHER_DATA:{"results":[...]}
```

---

## 🎯 Các tính năng đã implement

### ✅ Phase 1: Database & Auth Core
- [x] SQLite database với users, test_results tables
- [x] Password hashing với PBKDF2-HMAC-SHA256 + salt
- [x] User registration logic
- [x] Login verification
- [x] Session management với tokens
- [x] Input validation (username, password, email)

### ✅ Phase 2: Protocol & Server
- [x] REGISTER protocol handler
- [x] LOGIN protocol handler
- [x] Session validation middleware
- [x] Role-based request handling
- [x] Student test flow
- [x] Teacher dashboard data
- [x] Save test results to database

### ✅ Phase 3: Client UI
- [x] Login screen
- [x] Register screen
- [x] Role selection (Student/Teacher)
- [x] Student test UI (với timer)
- [x] Teacher dashboard UI
- [x] Result display
- [x] Error handling & validation

### ✅ Phase 4: Integration
- [x] Full authentication flow
- [x] Database persistence
- [x] Session management
- [x] Test results tracking
- [x] Statistics display

---

## 👥 Sử dụng hệ thống

### **Scenario 1: Student Register & Take Test**

1. **Chạy auth_server.py**
2. **Chạy auth_client.py**
3. Click **"Register"**
4. Chọn role: **"Student"**
5. Fill in:
   - Full Name: `Jane Student`
   - Username: `jane`
   - Password: `password123`
6. Click **"Register"** → Success!
7. Click **"Login"**
8. Enter credentials
9. Click **"Start Test"**
10. Answer questions
11. Click **"Submit Test"**
12. View result!

### **Scenario 2: Teacher Login & View Results**

1. **Login với teacher account**:
   - Username: `teacher1`
   - Password: `teacher123`
   - Role: Teacher
2. View **all students' test results**
3. See statistics

---

## 🗄️ Database Schema

### **users table**
```sql
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL
role            TEXT CHECK(role IN ('student', 'teacher'))
full_name       TEXT NOT NULL
email           TEXT
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### **test_results table**
```sql
id                  INTEGER PRIMARY KEY
student_id          INTEGER (FOREIGN KEY → users.id)
test_date           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
score               INTEGER NOT NULL
total_questions     INTEGER NOT NULL
answers             TEXT (JSON)
duration_seconds    INTEGER
```

---

## 🔐 Bảo mật

### **Password Hashing:**
- Algorithm: PBKDF2-HMAC-SHA256
- Iterations: 100,000
- Salt: 16 bytes random per password
- Format: `salt$hash`

### **Session Tokens:**
- URL-safe random tokens (32 bytes)
- 24-hour expiration
- Stored in server memory
- Validated on each request

### **Input Validation:**
- Username: 3-20 characters, alphanumeric
- Password: 6-50 characters
- Email: Basic format check
- Full name: 2-50 characters

---

## 📊 Database Statistics

Xem trong server UI hoặc query trực tiếp:

```python
from auth import Database

db = Database("data/users.db")
stats = db.get_statistics()

print(f"Students: {stats['total_students']}")
print(f"Teachers: {stats['total_teachers']}")
print(f"Test Attempts: {stats['total_attempts']}")
print(f"Average Score: {stats['average_score']}%")
```

---

## 🐛 Troubleshooting

### "Database not found"
```powershell
# Run test_auth.py to initialize database
python src/python/test_auth.py
```

### "Username already exists"
- Username phải unique
- Dùng username khác hoặc xóa database và tạo lại

### "Auth failed"
- Kiểm tra username/password đúng chưa
- Kiểm tra role đúng chưa (student vs teacher)

### "Connection refused"
- Chạy server trước
- Kiểm tra host:port đúng chưa

---

## 📈 Mở rộng thêm

### Ideas cho tương lai:

1. **Password Reset**
   - Email verification
   - Reset token

2. **Remember Me**
   - Longer session duration
   - Persistent cookies

3. **User Profile**
   - Edit profile
   - Change password
   - Avatar upload

4. **Admin Role**
   - Manage users
   - Delete accounts
   - View all sessions

5. **Test History**
   - View past results
   - Detailed answers review
   - Progress chart

6. **Multiple Tests**
   - Different subjects
   - Scheduled tests
   - Test categories

---

## 🎓 Học được gì

### Network Programming:
- ✅ Custom protocol design
- ✅ Client-server authentication
- ✅ Session management
- ✅ Role-based access control

### Database:
- ✅ SQLite operations
- ✅ CRUD operations
- ✅ Foreign keys
- ✅ Data persistence

### Security:
- ✅ Password hashing
- ✅ Salt & iterations
- ✅ Session tokens
- ✅ Input validation

### Python:
- ✅ OOP design
- ✅ Module organization
- ✅ Error handling
- ✅ Threading

---

## 📝 Summary

**🎉 Authentication System hoàn thành với:**

- ✅ Secure password storage
- ✅ User registration & login
- ✅ Role-based access (Student/Teacher)
- ✅ Session management
- ✅ Database persistence
- ✅ Modern GUI
- ✅ Custom network protocol
- ✅ Full error handling

**📦 Total Files Created:** 7 files
**⏱️ Development Time:** ~4 phases
**🔐 Security Level:** Production-ready for educational use

---

## 🚀 Quick Start Commands

```powershell
# 1. Test authentication core
python src/python/test_auth.py

# 2. Run server (Terminal 1)
python src/python/auth_server.py

# 3. Run client (Terminal 2)
python src/python/auth_client.py

# 4. Test accounts (created by test_auth.py):
#    Teacher: teacher1 / teacher123
#    Student: student1 / student123
```

---

**Made with ❤️ for Network Programming Course**

Enjoy your authenticated test system! 🎉

