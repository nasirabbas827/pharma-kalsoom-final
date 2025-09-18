import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ManageCategories:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.selected_category_id = None
        self.root.title("PharmaCare - Manage Categories")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_manage_categories_page()

    def create_manage_categories_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column: Categories Table
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            left_frame,
            text="Categories List",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))

        # Treeview for table
        columns = ("ID", "Category Name")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Category Name", text="Category Name")
        self.tree.column("ID", width=80)
        self.tree.column("Category Name", width=300)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right column: Category Form
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            right_frame,
            text="Category Form",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Form fields
        form_frame = tk.Frame(right_frame, bg="#ffffff")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Category Name
        tk.Label(
            form_frame,
            text="Category Name:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.category_name_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",  # Light gray
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.category_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Buttons
        button_frame = tk.Frame(right_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=20)

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

        tk.Button(button_frame, text="Add Category", command=self.add_category, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update Category", command=self.update_category, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Category", command=self.delete_category, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style).pack(side=tk.LEFT, padx=5)

        # Back button
        tk.Button(
            right_frame,
            text="Dashboard",
            command=self.back_to_dashboard,
            **button_style
        ).pack(pady=20)

        # Load categories
        self.load_categories()

    def load_categories(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                SELECT category_id, category_name 
                FROM categories 
                ORDER BY category_id
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_category_id = values[0]
            self.category_name_entry.delete(0, tk.END)
            self.category_name_entry.insert(0, values[1])

    def add_category(self):
        category_name = self.category_name_entry.get().strip()

        if not category_name:
            messagebox.showerror("Error", "Please enter category name")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO categories (category_name)
                VALUES (?)
            """, (category_name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category added successfully")
            self.clear_form()
            self.load_categories()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category name already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding category: {e}")

    def update_category(self):
        if not self.selected_category_id:
            messagebox.showerror("Error", "Please select a category to update")
            return

        category_name = self.category_name_entry.get().strip()

        if not category_name:
            messagebox.showerror("Error", "Please enter category name")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                UPDATE categories 
                SET category_name = ?
                WHERE category_id = ?
            """, (category_name, self.selected_category_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category updated successfully")
            self.clear_form()
            self.load_categories()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category name already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating category: {e}")

    def delete_category(self):
        if not self.selected_category_id:
            messagebox.showerror("Error", "Please select a category to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this category? Note: This may affect items using this category."):
            try:
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                cur.execute("DELETE FROM categories WHERE category_id = ?", (self.selected_category_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Category deleted successfully")
                self.clear_form()
                self.load_categories()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting category: {e}")

    def clear_form(self):
        self.category_name_entry.delete(0, tk.END)
        self.selected_category_id = None

    def back_to_dashboard(self):
        from admin_dashboard import AdminDashboard

        AdminDashboard(self.root, self.user_id, self.app)