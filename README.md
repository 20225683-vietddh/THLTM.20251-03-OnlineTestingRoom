# Online Multiple Choice Test Application
## Network Programming Project

<div align="center">

📝 **Ứng dụng thi trắc nghiệm online** với C Network Backend + Python GUI

![License](https://img.shields.io/badge/license-Educational-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![C](https://img.shields.io/badge/C-Network%20Layer-orange)
![Python](https://img.shields.io/badge/Python-GUI%20Layer-yellow)

</div>

---

## Giới thiệu

Dự án **Online Multiple Choice Testing Application** - Ứng dụng thi trắc nghiệm online cho môn **Lập trình Mạng**:

- **Backend (C)**: Xử lý tất cả các chức năng mạng (socket, TCP/IP, client-server communication)
- **Frontend (Python)**: GUI hiện đại với CustomTkinter, gọi các hàm C thông qua ctypes
- **Architecture**: Django-style clean modular architecture với Repository pattern
- **Protocol**: TAP (Test Application Protocol) v1.0 - Binary protocol with structured headers
- **Database**: SQLite với separated repositories (User, Test, Room, Stats)

### ⭐ Features v2.0

- ✅ **Clean Architecture**: Modular design, mỗi module < 300 dòng
- ✅ **Room Management**: Teacher tạo phòng thi, học sinh join bằng code
- ✅ **Real-time Control**: Teacher kiểm soát start/end test
- ✅ **Role-based Access**: Student vs Teacher interfaces
- ✅ **Session Management**: Token-based authentication
- ✅ **Statistics Dashboard**: Real-time stats cho teacher
- ✅ **Repository Pattern**: Separated database operations

### TAP Protocol v1.0

Dự án sử dụng **custom binary protocol**:

- **Binary Header (64 bytes)**: Magic number, version, message type, length, message ID, timestamp, session token
- **Message Types**: 16 message type codes cho các operations khác nhau
- **Error Codes**: Structured error codes (1000-6000 range)
- **Session Management**: Token-based authentication trong header
- **Versioning**: Protocol version field để hỗ trợ future upgrades
- **Security**: Length validation, magic number verification, timestamp tracking

Xem chi tiết: [PROTOCOL_SPEC.md](PROTOCOL_SPEC.md)

---

## Luồng chạy của Project

### **1️⃣ Kiến trúc tổng quan**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONLINE TEST APPLICATION                      │
└─────────────────────────────────────────────────────────────────┘

CLIENT (client/)                       SERVER (server/)
┌─────────────────┐                    ┌──────────────────┐
│  CustomTkinter  │                    │  CustomTkinter   │
│      GUI        │                    │    GUI (Admin)   │
├─────────────────┤                    ├──────────────────┤
│ client_app.py   │                    │  server_gui.py   │
│  (Main App)     │                    │  (Main Server)   │
│                 │                    │                  │
│ handlers.py     │                    │  handlers.py     │
│  - Teacher      │                    │  - Registration  │
│  - Student      │                    │  - Login/Auth    │
│                 │                    │  - Test grading  │
│ connection.py   │                    │                  │
│  - TCP Client   │                    │  room_manager.py │
│  - Protocol     │                    │  - Room CRUD     │
│                 │                    │  - Start/End     │
│ ui/             │                    │                  │
│  - Windows      │                    │  client_handler  │
│                 │                    │  - Routing       │
├─────────────────┤                    ├──────────────────┤
│                 │    TCP Socket      │                  │
│ protocol_wrapper│◄──────────────────►│ protocol_wrapper │
│    (Python)     │   TAP Protocol     │    (Python)      │
│                 │   Port: 5555       │                  │
├─────────────────┤                    ├──────────────────┤
│   ctypes        │                    │    ctypes        │
└────────┬────────┘                    └─────────┬────────┘
         │                                    │
         │                                    │
    ┌────▼────────────────────────────────────▼────┐
    │         C Network Layer (network.dll)        │
    │  - Socket operations (create, connect, send) │
    │  - Protocol functions (send/receive header)  │
    │  - Binary header packing/unpacking           │
    └──────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │    Database Layer (database/ package)        │
    │  - user_repository (User CRUD)               │
    │  - test_repository (Test results)            │
    │  - room_repository (Rooms & participants)    │
    │  - stats_repository (Statistics)             │
    └──────────────────────────────────────────────┘
```

### **2️⃣ Luồng đăng ký & đăng nhập**

```
CLIENT                              SERVER
  │                                   │
  │  1. Start app.py                  │  1. Start auth_server.py
  │  → Shows login_window             │  → Listening on port 5000
  │                                   │
  │  2. User clicks "Register"        │
  │  → Shows register_window          │
  │                                   │
  │  3. Fill form & submit            │
  │  ┌──────────────────────┐         │
  │  │ MSG_REGISTER_REQ     │         │
  │  │ Header (64 bytes)    │─────────┼──► 4. Receive & validate
  │  │ Payload: {           │         │      - Check username unique
  │  │   username, password,│         │      - Hash password (PBKDF2)
  │  │   role, full_name    │         │      - Insert to database
  │  │ }                    │         │
  │  └──────────────────────┘         │
  │                                   │
  │  5. Success! Show message         │  ┌──────────────────────┐
  │  ◄────────────────────────────────┼──┤ MSG_REGISTER_RES     │
  │  "Registered successfully!"       │  │ code: 1000 (SUCCESS) │
  │  → Auto redirect to login (2s)    │  │ data: {user_id, ...} │
  │                                   │  └──────────────────────┘
  │                                   │
  │  6. User enters credentials       │
  │  ┌──────────────────────┐         │
  │  │ MSG_LOGIN_REQ        │         │
  │  │ {username, password, │─────────┼──► 7. Authenticate
  │  │  role}               │         │      - Verify password hash
  │  │                      │         │      - Generate session token
  │  │ Session: (empty)     │         │      - Store in memory
  │  └──────────────────────┘         │
  │                                   │
  │  8. Store token locally           │  ┌──────────────────────┐
  │  protocol.set_session_token()     │  │ MSG_LOGIN_RES        │
  │  ◄────────────────────────────────┼──┤ session_token:       │
  │                                   │  │   "abc123..."        │
  │  9. Navigate based on role:       │  │ user_data: {...}     │
  │  - Student → student_window       │  └──────────────────────┘
  │  - Teacher → teacher_window       │
  │                                   │
```

### **3️⃣ Luồng làm bài thi (Student)**

```
CLIENT (student_window)               SERVER
  │                                   │
  │  Auto-receive after login         │
  │  ◄────────────────────────────────┼──┐ MSG_TEST_CONFIG
  │  {num_questions: 10,              │  │ Server tự động gửi
  │   duration: 30}                   │  │ ngay sau login
  │                                   │  │
  │  1. Show ready screen             │  │
  │  "Click Start to begin"           │  │
  │                                   │  │
  │  2. User clicks "Start Test"      │  │
  │  ┌──────────────────────┐         │  │
  │  │ MSG_TEST_START_REQ   │         │  │
  │  │ Session token in     │─────────┼──┼──► 3. Validate session
  │  │ header (auto)        │         │  │      Load questions
  │  │ {ready: true}        │         │  │
  │  └──────────────────────┘         │  │
  │                                   │  │
  │  4. Receive confirmation          │  │  ┌─────────────────┐
  │  ◄────────────────────────────────┼──┼──┤ MSG_TEST_START_RES
  │  Start timer countdown            │  │  └─────────────────┘
  │                                   │  │
  │  5. Receive questions             │  │  ┌─────────────────┐
  │  ◄────────────────────────────────┼──┼──┤ MSG_TEST_QUESTIONS
  │  Display question by question     │  │  │ {questions: [...]}
  │  Timer running (30 minutes)       │  │  └─────────────────┘
  │                                   │  │
  │  6. Student answers questions     │  │
  │  [... 30 minutes later ...]       │  │
  │                                   │  │
  │  7. Time up OR click Submit       │  │
  │  ┌──────────────────────┐         │  │
  │  │ MSG_TEST_SUBMIT      │         │  │
  │  │ {answers: [          │─────────┼──┼──► 8. Calculate score
  │  │   {question_id: 1,   │         │  │       Compare with correct
  │  │    selected: 0},     │         │  │       Save to database
  │  │   ...                │         │  │
  │  │ ]}                   │         │  │
  │  └──────────────────────┘         │  │
  │                                   │  │
  │  9. Show result screen            │  │  ┌─────────────────┐
  │  ◄────────────────────────────────┼──┼──┤ MSG_TEST_RESULT
  │  "Your score: 8/10 (80%)"         │  │  │ {score: 8,
  │  → Can logout or retake           │  │  │  total: 10,
  │                                   │  │  │  percentage: 80}
  │                                   │  │  └─────────────────┘
```

### **4️⃣ Luồng xem kết quả (Teacher)**

```
CLIENT (teacher_window)               SERVER
  │                                   │
  │  Auto-load after login            │
  │  ┌──────────────────────┐         │
  │  │ MSG_TEACHER_DATA_REQ │         │
  │  │ Session token in     │─────────┼──► 1. Validate session
  │  │ header (auto)        │         │      Check role = teacher
  │  │ {filter: {},         │         │      Query database:
  │  │  limit: 100}         │         │      - All test results
  │  └──────────────────────┘         │      - Calculate stats
  │                                   │
  │  2. Display dashboard             │  ┌─────────────────────┐
  │  ◄────────────────────────────────┼──┤ MSG_TEACHER_DATA_RES
  │  Table with:                      │  │ {results: [
  │  - Username                       │  │   {username, score,
  │  - Score                          │  │    date, ...}
  │  - Date/Time                      │  │  ],
  │  - Percentage                     │  │  stats: {
  │                                   │  │   avg: 7.5,
  │  Statistics:                      │  │   max: 10,
  │  - Average: 7.5/10                │  │   min: 5
  │  - Highest: 10/10                 │  │  }}
  │  - Lowest: 5/10                   │  └─────────────────────┘
  │                                   │
```

### **5️⃣ TAP Protocol Message Flow**

**Mọi message đều theo format:**

```
┌────────────────────────────────────┐
│   SEND MESSAGE                     │
├────────────────────────────────────┤
│ 1. Python: dict → JSON string      │
│ 2. protocol_wrapper.py:            │
│    - Create header (64 bytes)      │
│    - Add message type code         │
│    - Add session token (if any)    │
│    - Add timestamp                 │
│    - Calculate payload length      │
│ 3. Call C function:                │
│    send_protocol_message()         │
│ 4. C: Send header (64 bytes) first │
│ 5. C: Send payload (JSON) next     │
└────────────────────────────────────┘
         │
         │  TCP Socket
         ▼
┌────────────────────────────────────┐
│   RECEIVE MESSAGE                  │
├────────────────────────────────────┤
│ 1. C: Receive header (64 bytes)    │
│ 2. C: Validate magic number        │
│ 3. C: Check version                │
│ 4. C: Read payload length          │
│ 5. C: Receive payload (JSON)       │
│ 6. Return to Python                │
│ 7. protocol_wrapper.py:            │
│    - Parse header                  │
│    - JSON decode payload           │
│    - Return structured dict        │
└────────────────────────────────────┘
```

---

## Cấu trúc dự án

### 📂 Clean Architecture (Django-style)

```
Project/
├── src/
│   ├── network/                    # C Network Layer (DLL)
│   │   ├── network.h               # Header file & protocol constants
│   │   ├── network.c               # TCP/IP socket implementation
│   │   └── python_wrapper.c        # Python ctypes wrapper
│   │
│   └── python/                     # Python Application Layer
│       │
│       ├── server/                 SERVER MODULE (Django-style)
│       │   ├── __init__.py         # Package exports
│       │   ├── main.py             # Entry point (like manage.py)
│       │   ├── server_gui.py       # GUI window (275 lines)
│       │   ├── handlers.py         # Request handlers (296 lines)
│       │   ├── room_manager.py     # Room operations (190 lines)
│       │   └── client_handler.py   # Connection routing (84 lines)
│       │
│       ├── client/                 CLIENT MODULE (Symmetric)
│       │   ├── __init__.py         # Package exports
│       │   ├── main.py             # Entry point
│       │   ├── client_app.py       # Main application (199 lines)
│       │   ├── connection.py       # Connection manager (94 lines)
│       │   └── handlers.py         # Business logic (125 lines)
│       │
│       ├── database/               DATABASE (Repository Pattern)
│       │   ├── __init__.py         # Package exports
│       │   ├── database_manager.py # Facade pattern (112 lines)
│       │   ├── connection.py       # DB init & connection (132 lines)
│       │   ├── user_repository.py  # User CRUD (93 lines)
│       │   ├── test_repository.py  # Test results (92 lines)
│       │   ├── room_repository.py  # Rooms & participants (251 lines)
│       │   └── stats_repository.py # Statistics (52 lines)
│       │
│       ├── auth/                   AUTH MODULE
│       │   ├── __init__.py         # Module exports
│       │   ├── auth.py             # Password hashing & validation
│       │   └── session.py          # Session management
│       │
│       ├── ui/                     UI COMPONENTS
│       │   ├── __init__.py         # Module exports
│       │   ├── login_window.py     # Login screen
│       │   ├── register_window.py  # Registration screen
│       │   ├── student_window.py   # Student test interface
│       │   └── teacher_window.py   # Teacher dashboard + room mgmt
│       │
│       ├── tests/                  # Integration Tests
│       │   ├── test_auth.py        # Auth system tests
│       │   ├── test_protocol.py    # Protocol tests
│       │   ├── test_server.py      # Server tests
│       │   └── test_client.py      # Client tests
│       │
│       ├── protocol_wrapper.py     # TAP Protocol v1.0 wrapper
│       ├── network_wrapper.py      # Low-level network wrapper
│       ├── questions.json          # Question bank
│       ├── app_old.py              # Backup (monolithic version)
│       └── auth/database_old.py    # Backup (monolithic version)
│
├── data/                       # Data Storage
│   └── app.db                  # SQLite database (auto-created)
│
├── lib/                        # Compiled Libraries
│   └── network.dll             # C network library (auto-built)
│
├── build.bat                   # Windows build script (auto-detect architecture)
├── build.sh                    # Linux/macOS build script
├── Makefile                    # Cross-platform build configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # 📖 Main documentation
└── PROTOCOL_SPEC.md            # 📋 Protocol technical spec
```

### 📊 Module Statistics

| Module | Files | Total Lines | Avg per File |
|--------|-------|-------------|--------------|
| **server/** | 6 files | ~1,215 lines | ~202 lines |
| **client/** | 4 files | ~547 lines | ~137 lines |
| **database/** | 6 files | ~732 lines | ~122 lines |
| **auth/** | 2 files | ~200 lines | ~100 lines |
| **ui/** | 4 files | ~800 lines | ~200 lines |

**Total: ~3,500 lines** across **22 modular files** ✅

---

## Yêu cầu hệ thống

### Windows
- **GCC Compiler**: MinGW-w64 hoặc TDM-GCC
  - Download: [MinGW-w64](https://www.mingw-w64.org/) hoặc [TDM-GCC](https://jmeubank.github.io/tdm-gcc/)
- **Python 3.8+**
- **pip** (Python package manager)

### Linux
- **GCC**: `sudo apt-get install gcc`
- **Python 3.8+**: `sudo apt-get install python3 python3-pip`

### macOS
- **GCC**: `xcode-select --install`
- **Python 3.8+**: Pre-installed hoặc cài qua Homebrew

---

## Cài đặt và chạy

### Bước 1️⃣: Build thư viện C

#### Windows:
```bash
./build.bat
```

#### Linux/macOS:
```bash
chmod +x build.sh
./build.sh
```

Hoặc sử dụng Makefile:
```bash
make           # Build
make clean     # Clean build artifacts
make rebuild   # Clean and rebuild
```

### Bước 2️⃣: Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

Packages được cài đặt:
- `customtkinter` - Modern GUI library
- `darkdetect` - Auto dark/light theme detection
- `packaging` - Required by customtkinter

### Bước 3️⃣: Tạo database và test accounts

```bash
python src/python/tests/test_auth.py
```

**Kết quả:**
- ✅ Tạo database `data/app.db`
- ✅ Tạo 2 accounts mẫu:
  - Teacher: `teacher1` / `teacher123`
  - Student: `student1` / `student123`

---

### Bước 4️⃣: Chạy ứng dụng

## **Production Mode (Clean Architecture)**

### **🖥️ Server (Modular):**
```bash
# Chạy server
python src/python/server/main.py
```

Server tự động:
- Khởi tạo database
- Load câu hỏi từ `questions.json`
- Start listening trên port **5555**
- Hiển thị GUI với server log, statistics, và connected users

### **💻 Client (Modular):**
```bash
# Chạy client
python src/python/client/main.py
```

---

## 📖 Hướng dẫn sử dụng

### **👤 Đăng ký (lần đầu):**
1. Click **"Register"**
2. Chọn role: **Student** hoặc **Teacher**
3. Nhập thông tin đầy đủ
4. Click **"Register"** → Đăng ký thành công

### **🔐 Đăng nhập:**
1. Chọn role: **Student** hoặc **Teacher**
2. Nhập username và password
3. Click **"Login"**

---

### **👨‍🎓 Student - Làm bài thi:**

**Cách 1: Direct Test (Legacy)**
1. Login → Xem thông tin bài thi
2. Click **"Start Test"**
3. Trả lời câu hỏi (Next/Previous)
4. Click **"Submit Test"**
5. Xem kết quả

**Cách 2: Room-based Test** ⭐ NEW
1. Login → Vào Room Lobby
2. Nhập **Room Code** (6 ký tự từ teacher)
3. Click **"Join Room"**
4. Đợi teacher bắt đầu bài thi
5. Làm bài và submit

---

### **👨‍🏫 Teacher - Dashboard & Room Management:**

**Tab 1: 📊 Test Results**
- Xem tất cả kết quả thi
- Thống kê (average, max, min scores)
- Chi tiết từng học sinh

**Tab 2: 🏫 Test Rooms** ⭐ NEW
1. **Tạo phòng thi:**
   - Nhập tên phòng
   - Chọn số câu hỏi (1-50)
   - Chọn thời gian (5-180 phút)
   - Click **"Create Room"**
   - Nhận **Room Code** (VD: ABC123)

2. **Quản lý phòng:**
   - Xem danh sách phòng thi
   - Trạng thái: ⏳ Waiting | ▶️ Active | ✅ Ended
   - Số lượng học sinh tham gia
   - Start/End controls (coming soon)

3. **Chia sẻ Room Code với học sinh**
   - Học sinh nhập code để vào phòng
   - Teacher kiểm soát khi nào bắt đầu/kết thúc

---

## **Testing/Demo Mode (Đơn giản - không auth)**

### **Demo Server (no auth):**
```bash
python src/python/tests/test_server.py
```

### **Demo Client (no auth):**
```bash
python src/python/tests/test_client.py
```

**Khi nào dùng:**
- ✅ Demo network layer đơn giản
- ✅ Test C library
- ✅ Học network programming cơ bản
- ✅ Debug network issues

---

## Tùy chỉnh câu hỏi

### Chỉnh sửa file `src/python/questions.json`:

```json
{
  "duration": 10,
  "questions": [
    {
      "id": 1,
      "question": "Câu hỏi của bạn?",
      "options": [
        "Đáp án A",
        "Đáp án B",
        "Đáp án C",
        "Đáp án D"
      ],
      "answer": 0
    }
  ]
}
```

**Giải thích:**
- `duration`: Thời gian làm bài (phút)
- `id`: ID duy nhất của câu hỏi
- `question`: Nội dung câu hỏi
- `options`: Mảng 4 đáp án
- `answer`: Index của đáp án đúng (0 = A, 1 = B, 2 = C, 3 = D)

**File mẫu** đã có sẵn 10 câu hỏi về Network Programming!

---
