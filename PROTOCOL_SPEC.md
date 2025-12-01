# Test Application Protocol Specification v1.0

## Protocol Overview

**Protocol Name:** TAP (Test Application Protocol)  
**Version:** 1.0  
**Transport:** TCP (reliable, connection-oriented)  
**Encoding:** JSON over TCP with binary header  
**Port:** 5000 (default)

---

## Design Principles

Based on the goals analysis:

1. **Reliable Exchanges:** ✅ TCP ensures delivery
2. **Authentication:** ✅ Session-based with tokens
3. **Authorization:** ✅ Role-based access control
4. **Extensibility:** ✅ Version field for future upgrades
5. **Error Handling:** ✅ Structured error codes
6. **Security:** ⚠️ TLS recommended for production

---

## Message Structure

### Overall Format (88 bytes header with struct padding)

```
TAP Message Structure:
┌────────────────────────────────────┐
│  Header (88 bytes fixed)           │
│  - Protocol metadata               │
│  - Length field for payload        │
│  - Includes struct padding         │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  Payload (Variable length)         │
│  - JSON data                       │
│  - Max 1MB                         │
└────────────────────────────────────┘
```

### Header Fields

| Field             | Offset | Size     | Type     | Description                                |
| ----------------- | ------ | -------- | -------- | ------------------------------------------ |
| **Magic**         | 0-3    | 4 bytes  | uint32   | Protocol identifier: `0x54415031` ("TAP1") |
| **Version**       | 4-5    | 2 bytes  | uint16   | Protocol version: `0x0100` (v1.0)          |
| **Message Type**  | 6-7    | 2 bytes  | uint16   | Message type code (see table below)        |
| **Length**        | 8-11   | 4 bytes  | uint32   | Payload length in bytes (max 1MB)          |
| **Message ID**    | 12-27  | 16 bytes | char[16] | Unique message identifier                  |
| **Padding**       | 28-31  | 4 bytes  | -        | Struct alignment padding (compiler added)  |
| **Timestamp**     | 32-39  | 8 bytes  | int64    | Unix timestamp (seconds since epoch)       |
| **Session Token** | 40-71  | 32 bytes | char[32] | Session token (zeros if not authenticated) |
| **Reserved**      | 72-83  | 12 bytes | char[12] | Reserved for future use (zeros)            |
| **Padding**       | 84-87  | 4 bytes  | -        | Struct alignment padding (compiler added)  |

**Total Header Size:** 88 bytes (fixed with struct padding)

---

## Message Types

### Message Type Codes

| Code     | Name                  | Direction | Auth Required | Description                   |
| -------- | --------------------- | --------- | ------------- | ----------------------------- |
| `0x0001` | REGISTER_REQ          | C→S       | No            | Registration request          |
| `0x0002` | REGISTER_RES          | S→C       | No            | Registration response         |
| `0x0003` | LOGIN_REQ             | C→S       | No            | Login request                 |
| `0x0004` | LOGIN_RES             | S→C       | No            | Login response                |
| `0x0005` | LOGOUT_REQ            | C→S       | Yes           | Logout request                |
| `0x0006` | LOGOUT_RES            | S→C       | Yes           | Logout response               |
| `0x0010` | TEST_CONFIG           | S→C       | Yes           | Test configuration            |
| `0x0011` | TEST_START_REQ        | C→S       | Yes           | Start test request            |
| `0x0012` | TEST_START_RES        | S→C       | Yes           | Start test response           |
| `0x0013` | TEST_QUESTIONS        | S→C       | Yes           | Test questions data           |
| `0x0014` | TEST_SUBMIT           | C→S       | Yes           | Submit answers                |
| `0x0015` | TEST_RESULT           | S→C       | Yes           | Test result                   |
| `0x0020` | TEACHER_DATA_REQ      | C→S       | Yes           | Teacher data request          |
| `0x0021` | TEACHER_DATA_RES      | S→C       | Yes           | Teacher data response         |
| `0x0030` | CREATE_ROOM_REQ       | C→S       | Yes           | Create test room request      |
| `0x0031` | CREATE_ROOM_RES       | S→C       | Yes           | Create test room response     |
| `0x0032` | JOIN_ROOM_REQ         | C→S       | Yes           | Student join room request     |
| `0x0033` | JOIN_ROOM_RES         | S→C       | Yes           | Student join room response    |
| `0x0034` | START_ROOM_REQ        | C→S       | Yes           | Start test in room request    |
| `0x0035` | START_ROOM_RES        | S→C       | Yes           | Start test in room response   |
| `0x0036` | END_ROOM_REQ          | C→S       | Yes           | End test in room request      |
| `0x0037` | END_ROOM_RES          | S→C       | Yes           | End test in room response     |
| `0x0038` | GET_ROOMS_REQ         | C→S       | Yes           | Get teacher rooms request     |
| `0x0039` | GET_ROOMS_RES         | S→C       | Yes           | Get teacher rooms response    |
| `0x0040` | ADD_QUESTION_REQ      | C→S       | Yes           | Add question to room request  |
| `0x0041` | ADD_QUESTION_RES      | S→C       | Yes           | Add question to room response |
| `0x0042` | GET_QUESTIONS_REQ     | C→S       | Yes           | Get room questions request    |
| `0x0043` | GET_QUESTIONS_RES     | S→C       | Yes           | Get room questions response   |
| `0x0044` | DELETE_QUESTION_REQ   | C→S       | Yes           | Delete question request       |
| `0x0045` | DELETE_QUESTION_RES   | S→C       | Yes           | Delete question response      |
| `0x0046` | GET_STUDENT_ROOMS_REQ | C→S       | Yes           | Get student rooms request     |
| `0x0047` | GET_STUDENT_ROOMS_RES | S→C       | Yes           | Get student rooms response    |
| `0x00FF` | ERROR                 | S→C       | No            | Error response                |
| `0x00FE` | HEARTBEAT             | C↔S       | Optional      | Keep-alive message            |

