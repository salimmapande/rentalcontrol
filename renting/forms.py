from sqlalchemy.orm import defaultload
from sqlalchemy.sql.expression import label
from wtforms import validators
from wtforms.fields import choices
from wtforms.fields.simple import StringField
from renting import db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,SelectField
from wtforms.validators import DataRequired, Email, Length


from renting.models import HouseProperty

class HouseForm(FlaskForm):
    house_name = StringField(label="House Name", validators=[Length(max=30), DataRequired()])
    house_location = StringField(label="House Location", validators=[Length(max=30), DataRequired()])
    number_of_room = StringField(label="Number of rooms", validators=[DataRequired()])
    floor_number = StringField(label="Floor number", validators=[DataRequired()])
    category = SelectField("Category", choices=[('Select Category'),('Flat'),('House'),('Appartmant')])
    submit = SubmitField(label='Update')

class TenantForm(FlaskForm):
    first_name = StringField(label="First name: ", validators=[DataRequired()])
    surname = StringField(label="Surname: ", validators=[DataRequired()])
    phone = StringField(label="Phone number: ", validators=[DataRequired()])
    email = StringField(label="Email: ", validators=[Email()])
    nida = StringField(label="NIDA number: ", validators=[DataRequired()])
    house_id = SelectField("House Name: ", choices=[(h.id, h.house_name) for h in HouseProperty.query.all()])
    tenant_id = StringField(label="")
    num_room_to_take = SelectField("How many rooms", choices=[('Select nunber of rooms'),('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11'),('12')])
    price_each_room = StringField(label="Price for each room: ")
    total_payable = StringField(label="Rent Payable: ")
    months_of_payment = SelectField("Months to pay: ", choices=[('Select payment months'),('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11'),('12')])
    rent_per_month = StringField(label="Rent per month")
    paidamount = StringField(label="Amount Pain")
    paymentdate = StringField(label="Payment Date: ")
    paymentenddate = StringField(label="Payment End Date: ")
    image = StringField(label="Photo")
    month_name = StringField()
    date_start = StringField()
    date_end = StringField()
    submit = SubmitField(label="Create")


class Room(FlaskForm):
    room_number = StringField(label="Room number", validators=[DataRequired()])





