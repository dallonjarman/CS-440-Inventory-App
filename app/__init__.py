from flask import Flask
from .models import db
import os
from dotenv import load_dotenv  # added import

load_dotenv()  # load environment variables

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # updated to load from .env
    db.init_app(app)

    with app.app_context():
        # Only create tables if database doesn't exist
        if not os.path.exists('app/app.db'):
            db.create_all()
            
            # Add sample products with stock values
            from .models import Product
            if not Product.query.first():
                products = [
                    Product(name='Tomato', price=1.15, stock=10),
                    Product(name='Banana', price=0.99, stock=15),
                    Product(name='Apple', price=1.99, stock=20)
                ]
                db.session.add_all(products)
                db.session.commit()

    with app.app_context():
        from . import routes

    return app