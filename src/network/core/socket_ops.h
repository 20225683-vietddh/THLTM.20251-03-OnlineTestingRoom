#ifndef SOCKET_OPS_H
#define SOCKET_OPS_H

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

#include <stdint.h>

// ==================== CONSTANTS ====================

#define MAX_CLIENTS 10
#define SOCKET_BUFFER_SIZE 8192

// ==================== INITIALIZATION ====================

/**
 * @brief Initialize network subsystem (required on Windows - WSAStartup)
 * @return 0 on success, -1 on failure
 * 
 * Network Programming Note:
 * Windows requires WSAStartup() to initialize Winsock library before
 * any socket operations. UNIX/Linux systems don't need initialization.
 */
int socket_init_network(void);

/**
 * @brief Cleanup network subsystem (required on Windows - WSACleanup)
 * 
 * Network Programming Note:
 * Should be called when done with all socket operations.
 */
void socket_cleanup_network(void);

// ==================== SERVER OPERATIONS ====================

/**
 * @brief Create and configure a TCP server socket
 * @param port Port number to bind (1024-65535 recommended)
 * @return Socket descriptor on success, INVALID_SOCKET on failure
 * 
 * Network Programming Steps:
 * 1. socket()     - Create socket endpoint
 * 2. setsockopt() - Set SO_REUSEADDR to reuse address immediately
 * 3. bind()       - Bind socket to local address and port
 * 4. listen()     - Mark socket as passive (ready to accept connections)
 */
socket_t socket_create_server(int port);

/**
 * @brief Accept incoming client connection (blocking)
 * @param server_socket Server socket descriptor
 * @return Client socket descriptor on success, INVALID_SOCKET on failure
 * 
 * Network Programming Note:
 * This is a BLOCKING call - waits until a client connects.
 * The 3-way TCP handshake happens here:
 * 1. Client sends SYN
 * 2. Server responds with SYN-ACK
 * 3. Client sends ACK
 */
socket_t socket_accept_client(socket_t server_socket);

// ==================== CLIENT OPERATIONS ====================

/**
 * @brief Connect to a TCP server
 * @param host Server IP address (e.g., "127.0.0.1")
 * @param port Server port number
 * @return Socket descriptor on success, INVALID_SOCKET on failure
 * 
 * Network Programming Steps:
 * 1. socket()  - Create socket endpoint
 * 2. connect() - Initiate 3-way handshake with server
 */
socket_t socket_connect_to_server(const char* host, int port);

// ==================== DATA TRANSMISSION ====================

/**
 * @brief Send raw data over TCP socket
 * @param socket Socket descriptor
 * @param data Data buffer to send
 * @param length Number of bytes to send
 * @return Number of bytes sent on success, negative on error
 * 
 * Network Programming Note:
 * TCP guarantees delivery of bytes in order, but send() may not send
 * all bytes at once. This function ensures all data is sent.
 * 
 * Return codes:
 * >= 0: Success (number of bytes sent)
 * -1: Send failed (partial send or error)
 */
int socket_send_data(socket_t socket, const char* data, int length);

/**
 * @brief Receive raw data from TCP socket
 * @param socket Socket descriptor
 * @param buffer Buffer to store received data
 * @param buffer_size Maximum number of bytes to receive
 * @return Number of bytes received on success, negative on error
 * 
 * Network Programming Note:
 * recv() is a BLOCKING call - waits until data arrives or connection closes.
 * 
 * Return codes:
 * > 0: Success (number of bytes received)
 * 0: Connection closed by peer (graceful shutdown)
 * -1: Receive error
 */
int socket_receive_data(socket_t socket, char* buffer, int buffer_size);

// ==================== CONNECTION MANAGEMENT ====================

/**
 * @brief Close socket and release resources
 * @param socket Socket descriptor to close
 * 
 * Network Programming Note:
 * Closes the connection (sends FIN packet) and frees socket descriptor.
 * The 4-way termination handshake happens here:
 * 1. Active close sends FIN
 * 2. Passive side sends ACK
 * 3. Passive side sends FIN
 * 4. Active close sends ACK
 */
void socket_close(socket_t socket);

// ==================== ERROR HANDLING ====================

/**
 * @brief Get last socket error message (platform-specific)
 * @return Error message string
 * 
 * Network Programming Note:
 * Windows uses WSAGetLastError() and FormatMessage()
 * UNIX/Linux uses errno and strerror()
 */
const char* socket_get_error(void);

#endif // SOCKET_OPS_H
