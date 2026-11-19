
import tkinter as tk
from tkinter import messagebox

from gui.calibration import open_calibration
from gui.overlay import open_overlay


# ==========================================
# COLORS
# ==========================================

NAVY = "#17243A"
DARK = "#101A2B"
BEIGE = "#E8DCC5"
ACCENT = "#C9A66B"
GREEN = "#75B798"
RED = "#D97979"
GRAY = "#A9B0BA"


# ==========================================
# DASHBOARD
# ==========================================

def create_dashboard(root, settings):

    root.title("ForgeSight")
    root.geometry("1050x700")
    root.minsize(850, 600)
    root.configure(bg=BEIGE)

    # HEADER

    header = tk.Frame(
        root,
        bg=NAVY,
        height=85
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="ForgeSight",
        bg=NAVY,
        fg=BEIGE,
        font=("Segoe UI", 24, "bold")
    ).pack(
        side="left",
        padx=25,
        pady=15
    )

    tk.Label(
        header,
        text="VISION SYSTEM",
        bg=NAVY,
        fg=ACCENT,
        font=("Segoe UI", 10, "bold")
    ).pack(
        side="right",
        padx=25
    )

    # MAIN CONTENT

    main = tk.Frame(
        root,
        bg=BEIGE
    )

    main.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    # SYSTEM STATUS

    tk.Label(
        main,
        text="SYSTEM STATUS",
        bg=BEIGE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", pady=(0, 10))

    status_frame = tk.Frame(
        main,
        bg=BEIGE
    )

    status_frame.pack(
        fill="x",
        pady=(0, 20)
    )

    def create_status_card(parent, title, value):

        card = tk.Frame(
            parent,
            bg=NAVY,
            padx=18,
            pady=15
        )

        tk.Label(
            card,
            text=title,
            bg=NAVY,
            fg=GRAY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        value_label = tk.Label(
            card,
            text=value,
            bg=NAVY,
            fg=BEIGE,
            font=("Segoe UI", 15, "bold")
        )

        value_label.pack(
            anchor="w",
            pady=(5, 0)
        )

        return card, value_label

    for column in range(3):
        status_frame.columnconfigure(
            column,
            weight=1
        )

    capture_card, capture_status = create_status_card(
        status_frame,
        "CAPTURE",
        "READY"
    )

    capture_card.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 8)
    )

    vision_card, vision_status = create_status_card(
        status_frame,
        "VISION",
        "STANDBY"
    )

    vision_card.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=8
    )

    controller_card, controller_status = create_status_card(
        status_frame,
        "CONTROLLER",
        "OFFLINE"
    )

    controller_card.grid(
        row=0,
        column=2,
        sticky="nsew",
        padx=(8, 0)
    )

    # MINIGAME CONTROLLERS

    tk.Label(
        main,
        text="MINIGAME CONTROLLERS",
        bg=BEIGE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    controller_frame = tk.Frame(
        main,
        bg=NAVY,
        padx=18,
        pady=10
    )

    controller_frame.pack(
        fill="x",
        pady=(0, 20)
    )

    minigames = [
        "Heat Pumping",
        "Moving Bar",
        "Shape / Hammering"
    ]

    for name in minigames:

        row = tk.Frame(
            controller_frame,
            bg=NAVY
        )

        row.pack(
            fill="x",
            pady=8
        )

        tk.Label(
            row,
            text=name,
            bg=NAVY,
            fg=BEIGE,
            font=("Segoe UI", 11)
        ).pack(side="left")

        tk.Label(
            row,
            text="NOT INITIALIZED",
            bg=NAVY,
            fg=GRAY,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right")

    # CONFIGURATION

    tk.Label(
        main,
        text="CONFIGURATION",
        bg=BEIGE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    config_frame = tk.Frame(
        main,
        bg=NAVY,
        padx=18,
        pady=15
    )

    config_frame.pack(fill="x")

    resolution_label = tk.Label(
        config_frame,
        text=(
            f"Desktop resolution: "
            f"{root.winfo_screenwidth()} x "
            f"{root.winfo_screenheight()}"
        ),
        bg=NAVY,
        fg=BEIGE,
        font=("Segoe UI", 10)
    )

    resolution_label.pack(anchor="w")

    # BUTTONS

    button_frame = tk.Frame(
        main,
        bg=BEIGE
    )

    button_frame.pack(
        fill="x",
        pady=20
    )

    active_overlay = None

    def test_vision():
        print("[ForgeSight] TEST VISION clicked")

    try:
        from gui.overlay import open_overlay

        print("[ForgeSight] Import successful")
        open_overlay(root, settings)
        print("[ForgeSight] Overlay launched")

    except Exception as error:
        import traceback
        print("[ForgeSight] Overlay failed:")
        traceback.print_exc()

    def start_system():

        messagebox.showinfo(
            "ForgeSight",
            "The controller is not implemented yet."
        )

    def calibrate():

        open_calibration(
            root,
            settings,
            resolution_label
        )

    def create_button(parent, text, command, color):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=BEIGE,
            activebackground=ACCENT,
            activeforeground=NAVY,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=12,
            cursor="hand2"
        )

    create_button(
        button_frame,
        "CALIBRATE",
        calibrate,
        NAVY
    ).pack(
        side="left",
        padx=(0, 10)
    )

    create_button(
        button_frame,
        "TEST VISION",
        test_vision,
        NAVY
    ).pack(
        side="left",
        padx=10
    )

    create_button(
        button_frame,
        "START",
        start_system,
        ACCENT
    ).pack(side="right")
