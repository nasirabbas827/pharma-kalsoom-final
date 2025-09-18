import sqlite3

DB_NAME = "pharmacare.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        user_type TEXT NOT NULL DEFAULT 'user',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Categories table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    )
    """)

    # Items table (with image_path)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        description TEXT,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        current_stock INTEGER NOT NULL DEFAULT 0,
        image_path TEXT,  -- store file path of image
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    """)

    # Purchases table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        purchase_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(item_id)
    )
    """)

    # Sales table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        customer_name TEXT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(item_id)
    )
    """)

    # Insert default admin user (if not exists)
    cur.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users (username, password, full_name, user_type)
        VALUES (?, ?, ?, ?)
        """, ("admin", "admin", "System Administrator", "Admin"))
        print("Default admin user created (username: admin, password: admin123)")
    else:
        print("Admin user already exists")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    create_database()
