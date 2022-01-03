from sqlalchemy.orm import defaultload
from sqlalchemy.sql.expression import false, label
from wtforms import validators
from wtforms.fields import choices
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField
from renting import db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import datetime

from renting.models import HouseProperty, Tenant, User, TenantPayments

class HouseForm(FlaskForm):
    house_name = StringField(label="House Name", validators=[Length(max=30), DataRequired()])
    house_location = StringField(label="House Location", validators=[Length(max=30), DataRequired()])
    number_of_room = StringField(label="Number of rooms", validators=[DataRequired()])
    floor_number = StringField(label="Floor number", validators=[DataRequired()])
    category = SelectField("Category", choices=[('Select Category'),('Flat'),('House'),('Appartmant')])
    submit = SubmitField(label='Update')

class TenantPaymentForm(FlaskForm):
    
    tenant_id = SelectField('Select Tenant:', coerce= int, choices=[(t.id,t.first_name+'-'+t.surname+'-'+str(t.rent_per_month)) for t in Tenant.query.all()], validate_choice=false)
    balanced_amount  = StringField("Previous Balance:")
    total_payable = StringField(label="Rent Payable: ")
    house_id = SelectField("House Name: ", choices=[(h.id, h.house_name) for h in HouseProperty.query.all()], default=(0,"Select House"))
    paidamount = StringField(label="Amount:")
    paymentdate = StringField(label="Payment Date: ")
    paymentenddate = StringField(label="Payment End Date: ")
    month_name = StringField()
    date_start = DateField("From: ", validators=None, format="%Y-%m-%d", default = datetime.now())
    date_end = DateField("Valid until: ", validators=None, format="%Y-%m-%d", default=datetime.now())
    payment_receipt = StringField(label="Payment Receipt:")
    rent_per_month = StringField(label="Rent Per Month")
    submit = SubmitField(label="Create")


class TenantForm(FlaskForm):
    first_name = StringField(label="First name: ", validators=[DataRequired()])
    surname = StringField(label="Surname: ", validators=[DataRequired()])
    phone = StringField(label="Phone number: ", validators=[DataRequired()])
    email = StringField(label="Email: ", validators=[Email()])
    nida = StringField(label="NIDA number: ", validators=[DataRequired()])
    house_id = SelectField("House Name: ", choices=[(h.id, h.house_name) for h in HouseProperty.query.all()], default=(1,"Select House"))
    num_room_to_take = SelectField("How many rooms", choices=[('Select nunber of rooms'),('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11'),('12')])
    image = StringField(label="Photo")
    rent_per_month = StringField(label="Rent per month")
    price_each_room = StringField(label="Price for each room: ")
    submit = SubmitField(label="Create")

class RegisterForm(FlaskForm):
    def validate_username(self, check_user):
        user = User.query.filter_by(username = check_user.data).first()
        if user:
            raise ValidationError('This username already exists please try a different username')
    first_name = StringField(label="First name: ", validators=[DataRequired()])
    surname = StringField(label="Surname: ", validators=[DataRequired()])
    username = StringField(label='Username:', validators=[Length(min=2, max=30), DataRequired()])
    phone = StringField(label="Phone", validators=[Length(min=2), DataRequired()])
    email = StringField(label='Email:', validators=[Length(max=30), Email(), DataRequired()])
    password1  = PasswordField(label='Password:', validators=[Length(min=5), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[Length(min=2, max=30), DataRequired()])
    password  = PasswordField(label='Password:', validators=[Length(min=5), DataRequired()])
    submit = SubmitField(label='Log In')




