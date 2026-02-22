"""
Ecommerce clothing store - Men's & Women's fashion
Full flow: cart, wishlist, checkout, payment, order confirmation.
"""
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "thread-co-demo-secret-change-in-production"

# Dummy clothing data - Men & Women
# Image filenames: put your images in static/images/products/ (see README there)
PRODUCTS = [
    {"id": 1, "name": "Classic Linen Blazer", "category": "women", "price": 89.99, "image": "blazer.jpg", "description": "Elegant tailored blazer in soft linen"},
    {"id": 2, "name": "Floral Midi Dress", "category": "women", "price": 64.99, "image": "dress.jfif", "description": "Flowery print midi dress, perfect for summer"},
    {"id": 3, "name": "High-Waist Wide Leg Trousers", "category": "women", "price": 54.99, "image": "trousers.png", "description": "Comfortable wide leg pants in premium cotton"},
    {"id": 4, "name": "Cashmere Crew Neck Sweater", "category": "women", "price": 79.99, "image": "sweater.png", "description": "Luxurious cashmere blend sweater"},
    {"id": 5, "name": "Ribbed Crop Top", "category": "women", "price": 24.99, "image": "croptop.jpg", "description": "Stretchy ribbed crop top in multiple colors"},
    {"id": 6, "name": "Wool Blend Coat", "category": "women", "price": 149.99, "image": "coat.jpg", "description": "Warm wool blend winter coat"},
    {"id": 7, "name": "Oxford Cotton Shirt", "category": "men", "price": 49.99, "image": "shirt.jpg", "description": "Crisp formal shirt in pure cotton"},
    {"id": 8, "name": "Slim Fit Chinos", "category": "men", "price": 59.99, "image": "chinos.jpg", "description": "Versatile slim fit chinos"},
    {"id": 9, "name": "Merino Wool Jumper", "category": "men", "price": 69.99, "image": "jumper.jpg", "description": "Soft merino wool knit jumper"},
    {"id": 10, "name": "Denim Jacket", "category": "men", "price": 74.99, "image": "denim.jpg", "description": "Classic indigo denim jacket"},
    {"id": 11, "name": "Jogger Sweatpants", "category": "men", "price": 44.99, "image": "joggers.jpg", "description": "Comfortable fleece-lined joggers"},
    {"id": 12, "name": "Leather Belt", "category": "men", "price": 34.99, "image": "belt.jpg", "description": "Genuine leather dress belt"},
]

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}


def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


def get_wishlist():
    if "wishlist" not in session:
        session["wishlist"] = []
    return session["wishlist"]


def get_orders():
    if "orders" not in session:
        session["orders"] = []
    return session["orders"]


def cart_count():
    return sum(get_cart().values())


def cart_items_with_details():
    cart = get_cart()
    items = []
    for pid, qty in cart.items():
        if qty <= 0:
            continue
        p = PRODUCTS_BY_ID.get(int(pid))
        if p:
            items.append({"product": p, "quantity": qty, "subtotal": p["price"] * qty})
    return items


def cart_subtotal():
    return sum(item["subtotal"] for item in cart_items_with_details())


@app.context_processor
def inject_global():
    return {
        "cart_count": cart_count,
        "wishlist_ids": get_wishlist,
        "products_by_id": PRODUCTS_BY_ID,
    }


# ---------- Shop ----------
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/women")
def women():
    women_products = [p for p in PRODUCTS if p["category"] == "women"]
    return render_template("index.html", products=women_products, filter_category="women")


@app.route("/men")
def men():
    men_products = [p for p in PRODUCTS if p["category"] == "men"]
    return render_template("index.html", products=men_products, filter_category="men")


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("index"))
    return render_template("product.html", product=product)


# ---------- Cart ----------
@app.route("/cart")
def cart():
    items = cart_items_with_details()
    return render_template("cart.html", cart_items=items, subtotal=cart_subtotal())


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id):
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("index"))
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash(f'Added "{product["name"]}" to your cart.', "success")
    next_url = request.form.get("next") or request.referrer or url_for("index")
    return redirect(next_url)


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def cart_update(product_id):
    cart = get_cart()
    key = str(product_id)
    try:
        qty = int(request.form.get("quantity", 1))
        qty = max(0, min(99, qty))
    except (TypeError, ValueError):
        qty = 1
    if qty == 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


