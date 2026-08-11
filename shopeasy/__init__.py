"""
ShopEasy Application Package
Lab 1: Amazon EBS - Persistent Block Storage
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ------------------------------------------------------------------ #
    # Database configuration
    # The DATABASE_PATH env var controls where SQLite stores its file.
    # Default: <cwd>/data/shopeasy.db  (same folder as app.py)
    # ------------------------------------------------------------------ #
    default_db = os.path.join(os.getcwd(), "data", "shopeasy.db")
    database_path = os.environ.get("DATABASE_PATH", default_db)

    # ------------------------------------------------------------------ #
    # Upload folder configuration
    # ------------------------------------------------------------------ #
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


    if database_path.startswith(("postgresql://", "postgresql+psycopg2://","postgresql+psycopg://",)):
        # PostgreSQL
        app.config["SQLALCHEMY_DATABASE_URI"] = database_path
        app.config["DATABASE_PATH"] = database_path
    else:
        # SQLite
        db_path = os.path.abspath(database_path)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        app.config["DATABASE_PATH"] = db_path

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    db.init_app(app)

    # Register blueprints
    from shopeasy.routes.main import main_bp
    from shopeasy.routes.products import products_bp
    from shopeasy.routes.orders import orders_bp
    from shopeasy.routes.api import api_bp
    from shopeasy.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(profile_bp)

    # Always ensure tables exist — creates an empty schema if the DB file
    # was deleted. No seeding here; run init.sh to seed product data.
    with app.app_context():
        db.create_all()

    return app


def init_db():
    """
    Create all tables and seed the product catalogue.
    Called once by init.sh — never by the running application.
    """
    app = create_app()
    with app.app_context():
        db.create_all()
        _seed_if_empty()
        from shopeasy.models import Product, Order
        print(f"Database initialised at: {app.config['DATABASE_PATH']}")
        print(f"  Products : {Product.query.count()}")
        print(f"  Orders   : {Order.query.count()}")



def _seed_if_empty():
    """Seed initial product catalogue if the database is brand new."""
    from shopeasy.models import Product

    if Product.query.count() == 0:
        seed_products = [
            Product(
                name="Wireless Headphones",
                description="Premium noise-cancelling over-ear headphones with 30h battery life.",
                price=149.99,
                stock=42,
                category="Electronics",
                image_url="/static/img/headphones.svg",
            ),
            Product(
                name="Mechanical Keyboard",
                description="TKL layout with tactile switches and per-key RGB backlighting.",
                price=89.99,
                stock=28,
                category="Electronics",
                image_url="/static/img/keyboard.svg",
            ),
            Product(
                name="Ergonomic Mouse",
                description="Vertical ergonomic design with adjustable DPI and silent clicks.",
                price=49.99,
                stock=60,
                category="Electronics",
                image_url="/static/img/mouse.svg",
            ),
            Product(
                name="USB-C Hub",
                description="7-in-1 hub with 4K HDMI, 100W PD, and 3× USB-A ports.",
                price=39.99,
                stock=75,
                category="Accessories",
                image_url="/static/img/hub.svg",
            ),
            Product(
                name="Laptop Stand",
                description="Adjustable aluminium stand with ventilated design.",
                price=29.99,
                stock=50,
                category="Accessories",
                image_url="/static/img/stand.svg",
            ),
            Product(
                name="Webcam 1080p",
                description="Full HD webcam with built-in mic and auto-focus.",
                price=69.99,
                stock=33,
                category="Electronics",
                image_url="/static/img/webcam.svg",
            ),
        ]
        db.session.add_all(seed_products)
        db.session.commit()
