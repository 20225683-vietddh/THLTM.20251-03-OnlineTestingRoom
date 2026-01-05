# Online Multiple Choice Test Application

## Network Programming Project

<div align="center">

📝 **Ứng dụng thi trắc nghiệm online** với C Network Backend + Python GUI

![License](https://img.shields.io/badge/license-Educational-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![C](https://img.shields.io/badge/C-Network%20Layer-orange)
![Python](https://img.shields.io/badge/Python-GUI%20Layer-yellow)

</div>

## Cấu trúc dự án

```
Project/
├── src/
│   ├── network/                    # C Network Layer (Clean Architecture)
│   │   ├── core/                   # Core modules (layered design)
│   │   │   ├── socket_ops.h        # Transport Layer (TCP/IP)
│   │   │   ├── socket_ops.c
│   │   │   │
│   │   │   ├── protocol.h          # Application Layer (TAP Protocol)
│   │   │   ├── protocol.c
│   │   │   │
│   │   │   ├── utils.h             # Utilities
│   │   │   └── utils.c
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
├── README.md                   # Main documentation
└── PROTOCOL_SPEC.md            # Protocol technical spec
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
  - Teacher: `teacher1` / `teacher1`
  - Student: `student2` / `123456`

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
