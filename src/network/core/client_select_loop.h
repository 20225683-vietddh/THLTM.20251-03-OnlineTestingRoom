#ifndef CLIENT_SELECT_LOOP_H
#define CLIENT_SELECT_LOOP_H

#include <stdint.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <windows.h>
#else
    #include <pthread.h>
    #include <sys/select.h>
#endif

// ==================== CALLBACK TYPE ====================

/**
 * @brief Callback function type for broadcast messages
 * 
 * Called by C select loop when a broadcast message is received.
 * Python will register a callback function to handle broadcasts.
 * 
 * @param msg_type Protocol message type (e.g., MSG_ROOM_STATUS)
 * @param json_data JSON payload string
 */
typedef void (*broadcast_callback_t)(int msg_type, const char* json_data);

// ==================== DATA STRUCTURES ====================

/**
 * @brief Request queue node (for pending client requests)
 */
typedef struct request_node {
    int msg_type;                    // Protocol message type
    char* json_data;                 // JSON payload (owned by this struct)
    char* response_buf;              // Buffer for response (owned by caller)
    int response_buf_size;           // Size of response buffer
    int sent;                        // 1 if request already sent, 0 otherwise
    int completed;                   // 1 if request completed, 0 otherwise
    int result;                      // Result code (0 = success, -1 = error)
    
#ifdef _WIN32
    HANDLE event;                    // Windows event for blocking wait
#else
    pthread_cond_t cond;             // POSIX condition variable
    pthread_mutex_t mutex;           // POSIX mutex for condition variable
#endif
    
    struct request_node* next;       // Next node in linked list
} request_node_t;

/**
 * @brief Select loop context (global singleton)
 */
typedef struct {
    int socket;                      // Client socket descriptor
    int running;                     // 1 if loop is running, 0 to stop
    broadcast_callback_t callback;   // Python callback for broadcasts
    char session_token[33];          // Session token (32 chars + null terminator)
    
#ifdef _WIN32
    HANDLE thread;                   // Windows thread handle
    CRITICAL_SECTION lock;           // Windows mutex for queue
#else
    pthread_t thread;                // POSIX thread handle
    pthread_mutex_t lock;            // POSIX mutex for queue
#endif
    
    request_node_t* request_queue;   // Head of request queue linked list
} select_loop_context_t;

/**
 * @brief Global select loop context instance
 */
extern select_loop_context_t* g_select_context;

// ==================== SELECT LOOP CONTROL ====================

/**
 * @brief Start select loop in a background thread
 * 
 * Creates a C thread that uses select() to multiplex between:
 * - Incoming broadcast messages from server (non-blocking receive)
 * - Pending requests to send (queued by client_select_loop_send_request)
 * 
 * Network Programming Concept: I/O Multiplexing with select()
 * - Single socket monitored for readability
 * - Non-blocking architecture: UI thread never blocks on network I/O
 * - Broadcasts handled asynchronously via callback
 * - Requests queued and processed sequentially
 * 
 * Python calls this once after successful login.
 * 
 * @param socket Client socket descriptor (already connected)
 * @param session_token Session token from login (for authenticated requests)
 * @param callback Python callback function for broadcast messages
 * @return 0 on success, -1 on error
 */
int client_select_loop_start(int socket, const char* session_token, broadcast_callback_t callback);

/**
 * @brief Stop select loop thread and cleanup resources
 * 
 * Signals thread to stop, waits for thread to finish (pthread_join),
 * destroys mutex, frees all queued requests, and frees context.
 * 
 * Python calls this when disconnecting or closing application.
 */
void client_select_loop_stop(void);

// ==================== REQUEST HANDLING ====================

/**
 * @brief Send request and wait for response (blocking, thread-safe)
 * 
 * Queues request in select loop thread and blocks until response arrives.
 * Select loop thread will:
 * 1. Send request to server
 * 2. Wait for response via select()
 * 3. Copy response to caller's buffer
 * 4. Wake up this waiting thread
 * 
 * Thread-safe: Multiple Python threads can call this concurrently.
 * 
 * Network Programming Concept: Asynchronous send with synchronous wait
 * - Actual send() happens in select loop thread
 * - Caller blocks on condition variable/event
 * - Avoids race conditions between send/recv
 * 
 * @param msg_type Protocol message type
 * @param json_data JSON payload string
 * @param response_buf Buffer to store response (caller-owned)
 * @param response_buf_size Size of response buffer
 * @return 0 on success, -1 on error
 */
int client_select_loop_send_request(int msg_type, const char* json_data,
                                    char* response_buf, int response_buf_size);

/**
 * @brief Check if select loop is currently running
 * @return 1 if running, 0 otherwise
 */
int client_select_loop_is_running(void);

#endif // CLIENT_SELECT_LOOP_H
