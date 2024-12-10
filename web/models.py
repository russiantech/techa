import jwt, random, time
from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from flask import current_app
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from web.apis.utils.helpers import error_response

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

from flask_login import LoginManager
s_manager = LoginManager()

# Configure Login Manager
s_manager.login_view = 'auth.signin'
@s_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_role_association = db.Table(
    'user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    keep_existing=True
)

apportion_items_association = db.Table(
    'apportion_items_association',
    db.Column('apportion_id', db.Integer, db.ForeignKey('apportion.id')),
    db.Column('items_id', db.Integer, db.ForeignKey('items.id')),
    db.Column('deleted', db.Boolean, default=False)  # Add a 'deleted' column
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), index=True)
    username = db.Column(db.String(100), index=True, nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)  #str type recommended bcos they're not meant for calculations
    password = db.Column(db.String(500), index=True, nullable=False)
    photo = db.Column(db.String(1000))
    admin = db.Column(db.Boolean(), default=False)  #true/false)
    gender = db.Column(db.String(50))  # ['male','female','other']
    city = db.Column(db.String(50))
    about = db.Column(db.String(5000))
    ratings = db.Column(db.Integer)
    reviews = db.Column(db.Integer)
    acct_no = db.Column(db.String(50))
    bank = db.Column(db.String(50))
    socials = db.Column(db.JSON, default={}) # socials: { 'fb': '@chrisjsm', 'insta': '@chris', 'twit': '@chris','linkedin': '', 'whats':'@techa' }
    src = db.Column(db.String(50))
    cate = db.Column(db.String(50))
    online = db.Column(db.Boolean(), default=False)  # 1-online, 0-offline
    status = db.Column(db.Boolean(), default=False)  # [ active(1), not active(0)]
    verified = db.Column(db.Boolean(), default=False)  # verified or not
    ip = db.Column(db.String(50))

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False) 
    
    account_details = db.relationship('AccountDetail', backref='user', lazy=True)
    role = db.relationship('Role', secondary=user_role_association, back_populates='user', lazy='dynamic')
    notification = db.relationship("Notification", backref="user", lazy=True) 
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    order = db.relationship("Order", backref="user", lazy=True) 
    
    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return any(role.type == 'admin' for role in self.role)
    
    def roles(self):
        return [ r.type for r in self.role ]

    def generate_token(self, exp=600, type='reset'):
        payload = {'uid': self.id, 'exp': time.time() + exp, 'type': type }
        secret_key =  current_app.config['SECRET_KEY']
        return jwt.encode( payload, secret_key, algorithm='HS256')

    def set_password(self, password: str) -> None:
        """Hashes the password using bcrypt and stores it."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Checks the hashed password using bcrypt."""
        if not password:
            return False
        return bcrypt.check_password_hash(self.password, password)

    def make_token(self, token_type: str = "reset_password") -> str:
        """
        Single method can be used for different tokens['reset', 'verify/'confirm'].
        Generates a secure token for specified token type(like ["reset_password", "verify_email"] etc).
        """
        serializer = Serializer(current_app.config["SECRET_KEY"])
        return serializer.dumps({"user_email": self.email, "token_type": token_type}, salt=self.password)
        
    @staticmethod
    def check_token(user: 'User', token: str) -> 'User':
        from itsdangerous import BadSignature, SignatureExpired
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            token_data = serializer.loads(
                token,
                max_age=current_app.config["RESET_PASS_TOKEN_MAX_AGE"],
                salt=user.password,
            )
                
            if token_data["token_type"] in ["reset_password", "verify_email"]:
                user.token_type = token_data["token_type"]
                return user
            
            return None
        
        except SignatureExpired:
            return error_response("Token has expired. Please request a new one.")
            # return "Token has expired. Please request a new one."
        except BadSignature:
            return  error_response("Invalid token. Please request a new one.")
        except Exception as e:
            return  error_response(str(e))


    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.photo}')"
        
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    message = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_read = db.Column(db.Boolean, default=False)
    
    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

#class Role(db.Model, RoleMixin):
class Role(db.Model):
    '''Role Table'''
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(100), unique=True)
    user = db.relationship('User', secondary=user_role_association, back_populates='role', lazy='dynamic')

