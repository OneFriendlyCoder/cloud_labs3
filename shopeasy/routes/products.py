"""Products blueprint"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from shopeasy import db
from shopeasy.models import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
def list_products():
    category = request.args.get("category", "")
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    products = query.order_by(Product.created_at.desc()).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template("products/list.html", products=products, categories=categories, selected=category)


@products_bp.route("/new", methods=["GET", "POST"])
def new_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        category = request.form.get("category", "General").strip()
        if not name:
            flash("Product name is required.", "error")
            return redirect(url_for("products.new_product"))
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{name}" added successfully!', "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/new.html")


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("products/detail.html", product=product)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        product.name = request.form.get("name", product.name).strip()
        product.description = request.form.get("description", product.description).strip()
        product.price = float(request.form.get("price", product.price))
        product.stock = int(request.form.get("stock", product.stock))
        product.category = request.form.get("category", product.category).strip()
        db.session.commit()
        flash(f'Product "{product.name}" updated.', "success")
        return redirect(url_for("products.product_detail", product_id=product.id))
    return render_template("products/edit.html", product=product)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" deleted.', "success")
    return redirect(url_for("products.list_products"))
