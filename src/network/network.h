#ifndef NETWORK_H
#define NETWORK_H

// Include all core modules
#include "core/socket_ops.h"
#include "core/protocol.h"
#include "core/utils.h"
#include "core/thread_pool.h"

// ==================== VERSION INFO ====================

#define NETWORK_LIBRARY_VERSION "1.0.0"
#define NETWORK_LIBRARY_NAME "TAP Network Library"

// ==================== PYTHON API WRAPPER ====================

// These functions are exposed to Python via ctypes
// They provide a simple C API that Python can call

/**
 * @brief Initialize network subsystem (Python API)
 * @return 0 on success, -1 on failure
 */
int py_init_network(void);

/**
 * @brief Cleanup network subsystem (Python API)
 */
void py_cleanup_network(void);

/**
 * @brief Create server socket (Python API)
 * @param port Port number
 * @return Socket descriptor or INVALID_SOCKET
 */
socket_t py_create_server(int port);

/**
 * @brief Accept client connection (Python API)
 * @param server_socket Server socket descriptor
 * @return Client socket descriptor or INVALID_SOCKET
 */
socket_t py_accept_client(socket_t server_socket);

/**
 * @brief Connect to server (Python API)
 * @param host Server IP address
 * @param port Server port
 * @return Socket descriptor or INVALID_SOCKET
 */
socket_t py_connect_to_server(const char* host, int port);

/**
 * @brief Close socket (Python API)
 * @param socket Socket descriptor
 */
void py_close_socket(socket_t socket);

/**
 * @brief Send protocol message (Python API)
 * @param socket Socket descriptor
 * @param msg_type Message type
 * @param payload Payload string (JSON)
 * @param session_token Session token (can be NULL)
 * @return Bytes sent or negative on error
 */
int py_send_protocol_message(socket_t socket, uint16_t msg_type,
                              const char* payload, const char* session_token);

/**
 * @brief Receive protocol message (Python API)
 * @param socket Socket descriptor
 * @param header Pointer to header structure
 * @param payload Buffer for payload
 * @param max_payload_size Maximum payload size
 * @return Payload length or negative on error
 */
int py_receive_protocol_message(socket_t socket, protocol_header_t* header,
                                 char* payload, int max_payload_size);

/**
 * @brief Generate message ID (Python API)
 * @param message_id Buffer for message ID (16 bytes)
 */
void py_generate_message_id(char* message_id);

/**
 * @brief Get Unix timestamp (Python API)
 * @return Unix timestamp
 */
int64_t py_get_unix_timestamp(void);

// ==================== THREADING API (Python) ====================

/**
 * @brief Server accept loop (Python API)
 * Runs in a thread to accept incoming connections
 * @param context Server context pointer
 * @return NULL
 */
void* py_server_accept_loop(void* context);

/**
 * @brief Initialize server context (Python API)
 * @param ctx Server context
 * @param server_socket Server socket descriptor
 * @param handler Client handler function
 * @param user_data User-defined data
 * @return 0 on success, -1 on failure
 */
int py_server_context_init(server_context_t* ctx, socket_t server_socket,
                           client_handler_func handler, void* user_data);

/**
 * @brief Destroy server context (Python API)
 * @param ctx Server context
 */
void py_server_context_destroy(server_context_t* ctx);

/**
 * @brief Create client handler thread (Python API)
 * @param handler Client handler function
 * @param context Client context
 * @return 0 on success, -1 on failure
 */
int py_thread_create_client_handler(client_handler_func handler, client_context_t* context);

// ==================== BROADCAST API (Python) ====================

/**
 * @brief Initialize broadcast manager (Python API)
 * @param mgr Broadcast manager
 * @return 0 on success, -1 on failure
 */
int py_broadcast_manager_init(broadcast_manager_t* mgr);

/**
 * @brief Register client for broadcast (Python API)
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id Room ID
 * @param username Client username
 * @return 0 on success, -1 on failure
 */
int py_broadcast_manager_register(broadcast_manager_t* mgr, socket_t socket,
                                  int room_id, const char* username);

/**
 * @brief Unregister client from broadcast (Python API)
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @return 0 on success, -1 on failure
 */
int py_broadcast_manager_unregister(broadcast_manager_t* mgr, socket_t socket);

/**
 * @brief Update client's room (Python API)
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id New room ID
 * @return 0 on success, -1 on failure
 */
int py_broadcast_manager_update_room(broadcast_manager_t* mgr, socket_t socket, int room_id);

/**
 * @brief Broadcast message to room (Python API)
 * @param mgr Broadcast manager
 * @param room_id Target room ID
 * @param msg_type Message type
 * @param payload Message payload
 * @return Number of clients message was sent to
 */
int py_broadcast_to_room(broadcast_manager_t* mgr, int room_id,
                        uint16_t msg_type, const char* payload);

/**
 * @brief Destroy broadcast manager (Python API)
 * @param mgr Broadcast manager
 */
void py_broadcast_manager_destroy(broadcast_manager_t* mgr);

#endif // NETWORK_H
