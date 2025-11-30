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

REM Detect Python architecture
echo.
echo Detecting Python architecture...
for /f %%i in ('python -c "import struct; print(struct.calcsize('P') * 8)"') do set PYTHON_BITS=%%i
echo Python is %PYTHON_BITS%-bit

REM Set architecture flag for GCC
if "%PYTHON_BITS%"=="64" (
    set ARCH_FLAG=-m64
    echo Building 64-bit DLL...
) else (
    set ARCH_FLAG=-m32
    echo Building 32-bit DLL...
)

REM Compile the shared library
echo.
echo Compiling C library...
gcc -Wall -O2 %ARCH_FLAG% -shared ^
    src/network/core/socket_ops.c ^
    src/network/core/protocol.c ^
    src/network/core/utils.c ^
    src/network/python_wrapper.c ^
    -o lib/network.dll -lws2_32 -I src/network

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo Build successful!
    echo Library created: lib/network.dll
    echo ================================================
    echo.
    echo Next steps:
    echo 1. Install Python dependencies: pip install -r requirements.txt
    echo 2. Run server: python src/python/server/main.py
    echo 3. Run client: python src/python/client/main.py
    echo ================================================
) else (
    echo.
    echo ================================================
    echo Build failed! Please check the error messages above.
    echo ================================================
)

pause
