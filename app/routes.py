from flask import render_template, redirect, url_for, flash, session
from functools import wraps
from .models import User, Product, Order
from .forms import RegistrationForm, LoginForm, OrderForm, ProductForm, RestockForm
from . import db
from sqlalchemy.exc import IntegrityError

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

from flask import current_app as app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('You are already logged in!')
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check for existing user before creating
            existing_user = User.query.filter(
                db.or_(
                    User.username == form.username.data,
                    User.email == form.email.data
                )
            ).first()
            
            if existing_user:
                if existing_user.username == form.username.data:
                    form.username.errors.append('Username already taken')
                if existing_user.email == form.email.data:
                    form.email.errors.append('Email already registered')
                return render_template('register.html', form=form)
            
            # Create new user if no duplicates found
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('Registration failed. Please try again with different credentials.')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration.')
            app.logger.error(f'Registration error: {str(e)}')
            
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('products'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!')
            return redirect(url_for('products'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    form = OrderForm()
    # Only show products with stock > 0
    available_products = Product.query.filter(Product.stock > 0).all()
    form.product_id.choices = [(p.id, f"{p.name} (${p.price}) - {p.stock} left") for p in available_products]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product and product.reduce_stock(form.quantity.data):
            order = Order(
                user_id=session['user_id'],
                product_id=form.product_id.data,
                quantity=form.quantity.data
            )
            db.session.add(order)
            db.session.commit()
            flash('Order placed successfully!')
            return redirect(url_for('view_orders'))
        else:
            flash('Not enough stock available!')
    return render_template('orders.html', form=form)

@app.route('/restock/<int:product_id>', methods=['GET', 'POST'])
@login_required
def restock_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = RestockForm()
    if form.validate_on_submit():
        product.restock(form.amount.data)
        db.session.commit()
        flash(f'Successfully restocked {product.name}!')
        return redirect(url_for('products'))
    return render_template('restock.html', form=form, product=product)

@app.route('/view_orders')
@login_required
def view_orders():
    user_orders = Order.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_orders.html', orders=user_orders)