#include "utils.h"
#include <time.h>
#include <string.h>
#include <stdio.h>

#ifdef _WIN32
    #include <windows.h>
#else
    #include <sys/time.h>
#endif

// ==================== UTILITIES ====================

void utils_generate_message_id(char* message_id) {
    // Simple implementation: timestamp + counter
    static int counter = 0;
    time_t now = time(NULL);
    
    // Format: 8 hex digits (timestamp) + 8 hex digits (counter)
    snprintf(message_id, 16, "%08x%08x", (unsigned int)now, counter++);
    
    // Pad remaining bytes with zeros
    memset(message_id + strlen(message_id), 0, 16 - strlen(message_id));
}

int64_t utils_get_unix_timestamp(void) {
#ifdef _WIN32
    // Windows: Use time() for simplicity
    return (int64_t)time(NULL);
#else
    // UNIX/Linux: Can use gettimeofday() for microsecond precision
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (int64_t)tv.tv_sec;  // Return seconds only
#endif
}
