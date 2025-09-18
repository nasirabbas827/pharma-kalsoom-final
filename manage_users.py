import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ManageUsers:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.selected_user_id = None
        self.root.title("PharmaCare - Manage Users")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_manage_users_page()

    def create_manage_users_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column: Users Table
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            left_frame,
            text="Users List",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))

        # Treeview for table
        columns = ("ID", "Username", "Full Name", "User Type", "Created At")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "ID" else 80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right column: User Form
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            right_frame,
            text="User Form",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Form fields
        form_frame = tk.Frame(right_frame, bg="#ffffff")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Username
        tk.Label(
            form_frame,
            text="Username:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",  # Light gray
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.username_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = tk.Entry(
            form_frame,
            show="*",
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.password_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Full Name
        tk.Label(
            form_frame,
            text="Full Name:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fullname_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.fullname_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # User Type
        tk.Label(
            form_frame,
            text="User Type:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.user_type_combo = ttk.Combobox(
            form_frame,
            values=["user", "Admin"],
            width=22,
            state="readonly",
            font=("Arial", 12)
        )
        self.user_type_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Buttons
        button_frame = tk.Frame(right_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=10)

        button_style = {
            "font": ("Arial", 12, "bold"),
            "bg": "#3498db",  # Blue button
            "fg": "#ffffff",  # White text
            "activebackground": "#2980b9",  # Darker blue on click
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "width": 12
        }

        tk.Button(button_frame, text="Add User", command=self.add_user, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update User", command=self.update_user, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete User", command=self.delete_user, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_form, **button_style).pack(side=tk.LEFT, padx=5)

        # Back button
        tk.Button(
            right_frame,
            text="Dashboard",
            command=self.back_to_dashboard,
            **button_style
        ).pack(pady=20)

        # Load users
        self.load_users()

    def load_users(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                SELECT user_id, username, full_name, user_type, created_at 
                FROM users 
                ORDER BY user_id
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading users: {e}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_user_id = values[0]
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, values[1])
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, "")  # Don't show password
            self.fullname_entry.delete(0, tk.END)
            self.fullname_entry.insert(0, values[2])
            self.user_type_combo.set(values[3])

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        user_type = self.user_type_combo.get()

        if not all([username, password, full_name, user_type]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, password, full_name, user_type)
                VALUES (?, ?, ?, ?)
            """, (username, password, full_name, user_type))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User added successfully")
            self.clear_form()
            self.load_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding user: {e}")

    def update_user(self):
        if not self.selected_user_id:
            messagebox.showerror("Error", "Please select a user to update")
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        user_type = self.user_type_combo.get()

        if not all([username, full_name, user_type]):
            messagebox.showerror("Error", "Please fill required fields (password optional)")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            if password:
                cur.execute("""
                    UPDATE users 
                    SET username = ?, password = ?, full_name = ?, user_type = ?
                    WHERE user_id = ?
                """, (username, password, full_name, user_type, self.selected_user_id))
            else:
                cur.execute("""
                    UPDATE users 
                    SET username = ?, full_name = ?, user_type = ?
                    WHERE user_id = ?
                """, (username, full_name, user_type, self.selected_user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated successfully")
            self.clear_form()
            self.load_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating user: {e}")

    def delete_user(self):
        if not self.selected_user_id:
            messagebox.showerror("Error", "Please select a user to delete")
            return

        if self.selected_user_id == self.user_id:
            messagebox.showerror("Error", "Cannot delete your own account")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            try:
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE user_id = ?", (self.selected_user_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "User deleted successfully")
                self.clear_form()
                self.load_users()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting user: {e}")

    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.fullname_entry.delete(0, tk.END)
        self.user_type_combo.set("")
        self.selected_user_id = None

    def back_to_dashboard(self):
        from admin_dashboard import AdminDashboard

        AdminDashboard(self.root, self.user_id, self.app)