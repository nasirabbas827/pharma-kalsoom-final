import tkinter as tk
from tkinter import messagebox
import sqlite3
from manage_users import ManageUsers
from manage_categories import ManageCategories
from manage_items import ManageItems
from manage_purchase import ManagePurchases
from reports import Reports

class AdminDashboard:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.root.title("PharmaCare - Admin Dashboard")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_dashboard()

    def create_dashboard(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame with padding
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(expand=True)

        # Dashboard frame with white background and shadow effect
        dashboard_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        dashboard_frame.pack(pady=100, padx=50, ipadx=20, ipady=20)

        # Title
        tk.Label(
            dashboard_frame,
            text="PharmaCare Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(pady=20)

        # Welcome message
        tk.Label(
            dashboard_frame,
            text="Welcome, Admin!",
            font=("Arial", 16),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).pack(pady=10)

        # Button frame for grid layout
        button_frame = tk.Frame(dashboard_frame, bg="#ffffff")
        button_frame.pack(pady=20)

        # Button styles
        button_style = {
            "font": ("Arial", 14, "bold"),
            "bg": "#3498db",  # Blue button
            "fg": "#ffffff",  # White text
            "activebackground": "#2980b9",  # Darker blue on click
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "width": 20
        }

        # Buttons arranged in a 2x3 grid
        buttons = [
            ("Manage Users", self.manage_users),
            ("Manage Categories", self.manage_categories),
            ("Manage Items", self.manage_items),
            ("Manage Purchases", self.manage_purchases),
            ("Generate Reports", self.generate_reports),
            ("Logout", self.app.logout)
        ]

        for index, (text, command) in enumerate(buttons):
            row = index // 3  # Integer division to determine row
            col = index % 3   # Modulo to determine column
            tk.Button(
                button_frame,
                text=text,
                command=command,
                **button_style
            ).grid(row=row, column=col, padx=10, pady=10)

    def manage_users(self):
        ManageUsers(self.root, self.user_id, self.app)

    def manage_categories(self):
        ManageCategories(self.root, self.user_id, self.app)

    def manage_items(self):
        ManageItems(self.root, self.user_id, self.app)

    def manage_purchases(self):
        ManagePurchases(self.root, self.user_id, self.app)

    def generate_reports(self):
        Reports(self.root, self.user_id, self.app)