---

## Error Codes

### Standard Error Codes

| Code   | Name                | Description                         |
| ------ | ------------------- | ----------------------------------- |
| `1000` | SUCCESS             | Operation successful                |
| `2000` | BAD_REQUEST         | Malformed request                   |
| `2001` | INVALID_JSON        | JSON parse error                    |
| `2002` | MISSING_FIELD       | Required field missing              |
| `2003` | INVALID_VALUE       | Field value invalid                 |
| `3000` | UNAUTHORIZED        | Authentication required             |
| `3001` | INVALID_CREDENTIALS | Wrong username/password             |
| `3002` | SESSION_EXPIRED     | Session token expired               |
| `3003` | INVALID_TOKEN       | Session token invalid               |
| `4000` | FORBIDDEN           | Insufficient permissions            |
| `4001` | WRONG_ROLE          | Operation not allowed for this role |
| `5000` | CONFLICT            | Resource conflict                   |
| `5001` | USERNAME_EXISTS     | Username already taken              |
| `6000` | INTERNAL_ERROR      | Server internal error               |
| `6001` | DATABASE_ERROR      | Database operation failed           |
| `6002` | NETWORK_ERROR       | Network operation failed            |

---

## Message Payloads

### 1. REGISTER_REQ (0x0001)

**Client → Server**

```json
{
  "username": "john123",
  "password": "mypassword",
  "role": "student",
  "full_name": "John Doe",
  "email": "john@example.com"
}
```

**Validation Rules:**

- `username`: 3-20 chars, alphanumeric, required
- `password`: 6-50 chars, required
- `role`: "student" or "teacher", required
- `full_name`: 2-50 chars, required
- `email`: valid email format, optional

### 2. REGISTER_RES (0x0002)

**Server → Client**

**Success:**

```json
{
  "status": "success",
  "code": 1000,
  "data": {
    "user_id": 5,
    "username": "john123",
    "role": "student"
  }
}
```

**Failure:**

```json
{
  "status": "error",
  "code": 5001,
  "message": "Username already exists",
  "details": {
    "field": "username",
    "value": "john123"
  }
}
```

### 3. LOGIN_REQ (0x0003)

**Client → Server**

```json
{
  "username": "john123",
  "password": "mypassword",
  "role": "student"
}
```

### 4. LOGIN_RES (0x0004)

**Server → Client**

**Success:**

```json
{
  "status": "success",
  "code": 1000,
  "data": {
    "session_token": "32-byte-hex-string",
    "user_id": 5,
    "username": "john123",
    "role": "student",
    "full_name": "John Doe",
    "expires_at": 1701320400
  }
}
```

