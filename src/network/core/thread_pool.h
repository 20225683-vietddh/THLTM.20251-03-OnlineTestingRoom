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
 * @brief Create thread to handle client connection
 * @param handler Client handler function
 * @param context Client context
 * @return 0 on success, -1 on failure
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
 * @brief Detach thread (auto cleanup)
 * @param thread Thread handle
 * @return 0 on success, -1 on failure
 */
int thread_detach(thread_t thread);

// ==================== MUTEX (Thread Synchronization) ====================

/**
 * @brief Initialize mutex
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_init(mutex_t* mutex);

/**
 * @brief Lock mutex
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_lock(mutex_t* mutex);

/**
 * @brief Unlock mutex
 * @param mutex Pointer to mutex structure
 * @return 0 on success, -1 on failure
 */
int mutex_unlock(mutex_t* mutex);

/**
 * @brief Destroy mutex
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
 * @brief Server accept loop (spawns thread per client)
 * @param context Pointer to server_context_t
 * @return NULL
 */
void* server_accept_loop(void* context);

/**
 * @brief Initialize server context
 * @param ctx Server context
 * @param server_socket Server socket descriptor
 * @param handler Client handler function
 * @param user_data User-defined data
 * @return 0 on success, -1 on failure
 */
int server_context_init(server_context_t* ctx, socket_t server_socket,
                       client_handler_func handler, void* user_data);

/**
 * @brief Cleanup server context
 * @param ctx Server context
 */
void server_context_destroy(server_context_t* ctx);

#endif // THREAD_POOL_H
