"""
Run the CoTShield Web Viewer

This script starts the interactive web interface for analyzing reasoning traces.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.viewer import start_viewer


if __name__ == "__main__":
    print("\n🛡️  CoTShield - Reasoning Trace Viewer")
    print("=" * 60)
    print("\nStarting web viewer...")
    print("Open your browser to: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    try:
        start_viewer(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n\nShutting down viewer...")
        print("Goodbye! 👋\n")
