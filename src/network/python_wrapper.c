#include "network.h"

// Python wrapper functions for easier ctypes integration

// Export functions for Windows DLL
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

EXPORT int py_init_network() {
    return init_network();
}

EXPORT void py_cleanup_network() {
    cleanup_network();
}

EXPORT socket_t py_create_server(int port) {
    return create_server_socket(port);
}

EXPORT socket_t py_accept_client(socket_t server_socket) {
    return accept_client(server_socket);
}

EXPORT socket_t py_connect_to_server(const char* host, int port) {
    return connect_to_server(host, port);
}

EXPORT int py_send_message(socket_t socket, const char* message) {
    return send_message(socket, message);
}

EXPORT int py_receive_message(socket_t socket, char* buffer, int buffer_size) {
    return receive_message(socket, buffer, buffer_size);
}

EXPORT void py_close_socket(socket_t socket) {
    close_socket(socket);
}

