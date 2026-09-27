# db_models.py (새 이름!)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    """상품 모델"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, default=100.0)
    type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    image_filename = db.Column(db.String(200))
    purchase_url = db.Column(db.String(500))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'confidence': self.confidence,
            'type': self.type,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'purchase_url': self.purchase_url,
            'likes': self.likes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'