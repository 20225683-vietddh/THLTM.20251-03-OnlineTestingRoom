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

### 🎯 Các tính năng chính

#### Test Server (Dành cho Giáo viên)
- ✅ Quản lý câu hỏi từ file JSON
- ✅ Theo dõi danh sách học sinh kết nối
- ✅ Hiển thị trạng thái làm bài real-time
- ✅ Tự động chấm điểm
- ✅ Multi-client support (nhiều học sinh cùng lúc)
- ✅ Server logs chi tiết

#### Test Client (Dành cho Học sinh)
- ✅ Giao diện hiện đại, dễ sử dụng
- ✅ Đếm ngược thời gian làm bài (timer)
- ✅ Điều hướng giữa các câu hỏi
- ✅ Lưu đáp án tự động
- ✅ Cảnh báo khi hết thời gian
- ✅ Hiển thị kết quả ngay lập tức

---

## 📁 Cấu trúc dự án

```
Project/
├── src/
│   ├── network/              # C Network Layer
│   │   ├── network.h         # Header file với các định nghĩa
│   │   ├── network.c         # Implementation TCP/IP socket
│   │   └── python_wrapper.c  # Wrapper functions cho Python
│   │
│   └── python/               # Python GUI Layer
│       ├── network_wrapper.py   # Python ctypes wrapper
│       ├── test_server.py       # Server GUI (Giáo viên)
│       ├── test_client.py       # Client GUI (Học sinh)
│       └── questions.json       # Ngân hàng câu hỏi
│
├── lib/                      # Compiled libraries (tự động tạo)
│   └── network.dll/so/dylib  # Shared library
│
├── build.bat                 # Build script cho Windows
├── build.sh                  # Build script cho Linux/macOS
├── Makefile                  # Make configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # Tài liệu này
```

---

## 💻 Yêu cầu hệ thống

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

## 🚀 Cài đặt và chạy

### Bước 1️⃣: Build thư viện C

#### Windows:
```bash
build.bat
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

### Bước 3️⃣: Chạy ứng dụng

#### 🎓 Chạy Test Server (Giáo viên):
```bash
python src/python/test_server.py
```

**Hướng dẫn sử dụng:**
1. Nhập port (mặc định: 5000)
2. Click **"Start Server"**
3. Theo dõi học sinh kết nối và làm bài
4. Xem kết quả thi của từng học sinh

#### 👨‍🎓 Chạy Test Client (Học sinh):
```bash
python src/python/test_client.py
```

**Hướng dẫn làm bài:**
1. Nhập **tên của bạn**
2. Nhập **host** và **port** của server
3. Click **"Connect to Test Server"**
4. Đọc thông tin bài thi
5. Click **"Start Test"** để bắt đầu
6. Trả lời các câu hỏi (dùng Next/Previous để điều hướng)
7. Click **"Submit Test"** khi hoàn thành
8. Xem kết quả điểm số

---

## 📝 Tùy chỉnh câu hỏi

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

## 🔧 Protocol Communication

### Message Format

Ứng dụng sử dụng các message format sau giữa Client và Server:

#### 📤 Client → Server:
```
NAME:<student_name>          # Đăng ký tên học sinh
START                        # Request bắt đầu thi
ANSWERS:<json_data>          # Nộp bài thi
```

#### 📥 Server → Client:
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

---

## 🎨 Screenshots & Demo

### Server Interface (Giáo viên)
```
┌─────────────────────────────────────────┐
│  TEST SERVER                            │
│  ● Server Running                       │
│  Port: 5000                            │
│                                         │
│  Test Information                       │
│  - Total Questions: 10                  │
│  - Duration: 10 minutes                 │
│                                         │
│  Connected Students:                    │
│  📝 Nguyen Van A                        │
│     Score: 8/10                         │
│     Status: completed                   │
│                                         │
│  ✅ Tran Thi B                          │
│     Score: 9/10                         │
│     Status: completed                   │
└─────────────────────────────────────────┘
```

### Client Interface (Học sinh)
```
┌─────────────────────────────────────────┐
│  Time Remaining: 09:45     Question 3/10│
│                                         │
│  Question 3:                            │
│  What is the default port for HTTP?     │
│                                         │
│  ○ 21                                   │
│  ● 80                                   │
│  ○ 443                                  │
│  ○ 8080                                 │
│                                         │
│  [← Previous]    [Next →]  [Submit Test]│
└─────────────────────────────────────────┘
```

---

## 🔨 Mở rộng chức năng

### Thêm Network Functions mới

**Ví dụ: Thêm hàm broadcast message**

#### 1. Thêm hàm C trong `src/network/network.c`:
```c
int broadcast_message(socket_t* sockets, int count, const char* message) {
    for (int i = 0; i < count; i++) {
        if (send_message(sockets[i], message) < 0) {
            return -1;
        }
    }
    return 0;
}
```

#### 2. Export cho Python trong `src/network/python_wrapper.c`:
```c
EXPORT int py_broadcast_message(socket_t* sockets, int count, const char* message) {
    return broadcast_message(sockets, count, message);
}
```

#### 3. Thêm wrapper trong `src/python/network_wrapper.py`:
```python
def broadcast_message(self, sockets, message):
    socket_array = (ctypes.c_int64 * len(sockets))(*sockets)
    result = self.lib.py_broadcast_message(
        socket_array, 
        len(sockets), 
        message.encode('utf-8')
    )
    return result
