"""Main / Dashboard routes"""

import os
from flask import Blueprint, render_template, current_app
from shopeasy.models import Product, Order

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status="pending").count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock < 10).all()
    return render_template(
        "index.html",
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        recent_orders=recent_orders,
        low_stock=low_stock,
    )


@main_bp.route("/health")
def health():
    """Simple health-check used by Task 1.1 baseline inspection."""
    from flask import jsonify
    db_path = current_app.config.get("DATABASE_PATH", "unknown")
    return jsonify({
        "status": "ok",
        "db_path": db_path,
        "db_exists": os.path.exists(db_path),
        "db_size_bytes": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
    })


def _get_file_size(path: str) -> str:
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / 1024 ** 2:.1f} MB"
    except OSError:
        return "N/A"
