#!/usr/bin/env python3
"""
Main Entry Point for Test Client Application
Clean architecture matching server structure

Usage:
    python src/python/client/main.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.client_app import TestClientApp


def main():
    """Start the client application"""
    print("Starting Test Client...")
    app = TestClientApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()