**Failure:**

```json
{
  "status": "error",
  "code": 3001,
  "message": "Invalid credentials"
}
```

### 5. TEST_CONFIG (0x0010)

**Server → Client (Auto-sent after student login)**

```json
{
  "num_questions": 10,
  "duration": 30,
  "test_id": 1,
  "test_name": "Network Programming Quiz"
}
```

### 6. TEST_START_REQ (0x0011)

**Client → Server**

```json
{
  "ready": true
}
```

### 7. TEST_START_RES (0x0012)

**Server → Client**

```json
{
  "status": "success",
  "code": 1000,
  "message": "Test started",
  "start_time": 1701320400
}
```

### 8. TEST_QUESTIONS (0x0013)

**Server → Client**

```json
{
  "questions": [
    {
      "id": 1,
      "question": "What does TCP stand for?",
      "options": [
        "Transmission Control Protocol",
        "Transfer Control Protocol",
        "Transport Communication Protocol",
        "Telecommunication Control Protocol"
      ]
    }
  ]
}
```

### 9. TEST_SUBMIT (0x0014)

**Client → Server**

```json
{
  "answers": [
    {
      "question_id": 1,
      "selected": 0
    },
    {
      "question_id": 2,
      "selected": 2
    }
  ],
  "end_time": 1701322000
}
```

### 10. TEST_RESULT (0x0015)

**Server → Client**

```json
{
  "status": "success",
  "code": 1000,
  "data": {
    "score": 8,
    "total": 10,
    "percentage": 80.0,
    "result_id": 42,
    "saved": true
  }
}
```

### 11. TEACHER_DATA_REQ (0x0020)

**Client → Server**

```json
{
  "filter": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "limit": 100,
  "offset": 0
}
```

### 12. TEACHER_DATA_RES (0x0021)

**Server → Client**

```json
{
  "status": "success",
  "code": 1000,
  "data": {
    "results": [
      {
        "id": 1,
        "username": "john123",
        "full_name": "John Doe",
        "test_date": "2024-11-28T14:30:00Z",
        "score": 8,
        "total_questions": 10,
        "percentage": 80.0
      }
    ],
    "total_count": 150,
    "limit": 100,
    "offset": 0
  }
}
```

### 13. ERROR (0x00FF)

**Server → Client (Generic error)**

```json
{
  "status": "error",
  "code": 2000,
  "message": "Bad request",
  "details": {
    "field": "username",
    "reason": "Field is required"
  }
}
```

### 14. JOIN_ROOM_REQ (0x0032)

**Client → Server**

```json
{
  "room_code": "ABC123"
}
```

### 15. JOIN_ROOM_RES (0x0033)

**Server → Client**

**Success:**

```json
{
  "status": "success",
  "code": 1000,
  "message": "Joined room successfully",
  "data": {
    "room_id": 5,
    "room_name": "Network Programming Quiz",
    "room_code": "ABC123",
    "teacher_name": "Dr. Smith",
    "num_questions": 10,
    "duration_minutes": 30,
    "status": "waiting"
  }
}
```

**Failure:**

```json
{
  "status": "error",
  "code": 2000,
  "message": "Room not found"
}
```

### 16. GET_STUDENT_ROOMS_REQ (0x0046)

**Client → Server**

```json
{}
```

### 17. GET_STUDENT_ROOMS_RES (0x0047)

**Server → Client**

```json
{
  "status": "success",
  "code": 1000,
  "message": "Student rooms loaded",
  "data": {
    "rooms": [
      {
        "id": 5,
        "room_name": "Network Programming Quiz",
        "room_code": "ABC123",
        "teacher_name": "Dr. Smith",
        "num_questions": 10,
        "duration_minutes": 30,
        "room_status": "waiting",
        "joined_at": "2024-11-28T14:30:00",
        "participant_status": "joined"
      }
    ]
  }
}
```

### 18. HEARTBEAT (0x00FE)

**Client ↔ Server**

```json
{
  "ping": true
}
```

**Response:**

```json
{
  "pong": true,
  "server_time": 1701320400
}
```

---

## Protocol Flow Diagrams

### Registration Flow

