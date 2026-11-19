
import tkinter as tk

from core.settings import load_settings
from gui.dashboard import create_dashboard


# ==========================================
# FORGESIGHT APPLICATION
# ==========================================

def main():

    # Load application settings
    settings = load_settings()

    # Initialize main window
    root = tk.Tk()

    # Build dashboard
    create_dashboard(root, settings)

    # Start application
    root.mainloop()


if __name__ == "__main__":
    main()
