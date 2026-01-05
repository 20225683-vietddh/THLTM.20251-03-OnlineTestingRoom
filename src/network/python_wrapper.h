#ifndef PYTHON_WRAPPER_H
#define PYTHON_WRAPPER_H

#include "network.h"

/**
 * @brief Initialize network subsystem
 * @return 0 on success, -1 on failure
 */
int py_init_network(void);

/**
 * @brief Cleanup network subsystem
 */
void py_cleanup_network(void);

/**
 * @brief Create server socket
 * @param port Port number
 * @return Socket descriptor or INVALID_SOCKET
 */
socket_t py_create_server(int port);

/**
 * @brief Accept client connection
 * @param server_socket Server socket descriptor
 * @return Client socket descriptor or INVALID_SOCKET
 */
socket_t py_accept_client(socket_t server_socket);

/**
 * @brief Connect to server
 * @param host Server IP address
 * @param port Server port
 * @return Socket descriptor or INVALID_SOCKET
 */
socket_t py_connect_to_server(const char* host, int port);

/**
 * @brief Close socket
 * @param socket Socket descriptor
 */
void py_close_socket(socket_t socket);

/**
 * @brief Send protocol message
 * @param socket Socket descriptor
 * @param msg_type Message type
 * @param payload Payload string (JSON)
 * @param session_token Session token (NULL if none)
 * @return Bytes sent or negative on error
 */
int py_send_protocol_message(socket_t socket, uint16_t msg_type,
                              const char* payload, const char* session_token);

/**
 * @brief Receive protocol message
 * @param socket Socket descriptor
 * @param header Pointer to header structure
 * @param payload Buffer for payload
 * @param max_payload_size Maximum payload size
 * @return Payload length or negative on error
 */
int py_receive_protocol_message(socket_t socket, protocol_header_t* header,
                                 char* payload, int max_payload_size);

/**
 * @brief Generate message ID
 * @param message_id Buffer for 16-byte message ID
 */
void py_generate_message_id(char* message_id);

/**
 * @brief Get Unix timestamp
 * @return Unix timestamp in seconds
 */
int64_t py_get_unix_timestamp(void);

/**
 * @brief Check if socket connection is alive
 * @param socket Socket descriptor
 * @return 1 if alive, 0 if dead, -1 on error
 */
int py_socket_is_alive(socket_t socket);

/**
 * @brief Get client IP address
 * @param socket Client socket
 * @param ip_buffer Buffer for IP (min 16 bytes)
 * @return 0 on success, -1 on error
 */
int py_socket_get_client_ip(socket_t socket, char* ip_buffer);

/**
 * @brief Set receive timeout for socket
 * @param socket Socket descriptor
 * @param seconds Timeout in seconds (0 = disable)
 * @return 0 on success, -1 on error
 */
int py_socket_set_recv_timeout(socket_t socket, int seconds);

/**
 * @brief Set send timeout for socket
 * @param socket Socket descriptor
 * @param seconds Timeout in seconds (0 = disable)
 * @return 0 on success, -1 on error
 */
int py_socket_set_send_timeout(socket_t socket, int seconds);

/**
 * @brief Set both recv and send timeout for socket
 * @param socket Socket descriptor
 * @param seconds Timeout in seconds (0 = disable)
 * @return 0 on success, -1 on error
 */
int py_socket_set_timeout(socket_t socket, int seconds);

// ==================== THREADING API ====================

/**
 * @brief Server accept loop
 * @param context Server context pointer
 * @return NULL
 */
void* py_server_accept_loop(void* context);

/**
 * @brief Initialize server context
 * @param ctx Server context
 * @param server_socket Server socket descriptor
 * @param handler Client handler function
 * @param user_data User-defined data
 * @return 0 on success, -1 on failure
 */
int py_server_context_init(server_context_t* ctx, socket_t server_socket,
                           client_handler_func handler, void* user_data);

/**
 * @brief Destroy server context
 * @param ctx Server context
 */
void py_server_context_destroy(server_context_t* ctx);

/**
 * @brief Create client handler thread
 * @param handler Client handler function
 * @param context Client context
 * @return 0 on success, -1 on failure
 */
int py_thread_create_client_handler(client_handler_func handler, client_context_t* context);

// ==================== BROADCAST API ====================

/**
 * @brief Initialize broadcast manager
 * Must be called once at server startup
 */
void py_broadcast_init(void);

/**
 * @brief Destroy broadcast manager
 * Must be called at server shutdown
 */
void py_broadcast_destroy(void);

/**
 * @brief Register a client socket with a room ID
 * @param socket Client socket descriptor
 * @param room_id Room ID
 * @return 0 on success, -1 on error
 */
int py_broadcast_register(socket_t socket, int room_id);

/**
 * @brief Unregister a client socket
 * @param socket Client socket descriptor
 */
void py_broadcast_unregister(socket_t socket);

/**
 * @brief Update room ID for an existing client
 * @param socket Client socket descriptor
 * @param room_id New room ID
 * @return 0 on success, -1 if socket not found
 */
int py_broadcast_update_room(socket_t socket, int room_id);

/**
 * @brief Broadcast message to all clients in a room
 * @param room_id Room ID
 * @param msg_type Message type
 * @param json_data JSON payload
 * @return Number of clients that received the message
 */
int py_broadcast_to_room(int room_id, int msg_type, const char* json_data);

// ==================== CLIENT SELECT LOOP API ====================

/**
 * @brief Callback function type for broadcast messages
 * @param msg_type Message type
 * @param json_data JSON payload
 */
typedef void (*py_broadcast_callback_t)(int msg_type, const char* json_data);

/**
 * @brief Start client select loop in background thread
 * @param socket Client socket descriptor
 * @param session_token Session token for authenticated requests
 * @param callback Python callback for broadcast messages
 * @return 0 on success, -1 on error
 */
int py_client_select_loop_start(socket_t socket, const char* session_token, py_broadcast_callback_t callback);

/**
 * @brief Stop client select loop thread
 */
void py_client_select_loop_stop(void);

/**
 * @brief Send request and wait for response (blocking, thread-safe)
 * @param msg_type Message type
 * @param json_data JSON payload
 * @param response_buf Buffer for response
 * @param response_buf_size Buffer size
 * @return 0 on success, -1 on error
 */
int py_client_select_loop_send_request(int msg_type, const char* json_data,
                                        char* response_buf, int response_buf_size);

/**
 * @brief Check if select loop is running
 * @return 1 if running, 0 otherwise
 */
int py_client_select_loop_is_running(void);

#endif // PYTHON_WRAPPER_H
