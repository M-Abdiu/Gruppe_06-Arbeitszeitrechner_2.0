import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui import main as start_ui

if __name__ in {"__main__", "__mp_main__"}:
    start_ui()
