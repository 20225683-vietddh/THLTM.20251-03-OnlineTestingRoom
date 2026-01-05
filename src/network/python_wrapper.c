#include "python_wrapper.h"

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

int py_socket_is_alive(socket_t socket) {
    return socket_is_alive(socket);
}

int py_socket_get_client_ip(socket_t socket, char* ip_buffer) {
    return socket_get_client_ip(socket, ip_buffer);
}

int py_socket_set_recv_timeout(socket_t socket, int seconds) {
    return socket_set_recv_timeout(socket, seconds);
}

int py_socket_set_send_timeout(socket_t socket, int seconds) {
    return socket_set_send_timeout(socket, seconds);
}

int py_socket_set_timeout(socket_t socket, int seconds) {
    return socket_set_timeout(socket, seconds);
}

// ==================== THREADING API ====================

void* py_server_accept_loop(void* context) {
    return server_accept_loop(context);
}

int py_server_context_init(server_context_t* ctx, socket_t server_socket,
                           client_handler_func handler, void* user_data) {
    return server_context_init(ctx, server_socket, handler, user_data);
}

void py_server_context_destroy(server_context_t* ctx) {
    server_context_destroy(ctx);
}

int py_thread_create_client_handler(client_handler_func handler, client_context_t* context) {
    return thread_create_client_handler(handler, context);
}