"""
run_app.py - Convenience Launcher for Koraput Tourism Application.
Starts the server and automatically opens the application in your default web browser.
"""

import sys
import os
import webbrowser
import threading
import time

# Ensure koraput_tourism directory is in path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "koraput_tourism")
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import tornado.ioloop
from server import make_app

PORT = 8080

def open_browser():
    time.sleep(1.2)
    url = f"http://localhost:{PORT}"
    print(f"\n[Launching Browser] Opening {url}...")
    webbrowser.open(url)

if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print("=" * 65)
    print("       KORAPUT TOURISM APPLICATION - HEAVEN OF ODISHA")
    print("=" * 65)
    print(f" * Public Portal:      http://localhost:{PORT}")
    print(f" * Dedicated Admin:    http://localhost:{PORT}/admin/login")
    print(f" * Admin Credentials:  admin / koraput2026 (or 1-click Quick Bypass)")
    print(f" * Mascot:             Kora - The Spirit of Koraput")
    print(f" * AI Mode Enabled:    Ask Kora AI Tour Guide")
    print("=" * 65)
    
    # Auto open browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\n[Shutting down] Server stopped.")
