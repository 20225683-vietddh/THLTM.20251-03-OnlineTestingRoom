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

// ==================== PROTOCOL FUNCTIONS (New) ====================

EXPORT int py_send_protocol_message(socket_t socket, uint16_t msg_type, 
                                    const char* payload, const char* session_token) {
    return send_protocol_message(socket, msg_type, payload, session_token);
}

EXPORT int py_receive_protocol_message(socket_t socket, protocol_header_t* header,
                                       char* payload, int max_payload_size) {
    return receive_protocol_message(socket, header, payload, max_payload_size);
}

EXPORT void py_init_protocol_header(protocol_header_t* header, uint16_t msg_type,
                                    uint32_t length, const char* session_token) {
    init_protocol_header(header, msg_type, length, session_token);
}

EXPORT int py_validate_protocol_header(protocol_header_t* header) {
    return validate_protocol_header(header);
}

EXPORT void py_generate_message_id(char* message_id) {
    generate_message_id(message_id);
}

EXPORT int64_t py_get_unix_timestamp() {
    return get_unix_timestamp();
}

