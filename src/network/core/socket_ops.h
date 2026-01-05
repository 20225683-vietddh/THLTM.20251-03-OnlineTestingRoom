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
 * @brief Initialize network subsystem
 * @return 0 on success, -1 on failure
 */
int socket_init_network(void);

/**
 * @brief Cleanup network subsystem
 */
void socket_cleanup_network(void);

// ==================== SERVER OPERATIONS ====================

/**
 * @brief Create and configure TCP server socket
 * @param port Port number to bind
 * @return Socket descriptor on success, INVALID_SOCKET on failure
 */
socket_t socket_create_server(int port);

/**
 * @brief Accept incoming client connection (blocking)
 * @param server_socket Server socket descriptor
 * @return Client socket descriptor on success, INVALID_SOCKET on failure
 */
socket_t socket_accept_client(socket_t server_socket);

// ==================== CLIENT OPERATIONS ====================

/**
 * @brief Connect to TCP server
 * @param host Server IP address
 * @param port Server port number
 * @return Socket descriptor on success, INVALID_SOCKET on failure
 */
socket_t socket_connect_to_server(const char* host, int port);

// ==================== DATA TRANSMISSION ====================

/**
 * @brief Send data over TCP socket (blocking)
 * @param socket Socket descriptor
 * @param data Data buffer to send
 * @param length Number of bytes to send
 * @return Number of bytes sent on success, -1 on error
 */
int socket_send_data(socket_t socket, const char* data, int length);

/**
 * @brief Receive data from TCP socket (blocking)
 * @param socket Socket descriptor
 * @param buffer Buffer to store received data
 * @param buffer_size Number of bytes to receive
 * @return Number of bytes received on success, 0 if connection closed, -1 on error
 */
int socket_receive_data(socket_t socket, char* buffer, int buffer_size);

// ==================== CONNECTION MANAGEMENT ====================

/**
 * @brief Check if socket connection is still alive
 * @param socket Socket descriptor
 * @return 1 if alive, 0 if dead, -1 on error
 */
int socket_is_alive(socket_t socket);

/**
 * @brief Get client IP address from socket
 * @param socket Client socket descriptor
 * @param ip_buffer Buffer to store IP (min 16 bytes for IPv4)
 * @return 0 on success, -1 on error
 */
int socket_get_client_ip(socket_t socket, char* ip_buffer);

/**
 * @brief Close socket and release resources
 * @param socket Socket descriptor to close
 */
void socket_close(socket_t socket);

// ==================== ERROR HANDLING ====================

/**
 * @brief Get last socket error message
 * @return Error message string
 */
const char* socket_get_error(void);

#endif // SOCKET_OPS_H
