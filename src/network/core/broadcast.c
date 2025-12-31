#include "broadcast.h"
#include <string.h>

int broadcast_init(broadcast_manager_t* mgr) {
    if (!mgr) {
        return -1;
    }
    
    // Initialize all client slots as inactive
    for (int i = 0; i < MAX_BROADCAST_CLIENTS; i++) {
        mgr->clients[i].socket = INVALID_SOCKET;
        mgr->clients[i].room_id = 0;
        mgr->clients[i].active = 0;
    }
    
    mgr->client_count = 0;
    
    return mutex_init(&mgr->lock);
}

int broadcast_register(broadcast_manager_t* mgr, socket_t socket, int room_id) {
    if (!mgr || socket == INVALID_SOCKET) {
        return -1;
    }
    
    mutex_lock(&mgr->lock);
    
    // Find empty slot
    int slot = -1;
    for (int i = 0; i < MAX_BROADCAST_CLIENTS; i++) {
        if (!mgr->clients[i].active) {
            slot = i;
            break;
        }
    }
    
    if (slot == -1) {
        mutex_unlock(&mgr->lock);
        return -1;  // Manager full
    }
    
    // Register client
    mgr->clients[slot].socket = socket;
    mgr->clients[slot].room_id = room_id;
    mgr->clients[slot].active = 1;
    mgr->client_count++;
    
    mutex_unlock(&mgr->lock);
    return 0;
}

int broadcast_unregister(broadcast_manager_t* mgr, socket_t socket) {
    if (!mgr || socket == INVALID_SOCKET) {
        return -1;
    }
    
    mutex_lock(&mgr->lock);
    
    // Find and deactivate client
    for (int i = 0; i < MAX_BROADCAST_CLIENTS; i++) {
        if (mgr->clients[i].active && mgr->clients[i].socket == socket) {
            mgr->clients[i].active = 0;
            mgr->clients[i].socket = INVALID_SOCKET;
            mgr->client_count--;
            mutex_unlock(&mgr->lock);
            return 0;
        }
    }
    
    mutex_unlock(&mgr->lock);
    return -1;  // Client not found
}

int broadcast_update_room(broadcast_manager_t* mgr, socket_t socket, int room_id) {
    if (!mgr || socket == INVALID_SOCKET) {
        return -1;
    }
    
    mutex_lock(&mgr->lock);
    
    // Find and update client room
    for (int i = 0; i < MAX_BROADCAST_CLIENTS; i++) {
        if (mgr->clients[i].active && mgr->clients[i].socket == socket) {
            mgr->clients[i].room_id = room_id;
            mutex_unlock(&mgr->lock);
            return 0;
        }
    }
    
    mutex_unlock(&mgr->lock);
    return -1;  // Client not found
}

int broadcast_to_room(broadcast_manager_t* mgr, int room_id,
                      uint16_t msg_type, const char* payload) {
    if (!mgr) {
        return -1;
    }
    
    // Copy target sockets while holding lock (minimize lock time)
    socket_t targets[MAX_BROADCAST_CLIENTS];
    int target_count = 0;
    
    mutex_lock(&mgr->lock);
    
    for (int i = 0; i < MAX_BROADCAST_CLIENTS; i++) {
        if (mgr->clients[i].active && mgr->clients[i].room_id == room_id) {
            targets[target_count++] = mgr->clients[i].socket;
        }
    }
    
    mutex_unlock(&mgr->lock);
    
    // Send to targets without holding lock (I/O can be slow)
    int sent_count = 0;
    for (int i = 0; i < target_count; i++) {
        if (protocol_send_message(targets[i], msg_type, payload, NULL) > 0) {
            sent_count++;
        }
    }
    
    return sent_count;
}

void broadcast_destroy(broadcast_manager_t* mgr) {
    if (mgr) {
        mutex_destroy(&mgr->lock);
    }
}

