"""
ShopEasy Database Models
"""

from datetime import datetime
from shopeasy import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), default="General")
    image_url = db.Column(db.String(500), default="/static/img/placeholder.svg")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = db.relationship("OrderItem", backref="product", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Product {self.name}>"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="pending")   # pending | confirmed | shipped | delivered
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "status": self.status,
            "total_amount": self.total_amount,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
        }

    def __repr__(self):
        return f"<Order #{self.id} by {self.customer_name}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Unknown",
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": round(self.quantity * self.unit_price, 2),
        }

    def __repr__(self):
        return f"<OrderItem order={self.order_id} product={self.product_id} qty={self.quantity}>"