```

#### 4. Rebuild library:
```bash
make rebuild    # hoặc build.bat / build.sh
```

---

## 💡 Ý tưởng phát triển

### Tính năng nâng cao

#### 🗄️ Database Integration
- Lưu trữ câu hỏi, kết quả vào SQLite/MySQL
- Lịch sử điểm số của học sinh
- Thống kê theo lớp, môn học

#### 🔐 User Authentication
- Đăng nhập/đăng ký cho học sinh
- Phân quyền giáo viên/học sinh
- Session management

#### 📚 Question Management
- CRUD operations (thêm/sửa/xóa câu hỏi)
- Import/Export từ Excel, CSV
- Ngân hàng câu hỏi theo chủ đề
- Random câu hỏi từ question pool

#### 🎯 Advanced Test Features
- Nhiều loại câu hỏi: multiple choice, true/false, fill-in-blank
- Câu hỏi có hình ảnh
- Negative marking (trừ điểm câu sai)
- Review đáp án sau khi thi

#### 📊 Reporting & Analytics
- Thống kê điểm số theo lớp
- Biểu đồ phân bố điểm
- Export kết quả ra Excel/PDF
- Phân tích câu hỏi khó/dễ

#### 🔒 Security Features
- Mã hóa dữ liệu (SSL/TLS)
- Chống gian lận (disable copy/paste)
- Full screen mode
- Webcam proctoring

#### 🌐 Network Protocols
- **UDP**: Real-time notifications
- **HTTP/HTTPS**: RESTful API
- **WebSocket**: Bidirectional communication
- **FTP**: File transfer (đề thi, tài liệu)

---

## 🐛 Troubleshooting

### Windows: "gcc is not recognized"
**Giải pháp:**
- Cài đặt MinGW-w64 hoặc TDM-GCC
- Thêm GCC vào PATH:
  ```
  Control Panel → System → Advanced → Environment Variables
  → Path → Add: C:\TDM-GCC-64\bin
  ```

### Linux/macOS: "Permission denied"
```bash
chmod +x build.sh
./build.sh
```

### Python: "ModuleNotFoundError: customtkinter"
```bash
pip install -r requirements.txt
# hoặc
pip install customtkinter
```

### "Network library not found"
**Kiểm tra:**
1. Build script đã chạy thành công chưa?
2. Thư mục `lib/` có file dll/so/dylib chưa?
3. File có đúng tên không?
   - Windows: `network.dll`
   - Linux: `libnetwork.so`
   - macOS: `libnetwork.dylib`

### Học sinh không kết nối được Server
**Kiểm tra:**
1. ✅ Server đã start chưa?
2. ✅ Host và port đúng chưa?
3. ✅ Firewall đã cho phép port chưa?
   ```bash
   # Windows: Mở port trong firewall
   netsh advfirewall firewall add rule name="Test Server" dir=in action=allow protocol=TCP localport=5000
   ```
4. ✅ Cùng mạng LAN chưa? (nếu test trên nhiều máy)

### Timer không hoạt động
- Đảm bảo không block main thread
- Kiểm tra threading
- Test trên Python 3.8+

---

## 📚 Tài liệu tham khảo

### Network Programming
- 📖 [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) - Bible của Socket Programming
- 📖 [GeeksforGeeks - Socket Programming](https://www.geeksforgeeks.org/socket-programming-cc/)
- 📖 [TCP/IP Illustrated](https://en.wikipedia.org/wiki/TCP/IP_Illustrated)

### Python & GUI
- 🐍 [Python ctypes Documentation](https://docs.python.org/3/library/ctypes.html)
- 🎨 [CustomTkinter Documentation](https://github.com/TomSchimansky/CustomTkinter)
- 🎨 [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)

### Tools & Libraries
- 🔧 [MinGW-w64](https://www.mingw-w64.org/)
- 🔧 [GCC Documentation](https://gcc.gnu.org/onlinedocs/)

---

## 👥 Đóng góp

Dự án này được tạo cho mục đích **học tập** môn Lập trình Mạng.

**Contributions are welcome!**
- 🐛 Report bugs
- 💡 Suggest features
- 🔨 Submit pull requests

---

## 📄 License

**Free for educational purposes.**

Dự án này được phát triển cho mục đích học tập và nghiên cứu. Bạn có thể tự do sử dụng, chỉnh sửa và phân phối cho các mục đích giáo dục.

---

## 🎓 Học được gì từ dự án này?

### C Programming
- ✅ Socket Programming (TCP/IP)
- ✅ Client-Server Architecture
- ✅ Network Protocol Design
- ✅ Cross-platform Development
- ✅ Memory Management

### Python Programming
- ✅ GUI Development (CustomTkinter)
- ✅ Multi-threading
- ✅ ctypes - C/Python Integration
- ✅ JSON Data Handling
- ✅ Event-driven Programming

### Network Concepts
- ✅ TCP Protocol
- ✅ Socket API
- ✅ Client-Server Model
- ✅ Message Protocol Design
- ✅ Concurrent Connections

---

<div align="center">

**Made with ❤️ for Network Programming Course**

⭐ Star this repo if you find it helpful!

</div>
