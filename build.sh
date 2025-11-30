#!/bin/bash
# Build script for Linux/macOS

echo "================================================"
echo "Building Network Programming Project"
echo "================================================"

# Check if GCC is installed
if ! command -v gcc &> /dev/null; then
    echo "ERROR: GCC not found! Please install GCC first."
    echo "Ubuntu/Debian: sudo apt-get install gcc"
    echo "macOS: xcode-select --install"
    exit 1
fi

# Create lib directory
mkdir -p lib

# Detect OS and compile
OS_TYPE=$(uname -s)
echo ""
echo "Detected OS: $OS_TYPE"
echo "Compiling C library..."

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS
    gcc -Wall -O2 -fPIC -dynamiclib \
        src/network/core/socket_ops.c \
        src/network/core/protocol.c \
        src/network/core/utils.c \
        src/network/core/thread_pool.c \
        src/network/python_wrapper.c \
        -o lib/libnetwork.dylib -I src/network -lpthread
    LIB_FILE="lib/libnetwork.dylib"
else
    # Linux
    gcc -Wall -O2 -fPIC -shared \
        src/network/core/socket_ops.c \
        src/network/core/protocol.c \
        src/network/core/utils.c \
        src/network/core/thread_pool.c \
        src/network/python_wrapper.c \
        -o lib/libnetwork.so -I src/network -lpthread
    LIB_FILE="lib/libnetwork.so"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "Build successful!"
    echo "Library created: $LIB_FILE"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Install Python dependencies: pip install -r requirements.txt"
    echo "2. Run server: python src/python/chat_server.py"
    echo "3. Run client: python src/python/chat_client.py"
    echo "================================================"
else
    echo ""
    echo "================================================"
    echo "Build failed! Please check the error messages above."
    echo "================================================"
    exit 1
fi
