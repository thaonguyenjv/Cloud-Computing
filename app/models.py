from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    slug       = db.Column(db.String(50), unique=True, nullable=False)
    tax_rate   = db.Column(db.Float, default=0.08)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users        = db.relationship('User', backref='tenant', lazy=True)
    products     = db.relationship('Product', backref='tenant', lazy=True)
    transactions = db.relationship('Transaction', backref='tenant', lazy=True)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    tenant_id      = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256))
    role           = db.Column(db.String(20), default='staff')
    is_masteradmin = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    tenant_id   = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    price       = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(50))
    description = db.Column(db.String(200))
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id             = db.Column(db.Integer, primary_key=True)
    tenant_id      = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    tax_rate       = db.Column(db.Float, nullable=False)
    subtotal       = db.Column(db.Float, nullable=False)
    tax_amount     = db.Column(db.Float, nullable=False)
    total          = db.Column(db.Float, nullable=False)
    customer_email = db.Column(db.String(120))

    user  = db.relationship('User', backref='transactions')
    items = db.relationship('TransactionItem', backref='transaction', lazy=True)


class TransactionItem(db.Model):
    __tablename__ = 'transaction_items'
    id             = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_name   = db.Column(db.String(100), nullable=False)
    unit_price     = db.Column(db.Float, nullable=False)
    quantity       = db.Column(db.Integer, nullable=False)
    subtotal       = db.Column(db.Float, nullable=False)