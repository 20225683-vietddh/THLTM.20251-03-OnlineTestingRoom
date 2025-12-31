# Makefile for Network Programming Project
# Cross-platform build system

# Compiler
CC = gcc
CFLAGS = -Wall -O2 -fPIC

# Directories
SRC_DIR = src/network
CORE_DIR = $(SRC_DIR)/core
LIB_DIR = lib

# Source files
SOURCES = $(CORE_DIR)/socket_ops.c \
          $(CORE_DIR)/protocol.c \
          $(CORE_DIR)/utils.c \
          $(CORE_DIR)/thread_pool.c \
          $(CORE_DIR)/broadcast.c \
          $(SRC_DIR)/python_wrapper.c

# Header files
HEADERS = $(CORE_DIR)/socket_ops.h \
          $(CORE_DIR)/protocol.h \
          $(CORE_DIR)/utils.h \
          $(CORE_DIR)/thread_pool.h \
          $(CORE_DIR)/broadcast.h \
          $(SRC_DIR)/network.h

# Detect OS
ifeq ($(OS),Windows_NT)
    # Windows
    TARGET = $(LIB_DIR)/network.dll
    LDFLAGS = -shared -lws2_32
    RM = del /Q
    MKDIR = if not exist $(LIB_DIR) mkdir $(LIB_DIR)
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        # Linux
        TARGET = $(LIB_DIR)/libnetwork.so
        LDFLAGS = -shared
    else ifeq ($(UNAME_S),Darwin)
        # macOS
        TARGET = $(LIB_DIR)/libnetwork.dylib
        LDFLAGS = -dynamiclib
    endif
    RM = rm -f
    MKDIR = mkdir -p $(LIB_DIR)
endif

# Default target
all: $(TARGET)

# Create lib directory
$(LIB_DIR):
	$(MKDIR)

# Build shared library
$(TARGET): $(SOURCES) $(HEADERS) | $(LIB_DIR)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET) $(LDFLAGS)
	@echo "Build complete: $(TARGET)"

# Clean build artifacts
clean:
ifeq ($(OS),Windows_NT)
	if exist $(LIB_DIR) rmdir /S /Q $(LIB_DIR)
else
	$(RM) -r $(LIB_DIR)
endif
	@echo "Clean complete"

# Rebuild
rebuild: clean all

.PHONY: all clean rebuild
