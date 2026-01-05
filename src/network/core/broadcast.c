#include "broadcast.h"
#include "protocol.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ==================== GLOBAL STATE ====================

broadcast_manager_t* g_broadcast_manager = NULL;

// ==================== INITIALIZATION ====================

void broadcast_init() {
    if (g_broadcast_manager != NULL) {
        return;  // Already initialized
    }
    
    g_broadcast_manager = (broadcast_manager_t*)malloc(sizeof(broadcast_manager_t));
    if (!g_broadcast_manager) {
        return;
    }
    
    g_broadcast_manager->clients = NULL;
    g_broadcast_manager->client_count = 0;
    
#ifdef _WIN32
    InitializeCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_init(&g_broadcast_manager->lock, NULL);
#endif
}

void broadcast_destroy() {
    if (!g_broadcast_manager) {
        return;
    }
    
#ifdef _WIN32
    EnterCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_lock(&g_broadcast_manager->lock);
#endif
    
    // Free all client nodes
    broadcast_client_t* current = g_broadcast_manager->clients;
    while (current) {
        broadcast_client_t* next = current->next;
        free(current);
        current = next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_broadcast_manager->lock);
    DeleteCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_unlock(&g_broadcast_manager->lock);
    pthread_mutex_destroy(&g_broadcast_manager->lock);
#endif
    
    free(g_broadcast_manager);
    g_broadcast_manager = NULL;
}

// ==================== CLIENT MANAGEMENT ====================

int broadcast_register(int socket, int room_id) {
    if (!g_broadcast_manager) {
        return -1;
    }
    
#ifdef _WIN32
    EnterCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_lock(&g_broadcast_manager->lock);
#endif
    
    // Check if (socket + room_id) already registered
    broadcast_client_t* current = g_broadcast_manager->clients;
    while (current) {
        if (current->socket == socket && current->room_id == room_id) {
            // Already registered for this room, OK
#ifdef _WIN32
            LeaveCriticalSection(&g_broadcast_manager->lock);
#else
            pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
            return 0;
        }
        current = current->next;
    }
    
    // Create new client node
    broadcast_client_t* new_client = (broadcast_client_t*)malloc(sizeof(broadcast_client_t));
    if (!new_client) {
#ifdef _WIN32
        LeaveCriticalSection(&g_broadcast_manager->lock);
#else
        pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
        return -1;
    }
    
    new_client->socket = socket;
    new_client->room_id = room_id;
    new_client->next = g_broadcast_manager->clients;
    g_broadcast_manager->clients = new_client;
    g_broadcast_manager->client_count++;
    
#ifdef _WIN32
    LeaveCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
    
    return 0;
}

void broadcast_unregister(int socket) {
    if (!g_broadcast_manager) {
        return;
    }
    
#ifdef _WIN32
    EnterCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_lock(&g_broadcast_manager->lock);
#endif
    
    broadcast_client_t* current = g_broadcast_manager->clients;
    broadcast_client_t* prev = NULL;
    
    while (current) {
        if (current->socket == socket) {
            if (prev) {
                prev->next = current->next;
            } else {
                g_broadcast_manager->clients = current->next;
            }
            
            free(current);
            g_broadcast_manager->client_count--;
            
#ifdef _WIN32
            LeaveCriticalSection(&g_broadcast_manager->lock);
#else
            pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
            return;
        }
        
        prev = current;
        current = current->next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
}

int broadcast_update_room(int socket, int room_id) {
    if (!g_broadcast_manager) {
        return -1;
    }
    
#ifdef _WIN32
    EnterCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_lock(&g_broadcast_manager->lock);
#endif
    
    broadcast_client_t* current = g_broadcast_manager->clients;
    while (current) {
        if (current->socket == socket) {
            current->room_id = room_id;
#ifdef _WIN32
            LeaveCriticalSection(&g_broadcast_manager->lock);
#else
            pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
            return 0;
        }
        current = current->next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
    
    return -1;
}

// ==================== BROADCAST OPERATIONS ====================

int broadcast_to_room(int room_id, int msg_type, const char* json_data) {
    if (!g_broadcast_manager) {
        return 0;
    }
    
    int sent_count = 0;
    
#ifdef _WIN32
    EnterCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_lock(&g_broadcast_manager->lock);
#endif
    
    // Iterate through all clients and send to matching room
    broadcast_client_t* current = g_broadcast_manager->clients;
    while (current) {
        if (current->room_id == room_id) {
            // Send using protocol layer (handles header, byte order, timeout)
            int result = protocol_send_message(current->socket, msg_type, json_data, NULL);
            if (result > 0) {
                sent_count++;
            }
        }
        current = current->next;
    }
    
#ifdef _WIN32
    LeaveCriticalSection(&g_broadcast_manager->lock);
#else
    pthread_mutex_unlock(&g_broadcast_manager->lock);
#endif
    
    return sent_count;
}