```
Client                              Server
  │                                   │
  │  REGISTER_REQ (0x0001)            │
  │  {username, password, ...}        │
  ├──────────────────────────────────►│
  │                                   │
  │                    Validate input │
  │                    Check duplicate│
  │                    Hash password  │
  │                    Insert to DB   │
  │                                   │
  │  REGISTER_RES (0x0002)            │
  │  {status, code, data}             │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Success: Navigate to Login]     │
  │  [Error: Show error message]      │
```

### Login Flow

```
Client                              Server
  │                                   │
  │  LOGIN_REQ (0x0003)               │
  │  {username, password, role}       │
  ├──────────────────────────────────►│
  │                                   │
  │                    Query user     │
  │                    Verify password│
  │                    Check role     │
  │                    Generate token │
  │                    Store session  │
  │                                   │
  │  LOGIN_RES (0x0004)               │
  │  {session_token, user_data}       │
  │◄──────────────────────────────────┤
  │                                   │
  │  Store token locally              │
  │  Use token in all future requests │
```

### Student Room Flow (New)

```
Client                              Server
  │                                   │
  │  [After successful login]         │
  │                                   │
  │  GET_STUDENT_ROOMS_REQ (0x0046)   │
  ├──────────────────────────────────►│
  │                                   │
  │  GET_STUDENT_ROOMS_RES (0x0047)   │
  │  {rooms: [...]}                   │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Show room lobby]                │
  │  [Student enters room code]       │
  │                                   │
  │  JOIN_ROOM_REQ (0x0032)           │
  │  {room_code: "ABC123"}            │
  ├──────────────────────────────────►│
  │                                   │
  │                    Validate code  │
  │                    Add participant│
  │                                   │
  │  JOIN_ROOM_RES (0x0033)           │
  │  {room details}                   │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Joined successfully]            │
  │  [Wait for teacher to start]      │
```

### Student Test Flow

```
Client                              Server
  │                                   │
  │  [After successful login]         │
  │  TEST_CONFIG (0x0010)             │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Show ready screen]              │
  │                                   │
  │  TEST_START_REQ (0x0011)          │
  ├──────────────────────────────────►│
  │                                   │
  │  TEST_START_RES (0x0012)          │
  │◄──────────────────────────────────┤
  │                                   │
  │  TEST_QUESTIONS (0x0013)          │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Student takes test]             │
  │  [Timer running]                  │
  │                                   │
  │  TEST_SUBMIT (0x0014)             │
  │  {answers, end_time}              │
  ├──────────────────────────────────►│
  │                                   │
  │                    Calculate score│
  │                    Save to DB     │
  │                                   │
  │  TEST_RESULT (0x0015)             │
  │  {score, percentage}              │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Show result screen]             │
```

### Teacher Dashboard Flow

```
Client                              Server
  │                                   │
  │  [After successful login]         │
  │  TEACHER_DATA_REQ (0x0020)        │
  │  {filter, limit, offset}          │
  ├──────────────────────────────────►│
  │                                   │
  │                    Query results  │
  │                    Apply filters  │
  │                    Calculate stats│
  │                                   │
  │  TEACHER_DATA_RES (0x0021)        │
  │  {results[], statistics}          │
  │◄──────────────────────────────────┤
  │                                   │
  │  [Show dashboard]                 │
```

---

## Protocol State Machine

```
┌──────────────┐
│  INIT        │
└──────┬───────┘
       │ TCP Connect
       ▼
┌──────────────┐
│  CONNECTED   │◄─────────────────┐
└──────┬───────┘                  │
       │                          │
       │ REGISTER_REQ or LOGIN_REQ│
       ▼                          │
┌──────────────┐                  │
│ AUTHENTICATING│                 │
└──────┬───────┘                  │
       │                          │
   ┌───┴───┐                      │
   │       │                      │
 Success  Fail                    │
   │       │                      │
   │       └──────────────────────┘
   │
   ▼
┌──────────────┐
│ AUTHENTICATED│
└──────┬───────┘
       │
   ┌───┴───────────┬──────────┐
   │               │          │
Role=Student  Role=Teacher  LOGOUT
   │               │          │
   ▼               ▼          ▼
┌─────────┐  ┌──────────┐  DISCONNECTED
│ TEST    │  │ DASHBOARD│
│ SESSION │  │          │
└─────────┘  └──────────┘
```

