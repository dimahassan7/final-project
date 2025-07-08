from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
ORDERS_FILE = "orders.txt"
ADMIN_PASSWORD = "admin123"  # basic password for admin access

menu = {
    "Burgers": [
        {"name": "Classic Burger", "price": 5.99, "image": "/static/images/classic.jpg"},
        {"name": "Cheese Burger", "price": 6.49, "image": "/static/images/cheese.jpg"},
        {"name": "Veggie Burger", "price": 5.49, "image": "/static/images/veggie.jpg"}
    ],
    "Sides": [
        {"name": "Fries", "price": 2.49, "image": "/static/images/fries.jpg"},
        {"name": "Onion Rings", "price": 2.99, "image": "/static/images/onion.jpg"}
    ],
    "Drinks": [
        {"name": "Soda", "price": 1.99, "image": "/static/images/soda.jpg"},
        {"name": "Milkshake", "price": 3.49, "image": "/static/images/milkshake.jpg"}
    ]
}




@app.route("/")
def index():
    return render_template("index.html", menu=menu)

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
        file.write(f"Customer: {name}\n")
        for item in order:
            file.write(f"  {item['name']} - ${item['price']:.2f}\n")
        file.write(f"Total: ${total:.2f}\n---\n")

    return render_template("receipt.html", order=order, total=total, customer=name)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            with open(ORDERS_FILE, "r") as file:
                content = file.read()
            return render_template("admin.html", content=content)
        else:
            return render_template("admin.html", error="Incorrect password.")
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)