class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default='0', nullable=True)
    name = db.Column(db.String(80), nullable=False) 
    dept = db.Column(db.String(80), nullable=False, default='k') 
    in_stock = db.Column(db.Integer, nullable=True, default=0)
    c_price = db.Column(db.Integer, nullable=True) #cost-price
    s_price = db.Column(db.Integer, nullable=False) #selling-price, not-a
    new_stock = db.Column(db.Integer, nullable=True)
    photos = db.Column(db.JSON)
    
    disc = db.Column(db.Integer, default=0) #discount
    desc = db.Column(db.Text)
    
    attributes = db.Column(db.JSON) #[ weight, size, condition, model, type, subtype, processor etc] 
    color = db.Column(db.JSON) #color:- ['red','wine', 'etc'],
    size = db.Column(db.JSON) #size:- ['s','m', 'l', 'xl', 'xxl'],
    sku = db.Column(db.String(1000))  #just refference (stock keeping unit)
    ip = db.Column(db.String(50))
    status = db.Column(db.Boolean(), default= 1) #[sold, active,]
    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # apportioned_quantities = db.relationship('Apportion', secondary=apportion_items_association, backref='items')
    apportion_items = db.relationship('Apportion', secondary=apportion_items_association, backref='items')
    
    #tag = db.relationship('Tag', secondary=item_tag, back_populates='item', overlaps="tag")
    sales = db.relationship("Sales", backref="item", lazy=True)
    
    # Define the one-to-many relationship with StockHistory
    # s_history = db.relationship('StockHistory', back_populates='item')
    s_history = db.relationship('StockHistory', back_populates='item', cascade="all, delete")
    
    def item_exists(item):
        return Items.query.filter(Items.id==item).first() is not None

    __table_args__ = (
        db.UniqueConstraint('name', 'category_id', 'dept', 'deleted'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'name': self.name,
            'dept': self.dept,
            'in_stock': self.in_stock,
            'c_price': self.c_price,
            's_price': self.s_price,
            'new_stock': self.new_stock,
            'photos': self.photos,
            'disc': self.disc,
            'desc': self.desc,
            'attributes': self.attributes,
            'color': self.color,
            'size': self.size,
            'ip': self.ip,
            'status': self.status,
            'deleted': self.deleted,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
            'sku': self.sku,
            
            # Relationships (avoid recursion)
            'apportion_items': [item.id for item in self.apportion_items] if self.apportion_items else [],
            # 'tags': [tag.id for tag in self.tag.all()] if self.tag else [],
            'stock_history': [history.to_dict() for history in self.s_history] if self.s_history else [],
            
            # 'sales': [sale.to_dict() for sale in self.sales] if self.sales else [],
            # 'sales': [{'id': sale.id, 'title': sale.title} for sale in self.sales] if self.sales else [],
            # NOTE: Below is prefered instead of  to_dict() to avoid infinite loop that result to maximum recursion error due to 
            # multiple use of to_dict on both Items and other models like Sales
            
            'sales': [
                {
                    'id': sale.id,
                    'title': sale.title,
                    'qty': sale.qty,
                    'qty_left': sale.qty_left,
                    'price': sale.price,
                    'created': sale.created.isoformat() if isinstance(sale.created, datetime) else sale.created,
                    # Add other relevant fields for Sales as needed
                }
                for sale in self.sales
            ] if self.sales else [],
        }

class Apportion(db.Model):
    __tablename__ = 'apportion'
    id = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(80), nullable=False, default='k') 
    product_title = db.Column(db.String(255), nullable=False)
    main_qty = db.Column(db.Integer, nullable=False)
    initial_apportioning = db.Column(db.Integer, nullable=False)
    apportioned_qty = db.Column(db.Integer, nullable=False)
    extracted_qty = db.Column(db.Integer, default=0)
    cost_price = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean(), nullable=False, default= 0)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    extractions = db.relationship('Extraction', backref='apportion', lazy=True)
    s_history = db.relationship('StockHistory', backref='apportion')
    
    def to_dict(self):
        """Convert the Apportion instance to a dictionary."""
        return {
            "id": self.id,
            "product_title": self.product_title,
            "dept": self.dept,
            "main_qty": self.main_qty,
            "initial_apportioning": self.initial_apportioning,
            "apportioned_qty": self.apportioned_qty,
            "extracted_qty": self.extracted_qty or self.initial_apportioning - self.apportioned_qty,
            "cost_price": self.cost_price,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            # Additional details if needed
            "extractions": [ extraction.to_dict() for extraction in self.extractions] if self.extractions else [],
            "s_history": [ history.to_dict() for history in self.s_history ] if self.s_history else []
        }

