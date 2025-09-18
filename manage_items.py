import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from PIL import Image, ImageTk
import os

class ManageItems:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.selected_item_id = None
        self.old_image_path = ""
        self.root.title("PharmaCare - Manage Items")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.create_manage_items_page()

    def create_manage_items_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column: Items Table
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=(0, 20))

        # Search frame
        search_frame = tk.Frame(left_frame, bg="#ffffff")
        search_frame.pack(fill=tk.X, pady=(10, 10))
        tk.Label(
            search_frame,
            text="Search Items (by ID or Name):",
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
            text="Items List",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(anchor=tk.W, padx=20, pady=(5, 5))

        # Treeview for table
        columns = ("ID", "Category", "Description", "Purchase Price", "Sale Price", "Stock")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="tree headings", height=15)
        
        self.tree.heading("#0", text="Item")
        self.tree.column("#0", width=150, minwidth=100)  # Reduced width
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50)  # Reduced width
            elif col == "Description":
                self.tree.column(col, width=120)  # Reduced width
            else:
                self.tree.column(col, width=80)  # Reduced width
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right column: Item Form with scrollable canvas
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 20))

        canvas = tk.Canvas(right_frame, bg="#ffffff")
        scrollbar_y = tk.Scrollbar(right_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg="#ffffff")
        
        canvas.configure(yscrollcommand=scrollbar_y.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(
            self.form_frame,
            text="Item Form",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Form fields
        inner_form_frame = tk.Frame(self.form_frame, bg="#ffffff")
        inner_form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Item Name
        tk.Label(
            inner_form_frame,
            text="Item Name:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(
            inner_form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Category
        tk.Label(
            inner_form_frame,
            text="Category:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(
            inner_form_frame,
            width=22,
            state="readonly",
            font=("Arial", 12)
        )
        self.category_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Purchase Price
        tk.Label(
            inner_form_frame,
            text="Purchase Price:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.purch_entry = tk.Entry(
            inner_form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.purch_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Sale Price
        tk.Label(
            inner_form_frame,
            text="Sale Price:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sale_entry = tk.Entry(
            inner_form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.sale_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Current Stock
        tk.Label(
            inner_form_frame,
            text="Current Stock:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.stock_entry = tk.Entry(
            inner_form_frame,
            font=("Arial", 12),
            width=25,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.stock_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Description
        tk.Label(
            inner_form_frame,
            text="Description:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(
            inner_form_frame,
            font=("Arial", 12),
            width=25,
            height=4,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.desc_text.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        # Image Path
        tk.Label(
            inner_form_frame,
            text="Image Path:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.image_path_entry = tk.Entry(
            inner_form_frame,
            font=("Arial", 12),
            width=20,
            bg="#ecf0f1",
            fg="#2c3e50",
            bd=2,
            relief=tk.SOLID
        )
        self.image_path_entry.grid(row=6, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        tk.Button(
            inner_form_frame,
            text="Browse",
            command=self.select_image,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="#ffffff",
            activebackground="#2980b9",
            bd=0,
            relief=tk.FLAT
        ).grid(row=6, column=2, padx=5)

        self.image_label = tk.Label(
        inner_form_frame,
        width=250,  # Set to match image width
        height=250,  # Set to match image height
        bg="#ecf0f1",
        text="No Image",
        fg="#34495e",
        font=("Arial", 12)
    )
        self.image_label.grid(row=7, column=0, columnspan=3, pady=10)

        # Buttons
        button_frame = tk.Frame(self.form_frame, bg="#ffffff")
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

        # Arrange buttons in a 2x2 grid
        tk.Button(button_frame, text="Add Item", command=self.add_item, **button_style).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Update Item", command=self.update_item, **button_style).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Delete Item", command=self.delete_item, **button_style).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_form, **button_style).grid(row=1, column=1, padx=5, pady=5)

        # Back button
        tk.Button(
            self.form_frame,
            text="Dashboard",
            command=self.back_to_dashboard,
            **button_style
        ).pack(pady=20)

        # Load data
        self.load_categories()
        self.load_items()

    def load_categories(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
            self.categories = cur.fetchall()
            self.category_map = {row[1]: row[0] for row in self.categories}
            self.category_combo['values'] = sorted(list(self.category_map.keys()))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading categories: {e}")

    def load_items(self, search_term=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            if search_term:
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
                        ORDER BY i.item_id
                    """, (f"%{search_term}%",))
            else:
                cur.execute("""
                    SELECT i.item_id, i.item_name, c.category_name, i.description, i.purchase_price, 
                           i.sale_price, i.current_stock, i.image_path
                    FROM items i 
                    JOIN categories c ON i.category_id = c.category_id 
                    ORDER BY i.item_id
                """)
            rows = cur.fetchall()
            for row in rows:
                photo = self.create_thumbnail(row[7])
                text_value = row[1] if row[1] else "Unnamed Item"  # Sanitize text
                self.tree.insert("", tk.END, image=photo if photo else "", text=text_value,
                               values=(row[0], row[2], row[3], row[4], row[5], row[6]),
                               tags=(str(row[0]),))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading items: {e}")

    def search_items(self):
        search_term = self.search_entry.get().strip()
        if search_term:
            self.load_items(search_term)
        else:
            self.load_items()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_items()

    def create_thumbnail(self, image_path, size=(150, 150)):
        if not image_path or not os.path.exists(image_path):
            return None
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_item_id = int(item['tags'][0])
            try:
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                cur.execute("""
                    SELECT i.item_id, i.item_name, c.category_name, i.description, i.purchase_price, 
                           i.sale_price, i.current_stock, i.image_path
                    FROM items i JOIN categories c ON i.category_id = c.category_id
                    WHERE i.item_id = ?
                """, (self.selected_item_id,))
                row = cur.fetchone()
                conn.close()
                if row:
                    self.name_entry.delete(0, tk.END)
                    self.name_entry.insert(0, row[1])
                    self.category_combo.set(row[2])
                    self.purch_entry.delete(0, tk.END)
                    self.purch_entry.insert(0, str(row[4]))
                    self.sale_entry.delete(0, tk.END)
                    self.sale_entry.insert(0, str(row[5]))
                    self.stock_entry.delete(0, tk.END)
                    self.stock_entry.insert(0, str(row[6]))
                    self.desc_text.delete(1.0, tk.END)
                    self.desc_text.insert(1.0, row[3] or "")
                    self.image_path_entry.delete(0, tk.END)
                    self.image_path_entry.insert(0, row[7] or "")
                    self.old_image_path = row[7] or ""
                    self.load_image_preview(self.old_image_path)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading item: {e}")

    def load_image_preview(self, path):
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            except Exception:
                self.image_label.config(image="", text="Invalid Image")
        else:
            self.image_label.config(image="", text="No Image")


    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, filename)
            self.load_image_preview(filename)

    def add_item(self):
        name = self.name_entry.get().strip()
        cat_name = self.category_combo.get()
        desc = self.desc_text.get(1.0, tk.END).strip()
        image_path = self.image_path_entry.get().strip()
        try:
            purch = float(self.purch_entry.get())
            sale = float(self.sale_entry.get())
            stock = int(self.stock_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Purchase/Sale prices must be numbers, Stock must be integer")
            return
        if not all([name, cat_name]):
            messagebox.showerror("Error", "Item Name and Category are required")
            return
        cat_id = self.category_map.get(cat_name)
        if not cat_id:
            messagebox.showerror("Error", "Invalid category selected")
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO items (item_name, category_id, description, purchase_price, sale_price, 
                                  current_stock, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, cat_id, desc, purch, sale, stock, image_path))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item added successfully")
            self.clear_form()
            self.load_items()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding item: {e}")

    def update_item(self):
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select an item to update")
            return
        name = self.name_entry.get().strip()
        cat_name = self.category_combo.get()
        desc = self.desc_text.get(1.0, tk.END).strip()
        image_path_new = self.image_path_entry.get().strip()
        image_path = image_path_new if image_path_new else self.old_image_path
        try:
            purch = float(self.purch_entry.get())
            sale = float(self.sale_entry.get())
            stock = int(self.stock_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number formats")
            return
        if not all([name, cat_name]):
            messagebox.showerror("Error", "Item Name and Category are required")
            return
        cat_id = self.category_map.get(cat_name)
        if not cat_id:
            messagebox.showerror("Error", "Invalid category")
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""
                UPDATE items 
                SET item_name = ?, category_id = ?, description = ?, purchase_price = ?, 
                    sale_price = ?, current_stock = ?, image_path = ?
                WHERE item_id = ?
            """, (name, cat_id, desc, purch, sale, stock, image_path, self.selected_item_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item updated successfully")
            self.clear_form()
            self.load_items()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating item: {e}")

    def delete_item(self):
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select an item to delete")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            try:
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                cur.execute("DELETE FROM items WHERE item_id = ?", (self.selected_item_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Item deleted successfully")
                self.clear_form()
                self.load_items()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting item: {e}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.purch_entry.delete(0, tk.END)
        self.sale_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.desc_text.delete(1.0, tk.END)
        self.image_path_entry.delete(0, tk.END)
        self.image_label.config(image="", text="No Image")
        self.selected_item_id = None
        self.old_image_path = ""

    def back_to_dashboard(self):
        from admin_dashboard import AdminDashboard

        AdminDashboard(self.root, self.user_id, self.app)