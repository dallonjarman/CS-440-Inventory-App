from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, event

db = SQLAlchemy()

class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Add event listener to handle unique constraint violations
@event.listens_for(User, 'before_insert')
def check_duplicate_user(mapper, connection, target):
    if User.query.filter_by(username=target.username).first():
        raise ValueError("Username already exists")
    if User.query.filter_by(email=target.email).first():
        raise ValueError("Email already exists")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=10)
    orders = db.relationship('Order', backref='product', lazy=True)

    def restock(self, amount):
        self.stock += amount
        
    def reduce_stock(self, amount):
        if self.stock >= amount:
            self.stock -= amount
            return True
        return False

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)