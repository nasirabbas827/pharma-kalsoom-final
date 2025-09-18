import tkinter as tk
from tkinter import messagebox
import sqlite3
from admin_dashboard import AdminDashboard
from user_dashboard import UserDashboard

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PharmaCare - Login")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.db_name = "pharmacare.db"
        self.create_login_page()

    def create_login_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame with border and padding
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(expand=True)

        # Login Frame with white background and shadow effect
        login_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        login_frame.pack(pady=100, padx=50, ipadx=20, ipady=20)

        # Title
        tk.Label(
            login_frame,
            text="PharmaCare Login",
            font=("Arial", 24, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(pady=20)

        # Username
        tk.Label(
            login_frame,
            text="Username:",
            font=("Arial", 14),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).pack(pady=(10, 5), anchor=tk.W, padx=20)
        self.username_entry = tk.Entry(
            login_frame,
            font=("Arial", 14),
            width=30,
            bg="#ecf0f1",  # Very light gray
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.username_entry.pack(pady=(0, 10), padx=20)

        # Password
        tk.Label(
            login_frame,
            text="Password:",
            font=("Arial", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(pady=(10, 5), anchor=tk.W, padx=20)
        self.password_entry = tk.Entry(
            login_frame,
            show="*",
            font=("Arial", 14),
            width=30,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.password_entry.pack(pady=(0, 20), padx=20)

        # Login Button
        tk.Button(
            login_frame,
            text="Login",
            font=("Arial", 14, "bold"),
            bg="#3498db",  # Blue button
            fg="#ffffff",  # White text
            activebackground="#2980b9",  # Darker blue on click
            activeforeground="#ffffff",
            bd=0,
            relief=tk.FLAT,
            command=self.login,
            width=15
        ).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT user_id, user_type FROM users WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                user_id, user_type = user
                self.redirect_to_dashboard(user_id, user_type)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def redirect_to_dashboard(self, user_id, user_type):
        for widget in self.root.winfo_children():
            widget.destroy()

        if user_type == "Admin":
            AdminDashboard(self.root, user_id, self)
        else:
            UserDashboard(self.root, user_id, self)

    def logout(self):
        self.create_login_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()