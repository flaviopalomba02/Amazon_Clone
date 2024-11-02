from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Customer
from . import db
from .models import Product, Order

# l'account dell'admin ha id=4, questa è l'unica condizione
# per capire se un utente è l'admin, va migliorata

admin = Blueprint('admin', __name__)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 4:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.flash_sale = flash_sale
            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f"{product_name} added successfully", category='success')
                print('Product added')
                return render_template('add-shop-items.html', form=form, customer=current_user)

            except Exception as e:
                print(e)
                flash('Item Not added', category='error')


        return render_template('add-shop-items.html', form=form, customer=current_user)
    
    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
def shop_items():
    if current_user.id == 4:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop-items.html', items=items, customer=current_user)

    return render_template('404.html')

'''
send_from_directory dice a Flask esattamente da quale cartella prelevare il file, e si occupa di gestire correttamente 
i percorsi e la sicurezza del file system. Senza di esso, Flask non saprebbe come localizzare e inviare il file al browser.
'''
@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_shop_items(item_id):
    if current_user.id == 4:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)

        #precompila i campi del form con i dati prima della modifica
        #render_kv è per aggiungere un tag html, placeholder in questo caso
        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            previous_price = form.previous_price.data
            current_price = form.current_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update(dict(product_name=product_name,
                                                                previous_price=previous_price,
                                                                current_price=current_price,
                                                                in_stock=in_stock,
                                                                flash_sale=flash_sale,
                                                                product_picture = file_path))
                db.session.commit()
                flash(f"{product_name} updated successfully.", category='success')
                print("Product updated")

                return redirect('/shop-items')
            
            except Exception as e:
                print('Product not updated.', e)
                flash('Item not updated!', category='error')


        return render_template('update-items.html', form=form, customer=current_user)

    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 4:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit() 
            flash('Item deleted successfully.', category='success')
            print("Product deleted")
            return redirect('/shop-items')
        
        except Exception as e:
            flash("Item not deleted", category='error')
            print('Product not deleted.', e)
        
        return redirect('/shop-items')

    return render_template('404.html')

        
@admin.route('/view-orders')
@login_required
def view_orders():
    if current_user.id == 4:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders, customer=current_user)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 4:
        form = OrderForm()
        order = Order.query.get(order_id)

        if form.validate_on_submit():
            order.status = form.order_status.data

            try:
                db.session.commit()
                flash("Order updated successfully!", category='success')
                return redirect('/view-orders')
            
            except Exception as e:
                print(e)
                flash("Order has not been updated!", category='error')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form, customer=current_user)
    
    return render_template('404.html')

@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 4:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers, customer=current_user)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 4:
        return render_template('admin.html', customer=current_user)
    return render_template('404.html')


# id=4 è poco sicuro, @admin_required esiste?
# i campi dell'update dovrebbero essere già prescritti