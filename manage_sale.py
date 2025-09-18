import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ManageSales:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.selected_sale_id = None
        self.root.title("PharmaCare - Manage Sales")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_manage_sales_page()

    def create_manage_sales_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column: Sales Table
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=(0, 20))

        # Search frame
        search_frame = tk.Frame(left_frame, bg="#ffffff")
        search_frame.pack(fill=tk.X, pady=(10, 10))
        tk.Label(
            search_frame,
            text="Search Items (by ID, Name, or Category):",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(
            search_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",  # Light gray
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.search_entry.bind("<Return>", lambda e: self.search_items())
        tk.Button(
            search_frame,
            text="Search",
            command=self.search_items,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="#ffffff",
            activebackground="#2980b9",
            bd=0,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=(5, 0))
        tk.Button(
            search_frame,
            text="Clear Search",
            command=self.clear_search,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="#ffffff",
            activebackground="#2980b9",
            bd=0,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Label(
            left_frame,
            text="Sales List",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(anchor=tk.W, padx=20, pady=(5, 5))

        # Treeview for table
        columns = ("ID", "Customer", "Date", "Item", "Quantity", "Unit Price", "Total")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50)
            elif col == "Item" or col == "Customer":
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right column: Sale Form
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 20))

        tk.Label(
            right_frame,
            text="Sale Form",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Form fields
        form_frame = tk.Frame(right_frame, bg="#ffffff")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Customer Name
        tk.Label(
            form_frame,
            text="Customer Name:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.customer_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.customer_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Item
        tk.Label(
            form_frame,
            text="Item:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.item_combo = ttk.Combobox(
            form_frame,
            width=22,
            state="readonly",
            font=("Arial", 12)
        )
        self.item_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        self.item_combo.bind("<<ComboboxSelected>>", self.update_unit_price)

        # Quantity
        tk.Label(
            form_frame,
            text="Quantity:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.quantity_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        self.quantity_entry.bind("<KeyRelease>", self.update_total)

        # Unit Price (read-only)
        tk.Label(
            form_frame,
            text="Unit Price:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.unit_price_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID,
            state="readonly"
        )
        self.unit_price_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Total Amount (read-only)
        tk.Label(
            form_frame,
            text="Total Amount:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.total_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID,
            state="readonly"
        )
        self.total_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Buttons
        button_frame = tk.Frame(right_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=10)

        button_style = {
            "font": ("Arial", 12, "bold"),
            "bg": "#3498db",
            "fg": "#ffffff",
            "activebackground": "#2980b9",
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "width": 12
        }

        tk.Button(button_frame, text="Add Sale", command=self.add_sale, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style).pack(side=tk.LEFT, padx=5)

        # Back button
        tk.Button(
            right_frame,
            text="Dashboard",
            command=self.back_to_dashboard,
            **button_style
        ).pack(pady=20)

        # Load data
        self.load_items()
        self.load_sales()

    def load_items(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT item_id, item_name, sale_price, current_stock FROM items ORDER BY item_name")
            self.items = cur.fetchall()
            self.item_map = {row[1]: (row[0], row[2], row[3]) for row in self.items}  # item_id, sale_price, stock
            self.item_combo['values'] = sorted(list(self.item_map.keys()))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading items: {e}")

    def load_sales(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                SELECT s.sale_id, s.customer_name, s.sale_date, i.item_name, 
                       s.quantity, s.unit_price, s.total_amount
                FROM sales s 
                JOIN items i ON s.item_id = i.item_id 
                ORDER BY s.sale_date DESC
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading sales: {e}")

    def search_items(self):
        search_term = self.search_entry.get().strip()
        if search_term:
            try:
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                if search_term.isdigit():
                    cur.execute("""
                        SELECT i.item_id, i.item_name, c.category_name, i.description, i.purchase_price, 
                               i.sale_price, i.current_stock, i.image_path
                        FROM items i 
                        JOIN categories c ON i.category_id = c.category_id 
                        WHERE i.item_id = ?
                        ORDER BY i.item_id
                    """, (int(search_term),))
                else:
                    cur.execute("""
                        SELECT i.item_id, i.item_name, c.category_name, i.description, i.purchase_price, 
                               i.sale_price, i.current_stock, i.image_path
                        FROM items i 
                        JOIN categories c ON i.category_id = c.category_id 
                        WHERE LOWER(i.item_name) LIKE LOWER(?) 
                           OR LOWER(c.category_name) LIKE LOWER(?)
                        ORDER BY i.item_id
                    """, (f"%{search_term}%", f"%{search_term}%"))
                rows = cur.fetchall()
                self.item_combo['values'] = [row[1] for row in rows]
                self.item_map = {row[1]: (row[0], row[5], row[6]) for row in rows}  # item_id, sale_price, stock
                conn.close()
                if not rows:
                    messagebox.showinfo("No Results", "No items found matching the search criteria.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error searching items: {e}")
        else:
            self.load_items()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_items()

    def update_unit_price(self, event=None):
        item_name = self.item_combo.get()
        if item_name and item_name in self.item_map:
            _, sale_price, _ = self.item_map[item_name]
            self.unit_price_entry.config(state="normal")
            self.unit_price_entry.delete(0, tk.END)
            self.unit_price_entry.insert(0, f"{sale_price:.2f}")
            self.unit_price_entry.config(state="readonly")
            self.update_total()

    def update_total(self, event=None):
        try:
            quantity = int(self.quantity_entry.get() or 0)
            unit_price = float(self.unit_price_entry.get() or 0)
            total = quantity * unit_price
            self.total_entry.config(state="normal")
            self.total_entry.delete(0, tk.END)
            self.total_entry.insert(0, f"{total:.2f}")
            self.total_entry.config(state="readonly")
        except ValueError:
            self.total_entry.config(state="normal")
            self.total_entry.delete(0, tk.END)
            self.total_entry.insert(0, "0.00")
            self.total_entry.config(state="readonly")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_sale_id = values[0]
            self.customer_entry.delete(0, tk.END)
            self.customer_entry.insert(0, values[1] or "")
            self.item_combo.set(values[3])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(values[4]))
            self.update_unit_price()

    def add_sale(self):
        customer = self.customer_entry.get().strip()
        item_name = self.item_combo.get()
        try:
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
            total_amount = float(self.total_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer, Unit Price and Total must be numbers")
            return

        if not all([item_name, quantity > 0, unit_price > 0]):
            messagebox.showerror("Error", "Item and Quantity are required, Quantity/Unit Price must be positive")
            return

        item_id, _, stock = self.item_map.get(item_name, (None, 0, 0))
        if not item_id:
            messagebox.showerror("Error", "Invalid item selected")
            return

        if quantity > stock:
            messagebox.showerror("Error", f"Insufficient stock. Available: {stock}")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            # Insert sale
            cur.execute("""
                INSERT INTO sales (customer_name, item_id, quantity, unit_price, total_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (customer or None, item_id, quantity, unit_price, total_amount))
            # Update item stock
            cur.execute("""
                UPDATE items 
                SET current_stock = current_stock - ? 
                WHERE item_id = ?
            """, (quantity, item_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Sale added and stock updated successfully")
            self.clear_form()
            self.load_items()  # Reload items to update stock
            self.load_sales()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding sale: {e}")

    def clear_form(self):
        self.customer_entry.delete(0, tk.END)
        self.item_combo.set("")
        self.quantity_entry.delete(0, tk.END)
        self.unit_price_entry.config(state="normal")
        self.unit_price_entry.delete(0, tk.END)
        self.unit_price_entry.config(state="readonly")
        self.total_entry.config(state="normal")
        self.total_entry.delete(0, tk.END)
        self.total_entry.insert(0, "0.00")
        self.total_entry.config(state="readonly")
        self.selected_sale_id = None

    def back_to_dashboard(self):
        from user_dashboard import UserDashboard

        UserDashboard(self.root, self.user_id, self.app)