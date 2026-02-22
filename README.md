# Thread & Co. – Ecommerce Clothing Store

A full-flow Python (Flask) ecommerce site with cart, wishlist, checkout, and dummy payment – real-website feel.

## Setup

```bash
cd ecommerce
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Features

- **Shop**: All, Women, Men categories; product detail pages
- **Wishlist (like)**: Heart icon on products; toggle from listing or product page; wishlist page
- **Cart**: Add to cart, update quantity, remove; cart page with order summary
- **Buy now**: Adds one item and goes straight to checkout
- **Checkout**: Step 1 – shipping address (dummy form). Step 2 – payment (dummy card). Place order.
- **Order confirmation**: Order ID, summary, shipping address, “Continue shopping”
- **Header**: Search bar (placeholder), cart count, wishlist count, account placeholder
- **Responsive**: Mobile, tablet, desktop; sticky header and footer links

All data is in-session (cart, wishlist, orders). Use dummy details; replace with real payment and DB later.

## Project structure

```
ecommerce/
  app.py                 # Routes, session cart/wishlist/orders
  requirements.txt
  templates/
    base.html            # Header, nav, cart/wishlist badges, flash, footer
    index.html           # Product grid (like, add to cart, buy now)
    product.html         # Product detail
    cart.html
    wishlist.html
    checkout.html        # Shipping address
    payment.html         # Card form, place order
    order_confirmation.html
  static/
    css/style.css
    js/main.js
    images/products/     # Put your product images here (see README there)
```
