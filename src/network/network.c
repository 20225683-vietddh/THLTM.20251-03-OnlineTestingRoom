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

