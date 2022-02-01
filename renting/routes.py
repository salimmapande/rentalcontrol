#from _typeshed import ReadableBuffer

from ast import Pass
from datetime import date, datetime
from genericpath import exists
from gzip import READ
from hashlib import new
from os import error, path, pathsep
from re import T
#import re
from threading import Thread
from types import resolve_bases

#from typing_extensions import Required
from flask.helpers import url_for
from flask.scaffold import _matching_loader_thinks_module_is_package
import flask_login
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.expression import label
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.sql.type_api import to_instance
from validators import url
from werkzeug.datastructures import  EnvironHeaders
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers import request
from wtforms.fields import choices
from wtforms.form import Form
from wtforms.validators import ValidationError
from wtforms.widgets.core import DateTimeLocalInput, TableWidget
from renting import app
from flask import Flask, render_template, flash, request, jsonify, session
from renting import db
import calendar
from sqlalchemy import (Table, Column, String, Integer,
                        MetaData, select)
from flask_login import login_user, logout_user, current_user
from sqlalchemy.sql import func
import renting
import time

# import picamera.mmal as mmal
import atexit
from twilio.rest import Client
from renting.forms import HouseForm, TenantForm, TenantPaymentForm, RegisterForm, LoginForm
from renting.models import HouseProperty, Tenant, TenantPayments, User
from apscheduler.schedulers.background import BackgroundScheduler
from os.path import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
account_sid ="" #"AC23ae688c6704ed6fb3b1ca2204fb9b2f"
auth_token = "" #"51f5831d6594363a0d6a4cdbcd66a211"
# LOGIN USER BEGINS
@app.route('/', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'You have successfully logged in as { attempted_user.username }', category='success')
            #session['username'] = attempted_user.username
            return redirect(url_for('home_page'))
        else:
            flash(f'Username and Password incorrect, please try again', category='danger')
              
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error {err_msg} login you, please try again')
    return render_template('login.html', form=form)
# LOGIN USER ENDS
# LOGOUT USER BEGINS
@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info') 
    return redirect(url_for('login_page'))
# LOGOUT USER ENDS
# REGISTER USER #### BEGINS

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        #flash(form.surname)
        exists = db.session.query(User.id).filter_by(id=1).first() is not None
        if exists:
            flash('Tafadhali wasiliana na Admin')
            return redirect(request.url)
     
        _user = User(first_name = form.first_name.data,surname = form.surname.data,username = form.username.data,
                    email=form.email.data, 
                    phone = form.phone.data,
                    password = form.password1.data)
        db.session.add(_user)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error creating user {err_msg}', category='danger')
    return render_template('register.html', form=form)


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#HOME ########### BEGINS

@app.route("/home_page")
def home_page():
    tenant_month = TenantPayments.create_defaults()
    _date = datetime.today()
    _momth = calendar.month_name[_date.month]
    tenant = TenantPayments.query.filter_by(month_name = _momth)
    dt = datetime.today()
    year = dt.year
    house = HouseProperty.query.all()
    
    
    return render_template('index.html', tenant_month=tenant_month,tenant = tenant, year=year, houses = house)
    
#HOME ENDS
# USER ACCOUNT  ### BEGINS 
@app.route('/user_accounts')
def user_accounts():
    users  = User.query.all()
    return render_template('users.html', users = users)
# USER ACCOUNT ENDS
#HOUSE##### BEGINS 
# HOUSE LIST VIEW    
@app.route('/house_list')
def house_list_page():
    results = HouseProperty.query.all()
    return render_template('house_list.html', results = results)
# HOUSE LIST VIEW ENDS
# HOUSE DETAILS
@app.route('/housedetails/<int:id>')
def house_deatils_page(id):
    house = HouseProperty.query.get_or_404(id)
    return render_template('housedetails.html', house = house)
# HOUSE DETAILS ENDS

#GET HOUSE BY ID ### BEGINS
@app.route('/gethouse/<int:id>')
def get_house(id):
    house = db.session.query(HouseProperty, Tenant).filter(HouseProperty.id==Tenant.house_id).filter_by(id=id).add_columns(HouseProperty.house_name, HouseProperty.house_location, HouseProperty.number_of_room, HouseProperty.category, func.sum(Tenant.num_room_to_take).label("room_taken")).first()
    return render_template('house_by_id.html', house = house)

