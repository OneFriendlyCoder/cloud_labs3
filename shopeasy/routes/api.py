"""
REST API blueprint — used by Task 1.1 queries and lab autograder checks
"""

import os
import subprocess
from flask import Blueprint, jsonify, request, current_app
from shopeasy import db
from shopeasy.models import Product, Order, OrderItem

api_bp = Blueprint("api", __name__)


# ── Products ──────────────────────────────────────────────────────────────────

@api_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True)
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    product = Product(
        name=data["name"],
        description=data.get("description", ""),
        price=float(data.get("price", 0)),
        stock=int(data.get("stock", 0)),
        category=data.get("category", "General"),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@api_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@api_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(force=True) or {}
    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = float(data.get("price", product.price))
    product.stock = int(data.get("stock", product.stock))
    product.category = data.get("category", product.category)
    db.session.commit()
    return jsonify(product.to_dict())


@api_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"deleted": product_id})


# ── Orders ────────────────────────────────────────────────────────────────────

@api_bp.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@api_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    order = Order(
        customer_name=data.get("customer_name", "Anonymous"),
        customer_email=data.get("customer_email", "anon@shopeasy.local"),
    )
    db.session.add(order)
    total = 0.0
    for item_data in data.get("items", []):
        product = Product.query.get(item_data.get("product_id"))
        if not product:
            continue
        qty = int(item_data.get("quantity", 1))
        item = OrderItem(order=order, product_id=product.id, quantity=qty, unit_price=product.price)
        db.session.add(item)
        total += qty * product.price
        product.stock = max(0, product.stock - qty)
    order.total_amount = round(total, 2)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@api_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@api_bp.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"deleted": order_id})


# ── System / Lab helpers ──────────────────────────────────────────────────────

@api_bp.route("/system/info", methods=["GET"])
def system_info():
    """Returns storage and database diagnostic info (used in Task 1.1)."""
    db_path = current_app.config.get("DATABASE_PATH", "unknown")

    # Disk usage of the directory containing the DB
    df_info = {}
    try:
        result = subprocess.run(
            ["df", "-h", os.path.dirname(db_path)],
            capture_output=True, text=True, timeout=5,
        )
        df_info["df_output"] = result.stdout.strip()
    except Exception as e:
        df_info["df_error"] = str(e)

    # Block devices
    lsblk_info = {}
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"],
            capture_output=True, text=True, timeout=5,
        )
        lsblk_info["lsblk_output"] = result.stdout.strip()
    except Exception as e:
        lsblk_info["lsblk_error"] = str(e)

    return jsonify({
        "database": {
            "path": db_path,
            "exists": os.path.exists(db_path),
            "size_bytes": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
        },
        "upload_folder": current_app.config.get("UPLOAD_FOLDER", "unknown"),
        "stats": {
            "total_products": Product.query.count(),
            "total_orders": Order.query.count(),
        },
        **df_info,
        **lsblk_info,
    })


@api_bp.route("/system/reset", methods=["POST"])
def reset_database():
    """
    DROP + recreate all tables (simulates Task 1.3 database loss).
    WARNING: Destroys all data.
    """
    db.drop_all()
    db.create_all()
    return jsonify({"status": "reset", "message": "All data has been wiped."})


@api_bp.route("/stats", methods=["GET"])
def stats():
    from sqlalchemy import func
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0.0
    return jsonify({
        "total_products": Product.query.count(),
        "total_orders": Order.query.count(),
        "total_revenue": round(float(total_revenue), 2),
        "pending_orders": Order.query.filter_by(status="pending").count(),
    })
