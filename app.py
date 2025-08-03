from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import MenuItem, Order, User
from database import init_db
from database import get_connection
init_db()

app = Flask(__name__)
app.secret_key = "your_secure_secret_key_here"

ORDERS_FILE = "orders.txt" 
USERS_FILE = "users.txt"
ADMIN_PASSWORD = "admin123"
  
menu = {
    "Burgers": [
        MenuItem("Classic Burger", 5.99, "/static/images/classic.jpg", "Burgers"),
        MenuItem("Cheese Burger", 6.49, "/static/images/cheese.jpg", "Burgers"),
        MenuItem("Veggie Burger", 5.49, "/static/images/veggie.jpg", "Burgers"),
        MenuItem("Bacon Burger", 7.29, "/static/images/bacon.jpg", "Burgers"),
        MenuItem("Mushroom Swiss Burger", 7.49, "/static/images/mushroom_swiss.jpg", "Burgers"),
        MenuItem("Spicy Jalapeño Burger", 6.99, "/static/images/jalapeno.jpg", "Burgers")
    ],
    "Sides": [
        MenuItem("Fries", 2.49, "/static/images/fries.jpg", "Sides"),
        MenuItem("Onion Rings", 2.99, "/static/images/onion.jpg", "Sides"),
        MenuItem("Sweet Potato Fries", 3.49, "/static/images/sweet_potato_fries.jpg", "Sides"),
        MenuItem("Mozzarella Sticks", 4.29, "/static/images/mozzarella.jpg", "Sides")
    ],
    "Drinks": [
        MenuItem("Soda", 1.99, "/static/images/soda.jpg", "Drinks"),
        MenuItem("Milkshake", 3.49, "/static/images/milkshake.jpg", "Drinks"),
        MenuItem("Iced Tea", 2.29, "/static/images/iced_tea.jpg", "Drinks"),
        MenuItem("Lemonade", 2.29, "/static/images/lemonade.jpg", "Drinks")
    ]
}

@app.route("/")
def index():
    return render_template("index.html", menu=menu, user=session.get("user"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template("signup.html", error="Email and password required.")

        hashed = generate_password_hash(password)

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
            conn.commit()
            session["user"] = email
            return redirect(url_for("index"))
        except:
            return render_template("signup.html", error="Email already exists.")
        finally:
            conn.close()

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()

        if row and check_password_hash(row[0], password):
            session["user"] = email
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/receipt", methods=["POST"])
def receipt():
    name = request.form.get("customer_name", "Guest").strip()
    order_type = request.form.get("order_type", "Pickup")
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    selected_names = request.form.getlist("item")

    if not selected_names:
        return render_template("index.html", menu=menu, user=session.get("user"), error="Select at least one item.")

    # If Delivery is selected, require phone and address
    if order_type == "Delivery":
        if not phone or not address:
            return render_template("index.html", menu=menu, user=session.get("user"),
                                   error="Please provide phone number and delivery address for Delivery orders.")

    order_items = []
    total = 0

    for category in menu.values():
        for item in category:
            if item.name in selected_names:
                order_items.append(item)
                total += item.price

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (customer, user, total, order_type, phone, address) VALUES (?, ?, ?, ?, ?, ?)",
        (name, session.get("user", "guest"), total, order_type, phone if order_type == "Delivery" else None,
         address if order_type == "Delivery" else None)
    )
    order_id = c.lastrowid

    for item in order_items:
        c.execute("INSERT INTO order_items (order_id, item_name, item_price) VALUES (?, ?, ?)",
                  (order_id, item.name, item.price))

    conn.commit()
    conn.close()

    return render_template("receipt.html", order=order_items, total=total, customer=name, user=session.get("user"),
                           order_type=order_type, phone=phone, address=address)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin.html", error="Incorrect password.")
    return render_template("admin.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()

    output = ""
    for order in orders:
        order_id, customer, user, total, order_type, phone, address = order
        output += f"Order #{order_id} - {customer} (User: {user}) - {order_type}\n"
        if order_type == "Delivery":
            output += f"Phone: {phone}, Address: {address}\n"
        c.execute("SELECT item_name, item_price FROM order_items WHERE order_id = ?", (order_id,))
        items = c.fetchall()
        for name, price in items:
            output += f"  {name} - ${price:.2f}\n"
        output += f"Total: ${total:.2f}\n---\n"

    conn.close()
    return render_template("admin_dashboard.html", content=output)

@app.route("/admin/clear_orders", methods=["POST"])
def clear_orders():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM order_items")
    c.execute("DELETE FROM orders")
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)

 




