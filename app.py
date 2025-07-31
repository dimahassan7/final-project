from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your_secure_secret_key_here"

ORDERS_FILE = "orders.txt"
USERS_FILE = "users.txt"
ADMIN_PASSWORD = "admin123"

menu = {
    "Burgers": [
        {"name": "Classic Burger", "price": 5.99, "image": "/static/images/classic.jpg"},
        {"name": "Cheese Burger", "price": 6.49, "image": "/static/images/cheese.jpg"},
        {"name": "Veggie Burger", "price": 5.49, "image": "/static/images/veggie.jpg"},
        {"name": "Bacon Burger", "price": 7.29, "image": "/static/images/bacon.jpg"},
        {"name": "Mushroom Swiss Burger", "price": 7.49, "image": "/static/images/mushroom_swiss.jpg"},
        {"name": "Spicy Jalapeño Burger", "price": 6.99, "image": "/static/images/jalapeno.jpg"}
    ],
    "Sides": [
        {"name": "Fries", "price": 2.49, "image": "/static/images/fries.jpg"},
        {"name": "Onion Rings", "price": 2.99, "image": "/static/images/onion.jpg"},
        {"name": "Sweet Potato Fries", "price": 3.49, "image": "/static/images/sweet_potato_fries.jpg"},
        {"name": "Mozzarella Sticks", "price": 4.29, "image": "/static/images/mozzarella.jpg"}
    ],
    "Drinks": [
        {"name": "Soda", "price": 1.99, "image": "/static/images/soda.jpg"},
        {"name": "Milkshake", "price": 3.49, "image": "/static/images/milkshake.jpg"},
        {"name": "Iced Tea", "price": 2.29, "image": "/static/images/iced_tea.jpg"},
        {"name": "Lemonade", "price": 2.29, "image": "/static/images/lemonade.jpg"}
    ]
}

@app.route("/")
def index():
    return render_template("index.html", menu=menu, user=session.get("user"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("signup.html", error="Email and password required.")

        hashed = generate_password_hash(password)

        # Check if email already exists
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                for line in f:
                    saved_email, _ = line.strip().split(":")
                    if saved_email == email:
                        return render_template("signup.html", error="Email already exists.")

        with open(USERS_FILE, "a") as f:
            f.write(f"{email}:{hashed}\n")

        session["user"] = email
        return redirect(url_for("index"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Both fields are required.")

        if not os.path.exists(USERS_FILE):
            return render_template("login.html", error="No users registered.")

        with open(USERS_FILE, "r") as f:
            for line in f:
                saved_email, saved_hash = line.strip().split(":")
                if saved_email == email and check_password_hash(saved_hash, password):
                    session["user"] = email
                    return redirect(url_for("index"))

        return render_template("login.html", error="Invalid credentials.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/receipt", methods=["POST"])
def receipt():
    name = request.form.get("customer_name", "Guest")
    selected_items = request.form.getlist("item")
    order = []
    total = 0

    for category in menu.values():
        for item in category:
            if item["name"] in selected_items:
                order.append(item)
                total += item["price"]

    with open(ORDERS_FILE, "a") as file:
        file.write(f"Customer: {name} (User: {session.get('user', 'guest')})\n")
        for item in order:
            file.write(f"  {item['name']} - ${item['price']:.2f}\n")
        file.write(f"Total: ${total:.2f}\n---\n")

    return render_template("receipt.html", order=order, total=total, customer=name)

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

    orders = ""
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as file:
            orders = file.read()

    return render_template("admin_dashboard.html", content=orders)

@app.route("/admin/clear_orders", methods=["POST"])
def clear_orders():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    open(ORDERS_FILE, "w").close()
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)




