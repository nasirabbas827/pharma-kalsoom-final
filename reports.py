import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

class Reports:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.db_name = "pharmacare.db"
        self.root.title("PharmaCare - Generate Reports")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f4f8")  # Light blue-gray background
        self.current_report = ""  # Store current report text for printing
        self.create_reports_page()

    def create_reports_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left side: Report selection
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=(0, 20))

        tk.Label(
            left_frame,
            text="Generate Report",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"  # Dark blue-gray text
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Report type selection
        tk.Label(
            left_frame,
            text="Report Type:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"  # Slightly lighter blue-gray
        ).pack(anchor=tk.W, pady=5)
        self.report_type = ttk.Combobox(
            left_frame,
            values=["Sales Report", "Purchase Report", "Stock Report", "Profit Report"],
            width=20,
            state="readonly",
            font=("Arial", 12)
        )
        self.report_type.pack(anchor=tk.W, pady=5)
        self.report_type.set("Sales Report")

        # Start Date
        tk.Label(
            left_frame,
            text="Start Date:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).pack(anchor=tk.W, pady=5)
        self.start_date_entry = DateEntry(
            left_frame,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 12)
        )
        self.start_date_entry.pack(anchor=tk.W, pady=5)
        self.start_date_entry.set_date(datetime.now() - timedelta(days=30))  # Default: 30 days ago

        # End Date
        tk.Label(
            left_frame,
            text="End Date:",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#34495e"
        ).pack(anchor=tk.W, pady=5)
        self.end_date_entry = DateEntry(
            left_frame,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 12)
        )
        self.end_date_entry.pack(anchor=tk.W, pady=5)
        self.end_date_entry.set_date(datetime.now())  # Default: today

        # Buttons
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
        tk.Button(left_frame, text="Generate Report", command=self.generate_report, **button_style).pack(pady=10)
        tk.Button(left_frame, text="Print Report to PDF", command=self.print_report, **button_style).pack(pady=10)
        tk.Button(left_frame, text="Back to Dashboard", command=self.back_to_dashboard, **button_style).pack(pady=10)

        # Right side: Report display
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=5, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 20))

        tk.Label(
            right_frame,
            text="Report Output",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=20, pady=(10, 10))

        # Scrolled text for report
        self.report_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            height=25,
            width=80,
            bg="#ecf0f1",  # Light gray
            fg="#2c3e50",
            font=("Arial", 12),
            bd=2,
            relief=tk.SOLID
        )
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))

    def validate_dates(self, start_date_str, end_date_str):
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date.")
                return None, None
            if end_date > datetime.now().date():
                messagebox.showerror("Error", "End date cannot be in the future.")
                return None, None
            return start_date, end_date
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return None, None

    def generate_report(self):
        report_type = self.report_type.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        if not (start_date_str and end_date_str):
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        start_date, end_date = self.validate_dates(start_date_str, end_date_str)
        if not start_date:
            return

        # Clear previous report
        self.report_text.delete(1.0, tk.END)

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()

            report = f"PharmaCare {report_type}\n"
            report += f"{'='*50}\n\n"
            report += f"Period: {start_date} to {end_date}\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            if report_type == "Sales Report":
                cur.execute("""
                    SELECT s.sale_id, s.sale_date, i.item_name, s.quantity, s.unit_price, s.total_amount, 
                           s.customer_name
                    FROM sales s 
                    JOIN items i ON s.item_id = i.item_id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                    ORDER BY s.sale_date DESC
                """, (start_date, end_date))
                rows = cur.fetchall()
                cur.execute("""
                    SELECT SUM(quantity), SUM(total_amount) 
                    FROM sales 
                    WHERE DATE(sale_date) BETWEEN ? AND ?
                """, (start_date, end_date))
                total_qty, total_amt = cur.fetchone()
                total_qty = total_qty or 0
                total_amt = total_amt or 0

                report += f"Total Sales: {total_qty} units, Total Amount: ${total_amt:.2f}\n\n"
                report += f"{'ID':<6} {'Date':<12} {'Item':<20} {'Qty':<6} {'Unit Price':<12} {'Total':<10} {'Customer'}\n"
                report += f"{'-'*80}\n"
                for row in rows:
                    customer = row[6] or "N/A"
                    report += f"{row[0]:<6} {row[1]:<12} {row[2][:17]:<20} {row[3]:<6} ${row[4]:<11.2f} ${row[5]:<9.2f} {customer}\n"

            elif report_type == "Purchase Report":
                cur.execute("""
                    SELECT p.purchase_id, p.purchase_date, i.item_name, p.quantity, p.unit_price, 
                           p.total_amount, p.supplier_name
                    FROM purchases p 
                    JOIN items i ON p.item_id = i.item_id
                    WHERE DATE(p.purchase_date) BETWEEN ? AND ?
                    ORDER BY p.purchase_date DESC
                """, (start_date, end_date))
                rows = cur.fetchall()
                cur.execute("""
                    SELECT SUM(quantity), SUM(total_amount) 
                    FROM purchases 
                    WHERE DATE(purchase_date) BETWEEN ? AND ?
                """, (start_date, end_date))
                total_qty, total_amt = cur.fetchone()
                total_qty = total_qty or 0
                total_amt = total_amt or 0

                report += f"Total Purchases: {total_qty} units, Total Amount: ${total_amt:.2f}\n\n"
                report += f"{'ID':<6} {'Date':<12} {'Item':<20} {'Qty':<6} {'Unit Price':<12} {'Total':<10} {'Supplier'}\n"
                report += f"{'-'*80}\n"
                for row in rows:
                    supplier = row[6] or "N/A"
                    report += f"{row[0]:<6} {row[1]:<12} {row[2][:17]:<20} {row[3]:<6} ${row[4]:<11.2f} ${row[5]:<9.2f} {supplier}\n"

            elif report_type == "Stock Report":
                cur.execute("""
                    SELECT i.item_id, i.item_name, c.category_name, i.current_stock
                    FROM items i 
                    JOIN categories c ON i.category_id = c.category_id
                    ORDER BY i.item_name
                """)
                items = cur.fetchall()
                cur.execute("SELECT SUM(current_stock) FROM items")
                total_stock = cur.fetchone()[0] or 0

                report += f"Total Available Stock: {total_stock} units\n\n"
                report += f"{'ID':<6} {'Item':<20} {'Category':<20} {'Stock':<6} {'Last Update':<12} {'Qty Changed':<12}\n"
                report += f"{'-'*76}\n"
                for item in items:
                    item_id, item_name, category_name, stock = item
                    # Get latest purchase or sale for this item
                    cur.execute("""
                        SELECT 'Purchase', purchase_date, quantity 
                        FROM purchases 
                        WHERE item_id = ? 
                        UNION
                        SELECT 'Sale', sale_date, -quantity 
                        FROM sales 
                        WHERE item_id = ?
                        ORDER BY purchase_date DESC 
                        LIMIT 1
                    """, (item_id, item_id))
                    last_update = cur.fetchone()
                    if last_update:
                        update_type, update_date, qty_changed = last_update
                        update_date = update_date[:10]  # Truncate to date only
                        qty_changed = f"+{qty_changed}" if update_type == "Purchase" else f"{qty_changed}"
                    else:
                        update_date = "N/A"
                        qty_changed = "N/A"
                    report += f"{item_id:<6} {item_name[:17]:<20} {category_name[:17]:<20} {stock:<6} {update_date:<12} {qty_changed:<12}\n"

            elif report_type == "Profit Report":
                cur.execute("SELECT SUM(current_stock) FROM items")
                total_stock = cur.fetchone()[0] or 0
                cur.execute("""
                    SELECT SUM(quantity) FROM purchases 
                    WHERE DATE(purchase_date) BETWEEN ? AND ?
                """, (start_date, end_date))
                total_purchases = cur.fetchone()[0] or 0
                cur.execute("""
                    SELECT SUM(quantity) FROM sales 
                    WHERE DATE(sale_date) BETWEEN ? AND ?
                """, (start_date, end_date))
                total_sales = cur.fetchone()[0] or 0
                cur.execute("""
                    SELECT SUM( (s.unit_price - i.purchase_price) * s.quantity ) 
                    FROM sales s 
                    JOIN items i ON s.item_id = i.item_id
                    WHERE DATE(s.sale_date) BETWEEN ? AND ?
                """, (start_date, end_date))
                total_profit = cur.fetchone()[0] or 0

                report += f"Total Available Stock: {total_stock} units\n\n"
                report += f"Purchases in Period: {total_purchases} units\n"
                report += f"Sales in Period: {total_sales} units\n\n"
                report += f"Profit in Period: ${total_profit:.2f}\n"

            conn.close()
            self.current_report = report  # Store report for printing
            self.report_text.insert(tk.END, report)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error generating report: {e}")
            self.report_text.insert(tk.END, f"Error generating report: {e}")

    def print_report(self):
        if not self.current_report:
            messagebox.showerror("Error", "Please generate a report first.")
            return

        # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report as PDF"
        )
        if not file_path:
            return

        try:
            # Create PDF
            c = canvas.Canvas(file_path, pagesize=A4)
            c.setFont("Helvetica", 12)
            y = 750  # Start near top of page
            lines = self.current_report.split("\n")
            for line in lines:
                if y < 50:  # Move to new page if near bottom
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 750
                c.drawString(50, y, line)
                y -= 15  # Line spacing
            c.save()
            messagebox.showinfo("Success", f"Report saved as PDF at {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def back_to_dashboard(self):
        from admin_dashboard import AdminDashboard

        AdminDashboard(self.root, self.user_id, self.app)