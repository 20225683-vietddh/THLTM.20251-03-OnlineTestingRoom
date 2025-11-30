#ifndef NETWORK_H
#define NETWORK_H

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    typedef SOCKET socket_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    typedef int socket_t;
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>  // For uint32_t, uint16_t, int64_t

// Constants
#define BUFFER_SIZE 8192
#define MAX_CLIENTS 10
#define MAX_PAYLOAD_SIZE 1048576  // 1 MB
#define PROTOCOL_MAGIC 0x54415031  // "TAP1"
#define PROTOCOL_VERSION 0x0100    // v1.0

// Message Types
#define MSG_REGISTER_REQ 0x0001
#define MSG_REGISTER_RES 0x0002
#define MSG_LOGIN_REQ 0x0003
#define MSG_LOGIN_RES 0x0004
#define MSG_LOGOUT_REQ 0x0005
#define MSG_LOGOUT_RES 0x0006
#define MSG_TEST_CONFIG 0x0010
#define MSG_TEST_START_REQ 0x0011
#define MSG_TEST_START_RES 0x0012
#define MSG_TEST_QUESTIONS 0x0013
#define MSG_TEST_SUBMIT 0x0014
#define MSG_TEST_RESULT 0x0015
#define MSG_TEACHER_DATA_REQ 0x0020
#define MSG_TEACHER_DATA_RES 0x0021
// Test Room Management
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
#define MSG_ERROR           0x00FF
#define MSG_HEARTBEAT       0x00FE

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

// Protocol Header Structure (64 bytes)
typedef struct {
    uint32_t magic;              // 4 bytes: 0x54415031
    uint16_t version;            // 2 bytes: 0x0100
    uint16_t message_type;       // 2 bytes: Message type code
    uint32_t length;             // 4 bytes: Payload length
    char message_id[16];         // 16 bytes: UUID
    int64_t timestamp;           // 8 bytes: Unix timestamp
    char session_token[32];      // 32 bytes: Session token or zeros
    char reserved[12];           // 12 bytes: Reserved (zeros)
} protocol_header_t;

// Network initialization
int init_network();
void cleanup_network();

// Server functions
socket_t create_server_socket(int port);
socket_t accept_client(socket_t server_socket);
int send_message(socket_t socket, const char* message);
int receive_message(socket_t socket, char* buffer, int buffer_size);
void close_socket(socket_t socket);

// Client functions
socket_t connect_to_server(const char* host, int port);

// Protocol functions (New)
int send_protocol_message(socket_t socket, uint16_t msg_type, const char* payload, 
                          const char* session_token);
int receive_protocol_message(socket_t socket, protocol_header_t* header, 
                             char* payload, int max_payload_size);
void init_protocol_header(protocol_header_t* header, uint16_t msg_type, 
                         uint32_t length, const char* session_token);
int validate_protocol_header(protocol_header_t* header);

// Utility functions
const char* get_last_error();
void generate_message_id(char* message_id);  // Generate 16-byte UUID
int64_t get_unix_timestamp();  // Get current Unix timestamp

#endif // NETWORK_H

