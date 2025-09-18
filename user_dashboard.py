import tkinter as tk
from tkinter import messagebox
import sqlite3
from manage_sale import ManageSales
from datetime import datetime

class UserDashboard:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.root.title("PharmaCare - User Dashboard")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_dashboard()

    def create_dashboard(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        dashboard_frame = tk.Frame(self.root, bg="#ffffff", bd=5, relief=tk.RAISED)
        dashboard_frame.pack(pady=20, padx=20)

        tk.Label(
            dashboard_frame,
            text="User Dashboard",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(pady=10)

        # User functionalities
        tk.Label(
            dashboard_frame,
            text=f"Welcome, User! | {datetime.now().strftime('%I:%M %p PKT, %A, %B %d, %Y')}",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).pack(pady=10)

        button_style = {
            "font": ("Arial", 12, "bold"),
            "bg": "#3498db",  # Blue button
            "fg": "#ffffff",  # White text
            "activebackground": "#2980b9",  # Darker blue on click
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "width": 15
        }

        tk.Button(dashboard_frame, text="Make Sale", command=self.make_sale, **button_style).pack(pady=5)
        tk.Button(dashboard_frame, text="Logout", command=self.app.logout, **button_style).pack(pady=20)

    def make_sale(self):
        ManageSales(self.root, self.user_id, self.app)