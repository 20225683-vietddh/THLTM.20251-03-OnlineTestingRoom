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

### TAP Protocol v1.00

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
├─────────────────┤                    ├──────────────────┤
│                 │    TCP Socket      │                  │
│ protocol_wrapper│◄──────────────────►│ protocol_wrapper │
│    (Python)     │   TAP Protocol     │    (Python)      │
│                 │   Port: 5555       │                  │
├─────────────────┤                    ├──────────────────┤
│   ctypes FFI    │                    │    ctypes FFI    │
│  (Python ↔ C)   │                    │   (Python ↔ C)   │
└────────┬────────┘                    └─────────┬────────┘
         │  Load DLL/SO                       │  Load DLL/SO
         │  Call C functions                  │  Call C functions
    ┌────▼────────────────────────────────────▼────┐
    │  C Network Layer (network.dll/libnetwork.so) │
    │  ┌──────────────────────────────────────┐    │
    │  │ Python Wrapper (python_wrapper.c)    │    │
    │  │  - py_create_server()                │    │
    │  │  - py_connect_to_server()            │    │
    │  │  - py_send_protocol_message()        │    │
    │  │  - py_receive_protocol_message()     │    │
    │  ├──────────────────────────────────────┤    │
    │  │ Application Layer (protocol.c/h)     │    │
    │  │  - TAP Protocol implementation       │    │
    │  │  - Message framing & validation      │    │
    │  │  - Stream handling (fixed header)    │    │
    │  ├──────────────────────────────────────┤    │
    │  │ Transport Layer (socket_ops.c/h)     │    │
    │  │  - TCP socket operations             │    │
    │  │  - Connection management             │    │
    │  │  - Blocking I/O (send/recv loop)     │    │
    │  ├──────────────────────────────────────┤    │
    │  │ Concurrency (thread_pool.c/h)        │    │
    │  │  - Multi-threading (Windows/POSIX)   │    │
    │  │  - Thread-per-client model           │    │
    │  │  - Mutex synchronization             │    │
    │  ├──────────────────────────────────────┤    │
    │  │ Utilities (utils.c/h)                │    │
    │  │  - Message ID, timestamps            │    │
    │  └──────────────────────────────────────┘    │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │    Database Layer (database/ package)        │        
    └──────────────────────────────────────────────┘
```

---

## 🔗 Python-C Integration (ctypes FFI)

### **Thư viện: `ctypes` (Python Standard Library)**

**ctypes** cho phép Python gọi C functions từ compiled library:
- ✅ Load DLL/SO files
- ✅ Define C function signatures  
- ✅ Convert Python ↔ C types
- ✅ No compilation needed for Python code

### **How It Works**

**Step 1: C Side - Export Functions**

File: `src/network/python_wrapper.c`
```c
// Wrapper functions with "py_" prefix
int py_connect_to_server(const char* host, int port) {
    return socket_connect_to_server(host, port);
}

int py_send_protocol_message(socket_t socket, uint16_t msg_type,
                              const char* payload, const char* token) {
    return protocol_send_message(socket, msg_type, payload, token);
}
```
Compile → `lib/network.dll` (Windows) / `lib/libnetwork.so` (Linux)

**Step 2: Python Side - Load & Call**

File: `src/python/protocol_wrapper.py`
```python
import ctypes

# 1. Load C library
lib = ctypes.CDLL("lib/network.dll")

# 2. Define signatures
lib.py_connect_to_server.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.py_connect_to_server.restype = ctypes.c_int64

lib.py_send_protocol_message.argtypes = [
    ctypes.c_int64,   # socket
    ctypes.c_uint16,  # msg_type
    ctypes.c_char_p,  # payload
    ctypes.c_char_p   # token
]
lib.py_send_protocol_message.restype = ctypes.c_int

# 3. Call C functions
socket = lib.py_connect_to_server(b"127.0.0.1", 5555)
result = lib.py_send_protocol_message(socket, 0x0003, b'{"user":"test"}', b"token")
```

### **Type Conversion**

| Python | ctypes | C |
|--------|--------|---|
| `bytes` | `c_char_p` | `const char*` |
| `str.encode()` | `c_char_p` | `char*` |
| `int` | `c_int` | `int` |
| `int` | `c_uint16` | `uint16_t` |
| `int` (socket) | `c_int64` (Win) / `c_int` (Linux) | `SOCKET` / `int` |

### **C Struct → Python ctypes.Structure**

**C (`protocol.h`):**
```c
typedef struct {
    uint32_t magic;
    uint16_t message_type;
    uint32_t length;
    char     session_token[32];
} protocol_header_t;
```

**Python (`protocol_wrapper.py`):**
```python
class ProtocolHeader(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("message_type", ctypes.c_uint16),
        ("length", ctypes.c_uint32),
        ("session_token", ctypes.c_char * 32)
    ]
