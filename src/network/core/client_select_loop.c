#include "client_select_loop.h"
#include "protocol.h"
#include "socket_ops.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef _WIN32
    #include <unistd.h>
#endif

// ==================== GLOBAL STATE ====================

select_loop_context_t* g_select_context = NULL;

// ==================== REQUEST QUEUE HELPERS ====================

static void add_request_to_queue(request_node_t* req) {
#ifdef _WIN32
    EnterCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_lock(&g_select_context->lock);
#endif
    
    req->next = g_select_context->request_queue;
    g_select_context->request_queue = req;
    
#ifdef _WIN32
    LeaveCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_unlock(&g_select_context->lock);
#endif
}

static request_node_t* get_next_unsent_request() {
#ifdef _WIN32
    EnterCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_lock(&g_select_context->lock);
#endif
    
    request_node_t* current = g_select_context->request_queue;
    while (current) {
        if (!current->sent && !current->completed) {
#ifdef _WIN32
            LeaveCriticalSection(&g_select_context->lock);
#else
            pthread_mutex_unlock(&g_select_context->lock);
#endif
            return current;
        }
        current = current->next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_unlock(&g_select_context->lock);
#endif
    
    return NULL;
}

static request_node_t* get_next_sent_request() {
#ifdef _WIN32
    EnterCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_lock(&g_select_context->lock);
#endif
    
    request_node_t* current = g_select_context->request_queue;
    while (current) {
        if (current->sent && !current->completed) {
#ifdef _WIN32
            LeaveCriticalSection(&g_select_context->lock);
#else
            pthread_mutex_unlock(&g_select_context->lock);
#endif
            return current;
        }
        current = current->next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_unlock(&g_select_context->lock);
#endif
    
    return NULL;
}

static void complete_request(request_node_t* req, int result) {
    req->completed = 1;
    req->result = result;
    
#ifdef _WIN32
    SetEvent(req->event);
#else
    pthread_mutex_lock(&req->mutex);
    pthread_cond_signal(&req->cond);
    pthread_mutex_unlock(&req->mutex);
#endif
}

static void cleanup_completed_requests() {
#ifdef _WIN32
    EnterCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_lock(&g_select_context->lock);
#endif
    
    request_node_t* current = g_select_context->request_queue;
    request_node_t* prev = NULL;
    
    while (current) {
        if (current->completed) {
            request_node_t* to_free = current;
            
            if (prev) {
                prev->next = current->next;
                current = current->next;
            } else {
                g_select_context->request_queue = current->next;
                current = g_select_context->request_queue;
            }
            
            if (to_free->json_data) {
                free(to_free->json_data);
            }
#ifdef _WIN32
            CloseHandle(to_free->event);
#else
            pthread_cond_destroy(&to_free->cond);
            pthread_mutex_destroy(&to_free->mutex);
#endif
            free(to_free);
        } else {
            prev = current;
            current = current->next;
        }
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_select_context->lock);
#else
    pthread_mutex_unlock(&g_select_context->lock);
#endif
}

// ==================== SELECT LOOP THREAD ====================

#ifdef _WIN32
static DWORD WINAPI select_loop_thread_func(LPVOID arg) {
#else
static void* select_loop_thread_func(void* arg) {
#endif
    while (g_select_context->running) {
        // Setup select() parameters
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(g_select_context->socket, &read_fds);
        
        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        
        // Wait for socket to become readable (I/O multiplexing)
        int ret = select(g_select_context->socket + 1, &read_fds, NULL, NULL, &timeout);
        
        if (ret > 0 && FD_ISSET(g_select_context->socket, &read_fds)) {
            // Socket readable - receive message
            protocol_header_t header;
            char payload[MAX_PAYLOAD_SIZE];
            
            int recv_ret = protocol_receive_message(
                g_select_context->socket, 
                &header, 
                payload, 
                MAX_PAYLOAD_SIZE
            );
            
            if (recv_ret >= 0) {
                // Convert header fields to host byte order for comparison
                uint16_t msg_type = ntohs(header.message_type);
                
                // Classify message: broadcast or response
                if (msg_type == MSG_ROOM_STATUS) {
                    // Broadcast - call Python callback
                    if (g_select_context->callback) {
                        g_select_context->callback(msg_type, payload);
                    }
                } else {
                    // Response - complete sent request (FIFO order)
                    request_node_t* req = get_next_sent_request();
                    if (req) {
                        int copy_len = recv_ret;  // recv_ret is payload length
                        if (copy_len > req->response_buf_size - 1) {
                            copy_len = req->response_buf_size - 1;
                        }
                        memcpy(req->response_buf, payload, copy_len);
                        req->response_buf[copy_len] = '\0';
                        complete_request(req, 0);
                    }
                }
            } else {
                // Connection error
                g_select_context->running = 0;
                break;
            }
        }
        
        // Process unsent requests
        request_node_t* req = get_next_unsent_request();
        if (req) {
            // Send with session token for authenticated requests
            int send_ret = protocol_send_message(
                g_select_context->socket, 
                req->msg_type, 
                req->json_data, 
                g_select_context->session_token
            );
            if (send_ret > 0) {
                // Mark as sent, wait for response
                req->sent = 1;
            } else {
                // Send failed
                complete_request(req, -1);
            }
        }
        
        // Cleanup completed requests
        cleanup_completed_requests();
    }
    
#ifdef _WIN32
    return 0;
#else
    return NULL;
#endif
}

// ==================== PUBLIC API ====================

int client_select_loop_start(int socket, const char* session_token, broadcast_callback_t callback) {
    if (g_select_context != NULL) {
        return -1;  // Already running
    }
    
    g_select_context = (select_loop_context_t*)malloc(sizeof(select_loop_context_t));
    if (!g_select_context) {
        return -1;
    }
    
    g_select_context->socket = socket;
    g_select_context->running = 1;
    g_select_context->callback = callback;
    g_select_context->request_queue = NULL;
    
    // Store session token for authenticated requests
    if (session_token) {
        strncpy(g_select_context->session_token, session_token, 32);
        g_select_context->session_token[32] = '\0';
    } else {
        g_select_context->session_token[0] = '\0';
    }
    
#ifdef _WIN32
    InitializeCriticalSection(&g_select_context->lock);
    g_select_context->thread = CreateThread(NULL, 0, select_loop_thread_func, NULL, 0, NULL);
    if (!g_select_context->thread) {
        DeleteCriticalSection(&g_select_context->lock);
        free(g_select_context);
        g_select_context = NULL;
        return -1;
    }
#else
    pthread_mutex_init(&g_select_context->lock, NULL);
    if (pthread_create(&g_select_context->thread, NULL, select_loop_thread_func, NULL) != 0) {
        pthread_mutex_destroy(&g_select_context->lock);
        free(g_select_context);
        g_select_context = NULL;
        return -1;
    }
#endif
    
    return 0;
}

void client_select_loop_stop() {
    if (!g_select_context) {
        return;
    }
    
    g_select_context->running = 0;
    
#ifdef _WIN32
    WaitForSingleObject(g_select_context->thread, 5000);
    CloseHandle(g_select_context->thread);
    DeleteCriticalSection(&g_select_context->lock);
#else
    pthread_join(g_select_context->thread, NULL);
    pthread_mutex_destroy(&g_select_context->lock);
#endif
    
    // Free all remaining requests
    request_node_t* current = g_select_context->request_queue;
    while (current) {
        request_node_t* next = current->next;
        if (current->json_data) {
            free(current->json_data);
        }
#ifdef _WIN32
        CloseHandle(current->event);
#else
        pthread_cond_destroy(&current->cond);
        pthread_mutex_destroy(&current->mutex);
#endif
        free(current);
        current = next;
    }
    
    free(g_select_context);
    g_select_context = NULL;
}

int client_select_loop_send_request(int msg_type, const char* json_data, 
                                    char* response_buf, int response_buf_size) {
    if (!g_select_context || !g_select_context->running) {
        return -1;
    }
    
    // Create request node
    request_node_t* req = (request_node_t*)malloc(sizeof(request_node_t));
    if (!req) {
        return -1;
    }
    
    req->msg_type = msg_type;
    req->json_data = strdup(json_data);
    req->response_buf = response_buf;
    req->response_buf_size = response_buf_size;
    req->sent = 0;
    req->completed = 0;
    req->result = -1;
    req->next = NULL;
    
#ifdef _WIN32
    req->event = CreateEvent(NULL, FALSE, FALSE, NULL);
    if (!req->event) {
        free(req->json_data);
        free(req);
        return -1;
    }
#else
    pthread_mutex_init(&req->mutex, NULL);
    pthread_cond_init(&req->cond, NULL);
#endif
    
    // Add to queue
    add_request_to_queue(req);
    
    // Block until completed
#ifdef _WIN32
    WaitForSingleObject(req->event, INFINITE);
#else
    pthread_mutex_lock(&req->mutex);
    while (!req->completed) {
        pthread_cond_wait(&req->cond, &req->mutex);
    }
    pthread_mutex_unlock(&req->mutex);
#endif
    
    int result = req->result;
    return result;
}

int client_select_loop_is_running() {
    return g_select_context != NULL && g_select_context->running;
}
