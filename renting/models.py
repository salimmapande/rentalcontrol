from datetime import date, timedelta
from flask.app import Flask
from sqlalchemy.orm import relationship
from sqlalchemy.sql.operators import nullsfirst_op
from sqlalchemy.sql.schema import ForeignKey
from renting import db, login_manager
from renting import bcrypt 
from wtforms_alchemy import ModelForm, Form
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
    Date, desc, asc
)
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Tenant(db.Model):
    __tablename__ = 'tenant'
    id = db.Column(db.Integer(), primary_key = True)
    first_name =  db.Column(db.String(length = 50), nullable = False)
    surname =  db.Column(db.String(length = 50), nullable = False)
    phone =  db.Column(db.String(length = 15), nullable = False)
    email = db.Column(db.String(length=50), nullable = True)
    nida = db.Column(db.String(length=50), nullable = True)
    house_id = db.Column(db.Integer(), nullable = True)
    image_path = db.Column(db.String(200), nullable=True)
    rent_per_month = db.Column(db.Float(), nullable = True)
    num_room_to_take = db.Column(db.Integer(), nullable = True)
    price_each_room = db.Column(db.Integer(), nullable = True)
    date_moved_in = Column(Date, nullable=True)

    @property
    def price_format(self):
        if len(str(self.price_each_room)) >= 4:
            return f"{str(self.price_each_room[:-3])},{str(self.price_each_room)[-3:]}/="
        else:
            return f"{self.price_each_room}/="

class HouseProperty(db.Model):
    __tablename__ = 'house_property'
    id = db.Column(db.Integer(), autoincrement=True, primary_key = True)
    house_name = db.Column(db.String(length = 50), nullable = False)
    house_location = db.Column(db.String())
    floor_number = db.Column(db.Integer())
    number_of_room = db.Column(db.Integer())
    category = db.Column(db.String(length=30))
    


class TenantPayments(db.Model):
    __tablename__ = 'tenant_payment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    month_name = Column(String, nullable=True)
    date_start = Column(DateTime, nullable=True)
    date_end = Column(DateTime, nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), nullable=True)
    house_id = db.Column(db.Integer(), ForeignKey('house_property.id'), nullable = True)
    total_payable = db.Column(db.Float(), nullable = True)
    months_of_payment = db.Column(db.Integer(), nullable =True)
    paidamount = db.Column(db.Float(), nullable = True)
    balanced_amount = Column(Float,nullable=True)
    paymentdate = db.Column(db.DateTime, nullable = True)
    payment_receipt = Column(String, nullable=True)
    
   

    def __repr__(self):
        return '<id {}>'.format(self.id)


    @classmethod
    def create_defaults(self):
        return [
            TenantPayments(month_name="January"),
            TenantPayments(month_name="February"),
            TenantPayments(month_name="March"),
            TenantPayments(month_name="April"),
            TenantPayments(month_name="May"),
            TenantPayments(month_name="June"),
            TenantPayments(month_name="July"),
            TenantPayments(month_name="August"),
            TenantPayments(month_name="September"),
            TenantPayments(month_name="October"),
            TenantPayments(month_name="November"),
            TenantPayments(month_name="December"),
        ]

    # @classmethod
    # def get_peyment_year(self):
    #     return [TenantPayments(year_name=i+2020) for i in range(100)]


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    first_name =  db.Column(db.String(length = 50), nullable = False)
    surname =  db.Column(db.String(length = 50), nullable = False)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    phone =  db.Column(db.String(length = 15), nullable = False)
    email = db.Column(db.String(length=50), nullable = True)
    password_hash = db.Column(db.String(200), nullable = False)

    @property
    def password(self):
        return self.password

    @password.setter
    def  password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)