class Extraction(db.Model):
    __tablename__ = 'extracted'
    id = db.Column(db.Integer, primary_key=True)
    extracted_title  = db.Column(db.String(255), nullable=False)
    # Foreign key to Apportion table
    extracted_qty = db.Column(db.Integer, nullable=False)
    remaining_stock = db.Column(db.Integer)
    descr = db.Column(db.String(255))
    # sales_qty = db.Column(db.Integer, default=0)
    
    # One-to-many relationship with Sale
    sales = db.relationship('Sales', backref='extraction', lazy=True)
    apportion_id = db.Column(db.Integer, db.ForeignKey('apportion.id'), nullable=False)  # Fixing the FK reference

    deleted = db.Column(db.Boolean(), nullable=False, default= 0)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert the Apportion instance to a dictionary."""
        return {
            "id": self.id,
            "extracted_title": self.extracted_title,
            "product_title": self.apportion.product_title,
            "apportion_id": self.apportion_id,
            "extracted_qty": self.extracted_qty,
            "remaining_stock": self.remaining_stock,
            "descr": self.descr,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "created_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            
            # "sales": [sale.to_dict() for sale in self.sales] if self.sales else [],
            'sales': [
                {
                    'id': sale.id,
                    'title': sale.title,
                    'qty': sale.qty,
                    'qty_left': sale.qty_left,
                    'price': sale.price,
                    'created': sale.created.isoformat() if isinstance(sale.created, datetime) else sale.created,
                    # Add other relevant fields for Sales as needed
                }
                for sale in self.sales
            ] if self.sales else [],
        }
    
class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  # e.g., 'Chicken & Chips'
    qty_left = db.Column(db.Integer, default=0) #pcs-left
    qty = db.Column(db.Integer) #pcs-sold
    price = db.Column(db.Integer) # Combined price
    total = db.Column(db.Integer)
    dept = db.Column(db.String(80), nullable=False, default='k') #[k=kitchen, c=cocktail, b=bar]
    comment = db.Column(db.String(100))
    
    #!relationships
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    extracted_id = db.Column(db.Integer, db.ForeignKey('extracted.id'))

    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    # Check Constraint to ensure at least one of the columns is not null
    # __table_args__ = (
    # CheckConstraint(
    #     "(item_id IS NOT NULL OR extracted_id IS NOT NULL) AND "
    #     "(title IS NOT NULL AND price IS NOT NULL) AND "
    #     "(qty_left IS NOT NULL OR qty IS NOT NULL)",
    #     name="sales_item_extracted_qty_check"
    # ),
    # )
    
    __table_args__ = (
        CheckConstraint(
            "(item_id IS NOT NULL AND (qty IS NOT NULL OR qty_left IS NOT NULL)) "
            "OR (item_id IS NULL AND extracted_id IS NULL AND title IS NOT NULL AND price IS NOT NULL)",
            name="item_apportion_extraction_sales_constraints"
        ),
    )
    
    def to_dict(self):
        """Converts the Sales instance to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "qty_left": self.qty_left,
            "qty": self.qty,
            "price": self.price,
            # "c_price": self.item.c_price,
            # "s_price": self.item.s_price,
            "total": self.total,
            "dept": self.dept,
            "comment": self.comment,
            "item_id": self.item_id,
            "extracted_id": self.extracted_id,
            "deleted": self.deleted,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "updated": self.updated.isoformat() if isinstance(self.updated, datetime) else self.updated,
            # Related item and extraction information
            "items": self.item.to_dict() if self.item else None,
            "extraction": self.extraction.to_dict() if self.extraction else None,
        }
        
    def calctot(self, qty, price):
        self.total = qty * price

    def grandtot(self, total):
        return sum(total)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    cost = db.Column(db.Integer)
    dept = db.Column(db.String(80), nullable=False, default='k') #[k=kitchen, c=cocktail, b=bar]
    comment = db.Column(db.String(100)) #desc
    
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
   
