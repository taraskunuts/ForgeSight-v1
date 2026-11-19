
import tkinter as tk
from tkinter import messagebox

from core.settings import save_settings


# ==========================================
# CALIBRATION WINDOW
# ==========================================

def open_calibration(root, settings, dashboard_resolution):

    panel = tk.Toplevel(root)
    panel.title("ForgeSight - Calibration")
    panel.geometry("480x430")
    panel.minsize(420, 380)
    panel.configure(bg="#F5EBDD")
    panel.transient(root)

    # Colors
    NAVY = "#142B49"
    BEIGE = "#F5EBDD"
    GOLD = "#B58B58"
    DARK = "#202936"
    PANEL = "#FFFFFF"
    MUTED = "#7B8794"

    # Header
    tk.Label(
        panel,
        text="DISPLAY CALIBRATION",
        font=("Segoe UI", 17, "bold"),
        bg=BEIGE,
        fg=NAVY
    ).pack(anchor="w", padx=25, pady=(25, 5))

    tk.Label(
        panel,
        text="Detect your current desktop display resolution.",
        font=("Segoe UI", 10),
        bg=BEIGE,
        fg=MUTED
    ).pack(anchor="w", padx=25, pady=(0, 20))

    # Resolution display
    resolution_frame = tk.Frame(
        panel,
        bg=PANEL,
        padx=20,
        pady=20
    )
    resolution_frame.pack(fill="x", padx=25, pady=10)

    tk.Label(
        resolution_frame,
        text="DETECTED RESOLUTION",
        font=("Segoe UI", 9, "bold"),
        bg=PANEL,
        fg=MUTED
    ).pack(anchor="w")

    saved_width = settings["resolution_width"]
    saved_height = settings["resolution_height"]

    initial_resolution = (
        f"{saved_width} x {saved_height}"
        if saved_width and saved_height
        else "Not detected"
    )

    resolution_label = tk.Label(
        resolution_frame,
        text=initial_resolution,
        font=("Segoe UI", 23, "bold"),
        bg=PANEL,
        fg=NAVY
    )
    resolution_label.pack(anchor="w", pady=(8, 0))

    status = tk.Label(
        panel,
        text="Waiting for display scan...",
        bg=BEIGE,
        fg=MUTED,
        font=("Segoe UI", 9)
    )
    status.pack(pady=10)

    # Display scanning
    def scan_display():
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        settings["resolution_width"] = width
        settings["resolution_height"] = height

        resolution_label.config(
            text=f"{width} x {height}"
        )

        try:
            save_settings(settings)

            status.config(
                text="Display detected and saved!",
                fg="#287A45"
            )

            dashboard_resolution.config(
                text=f"{width} x {height}"
            )

        except OSError as error:
            messagebox.showerror(
                "Save failed",
                str(error),
                parent=panel
            )

    # Scan button
    tk.Button(
        panel,
        text="SCAN DISPLAY",
        command=scan_display,
        bg=NAVY,
        fg=BEIGE,
        activebackground=GOLD,
        activeforeground=NAVY,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=20,
        pady=12,
        cursor="hand2"
    ).pack(pady=15)

    # Overlay setting
    overlay_var = tk.BooleanVar(
        value=settings["show_overlay"]
    )

    def save_overlay():
        settings["show_overlay"] = overlay_var.get()

        try:
            save_settings(settings)

        except OSError as error:
            messagebox.showerror(
                "Save failed",
                str(error),
                parent=panel
            )

    tk.Checkbutton(
        panel,
        text="Enable vision detection overlay",
        variable=overlay_var,
        command=save_overlay,
        bg=BEIGE,
        fg=DARK,
        activebackground=BEIGE,
        font=("Segoe UI", 10)
    ).pack(anchor="w", padx=25, pady=10)
