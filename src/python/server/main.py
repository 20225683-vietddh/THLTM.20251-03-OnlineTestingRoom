#!/usr/bin/env python3
"""
Main Entry Point for Test Server Application
Django-style clean architecture with separated concerns

Usage:
    python src/python/server/main.py
    python -m src.python.server.main
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.server_gui import TestServerGUI


def main():
    """Start the server application"""
    print("Starting Test Server...")
    app = TestServerGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()

