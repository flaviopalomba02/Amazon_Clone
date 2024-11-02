from flask import Blueprint, render_template, flash, redirect, request, jsonify
from flask_login import current_user, login_user, login_required
from .models import Product, Cart, Order
from . import db
from intasend import APIService
import random

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'
API_TOKEN = 'YOUR_API_TOKEN'

@views.route('/')
def home():
    items = Product.query.order_by(Product.date_added).all()
    return render_template('home.html', customer=current_user, items=items, 
                            cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else [])

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_in_cart = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

    if item_in_cart:
        try:
            item_in_cart.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_to_add.product_name} has been updated.', category='success')
            return redirect(request.referrer) #torna alla pagina precedente
        
        except Exception as e: 
            print('Quantity not updated.', e)
            flash(f'Quantity of {item_to_add.product_name} not updated.', category='error')
            return redirect(request.referrer)
    
    else:
        new_cart_item = Cart()
        new_cart_item.quantity = 1
        new_cart_item.customer_link = current_user.id

        try:
            new_cart_item.product_link = item_id
            db.session.add(new_cart_item)
            db.session.commit()
            db.session.commit()
            flash(f'{item_to_add.product_name} added to cart', category='success')

        except Exception as e:
            print('Item not added to the cart. ', e)
            flash(f'{item_to_add.product_name} has been NOT added to cart', category='error')

        return redirect(request.referrer)
    

@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = calculate_amount_cart(cart)
    
    return render_template('cart.html', cart=cart, amount=amount, total=amount+200, customer=current_user)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)

        try:
            cart_item.quantity += 1
            db.session.commit()
        except Exception as e:
            print(e)

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = calculate_amount_cart(cart)

        print(cart_id)
        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)

        if cart_item.quantity > 0:
            try:
                cart_item.quantity -= 1
                db.session.commit()
            except Exception as e:
                print(e)

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = calculate_amount_cart(cart)

        print(cart_id)
        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    
@views.route('/removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)

        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = calculate_amount_cart(cart)

        print(cart_id)
        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    

@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()

    valid_order = True

    if customer_cart:

        for item in customer_cart:
            if item.quantity == 0:
                valid_order = False
                item_zero = item.product.product_name
                break
        
        if valid_order:
            for item in customer_cart:

                order = Order()
                order.quantity = item.quantity
                order.price = item.product.current_price
                order.status = 'Pending'    
                order.payment_id = random.randint(0, 99999)
                order.customer_link = item.customer_link
                order.product_link = item.product_link

                try:
                    db.session.add(order)
                    product = Product.query.get(item.product_link)
                    product.in_stock -= item.quantity
                    db.session.delete(item)
                    db.session.commit()

                except Exception as e:
                    flash("Order has been not placed!", category='error')
                    print(e)
                    return redirect('/')
                
        else:
            flash(f"You cannot place an order with {item_zero} 0 quantity!", category='error')
            return redirect('/cart')
        
    else:
        flash("Your cart is empty!", category='error')
        return redirect('/')
    
    flash("Order placed successfully!", category='success')
    return redirect('/orders')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders, customer=current_user)

@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [], customer=current_user)

    return render_template('search.html')

def calculate_amount_cart(cart):
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity
    return amount


# tasto remove funziona ma a volte non va
# problema valore sull'icona carrello quando elimini prodotti e torni alla home