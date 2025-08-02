# models.py

class MenuItem:
    def __init__(self, name, price, image, category):
        self.name = name
        self.price = price
        self.image = image
        self.category = category


class Order:
    def __init__(self, customer_name, items, user_email=None):
        self.customer_name = customer_name
        self.items = items  # list of MenuItem objects
        self.user_email = user_email
        self.total = sum(item.price for item in items)

    def __str__(self):
        lines = [f"{item.name} - ${item.price:.2f}" for item in self.items]
        return f"Customer: {self.customer_name} (User: {self.user_email or 'guest'})\n" + \
               "\n".join(lines) + f"\nTotal: ${self.total:.2f}\n---"


class User:
    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def check_password(self, password, check_hash_func):
        return check_hash_func(self.password_hash, password)
