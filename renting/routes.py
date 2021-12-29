from datetime import date, datetime
from os import error, stat
import re
#from typing_extensions import Required
from flask.helpers import url_for
from flask.scaffold import _matching_loader_thinks_module_is_package
from sqlalchemy.sql.expression import label
from sqlalchemy.sql.functions import func
from werkzeug.datastructures import  EnvironHeaders
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers import request
from wtforms.validators import ValidationError
from wtforms.widgets.core import DateTimeLocalInput, TableWidget
from renting import app
from flask import Flask, render_template, flash, request
from renting import db
import calendar
from sqlalchemy import (Table, Column, String, Integer,
                        MetaData, select, func)


from renting.forms import HouseForm, TenantForm
from renting.models import HouseProperty, Tenant, TenantPayments
from os.path import os, dirname, realpath


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#HOME ########### BEGINS
@app.route("/")
def home_page():
    tenant_month = TenantPayments.create_defaults()
    _date = datetime.today()
    _momth = calendar.month_name[_date.month]
    tenant = TenantPayments.query.filter_by(month_name = _momth)
    return render_template('index.html', tenant_month=tenant_month,tenant = tenant)
#HOME ENDS

#HOUSE##### BEGINS 
# HOUSE LIST VIEW    
@app.route('/house_list')
def house_list_page():
    results = HouseProperty.query.all()
    return render_template('house_list.html', results = results)
# HOUSE LIST VIEW ENDS

#CREATING HOUSE
@app.route('/createhouse', methods=['GET','POST'])
def house_page():
    form =  HouseForm()
    if form.validate_on_submit():
        _house = HouseProperty(house_name = form.house_name.data, house_location = form.house_location.data,floor_number = form.floor_number.data, number_of_room = form.number_of_room.data,category = form.category.data)
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
    results = db.session.query(Tenant, HouseProperty, TenantPayments).filter(Tenant.house_id == HouseProperty.id, TenantPayments.tenant_id == Tenant.id).add_columns(Tenant.first_name,Tenant.surname,Tenant.nida,TenantPayments.num_room_to_take, Tenant.phone, TenantPayments.total_payable,TenantPayments.months_of_payment,TenantPayments.rent_per_month,TenantPayments.paidamount, HouseProperty.house_name,Tenant.id, Tenant.image_path)
    return render_template('tenantlist.html', results=results)

#CREATING TENENT
@app.route('/leasetenant', methods = ['GET','POST'])
def lease_tenant():
    form = TenantForm()
    house = HouseProperty.query.all()
    if form.validate_on_submit():
        file = request.files['image']
        filename = ''
        if file.filename == '':
           pass
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif not ALLOWED_EXTENSIONS:
            flash('Allowed image types are -> png, jpg, jpeg, gif', category='danger')
            return redirect(request.url)
        houseObj = db.session.query(HouseProperty).filter_by(id = form.house_id.data).first()
        num_rooms = houseObj.number_of_room
        remain_room = (int(num_rooms) - int(form.num_room_to_take.data))
        if remain_room <= 0:
            flash(f'This house has only {num_rooms} room(s) left, please try another house', category='danger')
            return redirect(request.url)
        if form.paidamount.data != "" and form.paidamount.data is not None:
            form.paymentdate.data = datetime.now()
        else:
            form.paymentdate.data = None
            form.paidamount.data=0.00
    
        _tenant = Tenant(first_name = form.first_name.data, surname = form.surname.data,nida = form.nida.data, phone = form.phone.data, email = form.email.data, house_id = form.house_id.data, image_path = os.path.join(app.config['UPLOAD_FOLDER'],filename))
        db.session.add(_tenant)
        db.session.commit()

        obj = db.session.query(Tenant).order_by(Tenant.id.desc()).first()
        month = datetime.today()
        dt = calendar.monthrange(month.year,month.month)[1]
        
        _tenant_month = TenantPayments(month_name = calendar.month_name[month.month], date_start = datetime.now(),  date_end =datetime.strptime('{}/{}/{}'.format(dt,month.month,month.year),'%d/%m/%Y'), tenant_id =obj.id, num_room_to_take = form.num_room_to_take.data, price_each_room = form.price_each_room.data, total_payable = form.total_payable.data, months_of_payment = form.months_of_payment.data, rent_per_month = form.rent_per_month.data, paidamount = form.paidamount.data, paymentdate = datetime.now())
        db.session.add(_tenant_month)
        db.session.commit()
        return redirect(url_for('tenant_list_page'))
    if form.errors != {}:
        #for errMsg in form.errors.values:
        flash(f'There was error {form.errors} create the tenant', category='danger')
    #flash(datetime.now())
   
    return render_template('leasetenant.html', form = form)

#UPDATE TENENANT
@app.route('/updatetenant/<int:id>', methods=['GET','POST'])
def update_tenant_page(id):
    _tenant=''
    tenantpayment=''
    form = TenantForm()
    tenant_to_update = db.session.query(Tenant, TenantPayments, HouseProperty).filter(Tenant.id == TenantPayments.tenant_id, Tenant.house_id == HouseProperty.id).filter_by(id = id).add_columns(Tenant.first_name, Tenant.surname, Tenant.nida, HouseProperty.house_name, Tenant.phone, Tenant.image_path, Tenant.email, TenantPayments.total_payable, TenantPayments.num_room_to_take, TenantPayments.paidamount, TenantPayments.price_each_room, TenantPayments.rent_per_month, TenantPayments.months_of_payment, Tenant.house_id).first()
    house = HouseProperty.query.all()
    choices=[(h.id,h.house_name) for h in HouseProperty.query.all()]
    selected = request.args.get('house_id', tenant_to_update.house_id)
    
    state = {'house_id':selected}
    #flash(state)
    if request.method == 'POST':
        #flash(request.form['house_id'])
        if form.paidamount.data != "" and form.paidamount.data is not None:
            form.paymentdate.data = datetime.now()
        else:
             form.paymentdate.data = None
             form.paidamount.data=0.00
    
        db.session.query(Tenant).filter_by(id=id).update({'first_name': request.form['first_name'],
                'surname': request.form['surname'],
                'nida': request.form['nida'],
                'house_id': request.form['house_id'],
                'phone': request.form['phone'],
                'email': request.form['email'],})

        db.session.query(TenantPayments).update({'total_payable':request.form['total_payable'],
                'num_room_to_take': request.form['num_room_to_take'],
                'paidamount': request.form['paidamount'],
                'price_each_room': request.form['price_each_room'],
                'rent_per_month': request.form['rent_per_month'],
                'months_of_payment': request.form['months_of_payment'],})
    
    
           
   
        try:
            db.session.commit()
            return redirect(url_for('tenant_list_page'))
        except ValidationError:
             flash('There was error {ValidationError} updating tenant', category='danger')
    
   
    #housename = house.house_name
    return render_template('updatetenant.html', form = form, tenant_to_update = tenant_to_update, house=house, choices = choices, state=state)

#DELETE TENANT
@app.route('/deletetenant/<int:id>')
def delete_tenant_page(id):
    tenant_to_delete = Tenant.query.get_or_404(id)
    try:
        db.session.delete(tenant_to_delete)
        db.session.commit()
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






