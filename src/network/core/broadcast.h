#ifndef BROADCAST_H
#define BROADCAST_H

#include <stdint.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <windows.h>
#else
    #include <pthread.h>
#endif

// ==================== DATA STRUCTURES ====================

/**
 * @brief Broadcast client entry (linked list node)
 */
typedef struct broadcast_client {
    int socket;                      // Client socket descriptor
    int room_id;                     // Room ID client belongs to
    struct broadcast_client* next;   // Next node in linked list
} broadcast_client_t;

/**
 * @brief Broadcast manager (thread-safe singleton)
 */
typedef struct {
    broadcast_client_t* clients;     // Head of client linked list
    int client_count;                // Total number of registered clients
    
#ifdef _WIN32
    CRITICAL_SECTION lock;           // Windows mutex for thread safety
#else
    pthread_mutex_t lock;            // POSIX mutex for thread safety
#endif
} broadcast_manager_t;

/**
 * @brief Global broadcast manager instance
 */
extern broadcast_manager_t* g_broadcast_manager;

// ==================== LIFECYCLE MANAGEMENT ====================

/**
 * @brief Initialize broadcast manager
 * 
 * Must be called once at server startup before any broadcast operations.
 * Creates global broadcast_manager_t instance with empty client list.
 * Thread-safe: Uses mutex for concurrent access protection.
 */
void broadcast_init(void);

/**
 * @brief Destroy broadcast manager and free all resources
 * 
 * Must be called at server shutdown after all clients disconnected.
 * Frees all client nodes and destroys mutex.
 */
void broadcast_destroy(void);

// ==================== CLIENT MANAGEMENT ====================

/**
 * @brief Register a client socket with a room ID
 * 
 * Thread-safe: Can be called from multiple client handler threads.
 * If socket already registered, updates room_id instead of creating duplicate.
 * 
 * @param socket Client socket descriptor
 * @param room_id Room ID to associate with client
 * @return 0 on success, -1 on error
 */
int broadcast_register(int socket, int room_id);

/**
 * @brief Unregister a client socket
 * 
 * Thread-safe: Can be called from multiple client handler threads.
 * Removes client from broadcast list and frees memory.
 * 
 * @param socket Client socket descriptor to unregister
 */
void broadcast_unregister(int socket);

/**
 * @brief Update room ID for an existing client
 * 
 * Thread-safe: Can be called from multiple threads.
 * 
 * @param socket Client socket descriptor
 * @param room_id New room ID to assign
 * @return 0 on success, -1 if socket not found
 */
int broadcast_update_room(int socket, int room_id);

// ==================== BROADCAST OPERATIONS ====================

/**
 * @brief Broadcast message to all clients in a room
 * 
 * Thread-safe: Can be called from any thread.
 * Iterates through all registered clients and sends message to those
 * in the specified room. Uses protocol_send_message() for each client.
 * 
 * Network Programming Concept: Server-initiated push notification.
 * Server actively sends data to clients without client request.
 * 
 * @param room_id Target room ID
 * @param msg_type Protocol message type (e.g., MSG_ROOM_STATUS)
 * @param json_data JSON payload string
 * @return Number of clients that successfully received the message
 */
int broadcast_to_room(int room_id, int msg_type, const char* json_data);

#endif // BROADCAST_H
