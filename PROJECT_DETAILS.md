# Thread & Co. Ecommerce – Project Details & Developer Guide

This document is the single source of truth for the **technical story**, **execution plan**, **component overview**, and **how to understand the code**. Use it as a user manual for developers and as reference for resume or portfolio descriptions.

---

## 1. The Plan (Beginning to End)

### Goal
Build a **full-flow ecommerce website** (men’s and women’s clothing) that feels like a real site (e.g. Amazon-style): browse products, like/wishlist, add to cart, checkout with address and payment, and see order confirmation. Use **dummy data** everywhere so it can later be swapped for real APIs and a database.

### Design Decisions Up Front
- **Backend**: Python + Flask (simple, no DB for v1).
- **State**: Cart, wishlist, and orders live in **Flask session** (cookie-based).
- **Frontend**: Server-rendered HTML (Jinja2), one shared CSS file, minimal JS for UX (menu, card formatting).
- **Responsiveness**: CSS Grid/Flexbox, mobile-first; no separate mobile app.

### Phases We Executed

| Phase | What we did |
|-------|-------------|
| **1. Foundation** | Flask app, `PRODUCTS` list, routes for `/`, `/women`, `/men`. Single `index.html` with product grid. Base template + static CSS. |
| **2. Images** | Product images from `static/images/products/`; each product has an `image` filename. Template uses `<img>` with fallback to letter placeholder if file missing. |
| **3. Full flow** | Session cart (dict `product_id → quantity`), session wishlist (list of `product_id`), session orders (list of order dicts). Routes for cart, wishlist, checkout (address → payment → place order), order confirmation. |
| **4. UX polish** | Header: search placeholder, cart/wishlist icons with counts. Product cards: wishlist heart, Add to cart, Buy now. Flash messages. Footer links. Responsive layout and forms. |

No formal “design doc” was written first; the plan above was the mental model and then implemented in code.

---

## 2. Steps Taken to Execute the Plan

1. **Scaffold**  
   Created `app.py`, `templates/base.html`, `templates/index.html`, `static/css/style.css`, `static/js/main.js`, `requirements.txt`.

2. **Data model (in code)**  
   - `PRODUCTS`: list of dicts (id, name, category, price, image, description).  
   - `PRODUCTS_BY_ID`: same data keyed by id for O(1) lookup.

3. **Session helpers**  
   - `get_cart()` → `session["cart"]` (dict).  
   - `get_wishlist()` → `session["wishlist"]` (list).  
   - `get_orders()` → `session["orders"]` (list).  
   - `cart_count()`, `cart_items_with_details()`, `cart_subtotal()` for cart logic.

4. **Global template context**  
   `@app.context_processor` injects `cart_count`, `wishlist_ids`, `products_by_id` so every template can show header badges and “in wishlist” state without passing them per view.

5. **Shop routes**  
   `/`, `/women`, `/men` render `index.html` with the right product list. `/product/<id>` renders `product.html` for one product.

6. **Cart routes**  
   - `POST /cart/add/<id>`: add one to cart, redirect back or to `next`.  
   - `GET /cart`: cart page.  
   - `POST /cart/update/<id>`: set quantity from form (0 = remove).  
   - `POST /cart/remove/<id>`: remove item.

7. **Wishlist routes**  
   - `POST /wishlist/toggle/<id>`: add or remove product id from wishlist.  
   - `GET /wishlist`: wishlist page (list of products from ids).

8. **Checkout flow**  
   - `GET/POST /checkout`: form for shipping address; on POST save to `session["checkout_address"]`, redirect to payment.  
   - `GET/POST /checkout/payment`: form for card (dummy); on POST save to `session["checkout_payment"]`, redirect to same page so “Place order” appears.  
   - `POST /checkout/place-order`: build order dict (id, items, subtotal, shipping, tax, total, address, payment_last4), append to `session["orders"]`, clear cart and checkout session keys, redirect to order confirmation.  
   - `GET /order-confirmation/<order_id>`: render confirmation using order from `session["orders"]`.

9. **Buy now**  
   `POST /buy-now/<id>`: set cart[id]=1, redirect to `/checkout`.

10. **Templates**  
    One base (header, nav, flash, footer) and seven page templates: index, product, cart, wishlist, checkout, payment, order_confirmation.

11. **CSS**  
    Single `style.css`: variables, layout, header (search, icons, badges), product grid/cards, cart/checkout/summary, forms, buttons, order confirmation, footer, media queries for small screens.

12. **JS**  
    Mobile nav toggle; search Enter key; card number grouping and expiry MM/YY formatting on payment form.

13. **Docs**  
    `README.md` (run instructions, features), `static/images/products/README.md` (image filenames), and this file.

---

