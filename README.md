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
- **Architecture**: Client-Server model với multi-threaded handling
- **Protocol**: TAP (Test Application Protocol) v1.0 - Binary protocol with structured headers

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

CLIENT (app.py)                        SERVER (server.py)
┌─────────────────┐                    ┌──────────────────┐
│  CustomTkinter  │                    │  CustomTkinter   │
│      GUI        │                    │    GUI (Admin)   │
├─────────────────┤                    ├──────────────────┤
│                 │                    │                  │
│ UI Components   │                    │  Request Handler │
│ - login_window  │                    │  (multi-thread)  │
│ - register_win  │                    │                  │
│ - student_win   │                    │  Auth System     │
│ - teacher_win   │                    │  - database.py   │
│                 │                    │  - auth.py       │
│  App.py         │                    │  - session.py    │
│  (Orchestrator) │                    │                  │
├─────────────────┤                    ├──────────────────┤
│                 │    TCP Socket      │                  │
│ protocol_wrapper│◄──────────────────►│ protocol_wrapper │
│    (Python)     │   TAP Protocol     │    (Python)      │
│                 │   Port: 5000       │                  │
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

```
Project/
├── src/
│   ├── network/                 # C Network Layer
│   │   ├── network.h            # Header file với các định nghĩa
│   │   ├── network.c            # Implementation TCP/IP socket
│   │   └── python_wrapper.c     # Wrapper functions cho Python
│   │
│   └── python/                  # Python Application Layer
│       ├── auth/                # Authentication Module
│       │   ├── __init__.py      # Module exports
│       │   ├── database.py      # SQLite database operations
│       │   ├── auth.py          # Password hashing & validation
│       │   └── session.py       # Session management
│       │
│       ├── ui/                     # UI Components (Modular)
│       │   ├── __init__.py         # Module exports
│       │   ├── login_window.py     # Login screen component
│       │   ├── register_window.py  # Registration screen component
│       │   ├── student_window.py   # Student test interface
│       │   └── teacher_window.py   # Teacher dashboard
│       │
│       ├── tests/                  # Test Scripts & Demos
│       │   ├── test_auth.py        # Auth system tests
│       │   ├── test_protocol.py    # TAP protocol tests
│       │   ├── test_server.py      # Simple server (no auth)
│       │   └── test_client.py      # Simple client (no auth)
│       │
│       ├── network_wrapper.py   # Python ctypes wrapper (legacy)
│       ├── protocol_wrapper.py  # TAP Protocol wrapper ✅
│       ├── app.py               # Client application ✅
│       ├── server.py            # Server application ✅
│       └── questions.json       # Ngân hàng câu hỏi
│
├── data/                     # Data Storage
│   └── users.db              # SQLite database (auto-created)
│
├── lib/                      # Compiled libraries (tự động tạo)
│   └── network.dll/so/dylib  # Shared library
│
├── build.bat                 # Build script cho Windows
├── build.sh                  # Build script cho Linux/macOS
├── Makefile                  # Make configuration
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
├── README.md                 # 📖 Tài liệu chính
└── PROTOCOL_SPEC.md          # 📋 Technical reference (709 dòng)
```

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

## **Production Mode (Khuyên dùng)**

### **Server:**
```bash
python src/python/server.py
```

1. Click **"Start Server"**
2. Đợi log: `✓ Authentication server started on port 5000`

### **Client:**
```bash
python src/python/app.py
```

**Hướng dẫn sử dụng:**

#### **Đăng ký (lần đầu):**
1. Click **"Register"**
2. Chọn role: **Student** hoặc **Teacher**
3. Nhập thông tin đầy đủ
4. Click **"Register"** → Đợi 2 giây tự động chuyển sang Login

#### **Đăng nhập:**
1. Click **"Login"**
2. Chọn role: **Student** hoặc **Teacher**
3. Nhập username và password
4. Click **"Login"**

#### **Student - Làm bài thi:**
1. Sau khi login → Xem thông tin bài thi
2. Click **"Start Test"**
3. Trả lời câu hỏi (dùng Next/Previous)
4. Click **"Submit Test"**
5. Xem kết quả

#### **Teacher - Xem dashboard:**
1. Login với role Teacher
2. Xem tất cả kết quả thi
3. Xem thống kê (average, max, min scores)

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