# ENDS
#CREATING HOUSE
@app.route('/createhouse', methods=['GET','POST'])
def house_page():
    form =  HouseForm()
    if form.validate_on_submit():
        file = request.files['image']
        filename = ''
        if os.path.isfile(file.filename):
            flash("The file already exists")
        else:
            # Rename the file
            new_name = str(form.house_name.data).replace(" ","_")
            extension = os.path.splitext(file.filename)[1][1:]
            file.filename = new_name+"."+extension
          
        if file.filename == '':
           pass
        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif not ALLOWED_EXTENSIONS:
            flash('Allowed image types are -> png, jpg, jpeg, gif', category='danger')
            return redirect(request.url)
     
        _house = HouseProperty(house_name = form.house_name.data.upper(), house_location = form.house_location.data.upper(),floor_number = form.floor_number.data, number_of_room = form.number_of_room.data,category = form.category.data.upper(), image_path = file.filename)
        try:
            db.session.add(_house)
            db.session.commit()
            return redirect(url_for('house_list_page'))
        except ValidationError:
            flash(f'There was an error {ValidationError} creating house', category='danger')
    return render_template('house.html', form = form)
#UPDATE HOUSE
@app.route('/updatehouse/<int:id>', methods = ['GET','POST'])
def update_house_page(id):
    form = HouseForm()
    house_to_update = HouseProperty.query.get_or_404(id)
    if request.method == 'POST':
        house_to_update.house_name = request.form['house_name']
        house_to_update.house_location = request.form['house_location']
        house_to_update.floor_number = request.form['floor_number']
        house_to_update.number_of_room = request.form['number_of_room']
        house_to_update.category = request.form['category']
        house_to_update.rent_amount = request.form['rent_amount']
        house_to_update.image_path = request.form['image']
        try:
            db.session.commit()
            return redirect(url_for('house_list_page'))
        except ValidationError:
            flash('There was error {ValidationError} updating house', category='danger')
    return render_template('updatehouse.html', form = form, house_to_update = house_to_update)

#DELETE HOUSE
@app.route('/deletehouse/<int:id>')
def delete_house_page(id):
    house_to_delete = HouseProperty.query.get_or_404(id)
   
    try:
        db.session.delete(house_to_delete)
        db.session.commit()
        image = house_to_delete.image_path
        image_path = app.config['UPLOAD_FOLDER']
        full_path = str(image_path+image)
        if os.path.isfile(full_path):
            os.remove(full_path)
        return redirect(url_for('house_list_page'))
    except ValueError:
        flash('There was error {ValueError} delete house')

@app.route('/confirmdeletehouse/<int:id>', methods = ['GET', 'POST'])
def confirm_delete(id):
    to_delete = HouseProperty.query.get_or_404(id)
    return render_template('confrimdeletehouse.html', id = id, to_delete=to_delete)
#HOUSE####### ENDS

#TENANT######### BEGINS
#TENANT LIST VIEW
@app.route('/tenantlist')
def tenant_list_page():
    results = db.session.query(Tenant, HouseProperty).filter(Tenant.house_id == HouseProperty.id).add_columns(Tenant.first_name,Tenant.surname,Tenant.nida,Tenant.num_room_to_take, Tenant.phone, Tenant.rent_per_month, HouseProperty.house_name,Tenant.id, Tenant.image_path, Tenant.email)
    return render_template('tenantlist.html', results=results)

