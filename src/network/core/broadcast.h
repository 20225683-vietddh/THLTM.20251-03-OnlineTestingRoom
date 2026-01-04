#ifndef BROADCAST_H
#define BROADCAST_H

#include "socket_ops.h"
#include "protocol.h"
#include "thread_pool.h"

// Maximum number of clients in broadcast system
#define MAX_BROADCAST_CLIENTS 100

/**
 * @brief Client information for broadcast management
 */
typedef struct {
    socket_t socket;       // Client socket descriptor
    int room_id;           // Room ID (0 = lobby, no room)
    int active;            // 1 = active, 0 = disconnected
} broadcast_client_t;

/**
 * @brief Broadcast manager for room-based messaging
 * 
 * Thread-safe broadcast system allowing messages to be sent
 * to all clients in a specific room simultaneously.
 */
typedef struct {
    broadcast_client_t clients[MAX_BROADCAST_CLIENTS];
    int client_count;
    mutex_t lock;
} broadcast_manager_t;

/**
 * @brief Initialize broadcast manager
 * @param mgr Broadcast manager
 * @return 0 on success, -1 on failure
 */
int broadcast_init(broadcast_manager_t* mgr);

/**
 * @brief Register client for broadcast
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id Room ID
 * @return 0 on success, -1 on failure
 */
int broadcast_register(broadcast_manager_t* mgr, socket_t socket, int room_id);

/**
 * @brief Unregister client from broadcast
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @return 0 on success, -1 if not found
 */
int broadcast_unregister(broadcast_manager_t* mgr, socket_t socket);

/**
 * @brief Update client's room
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id New room ID
 * @return 0 on success, -1 if not found
 */
int broadcast_update_room(broadcast_manager_t* mgr, socket_t socket, int room_id);

/**
 * @brief Broadcast message to room (thread-safe)
 * @param mgr Broadcast manager
 * @param room_id Target room ID
 * @param msg_type Message type
 * @param payload Message payload (NULL if none)
 * @return Number of clients reached
 */
int broadcast_to_room(broadcast_manager_t* mgr, int room_id, 
                      uint16_t msg_type, const char* payload);

/**
 * @brief Cleanup broadcast manager
 * @param mgr Broadcast manager
 */
void broadcast_destroy(broadcast_manager_t* mgr);

#endif // BROADCAST_H
