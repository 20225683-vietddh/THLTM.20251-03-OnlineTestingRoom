#include "protocol.h"
#include "utils.h"
#include <string.h>
#include <time.h>

void protocol_init_header(protocol_header_t* header, uint16_t msg_type,
                          uint32_t length, const char* session_token) {
    // Zero out entire header first
    memset(header, 0, sizeof(protocol_header_t));
    
    // Set header fields (convert to network byte order)
    header->magic = htonl(PROTOCOL_MAGIC);        // Convert 32-bit to big-endian
    header->version = htons(PROTOCOL_VERSION);    // Convert 16-bit to big-endian
    header->message_type = htons(msg_type);       // Convert 16-bit to big-endian
    header->length = htonl(length);               // Convert 32-bit to big-endian
    
    // Set timestamp (current Unix time)
    header->timestamp = utils_get_unix_timestamp();
    
    // Generate unique message ID
    utils_generate_message_id(header->message_id);
    
    // Copy session token if provided (max 32 bytes)
    if (session_token != NULL) {
        strncpy(header->session_token, session_token, 32);
        header->session_token[31] = '\0';  // Ensure null-termination
    }
    
    // Reserved field already zeroed by memset
}

int protocol_validate_header(protocol_header_t* header) {
    // Check 1: Validate magic number
    uint32_t magic = ntohl(header->magic);  // Convert from network byte order
    if (magic != PROTOCOL_MAGIC) {
        return -1;  // Invalid magic - not our protocol
    }
    
    // Check 2: Validate version
    uint16_t version = ntohs(header->version);
    if (version != PROTOCOL_VERSION) {
        return -2;  // Version mismatch - unsupported version
    }
    
    // Check 3: Validate payload length
    uint32_t length = ntohl(header->length);
    if (length > MAX_PAYLOAD_SIZE) {
        return -3;  // Payload too large - prevent memory issues
    }
    
    return 0;  // Header is valid
}

int protocol_send_message(socket_t socket, uint16_t msg_type, 
                          const char* payload, const char* session_token) {
    protocol_header_t header;
    uint32_t payload_length = (payload != NULL) ? strlen(payload) : 0;
    
    // Step 1: Initialize header
    protocol_init_header(&header, msg_type, payload_length, session_token);
    
    // Step 2: Send header (64 bytes fixed)
    // Network Programming Note:
    // We send the header as-is since multi-byte fields are already
    // in network byte order (big-endian) from init_header()
    int header_sent = socket_send_data(socket, (char*)&header, sizeof(protocol_header_t));
    if (header_sent != sizeof(protocol_header_t)) {
        return -1;  // Header send failed
    }
    
    // Step 3: Send payload if exists
    if (payload_length > 0) {
        int payload_sent = socket_send_data(socket, payload, payload_length);
        if (payload_sent != (int)payload_length) {
            return -2;  // Payload send failed
        }
        return header_sent + payload_sent;  // Total bytes sent
    }
    
    return header_sent;  // Only header sent
}

int protocol_receive_message(socket_t socket, protocol_header_t* header,
                             char* payload, int max_payload_size) {
    // Step 1: Receive header (64 bytes fixed)
    // Network Programming Note:
    // TCP is a byte stream protocol, not message-based.
    // We need to receive exactly 64 bytes for the header.
    int bytes_received = socket_receive_data(socket, (char*)header, sizeof(protocol_header_t));
    if (bytes_received != sizeof(protocol_header_t)) {
        return -1;  // Header receive failed or connection closed
    }
    
    // Step 2: Validate header
    int validation = protocol_validate_header(header);
    if (validation != 0) {
        return validation;  // Return validation error code (-1, -2, or -3)
    }
    
    // Step 3: Get payload length (convert from network byte order)
    uint32_t payload_length = ntohl(header->length);
    
    // Check if payload buffer is large enough
    if (payload_length > (uint32_t)(max_payload_size - 1)) {
        return -4;  // Buffer too small for payload
    }
    
    // Step 4: Receive payload if exists
    if (payload_length > 0) {
        bytes_received = socket_receive_data(socket, payload, payload_length);
        if (bytes_received != (int)payload_length) {
            return -5;  // Payload receive failed
        }
        // Null-terminate payload (useful if it's JSON/text)
        payload[payload_length] = '\0';
    } else {
        // No payload
        payload[0] = '\0';
    }
    
    return (int)payload_length;  // Return payload length
}