#CREATING TENENT
@app.route('/leasetenant', methods = ['GET','POST'])
def lease_tenant():
    form = TenantForm()
    fullnumber=''
    if form.validate_on_submit():
        file = request.files['image']
        filename = ''
        if os.path.isfile(file.filename):
            flash("The file already exists")
        else:
            # Rename the file
            new_name = str(form.surname.data).replace(" ","_")
            extension = os.path.splitext(file.filename)[1][1:]
            # count num of rows 
            count = db.session.query(Tenant).count()
            _count = count+1
            file.filename = new_name+str(_count)+"."+extension
        if file.filename == '':
           pass
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif not ALLOWED_EXTENSIONS:
            flash('Allowed image types are -> png, jpg, jpeg, gif', category='danger')
            return redirect(request.url)
        
        if form.phone.data.isnumeric():
            if len(str(form.phone.data)) >=10:
                nozero = str(form.phone.data)[-9:]
                fullnumber = "255"+nozero
        else:
            raise ValidationError(f'Namba ya simu haitakiwi kuwa na herufi, tafadhali ihakiki', category='danger')
           
        if form.first_name.data.isnumeric():
            flash(f'Jina la kwanza halitakiwi kuwa na namba, tafadhali hakiki jina', category='danger')
            return redirect(request.url)
        else:
            pass
        if form.surname.data.isnumeric():
            flash(f'Jina la ukoo halitakiwi kuwa na namba, tafadhali hakiki jina la ukoo', category='danger')
            return redirect(request.url)
        else:
            pass


        #form.house_id.choices=[(h.id, h.house_name) for h in db.session.query(HouseProperty).all()]
        houseObj = db.session.query(HouseProperty).filter_by(id = form.house_id.data).first()
        num_rooms = houseObj.number_of_room
        num_of_room_taken = 0
        rooms_available = 0
        num_of_room_taken = db.session.query(func.sum(Tenant.num_room_to_take)).filter(Tenant.house_id==form.house_id.data).scalar()
        if num_of_room_taken == None:
            num_of_room_taken=0
        
        rooms_available = (int(num_rooms) - int(num_of_room_taken))

        if int(form.num_room_to_take.data) > int(rooms_available):
            flash(f'This house has only {rooms_available} room(s) left, please try another house', category='danger')
            return redirect(request.url)
     
        _tenant = Tenant(first_name = form.first_name.data.upper(), surname = form.surname.data.upper(),nida = form.nida.data, phone = fullnumber, email = form.email.data, house_id = form.house_id.data, image_path = file.filename, rent_per_month = form.rent_per_month.data, num_room_to_take = form.num_room_to_take.data,price_each_room = form.price_each_room.data, date_moved_in = datetime.today())
        try:
            db.session.add(_tenant)
            db.session.commit()
            return redirect(url_for('tenant_list_page'))
        except ValidationError:
            db.session.rollback()
            flash(f'Kulikuwa na tatizo {ValidationError} katika kusajili mpangaji', category='danger')
        return redirect(request.url)
    if form.errors != {}:
        flash(f'Kulikuwa na tatizo {form.errors} katika kusajili mpangaji', category='danger')
    houses=HouseProperty.query.all()
    return render_template('leasetenant.html', form = form, houses = houses)

#UPDATE TENENANT
@app.route('/updatetenant/<int:id>', methods=['GET','POST'])
def update_tenant_page(id):
    form = TenantForm()
    tenant_to_update = db.session.query(Tenant, HouseProperty).filter(Tenant.house_id == HouseProperty.id).filter_by(id = id).add_columns(Tenant.first_name, Tenant.surname, Tenant.nida, HouseProperty.house_name, Tenant.phone, Tenant.image_path, Tenant.email, Tenant.num_room_to_take, Tenant.price_each_room, Tenant.rent_per_month, Tenant.house_id).first()
    house = HouseProperty.query.all()
    choices=[(h.id,h.house_name) for h in HouseProperty.query.all()]
    selected = request.args.get('house_id', tenant_to_update.house_id)
    
    state = {'house_id':selected}
    #flash(state)
    if request.method == 'POST':
        file = request.files['image']
        #flash(file.filename)
        filename = ''
        if file.filename == '':
            file.filename  = tenant_to_update.image_path
        else:
            if file and allowed_file(file.filename):
                # Rename the file
                new_name = str(form.surname.data).replace(" ","_")
                extension = os.path.splitext(file.filename)[1][1:]
                # count num of rows 
                count = db.session.query(Tenant).count()
                _count = count+1
                file.filename = new_name+str(_count)+"."+extension
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            elif not ALLOWED_EXTENSIONS:
                flash('Allowed image types are -> png, jpg, jpeg, gif', category='danger')
                return redirect(request.url)

        db.session.query(Tenant).filter_by(id=id)\
        .update({'first_name': request.form['first_name'].upper(),
                'surname': request.form['surname'].upper(),
                'nida': request.form['nida'],
                'house_id': request.form['house_id'],
                'phone': request.form['phone'],
                'email': request.form['email'],
                'image_path': file.filename})
   
        try:
            db.session.commit()
           
            return redirect(url_for('tenant_list_page'))
        except ValidationError:
             flash('There was error {ValidationError} updating tenant', category='danger')
    
    return render_template('updatetenant.html', form = form, tenant_to_update = tenant_to_update, house=house, choices = choices, state=state)

