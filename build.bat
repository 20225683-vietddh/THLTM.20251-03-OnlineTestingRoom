@echo off
REM Build script for Windows

echo ================================================
echo Building Network Programming Project (Windows)
echo ================================================

REM Check if GCC is installed
where gcc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: GCC not found! Please install MinGW-w64 or TDM-GCC.
    echo Download from: https://www.mingw-w64.org/ or https://jmeubank.github.io/tdm-gcc/
    pause
    exit /b 1
)

REM Create lib directory
if not exist lib mkdir lib

REM Compile the shared library
echo.
echo Compiling C library...
gcc -Wall -O2 -shared src/network/network.c src/network/python_wrapper.c -o lib/network.dll -lws2_32

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo Build successful!
    echo Library created: lib/network.dll
    echo ================================================
    echo.
    echo Next steps:
    echo 1. Install Python dependencies: pip install -r requirements.txt
    echo 2. Run server: python src/python/chat_server.py
    echo 3. Run client: python src/python/chat_client.py
    echo ================================================
) else (
    echo.
    echo ================================================
    echo Build failed! Please check the error messages above.
    echo ================================================
)

pause