```

### **Complete Integration Flow**

```
Python GUI (student_window.py)
    ↓ Event handler
Python App (client_app.py)
    ↓ Call method
Python Handler (handlers.py)
    ↓ Prepare data
protocol_wrapper.py
    ↓ ctypes FFI
    lib.py_send_protocol_message(...)
    ↓
lib/network.dll (C compiled)
    ↓ Python wrapper exports
python_wrapper.c
    ↓ Call internal functions
protocol.c, socket_ops.c, thread_pool.c
    ↓ System calls
WinSock API / POSIX sockets
```

**Files:**
- `src/network/python_wrapper.c` - C exports
- `src/python/protocol_wrapper.py` - Python ctypes loader
- `lib/network.dll` - Compiled C library

---

## 📊 System Architecture Details

### **File Structure**

```
Project/
├── lib/
│   └── network.dll (libnetwork.so)     ← Compiled C library
├── src/
│   ├── network/                        ← C Network Layer (Core)
│   │   ├── core/
│   │   │   ├── socket_ops.c/h         ← TCP socket operations
│   │   │   ├── protocol.c/h           ← TAP protocol (framing)
│   │   │   ├── thread_pool.c/h        ← Multi-threading
│   │   │   └── utils.c/h              ← Utilities
│   │   ├── network.h                  ← Main header (includes all)
│   │   └── python_wrapper.c           ← Python FFI exports
│   └── python/                        ← Python Application Layer
│       ├── protocol_wrapper.py        ← ctypes DLL loader
│       ├── client/
│       │   ├── main.py                ← Entry point (client)
│       │   ├── client_app.py          ← Main client app
│       │   ├── connection.py          ← Client TCP connection
│       │   ├── handlers.py            ← Client-side business logic
│       │   └── ui/                    ← GUI (customtkinter)
│       │       ├── login_window.py
│       │       ├── register_window.py
│       │       ├── student_window.py
│       │       └── teacher_window.py
│       ├── server/
│       │   ├── main.py                ← Entry point (server)
│       │   ├── server_gui.py          ← Main server app (admin GUI)
│       │   ├── client_handler.py      ← Request routing
│       │   ├── handlers.py            ← Server-side business logic
│       │   └── room_manager.py        ← Room management
│       ├── database/
│       │   ├── database_manager.py    ← Facade pattern
│       │   ├── connection.py          ← SQLite connection
│       │   ├── user_repository.py     ← User CRUD
│       │   ├── test_repository.py     ← Test CRUD
│       │   ├── room_repository.py     ← Room CRUD
│       │   └── stats_repository.py    ← Statistics
│       └── auth/
│           ├── auth.py                ← Password hashing (PBKDF2)
│           └── session.py             ← Token management
├── data/
│   └── app.db                         ← SQLite database
├── Makefile / build.bat / build.sh    ← Build scripts
├── requirements.txt                   ← Python dependencies
├── README.md                          ← Project documentation
├── PROTOCOL_SPEC.md                   ← TAP protocol specification
└── NETWORK_IMPLEMENTATION.md          ← Network programming details
```

### **Layer Responsibilities**

| Layer | Technology | Files | Responsibilities |
|-------|-----------|-------|------------------|
| **Presentation** | Python `customtkinter` | `ui/*.py` | User interface, forms, event handling |
| **Application** | Python | `client_app.py`<br>`server_gui.py`<br>`handlers.py` | Business logic, validation, orchestration |
| **Protocol** | Python `ctypes` + C | `protocol_wrapper.py`<br>`protocol.c/h` | Message framing, serialization, TAP protocol |
| **Network** | C | `socket_ops.c/h`<br>`thread_pool.c/h` | TCP/IP, socket I/O, multi-threading |
| **Database** | Python `sqlite3` | `database/*.py` | Data persistence, CRUD, repositories |
| **Authentication** | Python | `auth/*.py` | Password hashing, token management |

### **Technology Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Network Layer** | C (socket API) | Low-level TCP/IP, performance-critical |
| **Protocol** | C + Python ctypes | Binary protocol implementation |
| **GUI** | Python customtkinter | Modern, cross-platform UI |
| **Business Logic** | Python | Application logic, easier to maintain |
| **Database** | SQLite3 | Lightweight, embedded database |
| **Authentication** | PBKDF2 (hashlib) | Secure password hashing |
| **FFI** | ctypes | Python ↔ C integration |
| **Build** | gcc / MSVC | Compile C to DLL/SO |

---

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

## 🏗️ C Network Architecture (Layered Design)

### **Network Programming Principles**

Code C được refactor theo **OSI Model layers** để dễ hiểu và maintain:

```
┌──────────────────────────────────────────────────────┐
│           APPLICATION LAYER (Layer 7)                │
│  ┌────────────────────────────────────────────────┐  │
│  │ protocol.h / protocol.c                        │  │
│  │ • TAP Protocol implementation                  │  │
│  │ • Message types & error codes                  │  │
│  │ • Header structure (64 bytes fixed)            │  │
│  │ • protocol_send_message()                      │  │
│  │ • protocol_receive_message()                   │  │
│  │ • protocol_validate_header()                   │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                         ↕
┌──────────────────────────────────────────────────────┐
│           TRANSPORT LAYER (Layer 4)                  │
│  ┌────────────────────────────────────────────────┐  │
│  │ socket_ops.h / socket_ops.c                    │  │
│  │ • TCP socket operations                        │  │
│  │ • socket_create_server() - Server setup       │  │
│  │ • socket_accept_client() - Accept connections │  │
│  │ • socket_connect_to_server() - Client connect │  │
│  │ • socket_send_data() - Send raw bytes         │  │
│  │ • socket_receive_data() - Receive raw bytes   │  │
│  │ • socket_close() - Close connection            │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                         ↕
┌──────────────────────────────────────────────────────┐
│              UTILITIES                               │
│  ┌────────────────────────────────────────────────┐  │
│  │ utils.h / utils.c                              │  │
│  │ • utils_generate_message_id()                  │  │
│  │ • utils_get_unix_timestamp()                   │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                         ↕
┌──────────────────────────────────────────────────────┐
│              PYTHON INTERFACE                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ python_wrapper.c                               │  │
│  │ • py_init_network()                            │  │
│  │ • py_create_server()                           │  │
│  │ • py_send_protocol_message()                   │  │
│  │ • py_receive_protocol_message()                │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### **Why This Structure?**

✅ **Separation of Concerns**: Mỗi layer có responsibility riêng
✅ **Testability**: Test từng layer độc lập
✅ **Educational**: Rõ ràng Transport vs Application layer
✅ **Maintainability**: Dễ debug và extend
✅ **Professional**: Follow industry best practices

### **Key Network Programming Concepts Demonstrated:**

1. **Transport Layer (socket_ops.c)**:
   - TCP 3-way handshake (SYN, SYN-ACK, ACK)
   - Connection termination (FIN, ACK)
   - Blocking I/O operations
   - Socket address structures

2. **Application Layer (protocol.c)**:
   - Custom protocol design
   - Message framing (fixed header + variable payload)
   - Network byte order (Big-endian)
   - Protocol versioning

3. **Cross-platform Compatibility**:
   - Windows (Winsock2) vs UNIX sockets
   - Platform-specific error handling
   - Portable data types (uint32_t, socket_t)

---

## Cấu trúc dự án

### 📂 Clean Architecture (Django-style)

```
Project/
├── src/
│   ├── network/                    # C Network Layer (Clean Architecture)
│   │   ├── core/                   # Core modules (layered design)
│   │   │   ├── socket_ops.h        # Transport Layer (TCP/IP)
│   │   │   ├── socket_ops.c        #   - Socket creation & management
│   │   │   │                       #   - Connection establishment
│   │   │   │                       #   - Raw data transmission
│   │   │   │
│   │   │   ├── protocol.h          # Application Layer (TAP Protocol)
│   │   │   ├── protocol.c          #   - Message framing
│   │   │   │                       #   - Header packing/unpacking
│   │   │   │                       #   - Protocol validation
│   │   │   │
│   │   │   ├── utils.h             # Utilities
│   │   │   └── utils.c             #   - Message ID generation
│   │   │                           #   - Unix timestamp
│   │   │
│   │   ├── network.h               # Main header (includes all)
│   │   └── python_wrapper.c        # Python ctypes interface
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

**Build script tự động:**
- Detect Python architecture (32-bit/64-bit)
- Compile all core modules
- Link into single shared library (.dll/.so/.dylib)

#### Windows:
```bash
./build.bat
```
Compiles:
- `core/socket_ops.c` → TCP socket layer
- `core/protocol.c` → TAP protocol layer  
- `core/utils.c` → Utility functions
- `python_wrapper.c` → Python bindings
→ Output: `lib/network.dll`

#### Linux/macOS:
```bash
chmod +x build.sh
./build.sh
```
→ Output: `lib/libnetwork.so` (Linux) hoặc `lib/libnetwork.dylib` (macOS)

#### Hoặc sử dụng Makefile:
```bash
make           # Build all modules
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
