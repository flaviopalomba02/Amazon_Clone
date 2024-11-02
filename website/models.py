from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from  werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=func.now())

    '''Il backref in Flask-SQLAlchemy crea una relazione bidirezionale tra due modelli, 
    consentendo di accedere facilmente ai dati da entrambi i lati della relazione. 
    Il parametro lazy=True permette di caricare i dati collegati solo quando vengono 
    effettivamente richiesti, ottimizzando le prestazioni.'''

    cart_item = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    # password getter
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")
    
    #password setter
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)
    
    def __str__(self):
        return '<Customer %r>' % Customer.id
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=func.now())

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return '<Product %r>' % self.product_name
    
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return '<Cart %r>' % self.id
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'))
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'))
    
    def __str__(self):
        return '<Order %r>' % self.id