#DELETE TENANT
@app.route('/deletetenant/<int:id>')
def delete_tenant_page(id):
    tenant_to_delete = Tenant.query.get_or_404(id)
    try:
        db.session.delete(tenant_to_delete)
        db.session.commit()
        image = tenant_to_delete.image_path
        image_path = app.config['UPLOAD_FOLDER']
        full_path = str(image_path+image)
        if os.path.isfile(full_path):
            os.remove(full_path)
        return redirect(url_for('tenant_list_page'))
    except ValueError:
        flash('There was error {ValueError} delete tenant')

@app.route('/confirmdeletetenant/<int:id>', methods = ['GET', 'POST'])
def confirm_delete_tenant(id):
    to_delete = Tenant.query.get_or_404(id)
    return render_template('confrimdeletetenant.html', id = id, to_delete=to_delete)

@app.route('/tenantmonthly/<month_name>')
def tenant_monthly(month_name):
   
    tenant = db.session.query(TenantPayments, Tenant).filter(Tenant.id == TenantPayments.tenant_id).filter_by(month_name = month_name).add_columns(Tenant.first_name,Tenant.surname, TenantPayments.total_payable,TenantPayments.month_name, TenantPayments.paidamount, TenantPayments.paymentdate, (TenantPayments.paidamount - TenantPayments.total_payable).label("balance"))
    return render_template('tenantmonthly.html', tenant =tenant)
#DELETE TENANT ### ENDS

#TENANT DETAILS OVERVIEW
@app.route('/tenantdetails/<int:id>')
def tenant_details(id):
    tenObj = db.session.query(Tenant, HouseProperty).filter(Tenant.house_id == HouseProperty.id).filter_by(id=id).add_columns(Tenant.first_name,Tenant.surname,Tenant.nida,Tenant.num_room_to_take, Tenant.phone, Tenant.rent_per_month, HouseProperty.house_name,Tenant.id, Tenant.image_path, Tenant.email, Tenant.date_moved_in).first()
    
    return render_template('tenantdetails.html', tenObj = tenObj)
