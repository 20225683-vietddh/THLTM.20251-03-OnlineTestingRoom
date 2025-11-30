#include "network.h"

// ==================== PYTHON API IMPLEMENTATION ====================

int py_init_network(void) {
    return socket_init_network();
}

void py_cleanup_network(void) {
    socket_cleanup_network();
}

socket_t py_create_server(int port) {
    return socket_create_server(port);
}

socket_t py_accept_client(socket_t server_socket) {
    return socket_accept_client(server_socket);
}

socket_t py_connect_to_server(const char* host, int port) {
    return socket_connect_to_server(host, port);
}

void py_close_socket(socket_t socket) {
    socket_close(socket);
}

int py_send_protocol_message(socket_t socket, uint16_t msg_type,
                              const char* payload, const char* session_token) {
    return protocol_send_message(socket, msg_type, payload, session_token);
}

int py_receive_protocol_message(socket_t socket, protocol_header_t* header,
                                 char* payload, int max_payload_size) {
    return protocol_receive_message(socket, header, payload, max_payload_size);
}

void py_generate_message_id(char* message_id) {
    utils_generate_message_id(message_id);
}

int64_t py_get_unix_timestamp(void) {
    return utils_get_unix_timestamp();
}
