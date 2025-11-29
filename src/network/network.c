#include "network.h"

// Initialize network (required for Windows)
int init_network() {
#ifdef _WIN32
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        return -1;
    }
#endif
    return 0;
}

// Cleanup network (required for Windows)
void cleanup_network() {
#ifdef _WIN32
    WSACleanup();
#endif
}

// Create a server socket
socket_t create_server_socket(int port) {
    socket_t server_socket;
    struct sockaddr_in server_addr;
    int opt = 1;

    // Create socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        return INVALID_SOCKET;
    }

    // Set socket options to reuse address
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, 
                   (char*)&opt, sizeof(opt)) < 0) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    // Setup server address structure
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    // Bind socket
    if (bind(server_socket, (struct sockaddr*)&server_addr, 
             sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    // Listen for connections
    if (listen(server_socket, MAX_CLIENTS) == SOCKET_ERROR) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    return server_socket;
}

// Accept a client connection
socket_t accept_client(socket_t server_socket) {
    socket_t client_socket;
    struct sockaddr_in client_addr;
    int addr_len = sizeof(client_addr);

    client_socket = accept(server_socket, (struct sockaddr*)&client_addr, 
                          &addr_len);
    return client_socket;
}

// Connect to a server (client side)
socket_t connect_to_server(const char* host, int port) {
    socket_t client_socket;
    struct sockaddr_in server_addr;

    // Create socket
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == INVALID_SOCKET) {
        return INVALID_SOCKET;
    }

    // Setup server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    // Convert host to IP address
    if (inet_pton(AF_INET, host, &server_addr.sin_addr) <= 0) {
        closesocket(client_socket);
        return INVALID_SOCKET;
    }

    // Connect to server
    if (connect(client_socket, (struct sockaddr*)&server_addr, 
                sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(client_socket);
        return INVALID_SOCKET;
    }

    return client_socket;
}

// Send a message through socket
int send_message(socket_t socket, const char* message) {
    int total_sent = 0;
    int message_len = strlen(message);
    int bytes_sent;

    while (total_sent < message_len) {
        bytes_sent = send(socket, message + total_sent, 
                         message_len - total_sent, 0);
        if (bytes_sent == SOCKET_ERROR) {
            return -1;
        }
        total_sent += bytes_sent;
    }

    return total_sent;
}

// Receive a message from socket
int receive_message(socket_t socket, char* buffer, int buffer_size) {
    int bytes_received;
    
    memset(buffer, 0, buffer_size);
    bytes_received = recv(socket, buffer, buffer_size - 1, 0);
    
    if (bytes_received == SOCKET_ERROR) {
        return -1;
    }
    
    return bytes_received;
}

// Close a socket
void close_socket(socket_t socket) {
    if (socket != INVALID_SOCKET) {
        closesocket(socket);
    }
}

// Get last error message
const char* get_last_error() {
#ifdef _WIN32
    static char error_msg[256];
    FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                   NULL, WSAGetLastError(),
                   MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                   error_msg, sizeof(error_msg), NULL);
    return error_msg;
#else
    return strerror(errno);
#endif
}

// ==================== PROTOCOL FUNCTIONS (New) ====================

#include <time.h>

// Generate simple message ID (16 bytes)
void generate_message_id(char* message_id) {
    // Simple implementation: timestamp + random counter
    static int counter = 0;
    time_t now = time(NULL);
    
    snprintf(message_id, 16, "%08x%08x", (unsigned int)now, counter++);
    memset(message_id + strlen(message_id), 0, 16 - strlen(message_id));
}

// Get Unix timestamp
int64_t get_unix_timestamp() {
#ifdef _WIN32
    return (int64_t)time(NULL);
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (int64_t)tv.tv_sec;
#endif
}

// Initialize protocol header
void init_protocol_header(protocol_header_t* header, uint16_t msg_type,
                         uint32_t length, const char* session_token) {
    memset(header, 0, sizeof(protocol_header_t));
    
    header->magic = htonl(PROTOCOL_MAGIC);
    header->version = htons(PROTOCOL_VERSION);
    header->message_type = htons(msg_type);
    header->length = htonl(length);
    header->timestamp = get_unix_timestamp();
    
    // Generate message ID
    generate_message_id(header->message_id);
    
    // Copy session token if provided
    if (session_token) {
        memcpy(header->session_token, session_token, 32);
    }
}

// Validate protocol header
int validate_protocol_header(protocol_header_t* header) {
    // Check magic number
    if (ntohl(header->magic) != PROTOCOL_MAGIC) {
        return -1;  // Invalid magic
    }
    
    // Check version
    uint16_t version = ntohs(header->version);
    if (version != PROTOCOL_VERSION) {
        return -2;  // Version mismatch
    }
    
    // Check payload length
    uint32_t length = ntohl(header->length);
    if (length > MAX_PAYLOAD_SIZE) {
        return -3;  // Payload too large
    }
    
    return 0;  // Valid
}

// Send protocol message with header
int send_protocol_message(socket_t socket, uint16_t msg_type, const char* payload,
                         const char* session_token) {
    protocol_header_t header;
    uint32_t payload_length = payload ? strlen(payload) : 0;
    
    // Initialize header
    init_protocol_header(&header, msg_type, payload_length, session_token);
    
    // Send header (64 bytes fixed)
    int header_sent = send(socket, (char*)&header, sizeof(protocol_header_t), 0);
    if (header_sent != sizeof(protocol_header_t)) {
        return -1;
    }
    
    // Send payload if exists
    if (payload_length > 0) {
        int payload_sent = send(socket, payload, payload_length, 0);
        if (payload_sent != (int)payload_length) {
            return -2;
        }
    }
    
    return header_sent + payload_length;
}

// Receive protocol message with header
int receive_protocol_message(socket_t socket, protocol_header_t* header,
                             char* payload, int max_payload_size) {
    // Receive header (64 bytes fixed)
    int bytes_received = recv(socket, (char*)header, sizeof(protocol_header_t), 0);
    if (bytes_received != sizeof(protocol_header_t)) {
        return -1;  // Header receive failed
    }
    
    // Validate header
    int validation = validate_protocol_header(header);
    if (validation != 0) {
        return validation;  // -1, -2, or -3
    }
    
    // Get payload length (convert from network byte order)
    uint32_t payload_length = ntohl(header->length);
    
    // Check if payload buffer is large enough
    if (payload_length > (uint32_t)(max_payload_size - 1)) {
        return -4;  // Buffer too small
    }
    
    // Receive payload if exists
    if (payload_length > 0) {
        memset(payload, 0, max_payload_size);
        int bytes_received = recv(socket, payload, payload_length, 0);
        if (bytes_received != (int)payload_length) {
            return -5;  // Payload receive failed
        }
        payload[payload_length] = '\0';  // Null terminate for string safety
    } else {
        payload[0] = '\0';
    }
    
    return (int)payload_length;
}