# ---------- Wishlist (Like) ----------
@app.route("/wishlist")
def wishlist():
    wl = get_wishlist()
    products = [PRODUCTS_BY_ID[pid] for pid in wl if pid in PRODUCTS_BY_ID]
    return render_template("wishlist.html", products=products)


@app.route("/wishlist/toggle/<int:product_id>", methods=["POST"])
def wishlist_toggle(product_id):
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        return redirect(url_for("index"))
    wl = get_wishlist()
    if product_id in wl:
        wl.remove(product_id)
        session["wishlist"] = wl
        flash(f'Removed "{product["name"]}" from your wishlist.', "info")
    else:
        wl.append(product_id)
        session["wishlist"] = wl
        flash(f'Added "{product["name"]}" to your wishlist.', "success")
    next_url = request.form.get("next") or request.referrer or url_for("index")
    return redirect(next_url)


# ---------- Checkout ----------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items_with_details()
    if not items:
        flash("Your cart is empty. Add items before checkout.", "warning")
        return redirect(url_for("cart"))
    if request.method == "POST":
        session["checkout_address"] = {
            "full_name": request.form.get("full_name", "").strip(),
            "address_line1": request.form.get("address_line1", "").strip(),
            "address_line2": request.form.get("address_line2", "").strip(),
            "city": request.form.get("city", "").strip(),
            "state": request.form.get("state", "").strip(),
            "zip_code": request.form.get("zip_code", "").strip(),
            "country": request.form.get("country", "").strip(),
            "phone": request.form.get("phone", "").strip(),
        }
        return redirect(url_for("payment"))
    address = session.get("checkout_address") or {}
    return render_template("checkout.html", cart_items=items, subtotal=cart_subtotal(), address=address)


@app.route("/checkout/payment", methods=["GET", "POST"])
def payment():
    if "checkout_address" not in session:
        return redirect(url_for("checkout"))
    items = cart_items_with_details()
    if not items:
        return redirect(url_for("cart"))
    if request.method == "POST":
        session["checkout_payment"] = {
            "card_number": request.form.get("card_number", "").replace(" ", ""),
            "expiry": request.form.get("expiry", "").strip(),
            "cvv": request.form.get("cvv", "").strip(),
            "name_on_card": request.form.get("name_on_card", "").strip(),
        }
        return redirect(url_for("payment"))
    payment_data = session.get("checkout_payment") or {}
    return render_template("payment.html", cart_items=items, subtotal=cart_subtotal(), payment=payment_data)


@app.route("/checkout/place-order", methods=["POST"])
def place_order():
    address = session.get("checkout_address") or {}
    payment_data = session.get("checkout_payment") or {}
    items = cart_items_with_details()
    if not items:
        return redirect(url_for("cart"))
    order_id = str(uuid.uuid4())[:8].upper()
    order = {
        "order_id": order_id,
        "items": [{"product": item["product"], "quantity": item["quantity"], "subtotal": item["subtotal"]} for item in items],
        "subtotal": cart_subtotal(),
        "shipping": 5.99,
        "tax": round(cart_subtotal() * 0.08, 2),
        "address": address,
        "payment_last4": payment_data.get("card_number", "0000")[-4:] if len(payment_data.get("card_number", "")) >= 4 else "0000",
    }
    order["total"] = round(order["subtotal"] + order["shipping"] + order["tax"], 2)
    orders = get_orders()
    orders.append(order)
    session["orders"] = orders
    session["cart"] = {}
    session.pop("checkout_address", None)
    session.pop("checkout_payment", None)
    session["last_order_id"] = order_id
    return redirect(url_for("order_confirmation", order_id=order_id))


@app.route("/order-confirmation/<order_id>")
def order_confirmation(order_id):
    orders = get_orders()
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("index"))
    return render_template("order_confirmation.html", order=order)


# Buy now: add one to cart and go to checkout
@app.route("/buy-now/<int:product_id>", methods=["POST"])
def buy_now(product_id):
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        return redirect(url_for("index"))
    cart = get_cart()
    cart[str(product_id)] = 1
    session["cart"] = cart
    return redirect(url_for("checkout"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
