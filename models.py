from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from time import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://olabode:azeez007@localhost/wisefex'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dataslid:azeez007@dataslid.mysql.pythonanywhere-services.com/dataslid$betbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = "d27e0926-13d9-11eb-900d-18f46ae7891sse"
app.config['TOKEN_EXPIRY_TIME'] = "10"


db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, default=False)
    account_number = db.Column(db.String(10))
    mobile_number = db.Column(db.String(20))
    country = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    invest_wallet = db.Column(db.Integer, default=0)
    bonus_wallet = db.Column(db.Integer, default=0)
    bitcoin_addr = db.Column(db.String(2000))
    referral = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(150))
    new = db.Column(db.Boolean, default=True)

class Admin_tasks(db.Model):
    __tablename__ = 'admin_tasks'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200))
    value = db.Column(db.String(200))

class Investments(db.Model):
    __tablename__ = "investments"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref=db.backref('investments', uselist=False), lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    paid = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    pending = db.Column(db.Boolean, default=False)
    reject = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(6000))
    date = db.Column(db.Integer, default=time())
    invest_type = db.Column(db.String(200))
    datetime = db.Column(db.DateTime, default=datetime.now())
    proof = db.Column(db.String(5000))
    proof_key = db.Column(db.String(500))
    return_date = db.Column(db.Integer())
    capital = db.Column(db.Integer())
    expected_return = db.Column(db.Integer())
    capital_withdraw = db.Column(db.Boolean, default=False)
    profit_withdraw = db.Column(db.Boolean, default=False)

class Withdrawal(db.Model):
    __tablename__ = "withdrawal"
    id = db.Column(db.Integer, primary_key=True)
    investment = db.relationship(Investments, backref=db.backref('withdrawal', uselist=False), lazy=True)
    investment_id = db.Column(db.Integer(), db.ForeignKey(Investments.id))
    paid = db.Column(db.Boolean, default=False)
    withdraw_type = db.Column(db.String(100))
    amount = db.Column(db.String(80))
    time = db.Column(db.Integer, default=time())
    # user  = db.relationship(User, backref=db.backref('Withdrawal', uselist=False), lazy=True)
    # user_id = db.Column(db.Integer(), db.ForeignKey(User.id))

class Reset_password(db.Model):
    __tablename__ = 'reset_password'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='reset_password', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    mail = db.Column(db.String(100))
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))
    
class Confirm_mail(db.Model):
    __tablename__ = 'confirm_mail'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100))
    user_details = db.Column(db.String(500))
    dateTime = db.Column(db.Integer)
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))

if __name__ == '__main__':
    manager.run()
