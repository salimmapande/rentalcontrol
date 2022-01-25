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
    house_name = StringField(label="JINA NA NYUMBA", validators=[Length(max=30), DataRequired()])
    house_location = StringField(label="ANUWANI YA NYUMBA", validators=[Length(max=30), DataRequired()])
    number_of_room = StringField(label="IDADI YA VYUMBA", validators=[DataRequired()])
    floor_number = StringField(label="IDADI YA GHOROFA", validators=[DataRequired()])
    category = SelectField("AINA YA NYUMBA", choices=[('Select Category'),('GOROFA'),('NYUMBA YA CHINI'),('APPARTMENT')])
    submit = SubmitField(label='SAJILI')

class TenantPaymentForm(FlaskForm):
    paymenttype = SelectField("AINA YA MALIPO", choices=[('CHAGUA AINA YA MALIPO'),('LIPA KUANZIA SASA'),('LIPA DENI')])
    tenant_id = SelectField('CHAGUA MPANGAJI:', coerce= int, choices=[(t.id,t.first_name+'-'+t.surname+'-'+str(t.rent_per_month)) for t in Tenant.query.all()], validate_choice=false)

    balanced_amount  = StringField("DENI LILILOPITA:")
    total_payable = StringField(label="KODI: ")
    house_id = SelectField("JINA LA NYUMBA: ", choices=[(h.id, h.house_name) for h in HouseProperty.query.all()], default=(0,"CHAGUA NYUMBA"))
    paidamount = StringField(label="KIASI CHA KULIPIA:")
    paymentdate = StringField(label="TAREHE YA MALIPO: ")
    paymentenddate = StringField(label="TAREHE YA MWISHO: ")
    month_name = StringField()
    date_start = DateField("KUANZIA: ", validators=None, format="%Y-%m-%d", default = datetime.now())
    date_end = DateField("TAREHE YA MWISHO: ", validators=[DataRequired()], format="%Y-%m-%d", default=datetime.now())
    payment_receipt = StringField(label="RISITI YA MALIPO:")
    rent_per_month = StringField(label="KODI YA MWEZI")
    #SearchBox = StringField("Search for Tenant Phone",validators=[DataRequired()])
    submit = SubmitField(label="SAJILI")


class TenantForm(FlaskForm):
    def check_numeric_nida(flaskform, nida):
        if nida.data.isnumeric():
            pass
        else:
            raise ValidationError('Namba ya NIDA ni tarakimu na si herufi, tafhadhli hakiki')
    
    def check_numeric_first_name(flaskform, first_name):
        if first_name.data.isnumeric():
            raise ValidationError('Jina la kwanza ni herufi na si tarakimu, tafhadhli hakiki')
        else:
            pass
    def check_numeric_surname(flaskform, surname):
        if surname.data.isnumeric():
            raise ValidationError('Jina la Ukoo ni herufi na si tarakimu, tafhadhli hakiki')
        else:
            pass
    first_name = StringField(label="JINA LA KWANZA: ", validators=[DataRequired(),check_numeric_first_name])
    surname = StringField(label="JINA LA UKOO: ", validators=[DataRequired(), check_numeric_surname])
    phone = StringField(label="NAMBA YA SIMU: ", validators=[DataRequired()])
    email = StringField(label="BARUA PEPE(Email): ", validators=[Email()])
    nida = StringField(label="NAMBA YA NIDA: ", validators=[DataRequired(), check_numeric_nida])
    house_id = SelectField("JINA LA NYUMBA: ", choices=[(h.id, h.house_name.upper()) for h in HouseProperty.query.all()], default=(1,"CHAGUA NYUMBA"))
    num_room_to_take = SelectField("IDADI YA VYUMBA", choices=[('CHAGUA IDADI YA VYUMBA'),('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11'),('12')])
    image = StringField(label="PICHA")
    rent_per_month = StringField(label="KODI YA MWEZI")
    price_each_room = StringField(label="KIASI CHA KODI YA MWEZI: ")
    date_moved_in = DateField(label="TAREHE YA KUHAMIA:")
    submit = SubmitField(label="SAJILI")
    

class RegisterForm(FlaskForm):
    def validate_username(self, check_user):
        user = User.query.filter_by(username = check_user.data).first()
        if user:
            raise ValidationError('username huyu amesajiliwa na mtu mwingine, tafadhali jaribu username nyingine')
    first_name = StringField(label="JINA LA KWANZA: ", validators=[DataRequired()])
    surname = StringField(label="JINA LA UKOO: ", validators=[DataRequired()])
    username = StringField(label='USERNAME:', validators=[Length(min=2, max=30), DataRequired()])
    phone = StringField(label="NAMBA YA SIMU", validators=[Length(min=2), DataRequired()])
    email = StringField(label='BARUA PEPE (Email):', validators=[Length(max=30), Email(), DataRequired()])
    password1  = PasswordField(label='NENOSIRI:', validators=[Length(min=5), DataRequired()])
    password2 = PasswordField(label='HAKIKI NENOSIRI:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='TENGENEZA AKAUNTI')


class LoginForm(FlaskForm):
    username = StringField(label='USERNAME:', validators=[Length(min=2, max=30), DataRequired()])
    password  = PasswordField(label='NENOSIRI:', validators=[Length(min=5), DataRequired()])
    submit = SubmitField(label='INGIA')




