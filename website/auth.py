from flask import Blueprint, render_template, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user
from .forms import SignUpForm, LoginForm, PasswordChangeForm
from .models import Customer
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email=email).first()
        if customer:
            if customer.verify_password(password=password):
                flash("Login completed successfully.", category='success')
                login_user(customer)
                return redirect('/admin-page') if current_user.id == 4 else redirect('/')
            else:
                flash("Incorrect password. Try again.", category='error')
        else:
            flash("Account does not exist!", category='error')

    return render_template('login.html', form=form)


@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    form = SignUpForm()

    # non devo fare manualmente tutti i controlli
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2:
            new_customer =  Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash("Account created. Now you can login.", category='success')
                return redirect('/login')
            except Exception as e:
                print(e)
                flash("Email already exists!", category='error')
            
        else:
            flash("Passwords don't match!", category='error')

    return render_template('signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    print(f'Customer id: {customer_id}')
    return render_template('profile.html', customer=customer)

@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password Updated Successfully', category='success')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New Passwords do not match!!', category='error')

        else:
            flash('Current Password is Incorrect', category='error')

    return render_template('change_password.html', form=form, customer=customer)