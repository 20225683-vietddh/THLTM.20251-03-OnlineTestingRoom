#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>

/**
 * @brief Generate unique message ID (16 bytes)
 * @param message_id Buffer to store message ID (must be at least 16 bytes)
 * 
 * Implementation:
 * Simple approach using timestamp + counter for uniqueness
 * Format: 8 bytes timestamp + 8 bytes counter
 */
void utils_generate_message_id(char* message_id);

/**
 * @brief Get current Unix timestamp
 * @return Unix timestamp (seconds since epoch: 1970-01-01 00:00:00 UTC)
 * 
 * Network Programming Note:
 * Unix timestamp is timezone-independent, making it ideal for
 * distributed systems and network protocols.
 */
int64_t utils_get_unix_timestamp(void);

#endif // UTILS_H