## 3. How the Components Fit Together

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser                                                        │
│  (Session cookie holds: cart, wishlist, orders, checkout_*)    │
└───────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Flask (app.py)                                                 │
│  • Routes: shop, cart, wishlist, checkout, payment, place_order  │
│  • Helpers: get_cart, get_wishlist, cart_items_with_details…    │
│  • Context: cart_count, wishlist_ids → every template           │
└───────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Templates      │ │  Static          │ │  Data (in code)  │
│  (Jinja2)       │ │  CSS + JS        │ │  PRODUCTS       │
│  base, index,   │ │  style.css       │ │  PRODUCTS_BY_ID │
│  product, cart, │ │  main.js         │ │  Session        │
│  wishlist,      │ │  images/products │ │  (cart, wishlist,│
│  checkout,      │ │                  │ │   orders,       │
│  payment,       │ │                  │ │   checkout_*)    │
│  order_confirm  │ │                  │ │                  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

- **Request flow**: User hits a URL → Flask route runs → uses session and `PRODUCTS`/`PRODUCTS_BY_ID` → renders a template with the right variables → HTML + links/forms point to other routes (e.g. add to cart, checkout).
- **State**: All mutable state is in `session` (cart, wishlist, orders, checkout address/payment). No database; restart clears everything.
- **Templates**: Extend `base.html`; blocks are `title` and `content`. Flash messages and header badges come from context processor and `get_flashed_messages()`.

---

## 4. Developer Guide – Understanding the Code

### Where to Start
1. **`app.py`**  
   Read top to bottom: constants (`PRODUCTS`, `PRODUCTS_BY_ID`), session helpers, `inject_global`, then routes in order (shop → cart → wishlist → checkout → payment → place_order → order_confirmation, buy_now).

2. **`templates/base.html`**  
   Structure of every page: header (logo, search, nav, cart/wishlist badges), flash block, `{% block content %}`, footer. Links use `url_for('index')`, `url_for('cart')`, etc.

3. **`templates/index.html`**  
   Loop over `products`; each item: link to product page, image, category, name, description, price, forms for wishlist toggle, add to cart, buy now. `wishlist_ids()` used to show filled heart.

4. **Cart/wishlist**  
   - Cart: `session["cart"]` is `{ "product_id": quantity }`.  
   - Wishlist: `session["wishlist"]` is `[product_id, ...]`.  
   - Views that need “current cart as list of items with product details” use `cart_items_with_details()`.

5. **Checkout**  
   - User must have items in cart to see checkout.  
   - Address form POST → save to `session["checkout_address"]` → redirect to payment.  
   - Payment form POST → save to `session["checkout_payment"]` → redirect to same page; template then shows “Place order” button.  
   - “Place order” POST → build order, append to `session["orders"]`, clear cart and checkout keys, redirect to `/order-confirmation/<order_id>`.

6. **Static**  
   - `style.css`: all layout and components; variables at top; media queries at bottom.  
   - `main.js`: only nav toggle, search submit, and payment field formatting.  
   - Product images: put files in `static/images/products/` with names matching `product["image"]` (e.g. `blazer.jpg`).

### Key Conventions
- **Routes**: GET for pages, POST for actions (add to cart, update quantity, submit address, submit payment, place order). Redirect after POST to avoid resubmit.
- **Forms**: Method POST, `action="{{ url_for('...') }}"`. Hidden `next` for “return URL” where useful (e.g. wishlist toggle).
- **Session keys**: `cart`, `wishlist`, `orders`, `checkout_address`, `checkout_payment`, `last_order_id` (optional).
- **Flash**: `flash("Message", "success"|"error"|"info"|"warning")`; base template renders them with matching CSS class.

### How to Extend
- **Real DB**: Replace `PRODUCTS`/`PRODUCTS_BY_ID` with DB queries; store cart/wishlist/orders in DB keyed by user/session id.  
- **Real payment**: Replace “Place order” with a call to Stripe/PayPal etc.; keep address and order creation logic.  
- **Auth**: Add login/signup; tie session cart to user id and merge on login.  
- **Search**: Use the search input; in a route (e.g. `index`) read `request.args.get("q")` and filter `PRODUCTS` (or query DB) before rendering.

---

## 5. Resume / Portfolio – Bullet Points

Use these as-is or adapt for resume or project description:

- **Built a full-flow ecommerce web app in Python/Flask** with product listing, category filters (men/women), product detail pages, and responsive UI (mobile-first CSS).
- **Implemented cart, wishlist, and checkout** using Flask session: add/update/remove cart items, toggle wishlist, multi-step checkout (shipping address + dummy payment), place order, and order confirmation page with summary and shipping details.
- **Designed a clear request/response and state model**: server-rendered Jinja2 templates, context processor for global cart/wishlist counts, and consistent use of POST-redirect-GET for form actions to avoid duplicate submissions.
- **Delivered a production-style UX** (header with search placeholder, cart/wishlist badges, flash messages, footer links) and documented architecture, execution steps, and developer guide in a single `PROJECT_DETAILS` file for handoff and portfolio reference.

---

*File: `PROJECT_DETAILS.md` – Thread & Co. Ecommerce – Technical story, execution plan, component overview, developer guide, and resume bullets.*
