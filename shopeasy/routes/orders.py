"""Orders blueprint"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from shopeasy import db
from shopeasy.models import Order, OrderItem, Product

orders_bp = Blueprint("orders", __name__)

VALID_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"]


@orders_bp.route("/")
def list_orders():
    status_filter = request.args.get("status", "")
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template("orders/list.html", orders=orders, statuses=VALID_STATUSES, selected=status_filter)


@orders_bp.route("/new", methods=["GET", "POST"])
def new_order():
    products = Product.query.filter(Product.stock > 0).all()
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        if not customer_name or not customer_email:
            flash("Customer name and email are required.", "error")
            return render_template("orders/new.html", products=products)

        order = Order(customer_name=customer_name, customer_email=customer_email)
        db.session.add(order)

        total = 0.0
        for product in products:
            qty_key = f"qty_{product.id}"
            qty = int(request.form.get(qty_key, 0))
            if qty > 0:
                qty = min(qty, product.stock)
                item = OrderItem(
                    order=order,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=product.price,
                )
                db.session.add(item)
                product.stock -= qty
                total += qty * product.price

        if total == 0:
            db.session.rollback()
            flash("Please add at least one item to the order.", "error")
            return render_template("orders/new.html", products=products)

        order.total_amount = round(total, 2)
        db.session.commit()
        flash(f"Order #{order.id} placed successfully! Total: ${order.total_amount:.2f}", "success")
        return redirect(url_for("orders.order_detail", order_id=order.id))
    return render_template("orders/new.html", products=products)


@orders_bp.route("/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("orders/detail.html", order=order, statuses=VALID_STATUSES)


@orders_bp.route("/<int:order_id>/status", methods=["POST"])
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    if new_status in VALID_STATUSES:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} status updated to {new_status}.", "success")
    else:
        flash("Invalid status.", "error")
    return redirect(url_for("orders.order_detail", order_id=order.id))


@orders_bp.route("/<int:order_id>/delete", methods=["POST"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f"Order #{order_id} deleted.", "success")
    return redirect(url_for("orders.list_orders"))
