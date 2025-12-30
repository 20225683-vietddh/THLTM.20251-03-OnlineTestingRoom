#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include "socket_ops.h"

#ifdef _WIN32
    #include <windows.h>
    typedef HANDLE thread_t;
    typedef CRITICAL_SECTION mutex_t;
#else
    #include <pthread.h>
    typedef pthread_t thread_t;
    typedef pthread_mutex_t mutex_t;
#endif

// ==================== CONSTANTS ====================

#define MAX_THREADS 50      // Maximum concurrent client threads
#define MAX_QUEUE 100       // Maximum pending connections queue

// ==================== CLIENT CONTEXT ====================

/**
 * @brief Context structure passed to each client handler thread
 * 
 * Contains all necessary information for a thread to handle
 * a client connection independently.
 */
typedef struct {
    socket_t client_socket;         // Client socket descriptor
    int thread_id;                  // Thread identifier
    void* user_data;                // User-defined data (callbacks, etc.)
} client_context_t;

/**
 * @brief Client handler function prototype
 * 
 * This function is called in a new thread for each client connection.
 * It should handle all communication with the client and clean up resources.
 * 
 * @param context Client context containing socket and thread info
 * @return NULL (unused)
 */
typedef void* (*client_handler_func)(void* context);

// ==================== THREAD MANAGEMENT ====================

/**
 * @brief Create and start a new thread to handle client connection
 * 
 * Network Programming Note:
 * Multi-threaded server architecture - one thread per client.
 * This allows the server to handle multiple clients concurrently
 * while each thread performs BLOCKING I/O operations.
 * 
 * @param handler Function to handle client (runs in new thread)
 * @param context Client context to pass to handler
 * @return 0 on success, -1 on failure
 * 
 * Example:
 *   client_context_t* ctx = malloc(sizeof(client_context_t));
 *   ctx->client_socket = client_sock;
 *   ctx->thread_id = 1;
 *   thread_create_client_handler(my_handler, ctx);
 */
int thread_create_client_handler(client_handler_func handler, client_context_t* context);

/**
 * @brief Wait for a thread to complete
 * 
 * @param thread Thread handle
 * @return 0 on success, -1 on failure
 */
int thread_join(thread_t thread);

/**
 * @brief Detach a thread (automatic cleanup when finished)
 * 
 * Network Programming Note:
 * Detached threads clean up their resources automatically when they exit.
 * This is useful for server threads that handle clients independently.
 * 
 * @param thread Thread handle
 * @return 0 on success, -1 on failure
 */
int thread_detach(thread_t thread);

// ==================== MUTEX (Thread Synchronization) ====================

/**
 * @brief Initialize a mutex for thread-safe access
 * 
 * Network Programming Note:
 * Mutexes are used to protect shared resources (like client list,
 * server state) from concurrent access by multiple threads.
 * 
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_init(mutex_t* mutex);

/**
 * @brief Lock mutex (wait if already locked)
 * 
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_lock(mutex_t* mutex);

/**
 * @brief Unlock mutex
 * 
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_unlock(mutex_t* mutex);

/**
 * @brief Destroy mutex (cleanup)
 * 
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_destroy(mutex_t* mutex);

// ==================== SERVER THREAD POOL ====================

/**
 * @brief Server context for multi-threaded accept loop
 */
typedef struct {
    socket_t server_socket;         // Server socket
    client_handler_func handler;    // Client handler function
    int running;                    // Server running flag
    mutex_t clients_mutex;          // Mutex for client list
    int active_clients;             // Number of active clients
    void* user_data;                // User-defined data
} server_context_t;

/**
 * @brief Start multi-threaded server accept loop
 * 
 * Network Programming Note:
 * This function runs in a dedicated thread and continuously accepts
 * incoming client connections. For each new client, it spawns a new
 * thread to handle that client's requests.
 * 
 * Architecture:
 *   Main Thread (GUI/Control)
 *       ↓ starts
 *   Accept Thread (this function)
 *       ↓ spawns (for each client)
 *   Client Thread 1, 2, 3, ... N
 * 
 * @param context Server context
 * @return NULL (unused)
 */
void* server_accept_loop(void* context);

/**
 * @brief Initialize server context for multi-threaded operation
 * 
 * @param ctx Server context to initialize
 * @param server_socket Server socket descriptor
 * @param handler Client handler function
 * @param user_data User-defined data
 * @return 0 on success, -1 on failure
 */
int server_context_init(server_context_t* ctx, socket_t server_socket,
                       client_handler_func handler, void* user_data);

/**
 * @brief Cleanup server context
 * 
 * @param ctx Server context
 */
void server_context_destroy(server_context_t* ctx);

// ==================== BROADCAST MANAGER ====================

#define MAX_BROADCAST_CLIENTS 100

/**
 * @brief Client info for broadcast
 */
typedef struct {
    socket_t socket;        // Client socket
    int room_id;           // Room ID (0 = not in any room)
    char username[32];     // Username for identification
    int active;            // 1 = active, 0 = disconnected
} broadcast_client_t;

/**
 * @brief Broadcast manager for room-based messaging
 * 
 * Allows broadcasting messages to all clients in a specific room.
 * Thread-safe with mutex protection.
 */
typedef struct {
    broadcast_client_t clients[MAX_BROADCAST_CLIENTS];
    int client_count;
    mutex_t lock;
} broadcast_manager_t;

/**
 * @brief Initialize broadcast manager
 * 
 * @param mgr Pointer to broadcast manager
 * @return 0 on success, -1 on failure
 */
int broadcast_manager_init(broadcast_manager_t* mgr);

/**
 * @brief Register client for broadcast
 * 
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id Room ID
 * @param username Client username
 * @return 0 on success, -1 on failure
 */
int broadcast_manager_register(broadcast_manager_t* mgr, socket_t socket, 
                               int room_id, const char* username);

/**
 * @brief Unregister client from broadcast
 * 
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @return 0 on success, -1 on failure
 */
int broadcast_manager_unregister(broadcast_manager_t* mgr, socket_t socket);

/**
 * @brief Update client's room
 * 
 * @param mgr Broadcast manager
 * @param socket Client socket
 * @param room_id New room ID
 * @return 0 on success, -1 on failure
 */
int broadcast_manager_update_room(broadcast_manager_t* mgr, socket_t socket, int room_id);

/**
 * @brief Broadcast message to all clients in a room
 * 
 * @param mgr Broadcast manager
 * @param room_id Target room ID
 * @param msg_type Protocol message type
 * @param payload Message payload (JSON string)
 * @return Number of clients message was sent to
 */
int broadcast_to_room(broadcast_manager_t* mgr, int room_id, 
                      uint16_t msg_type, const char* payload);

/**
 * @brief Cleanup broadcast manager
 * 
 * @param mgr Broadcast manager
 */
void broadcast_manager_destroy(broadcast_manager_t* mgr);

#endif // THREAD_POOL_H
