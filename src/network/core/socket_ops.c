#include "socket_ops.h"
#include <stdio.h>
#include <string.h>

// ==================== INITIALIZATION ====================

int socket_init_network(void) {
#ifdef _WIN32
    WSADATA wsa_data;
    // Initialize Winsock 2.2
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        return -1;
    }
#endif
    return 0;
}

void socket_cleanup_network(void) {
#ifdef _WIN32
    WSACleanup();
#endif
}

// ==================== SERVER OPERATIONS ====================

socket_t socket_create_server(int port) {
    socket_t server_socket;
    struct sockaddr_in server_addr;
    int opt = 1;

    // Step 1: Create TCP socket (SOCK_STREAM = TCP, AF_INET = IPv4)
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        return INVALID_SOCKET;
    }

    // Step 2: Set SO_REUSEADDR to allow immediate reuse of port
    // Useful during development - avoids "Address already in use" error
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, 
                   (char*)&opt, sizeof(opt)) < 0) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    // Step 3: Setup server address structure
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;           // IPv4
    server_addr.sin_addr.s_addr = INADDR_ANY;   // Bind to all interfaces (0.0.0.0)
    server_addr.sin_port = htons(port);         // Convert port to network byte order

    // Step 4: Bind socket to local address and port
    // Associates the socket with a specific port on the local machine
    if (bind(server_socket, (struct sockaddr*)&server_addr, 
             sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    // Step 5: Listen for incoming connections
    // Marks socket as passive - ready to accept connections
    // Backlog queue of MAX_CLIENTS pending connections
    if (listen(server_socket, MAX_CLIENTS) == SOCKET_ERROR) {
        closesocket(server_socket);
        return INVALID_SOCKET;
    }

    return server_socket;
}

socket_t socket_accept_client(socket_t server_socket) {
    socket_t client_socket;
    struct sockaddr_in client_addr;
    
#ifdef _WIN32
    int addr_len = sizeof(client_addr);
#else
    socklen_t addr_len = sizeof(client_addr);
#endif

    // Accept incoming connection (BLOCKING call)
    // Completes the 3-way TCP handshake:
    // Client -> Server: SYN
    // Server -> Client: SYN-ACK
    // Client -> Server: ACK
    client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &addr_len);
    
    return client_socket;
}

// ==================== CLIENT OPERATIONS ====================

socket_t socket_connect_to_server(const char* host, int port) {
    socket_t client_socket;
    struct sockaddr_in server_addr;

    // Step 1: Create TCP socket
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == INVALID_SOCKET) {
        return INVALID_SOCKET;
    }

    // Step 2: Setup server address structure
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    // Convert IP address from string to binary form
    // Using inet_addr for compatibility with older Windows/MinGW
    unsigned long addr = inet_addr(host);
    if (addr == INADDR_NONE) {
        closesocket(client_socket);
        return INVALID_SOCKET;
    }
    server_addr.sin_addr.s_addr = addr;

    // Step 3: Connect to server (initiates 3-way handshake)
    if (connect(client_socket, (struct sockaddr*)&server_addr, 
                sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(client_socket);
        return INVALID_SOCKET;
    }

    return client_socket;
}

// ==================== DATA TRANSMISSION ====================

int socket_send_data(socket_t socket, const char* data, int length) {
    int total_sent = 0;
    int bytes_sent;

    // Validate input
    if (!data || length <= 0) {
        return -1;
    }

    // Loop until all data is sent (TCP may send partial data)
    while (total_sent < length) {
        bytes_sent = send(socket, data + total_sent, length - total_sent, 0);
        
        if (bytes_sent == SOCKET_ERROR) {
            return -1;  // Network error
        }
        
        if (bytes_sent == 0) {
            return -1;  // Connection closed by peer
        }
        
        total_sent += bytes_sent;
    }

    return total_sent;
}

int socket_receive_data(socket_t socket, char* buffer, int buffer_size) {
    int total_received = 0;
    int bytes_received;
    
    // Validate input
    if (!buffer || buffer_size <= 0) {
        return -1;
    }
    
    // Loop until all requested bytes received (TCP stream may be fragmented)
    while (total_received < buffer_size) {
        bytes_received = recv(socket, buffer + total_received, 
                             buffer_size - total_received, 0);
        
        if (bytes_received == 0) {
            // Connection closed by peer - return partial data
            return total_received;
        }
        
        if (bytes_received == SOCKET_ERROR) {
            return -1;  // Network error
        }
        
        total_received += bytes_received;
    }
    
    return total_received;
}

// ==================== CONNECTION MANAGEMENT ====================