class Category(db.Model):
    """ levels-> (super1->main2->sub3->mini4) """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('category.id')) #or root
    lev = db.Column(db.Integer, default=0)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(100))
    photo = db.Column(db.String(50))
    dept = db.Column(db.String(50), nullable=False, default='k')
    children = db.relationship("Category")
    items = db.relationship('Items', backref='categories', lazy=True)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

class Feedback(db.Model):
    """ can be comments/likes/dislikes/reviews/views """
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)  # ranges from 1(worst) to 5(best)
    comment = db.Column(db.Text)  # reviews/comment/feed-back texts
    
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # user->feedback
    items = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)  # user->course
from sqlalchemy import Enum
from enum import Enum as PyEnum

class AccountType(PyEnum):
    EXCHANGE = "exchange"
    PAYPAL = "paypal"
    CASH_APP = "cash_app"
    
class AccountDetail(db.Model):
    __tablename__ = 'accountdetails'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(Enum(AccountType), nullable=False, default=AccountType.PAYPAL)

    account_name = db.Column(db.String(100), nullable=False)
    account_phone = db.Column(db.String(20), nullable=True)
    exchange = db.Column(db.String(100), nullable=True)
    exchange_address = db.Column(db.String(255), nullable=True)

    bank_account = db.Column(db.String(50), nullable=True)
    short_code = db.Column(db.String(20), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    
    cash_app_email = db.Column(db.String(100), nullable=True)
    cash_app_username = db.Column(db.String(100), nullable=True)
    
    paypal_phone = db.Column(db.String(100), nullable=True)
    paypal_email = db.Column(db.String(100), nullable=True)
    
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<AccountDetail {self.account_name} - {self.account_type}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=True)  # Nullable ForeignKey to Plan
    is_subscription = db.Column(db.Boolean(), nullable=False, default=False)
    tx_id = db.Column(db.String(100))
    tx_ref = db.Column(db.String(100))
    tx_amount = db.Column(db.Integer)
    tx_descr = db.Column(db.Text)
    tx_status = db.Column(db.String(100), default='pending')
    currency_code = db.Column(db.String(100), default='USD')
    provider = db.Column(db.String(100))
    deleted = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationship to Plan (nullable)
    plan = db.relationship("Plan", back_populates="transactions")

class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    plan_title = db.Column(db.String(100))
    plan_amount = db.Column(db.Integer)
    plan_currency = db.Column(db.String(100), default='USD')
    plan_descr = db.Column(db.Text)
    plan_type = db.Column(db.String(100), default='monthly')
    plan_duration = db.Column(db.Integer, default=30)
    plan_features = db.Column(db.JSON)
    plan_avatar = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)

    # Relationship to Transaction (optional)
    transactions = db.relationship("Transaction", back_populates="plan")

    def to_dict(self):
        return {
            "id": self.id,
            "plan_title": self.plan_title,
            "plan_amount": self.plan_amount,
            "plan_currency": self.plan_currency,
            "plan_descr": self.plan_descr,
            "plan_type": self.plan_type,
            "plan_duration": self.plan_duration,
            "plan_features": self.plan_features,
            "plan_avatar": self.plan_avatar,
            "created": self.created_at,
            "updated_at": self.updated_at,
            "deleted": self.deleted,
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    order_item = db.Column(db.JSON) #['key:alue' / 'itemid:Qty']
    
    order_id = db.Column(db.Integer, unique=True, nullable=False, default=(random.randint(0, 999999)))    

    pment_option = db.Column(db.String(45), nullable=False, default='fw') #[flutterwave, paystack, paypal,cash-on-delivery,cheque, etc]
    order_status = db.Column(db.String(50), nullable=True, default='pending') #[received, pending, delivered, processing, underway]
    in_cart = db.Column(db.Boolean(), default=False)  #[set to true if user-placed the order, set to false if it's a carted order(items in user cart)]

    name = db.Column(db.String(45), nullable=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(45), nullable=True)
    zipcode = db.Column(db.String(45), nullable=False)
    adrs= db.Column(db.String(45), nullable=False)
    state = db.Column(db.String(45), nullable=False)
    country = db.Column(db.String(45), nullable=False)

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