#TENANT OVERVIEW ENDS
#PAYMENT MODULE #### BEGINS
#CREATE PAYMENT
@app.route('/tenantpayment', methods=['GET','POST'])
def tenant_payment():
    form = TenantPaymentForm()
    house = HouseProperty.query
    if form.validate_on_submit():
      
        form.tenant_id.choices = [(t.id,t.first_name+'-'+t.surname+'-'+str(t.rent_per_month)) for t in Tenant.query.all()]
        month_of_payment = month_diff(form.date_end.data, datetime.today())
        if form.paidamount.data == None or form.paidamount.data =="":
            form.paidamount.data=0.00
        if form.balanced_amount.data == None or form.balanced_amount.data =="":
            form.balanced_amount.data=0.00
        if form.total_payable.data == None or form.total_payable.data =="":
            form.total_payable.data = 0.00
        form.paymentdate.data = datetime.now()
        checkbalance_advanced = db.session.query(db.session.query(TenantPayments).filter(TenantPayments.tenant_id == form.tenant_id.data).order_by(TenantPayments.tenant_id.desc()).filter(TenantPayments.balanced_amount > 0.0).exists()
).scalar()
       
        checkbalance_owed = db.session.query(db.session.query(TenantPayments).filter(TenantPayments.tenant_id == form.tenant_id.data).order_by(TenantPayments.tenant_id.desc()).filter(TenantPayments.balanced_amount < 0).exists()
).scalar()
       
        if form.paymenttype.data == "LIPA KUANZIA SASA":
            if float(form.balanced_amount.data) < 0:
                flash('Unatakiwa kulipa deni, tafadhali chagua aina ya malipo kulipa deni', category='danger')
                return redirect(request.url)
            else:
                pass
           
            if float(form.balanced_amount.data) > 0.0:
                if float(form.total_payable.data) == 0.0:
                    flash(f'Tafadhali chagua tarehe ya mwisho ya malipo', category='danger')
                    return redirect(request.url)
            if float(form.paidamount.data) > 0:
                if float(form.total_payable.data) > float(form.paidamount.data):
                    form.balanced_amount.data = float(form.balanced_amount.data) + float(form.paidamount.data) - float(form.total_payable.data)
                else:
                    _paidamount = float(form.paidamount.data) + float(form.balanced_amount.data)
                    form.paidamount.data = _paidamount
                    form.balanced_amount.data = _paidamount - float(form.total_payable.data)
            else:
                #form.total_payable.data = float(form.total_payable.data) - float(form.balanced_amount.data)
                form.paidamount.data = float(form.balanced_amount.data)
                form.balanced_amount.data = float(form.balanced_amount.data) - float(form.total_payable.data)
                
           
        elif form.paymenttype.data == "LIPA DENI":
            if float(form.balanced_amount.data) > 0.0:
                flash('Huna deni, tafadhali chagua aina ya malipo, kulipa kuanzia sasa', category='danger')
                return redirect(request.url)
            if float(form.balanced_amount.data) < 0.0:
                paymentObj = db.session.query(TenantPayments).filter(TenantPayments.tenant_id == form.tenant_id.data).filter(TenantPayments.balanced_amount < 0).first()
              
                payment_id = int(paymentObj.id)
                if float(form.paidamount.data) > 0:
                    if float(form.total_payable.data) > float(form.paidamount.data):
                        form.balanced_amount.data = float(form.balanced_amount.data) - float(form.paidamount.data)
                    else:
                        form.balanced_amount.data = float(form.paidamount.data) - float(form.total_payable.data)
                to_be_updated = db.session.query(TenantPayments).filter_by(id=payment_id).first()
                to_be_updated.balanced_amount =  form.balanced_amount.data
                to_be_updated.paidamount = form.paidamount.data
                to_be_updated.total_payable = form.total_payable.data
        
                db.session.commit()
                tenObj = db.session.query(Tenant).filter_by(id=form.tenant_id.data).first()
                fullname = tenObj.first_name+'-'+tenObj.surname
                houseObj = db.session.query(HouseProperty).filter_by(id = form.house_id.data).first()
                client = Client(account_sid, auth_token)

                message = client.messages \
                    .create(
                        body=f'Deni la shilingi: {form.balanced_amount.data} kwa nyumba: {houseObj.house_name} limelipwa na: {fullname} tarehe: {datetime.today()}',
                        from_='+12542795811',
                        to='+255 769 176 767'
                    )

                print(message.sid)
                return redirect(url_for('payment_list'))    
        else:
            flash('Please select payment type',category='danger')
            return redirect(request.url)
                
        month = datetime.today()
        #dt = calendar.monthrange(month.year,month.month)[1]
        
        # retuns the last date of the month: datetime.strptime('{}/{}/{}'.format(dt,month.month,month.year),'%d/%m/%Y')
        _tenant_month = TenantPayments(month_name = calendar.month_name[month.month], date_start = datetime.today(),  date_end = form.date_end.data, tenant_id =form.tenant_id.data, total_payable = form.total_payable.data, months_of_payment = month_of_payment+1, paidamount = form.paidamount.data, paymentdate = datetime.today(), house_id = form.house_id.data, balanced_amount = form.balanced_amount.data, payment_receipt = form.payment_receipt.data)
        db.session.add(_tenant_month)
        db.session.commit()
        tenObj = db.session.query(Tenant).filter_by(id=form.tenant_id.data).first()
        fullname = tenObj.first_name+'-'+tenObj.surname
        houseObj = db.session.query(HouseProperty).filter_by(id = form.house_id.data).first()
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                body=f'Kodi ya shilingi: {form.paidamount.data} kwa nyumba: {houseObj.house_name} limelipwa na: {fullname} tarehe: {datetime.today()}',
                from_='+12542795811',
                to='+255 769 176 767'
            )

        print(message.sid)
       
        return redirect(url_for('payment_list'))
    if form.errors != {}:
        flash(f'There was error {form.errors} saving payments', category='danger')

    return render_template('tenantpayment.html', form=form, house = house)