int socket_is_alive(socket_t socket) {
    // Use MSG_PEEK to check without consuming data
    // MSG_DONTWAIT/O_NONBLOCK for non-blocking check
    char buf[1];
    
#ifdef _WIN32
    // Windows: Use ioctlsocket to set non-blocking temporarily
    u_long mode = 1;  // Non-blocking
    ioctlsocket(socket, FIONBIO, &mode);
    
    int result = recv(socket, buf, 1, MSG_PEEK);
    
    // Restore blocking mode
    mode = 0;
    ioctlsocket(socket, FIONBIO, &mode);
    
    if (result == 0) {
        return 0;  // Connection closed gracefully
    }
    
    if (result == SOCKET_ERROR) {
        int error = WSAGetLastError();
        if (error == WSAEWOULDBLOCK) {
            return 1;  // No data available but connection alive
        }
        return 0;  // Error = connection dead
    }
    
    return 1;  // Has data = alive
#else
    // Linux/Unix: Use MSG_DONTWAIT flag
    int result = recv(socket, buf, 1, MSG_PEEK | MSG_DONTWAIT);
    
    if (result == 0) {
        return 0;  // Connection closed gracefully
    }
    
    if (result == SOCKET_ERROR) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 1;  // No data available but connection alive
        }
        return 0;  // Error = connection dead
    }
    
    return 1;  // Has data = alive
#endif
}

int socket_get_client_ip(socket_t socket, char* ip_buffer) {
    if (!ip_buffer) {
        return -1;
    }
    
    struct sockaddr_in addr;
#ifdef _WIN32
    int addr_len = sizeof(addr);
#else
    socklen_t addr_len = sizeof(addr);
#endif
    
    // Get peer address
    if (getpeername(socket, (struct sockaddr*)&addr, &addr_len) == SOCKET_ERROR) {
        return -1;
    }
    
    // Convert to string (IPv4)
    const char* ip_str = inet_ntoa(addr.sin_addr);
    if (ip_str) {
        strncpy(ip_buffer, ip_str, 16);
        ip_buffer[15] = '\0';  // Ensure null-terminated
        return 0;
    }
    
    return -1;
}

int socket_set_recv_timeout(socket_t socket, int seconds) {
#ifdef _WIN32
    // Windows: timeout in milliseconds (DWORD)
    DWORD timeout = seconds * 1000;
    if (setsockopt(socket, SOL_SOCKET, SO_RCVTIMEO, 
                   (const char*)&timeout, sizeof(timeout)) == SOCKET_ERROR) {
        return -1;
    }
#else
    // UNIX/Linux: timeout in struct timeval
    struct timeval timeout;
    timeout.tv_sec = seconds;
    timeout.tv_usec = 0;
    if (setsockopt(socket, SOL_SOCKET, SO_RCVTIMEO, 
                   &timeout, sizeof(timeout)) < 0) {
        return -1;
    }
#endif
    return 0;
}

int socket_set_send_timeout(socket_t socket, int seconds) {
#ifdef _WIN32
    // Windows: timeout in milliseconds (DWORD)
    DWORD timeout = seconds * 1000;
    if (setsockopt(socket, SOL_SOCKET, SO_SNDTIMEO, 
                   (const char*)&timeout, sizeof(timeout)) == SOCKET_ERROR) {
        return -1;
    }
#else
    // UNIX/Linux: timeout in struct timeval
    struct timeval timeout;
    timeout.tv_sec = seconds;
    timeout.tv_usec = 0;
    if (setsockopt(socket, SOL_SOCKET, SO_SNDTIMEO, 
                   &timeout, sizeof(timeout)) < 0) {
        return -1;
    }
#endif
    return 0;
}

int socket_set_timeout(socket_t socket, int seconds) {
    // Set both recv and send timeout
    if (socket_set_recv_timeout(socket, seconds) != 0) {
        return -1;
    }
    if (socket_set_send_timeout(socket, seconds) != 0) {
        return -1;
    }
    return 0;
}

void socket_close(socket_t socket) {
    if (socket != INVALID_SOCKET) {
        // Close socket (initiates connection termination)
        // Sends FIN packet to peer
        closesocket(socket);
    }
}

// ==================== ERROR HANDLING ====================

const char* socket_get_error(void) {
#ifdef _WIN32
    // Windows: Get error from WSAGetLastError()
    static char error_msg[256];
    FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                   NULL, WSAGetLastError(),
                   MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                   error_msg, sizeof(error_msg), NULL);
    return error_msg;
#else
    // UNIX/Linux: Use errno and strerror()
    return strerror(errno);
#endif
}
