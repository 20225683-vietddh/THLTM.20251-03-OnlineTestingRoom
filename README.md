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

## 📖 Giới thiệu

Dự án **Online Multiple Choice Testing Application** - Ứng dụng thi trắc nghiệm online cho môn **Lập trình Mạng**:

- **Backend (C)**: Xử lý tất cả các chức năng mạng (socket, TCP/IP, client-server communication)
- **Frontend (Python)**: GUI hiện đại với CustomTkinter, gọi các hàm C thông qua ctypes
- **Architecture**: Client-Server model với multi-threaded handling

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
│       ├── auth/                # 🔐 Authentication Module
│       │   ├── __init__.py      # Module exports
│       │   ├── database.py      # SQLite database operations
│       │   ├── auth.py          # Password hashing & validation
│       │   └── session.py       # Session management
│       │
│       ├── ui/                  # 🎨 UI Components (Modular)
│       │   ├── __init__.py      # Module exports
│       │   ├── login_window.py     # Login screen component
│       │   ├── register_window.py  # Registration screen component
│       │   ├── student_window.py   # Student test interface
│       │   └── teacher_window.py   # Teacher dashboard
│       │
│       ├── tests/               # 🧪 Test Scripts & Demos
│       │   ├── __init__.py      # Module exports
│       │   ├── test_auth.py        # Auth system tests
│       │   ├── test_server.py      # Simple server (no auth)
│       │   └── test_client.py      # Simple client (no auth)
│       │
│       ├── network_wrapper.py   # Python ctypes wrapper
│       ├── app.py               # 🆕 Main application (Clean architecture)
│       ├── auth_server.py       # Authentication server
│       └── questions.json       # Ngân hàng câu hỏi
│
├── data/                     # 💾 Data Storage
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
├── README.md                 # Tài liệu chính
└── AUTH_GUIDE.md             # Hướng dẫn Authentication system
```

---

## Yêu cầu hệ thống

### Windows
- **GCC Compiler**: MinGW-w64 hoặc TDM-GCC
  - 📥 Download: [MinGW-w64](https://www.mingw-w64.org/) hoặc [TDM-GCC](https://jmeubank.github.io/tdm-gcc/)
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
- ✅ Tạo database `data/users.db`
- ✅ Tạo 2 accounts mẫu:
  - Teacher: `teacher1` / `teacher123`
  - Student: `student1` / `student123`

---

### Bước 4️⃣: Chạy ứng dụng

## 🎯 **Production Mode (Khuyên dùng)**

### **Server:**
```bash
python src/python/auth_server.py
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

### **Simple Server:**
```bash
python src/python/tests/test_server.py
```

### **Simple Client:**
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

## Protocol Communication

### Message Format

Ứng dụng sử dụng các message format sau giữa Client và Server:

#### Client → Server:
```
NAME:<student_name>          # Đăng ký tên học sinh
START                        # Request bắt đầu thi
ANSWERS:<json_data>          # Nộp bài thi
```

#### Server → Client:
```
CONFIG:<json_data>           # Cấu hình bài thi (số câu, thời gian)
QUESTIONS:<json_data>        # Danh sách câu hỏi
RESULT:<json_data>           # Kết quả điểm số
```

### JSON Data Structures

**CONFIG:**
```json
{
  "num_questions": 10,
  "duration": 30
}
```

**QUESTIONS:**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What does TCP stand for?",
      "options": ["Option A", "Option B", "Option C", "Option D"]
    }
  ]
}
```

**ANSWERS:**
```json
[
  {"question_id": 1, "selected": 0},
  {"question_id": 2, "selected": 2}
]
```

**RESULT:**
```json
{
  "score": 8,
  "total": 10,
  "percentage": 80.0
}
```
