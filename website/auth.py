from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, SkincareFormEntry, Producte
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import requests


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)




submitted_products = []
@auth.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        # Process form submission
        name = request.form.get('name')
        brand = request.form.get('brand')
        description = request.form.get('description')
        price = request.form.get('price')
        target = request.form.get('target')
       

        new_entry = Producte(
            name=name,
            brand=brand,
            description=description,
            price=price,
            target=target,
           
            
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Skincare form submitted successfully!', category='success')

        product = {
            'name': name,
            'brand': brand,
            'description': description,
            'price': price,
            'target': target,
           
        }
        #return render_template("product.html", user=current_user, submitted=True, product=product)
        #return render_template("product.html", user=current_user, submitted=True, entries=[product])
        submitted_products.append(product)


        # Redirect to GET request to prevent form resubmission on page refresh
        return redirect(url_for('auth.product'))

    # Handle GET request to display existing entries
    entries = Producte.query.all()
    #return render_template("product.html", user=current_user, entries=entries)
    return render_template("product.html", user=current_user, entries=entries, submitted_products=submitted_products)
    








@auth.route('/skincare-form', methods=['GET', 'POST'])
def skincare_form():
    if request.method == 'POST':
        # Process form submission
        cleanser = request.form.get('cleanser')
        toner = request.form.get('toner')
        moisturizer = request.form.get('moisturizer')
        serum = request.form.get('serum')
        sunscreen = request.form.get('sunscreen')


        new_entry = SkincareFormEntry(
            cleanser=cleanser,
            toner=toner,
            moisturizer=moisturizer,
            serum=serum,
            sunscreen=sunscreen
            
            
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Skincare form submitted successfully!', category='success')

        # Redirect to GET request to prevent form resubmission on page refresh
        return redirect(url_for('auth.skincare_form'))

    # Handle GET request to display existing entries
    entries = SkincareFormEntry.query.all()
    return render_template("skincare_form.html", user=current_user, entries=entries)


@auth.route('/delete-entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = SkincareFormEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', category='success')
    return redirect(url_for('auth.skincare_form'))



@auth.route('/sort-entries', methods=['POST'])
def sort_entries():
    data = request.json
    sort_key = data.get('sort_key')
    sort_order = data.get('sort_order', 'asc')

    # Fetch the entries from the database without sorting
    entries = SkincareFormEntry.query.all()

    # Prepare the entries list with delete_url included
    entries_list = [{
        'id': entry.id,
        'cleanser': entry.cleanser,
        'toner': entry.toner,
        'moisturizer': entry.moisturizer,
        'serum': entry.serum,
        'sunscreen': entry.sunscreen,
        'delete_url': url_for('auth.delete_entry', entry_id=entry.id)  # Ensure correct blueprint reference
    } for entry in entries]

    # Send the data to the microservice for sorting
    response = requests.post('http://localhost:5001/sort', json={
        'entries': entries_list,
        'sort_key': sort_key,
        'sort_order': sort_order
    })

    # Check if the response from the microservice was successful
    if response.status_code == 200:
        sorted_entries = response.json()
    else:
        sorted_entries = entries_list  # Fallback to unsorted entries in case of an error
    
    return jsonify(sorted_entries)







@auth.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    brand = request.args.get('brand')
    price_range = request.args.get('price_range')

    # Filter entries based on query and filters
    entries = Producte.query

    if query:
        entries = entries.filter(Producte.name.ilike(f'%{query}%'))
    
    if brand:
        entries = entries.filter(Producte.brand == brand)
    
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
        entries = entries.filter(Producte.price.between(min_price, max_price))

    entries = entries.all()

    return render_template("search_results.html", user=current_user, entries=entries, query=query)