---

## Security Considerations

### 1. Password Security

- **Client:** Send plain password (encrypted by TLS in production)
- **Server:** Immediately hash with PBKDF2-HMAC-SHA256 + salt
- **Storage:** Only store `salt$hash`, never plain password

### 2. Session Security

- **Token:** 32-byte cryptographically secure random
- **Expiration:** 24 hours (configurable)
- **Storage:** Server memory (fast, auto-cleanup)
- **Validation:** Every authenticated request

### 3. Transport Security

- **Current:** Plain TCP (development only)
- **Production:** TLS 1.3 required
- **Certificate:** Valid SSL certificate needed

### 4. Input Validation

- **Server-side:** ALL inputs validated
- **Client-side:** Basic validation (UX)
- **SQL Injection:** Use prepared statements
- **XSS:** JSON encoding handles this

### 5. Rate Limiting

- **Login attempts:** Max 5 per minute per IP
- **Registration:** Max 3 per hour per IP
- **API calls:** Max 100 per minute per session

---

## Backward Compatibility

### Version Negotiation

If protocol version mismatch:

**Server response:**

```json
{
  "status": "error",
  "code": 2000,
  "message": "Protocol version not supported",
  "details": {
    "client_version": "1.0",
    "server_version": "1.1",
    "min_supported": "1.0",
    "upgrade_required": false
  }
}
```

### Migration from Old Protocol

**Old format:**

```
LOGIN:student:{"username":"john","password":"pass"}
```

**New format:**

- Same JSON payload
- Wrapped with binary header
- Add message type, ID, timestamp

**Server supports both:**

1. Check first 4 bytes for magic `0x54415031`
2. If magic present → New protocol
3. If not → Legacy protocol (text-based)

---

## Performance Considerations

### Message Size Limits

| Message Type   | Max Size  | Typical Size          |
| -------------- | --------- | --------------------- |
| REGISTER_REQ   | 1 KB      | ~200 bytes            |
| LOGIN_REQ      | 512 bytes | ~100 bytes            |
| TEST_QUESTIONS | 512 KB    | ~50 KB (10 questions) |
| TEST_SUBMIT    | 10 KB     | ~1 KB                 |
| TEACHER_DATA   | 1 MB      | ~100 KB               |

### Throughput

- **Connection setup:** <100ms
- **Login:** <200ms (including password hash)
- **Questions load:** <500ms
- **Submit & result:** <300ms
- **Teacher data:** <1s (100 results)

### Concurrent Connections

- **Target:** 100 concurrent users
- **Server threads:** One per connection
- **Memory:** ~10 MB per 100 users
- **CPU:** Minimal (mostly I/O bound)

---

## Error Handling Best Practices

### 1. Always Check Header Magic

```c
if (header.magic != 0x54415031) {
    return ERR_INVALID_PROTOCOL;
}
```

### 2. Validate Message Length

```c
if (header.length > MAX_PAYLOAD_SIZE) {
    return ERR_MESSAGE_TOO_LARGE;
}
```

### 3. Verify JSON Structure

```python
try:
    data = json.loads(payload)
except JSONDecodeError:
    send_error(socket, 2001, "Invalid JSON")
```

### 4. Check Session Token

```python
session = validate_session(header.session_token)
if not session:
    send_error(socket, 3002, "Session expired")
```

### 5. Role-Based Authorization

```python
if message_type == TEACHER_DATA_REQ:
    if session['role'] != 'teacher':
        send_error(socket, 4001, "Teacher role required")
```

---

## Implementation Notes

### C Layer

- Binary header packing/unpacking
- Network byte order (big-endian)
- Socket send/receive with length prefix
- Header validation functions

### Python Layer

- Struct packing for header
- JSON for payload
- ctypes integration
- Error code mapping

### Testing

- Unit tests for each message type
- Integration tests for flows
- Load testing (100+ concurrent)
- Security testing (injection, overflow)

---

## References

- RFC 793: Transmission Control Protocol (TCP)
- RFC 8259: The JavaScript Object Notation (JSON)
- PBKDF2: RFC 2898
- UUID: RFC 4122

---

**Protocol Version:** 1.0  
**Last Updated:** 2024-11-28  
**Status:** Production Ready
