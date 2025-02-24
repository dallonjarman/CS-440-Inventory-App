from flask import Flask
from .models import db
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import click

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    migrate.init_app(app, db)

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with sample data."""
        from .models import Product
        if not Product.query.first():
            products = [
                Product(name='Tomato', price=1.15, stock=10),
                Product(name='Banana', price=0.99, stock=15),
                Product(name='Apple', price=1.99, stock=20)
            ]
            db.session.add_all(products)
            db.session.commit()
            click.echo('Database seeded with sample products!')
        else:
            click.echo('Database already contains products!')

    with app.app_context():
        from . import routes

    return app