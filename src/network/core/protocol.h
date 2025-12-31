#ifndef PROTOCOL_H
#define PROTOCOL_H

#include "socket_ops.h"
#include <stdint.h>

// ==================== PROTOCOL CONSTANTS ====================

#define PROTOCOL_MAGIC 0x54415031      // "TAP1" in hex
#define PROTOCOL_VERSION 0x0100        // v1.0
#define MAX_PAYLOAD_SIZE 1048576       // 1 MB maximum payload

// Message Types - Authentication
#define MSG_REGISTER_REQ 0x0001
#define MSG_REGISTER_RES 0x0002
#define MSG_LOGIN_REQ 0x0003
#define MSG_LOGIN_RES 0x0004
#define MSG_LOGOUT_REQ 0x0005
#define MSG_LOGOUT_RES 0x0006

// Message Types - Test Flow (Legacy)
#define MSG_TEST_CONFIG 0x0010
#define MSG_TEST_START_REQ 0x0011
#define MSG_TEST_START_RES 0x0012
#define MSG_TEST_QUESTIONS 0x0013
#define MSG_TEST_SUBMIT 0x0014
#define MSG_TEST_RESULT 0x0015

// Message Types - Teacher
#define MSG_TEACHER_DATA_REQ 0x0020
#define MSG_TEACHER_DATA_RES 0x0021

// Message Types - Room Management
#define MSG_CREATE_ROOM_REQ  0x0030
#define MSG_CREATE_ROOM_RES  0x0031
#define MSG_JOIN_ROOM_REQ    0x0032
#define MSG_JOIN_ROOM_RES    0x0033
#define MSG_START_ROOM_REQ   0x0034
#define MSG_START_ROOM_RES   0x0035
#define MSG_END_ROOM_REQ     0x0036
#define MSG_END_ROOM_RES     0x0037
#define MSG_GET_ROOMS_REQ    0x0038
#define MSG_GET_ROOMS_RES    0x0039
#define MSG_ROOM_STATUS      0x003A

// Message Types - Questions
#define MSG_ADD_QUESTION_REQ    0x0040
#define MSG_ADD_QUESTION_RES    0x0041
#define MSG_GET_QUESTIONS_REQ   0x0042
#define MSG_GET_QUESTIONS_RES   0x0043
#define MSG_DELETE_QUESTION_REQ 0x0044
#define MSG_DELETE_QUESTION_RES 0x0045

// Message Types - Student Rooms
#define MSG_GET_STUDENT_ROOMS_REQ   0x0046
#define MSG_GET_STUDENT_ROOMS_RES   0x0047
#define MSG_GET_AVAILABLE_ROOMS_REQ 0x0048
#define MSG_GET_AVAILABLE_ROOMS_RES 0x0049

// Message Types - Room Testing
#define MSG_START_ROOM_TEST_REQ  0x004A
#define MSG_START_ROOM_TEST_RES  0x004B
#define MSG_SUBMIT_ROOM_TEST_REQ 0x004C
#define MSG_SUBMIT_ROOM_TEST_RES 0x004D
#define MSG_AUTO_SAVE_REQ        0x004E
#define MSG_AUTO_SAVE_RES        0x004F

// Message Types - Control
#define MSG_ERROR     0x00FF
#define MSG_HEARTBEAT 0x00FE

// Error Codes
#define ERR_SUCCESS         1000
#define ERR_BAD_REQUEST     2000
#define ERR_INVALID_JSON    2001
#define ERR_UNAUTHORIZED    3000
#define ERR_INVALID_CREDS   3001
#define ERR_SESSION_EXPIRED 3002
#define ERR_FORBIDDEN       4000
#define ERR_WRONG_ROLE      4001
#define ERR_CONFLICT        5000
#define ERR_USERNAME_EXISTS 5001
#define ERR_INTERNAL        6000

typedef struct {
    uint32_t magic;              // 4 bytes: Protocol identifier (0x54415031)
    uint16_t version;            // 2 bytes: Protocol version (0x0100)
    uint16_t message_type;       // 2 bytes: Message type code
    uint32_t length;             // 4 bytes: Payload length in bytes
    char message_id[16];         // 16 bytes: Unique message identifier
                                 // 4 bytes: Padding (compiler added for int64_t alignment)
    int64_t timestamp;           // 8 bytes: Unix timestamp (seconds since epoch)
    char session_token[32];      // 32 bytes: Session token (or zeros if not authenticated)
    char reserved[12];           // 12 bytes: Reserved for future use (zeros)
                                 // 4 bytes: Padding (compiler added for struct alignment)
} protocol_header_t;             // Total: 88 bytes with padding

/**
 * @brief Initialize protocol header
 * @param header Pointer to header structure
 * @param msg_type Message type code
 * @param length Payload length in bytes
 * @param session_token Session token (NULL if not authenticated)
 */
void protocol_init_header(protocol_header_t* header, uint16_t msg_type,
                          uint32_t length, const char* session_token);

/**
 * @brief Validate protocol header
 * @param header Pointer to header structure
 * @return 0 on success, -1 invalid magic, -2 version mismatch, -3 payload too large
 */
int protocol_validate_header(protocol_header_t* header);

/**
 * @brief Send protocol message (header + payload)
 * @param socket Socket descriptor
 * @param msg_type Message type code
 * @param payload Payload data (NULL if none)
 * @param session_token Session token (NULL if not authenticated)
 * @return Bytes sent on success, -1 header failed, -2 payload failed
 */
int protocol_send_message(socket_t socket, uint16_t msg_type, 
                          const char* payload, const char* session_token);

/**
 * @brief Receive protocol message (header + payload)
 * @param socket Socket descriptor
 * @param header Pointer to header structure
 * @param payload Buffer to store payload
 * @param max_payload_size Maximum payload size
 * @return Payload length on success, -1 recv failed, -2 invalid magic, -3 version mismatch, -4 too large, -5 payload failed
 */
int protocol_receive_message(socket_t socket, protocol_header_t* header,
                             char* payload, int max_payload_size);

#endif // PROTOCOL_H