# CREATE PAYMENT #### ENDS
# LIST OF PAYMENTS BEGINS
@app.route('/paymentlist')
def payment_list():
    
    payments = db.session.query(TenantPayments, Tenant, HouseProperty).filter(Tenant.id == TenantPayments.tenant_id, HouseProperty.id == Tenant.house_id).add_columns(TenantPayments.id,Tenant.first_name,Tenant.surname, TenantPayments.total_payable,HouseProperty.house_name, TenantPayments.paidamount, TenantPayments.paymentdate, TenantPayments.balanced_amount, TenantPayments.months_of_payment)
    return render_template('paymentlist.html', payments = payments)
# LIST OF PAYMENTS #### ENDS

#DELETE A PAYMENT ### BEGINS
@app.route('/deletepayment/<int:id>', methods=['GET','POST'])
def delete_payment(id):
    payment_to_delete = TenantPayments.query.get_or_404(id)
    try:
        db.session.delete(payment_to_delete)
        db.session.commit()
        return redirect(url_for('payment_list'))
    except ValueError:
        flash('There was error {ValueError} delete payment')

#DELETE A PAYMENT ###ENDS

#CONFIRM DELETE A PAYMENT ### BEGINS
@app.route('/confirmdeletepayment/<int:id>', methods=['GET','POST'])
def confirm_delete_payment(id):
    to_delete = TenantPayments.query.get_or_404(id)
    return render_template('confirmdeletepayment.html', id = id, to_delete=to_delete)
#CONFIRM DELETE A PAYMENT #### ENDS


###########################################
# FUNCTIONS
# SEARCH FOR TENANTS BY HOUSE_ID ## BEGINS
@app.route('/house/<house_id>')
def tenant_by_id(house_id):
    
    tenants = db.session.query(Tenant, TenantPayments).filter(Tenant.house_id==TenantPayments.house_id).filter_by(house_id = house_id).add_columns(Tenant.id,Tenant.first_name,Tenant.surname,Tenant.rent_per_month,TenantPayments.balanced_amount).all()
    tenantArray = []
    for ten in tenants:
        tenantObj = {}
        tenantObj['id'] = ten.id
        tenantObj['first_name'] = ten.first_name
        tenantObj['surname'] = ten.surname
        tenantObj['rent_per_month'] = ten.rent_per_month
        tenantObj['balanced_amount']= ten.balanced_amount
        tenantArray.append(tenantObj)
    return jsonify({'tenants': tenantArray})
# ENDS
# RETURNS NUMBER OF MONTH FROM THE DATE RANGE
def month_diff(d1, d2): 
    """Return the number of months between d1 and d2, 
    such that d2 + month_diff(d1, d2) == d1
    """
    diff = (12 * d1.year + d1.month) - (12 * d2.year + d2.month)
    return diff

#RETURNS ARRAY OBJECT FOR TENANT
@app.route('/searchtenant/<phone>')
def search_by_phone(phone):
    
    tenants = db.session.query(Tenant).filter_by(phone = phone).add_columns(Tenant.id,Tenant.first_name,Tenant.surname,Tenant.rent_per_month, Tenant.house_id).all()
    tenantArray = []
    for ten in tenants:
        tenantObj = {}
        tenantObj['id'] = ten.id
        tenantObj['first_name'] = ten.first_name
        tenantObj['surname'] = ten.surname
        tenantObj['rent_per_month'] = ten.rent_per_month
        tenantObj['house_id'] = ten.house_id
        tenantArray.append(tenantObj)
    return jsonify({'tenants': tenantArray})

#RETURNS BALANCE AMOUNT FOR A TENANT
@app.route('/balancesearch/<int:id>')
def balance_search(id):
    
    paymentObj = db.session.query(TenantPayments).order_by(TenantPayments.tenant_id.desc()).filter(TenantPayments.tenant_id == id).all()
    paymentArray = []
    for pay in paymentObj:
        payObj = {}
        payObj['balanced_amount'] = pay.balanced_amount
        paymentArray.append(payObj)
    return jsonify({'paymentamount': paymentArray})







