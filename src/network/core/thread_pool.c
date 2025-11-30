#include "thread_pool.h"
#include <stdlib.h>
#include <string.h>

// ==================== THREAD CREATION ====================

int thread_create_client_handler(client_handler_func handler, client_context_t* context) {
#ifdef _WIN32
    // Windows threading (CreateThread API)
    HANDLE thread = CreateThread(
        NULL,                   // Default security attributes
        0,                      // Default stack size
        (LPTHREAD_START_ROUTINE)handler,  // Thread function
        context,                // Parameter to thread function
        0,                      // Default creation flags
        NULL                    // Don't return thread ID
    );
    
    if (thread == NULL) {
        return -1;
    }
    
    // Detach thread (automatic cleanup)
    CloseHandle(thread);
    return 0;
    
#else
    // POSIX threading (pthread API)
    pthread_t thread;
    pthread_attr_t attr;
    
    // Initialize thread attributes
    pthread_attr_init(&attr);
    
    // Set detached state (automatic cleanup when thread exits)
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
    
    // Create thread
    int result = pthread_create(&thread, &attr, handler, context);
    
    // Cleanup attributes
    pthread_attr_destroy(&attr);
    
    return (result == 0) ? 0 : -1;
#endif
}

int thread_join(thread_t thread) {
#ifdef _WIN32
    if (WaitForSingleObject(thread, INFINITE) == WAIT_FAILED) {
        return -1;
    }
    CloseHandle(thread);
    return 0;
#else
    return pthread_join(thread, NULL) == 0 ? 0 : -1;
#endif
}

int thread_detach(thread_t thread) {
#ifdef _WIN32
    CloseHandle(thread);
    return 0;
#else
    return pthread_detach(thread) == 0 ? 0 : -1;
#endif
}

// ==================== MUTEX OPERATIONS ====================

int mutex_init(mutex_t* mutex) {
#ifdef _WIN32
    InitializeCriticalSection(mutex);
    return 0;
#else
    return pthread_mutex_init(mutex, NULL) == 0 ? 0 : -1;
#endif
}

int mutex_lock(mutex_t* mutex) {
#ifdef _WIN32
    EnterCriticalSection(mutex);
    return 0;
#else
    return pthread_mutex_lock(mutex) == 0 ? 0 : -1;
#endif
}

int mutex_unlock(mutex_t* mutex) {
#ifdef _WIN32
    LeaveCriticalSection(mutex);
    return 0;
#else
    return pthread_mutex_unlock(mutex) == 0 ? 0 : -1;
#endif
}

int mutex_destroy(mutex_t* mutex) {
#ifdef _WIN32
    DeleteCriticalSection(mutex);
    return 0;
#else
    return pthread_mutex_destroy(mutex) == 0 ? 0 : -1;
#endif
}

// ==================== SERVER ACCEPT LOOP ====================

void* server_accept_loop(void* context) {
    server_context_t* ctx = (server_context_t*)context;
    
    while (ctx->running) {
        // Accept incoming connection (BLOCKING)
        // Network Programming Note:
        // accept() blocks until a client connects, then returns
        // a new socket dedicated to that client
        socket_t client_socket = socket_accept_client(ctx->server_socket);
        
        if (client_socket == INVALID_SOCKET) {
            // Error or server shutting down
            if (ctx->running) {
                // Only log error if still running
                continue;
            }
            break;
        }
        
        // Update active clients count (thread-safe)
        mutex_lock(&ctx->clients_mutex);
        ctx->active_clients++;
        int client_id = ctx->active_clients;
        mutex_unlock(&ctx->clients_mutex);
        
        // Create client context
        client_context_t* client_ctx = (client_context_t*)malloc(sizeof(client_context_t));
        if (!client_ctx) {
            socket_close(client_socket);
            continue;
        }
        
        client_ctx->client_socket = client_socket;
        client_ctx->thread_id = client_id;
        client_ctx->user_data = ctx->user_data;
        
        // Spawn new thread to handle this client
        // Network Programming Note:
        // Each client gets its own thread for independent I/O operations.
        // This allows the server to handle multiple clients concurrently
        // while keeping the code simple with blocking I/O.
        if (thread_create_client_handler(ctx->handler, client_ctx) != 0) {
            // Failed to create thread
            free(client_ctx);
            socket_close(client_socket);
            
            mutex_lock(&ctx->clients_mutex);
            ctx->active_clients--;
            mutex_unlock(&ctx->clients_mutex);
        }
        
        // Note: client_ctx will be freed by the handler thread
    }
    
    return NULL;
}

int server_context_init(server_context_t* ctx, socket_t server_socket,
                       client_handler_func handler, void* user_data) {
    if (!ctx) {
        return -1;
    }
    
    ctx->server_socket = server_socket;
    ctx->handler = handler;
    ctx->running = 1;
    ctx->active_clients = 0;
    ctx->user_data = user_data;
    
    // Initialize mutex for thread-safe client count
    return mutex_init(&ctx->clients_mutex);
}

void server_context_destroy(server_context_t* ctx) {
    if (ctx) {
        ctx->running = 0;
        mutex_destroy(&ctx->clients_mutex);
    }
}

