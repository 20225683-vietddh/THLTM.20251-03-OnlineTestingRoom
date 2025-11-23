#ifndef NETWORK_H
#define NETWORK_H

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
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

// Constants
#define BUFFER_SIZE 8192
#define MAX_CLIENTS 10

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

// Utility functions
const char* get_last_error();

#endif // NETWORK_H

