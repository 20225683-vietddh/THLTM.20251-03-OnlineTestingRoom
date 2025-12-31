#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>

/**
 * @brief Generate unique message ID
 * @param message_id Buffer to store 16-byte message ID
 */
void utils_generate_message_id(char* message_id);

/**
 * @brief Get current Unix timestamp
 * @return Unix timestamp in seconds
 */
int64_t utils_get_unix_timestamp(void);

#endif // UTILS_H
