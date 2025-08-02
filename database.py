import sqlite3

def get_connection():
    return sqlite3.connect("data.db")

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            user TEXT,
            total REAL
        )
    ''')

    # Order items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            item_price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    ''')

    conn.commit()
    conn.close()
