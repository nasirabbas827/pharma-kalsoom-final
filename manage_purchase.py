import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ManagePurchases:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.selected_purchase_id = None
        self.root.title("PharmaCare - Manage Purchases")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_manage_purchases_page()

    def create_manage_purchases_page(self):
        # Clear widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column: Purchases Table
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            left_frame,
            text="Purchases List",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))

        # Treeview for table
        columns = ("ID", "Supplier", "Date", "Item", "Quantity", "Unit Price", "Total")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50)
            elif col in ("Item", "Supplier"):
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right column: Purchase Form
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            right_frame,
            text="Purchase Form",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))
        
        # Form fields
        form_frame = tk.Frame(right_frame, bg="#ffffff")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        label_style = {"font": ("Arial", 12), "bg": "#ffffff", "fg": "#34495e"}
        entry_style = {"font": ("Arial", 12), "bg": "#ecf0f1", "fg": "#2c3e50", "bd": 2, "relief": tk.SOLID}

        tk.Label(form_frame, text="Supplier Name:", **label_style).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.supplier_entry = tk.Entry(form_frame, width=25, **entry_style)
        self.supplier_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        tk.Label(form_frame, text="Item:", **label_style).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.item_combo = ttk.Combobox(form_frame, width=23, state="readonly", font=("Arial", 12))
        self.item_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        tk.Label(form_frame, text="Quantity:", **label_style).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = tk.Entry(form_frame, width=25, **entry_style)
        self.quantity_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        tk.Label(form_frame, text="Unit Price:", **label_style).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.unit_price_entry = tk.Entry(form_frame, width=25, **entry_style)
        self.unit_price_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        tk.Label(form_frame, text="Total Amount:", **label_style).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.total_entry = tk.Entry(form_frame, width=25, state="readonly", **entry_style)
        self.total_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        self.quantity_entry.bind("<KeyRelease>", self.update_total)
        self.unit_price_entry.bind("<KeyRelease>", self.update_total)

        # Buttons
        button_frame = tk.Frame(right_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=20)

        button_style = {
            "font": ("Arial", 12, "bold"),
            "bg": "#3498db",
            "fg": "#ffffff",
            "activebackground": "#2980b9",
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": tk.FLAT,
            "width": 15
        }

        tk.Button(button_frame, text="Add Purchase", command=self.add_purchase, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style).pack(side=tk.LEFT, padx=5)

        tk.Button(
            right_frame,
            text="Back to Dashboard",
            command=self.back_to_dashboard,
            **button_style
        ).pack(pady=20)

        self.load_items()
        self.load_purchases()

    def load_items(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT item_id, item_name FROM items ORDER BY item_name")
            self.items = cur.fetchall()
            self.item_map = {row[1]: row[0] for row in self.items}
            self.item_combo['values'] = sorted(list(self.item_map.keys()))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading items: {e}")

    def load_purchases(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                SELECT p.purchase_id, p.supplier_name, p.purchase_date, i.item_name, 
                       p.quantity, p.unit_price, p.total_amount
                FROM purchases p 
                JOIN items i ON p.item_id = i.item_id 
                ORDER BY p.purchase_date DESC
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading purchases: {e}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_purchase_id = values[0]
            self.supplier_entry.delete(0, tk.END)
            self.supplier_entry.insert(0, values[1])
            self.item_combo.set(values[3])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(values[4]))
            self.unit_price_entry.delete(0, tk.END)
            self.unit_price_entry.insert(0, str(values[5]))
            self.update_total()

    def update_total(self, event=None):
        try:
            quantity = float(self.quantity_entry.get() or 0)
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

    def add_purchase(self):
        supplier = self.supplier_entry.get().strip()
        item_name = self.item_combo.get()
        try:
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
            total_amount = float(self.total_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer, Unit Price and Total must be numbers")
            return

        if not all([supplier, item_name, quantity > 0, unit_price > 0]):
            messagebox.showerror("Error", "All fields are required and Quantity/Unit Price must be positive")
            return

        item_id = self.item_map.get(item_name)
        if not item_id:
            messagebox.showerror("Error", "Invalid item selected")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            # Insert purchase
            cur.execute("""
                INSERT INTO purchases (supplier_name, item_id, quantity, unit_price, total_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (supplier, item_id, quantity, unit_price, total_amount))
            # Update item stock
            cur.execute("""
                UPDATE items 
                SET current_stock = current_stock + ? 
                WHERE item_id = ?
            """, (quantity, item_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Purchase added and stock updated successfully")
            self.clear_form()
            self.load_purchases()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding purchase: {e}")

    def clear_form(self):
        self.supplier_entry.delete(0, tk.END)
        self.item_combo.set("")
        self.quantity_entry.delete(0, tk.END)
        self.unit_price_entry.delete(0, tk.END)
        self.total_entry.config(state="normal")
        self.total_entry.delete(0, tk.END)
        self.total_entry.insert(0, "0.00")
        self.total_entry.config(state="readonly")
        self.selected_purchase_id = None

    def back_to_dashboard(self):
        from admin_dashboard import AdminDashboard
        AdminDashboard(self.root, self.user_id, self.app)