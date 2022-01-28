import imp

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import time
from datetime import datetime
import atexit
import calendar
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler


account_sid =''#"AC23ae688c6704ed6fb3b1ca2204fb9b2f"
auth_token = ''#"8556b7ce3586aded0a10fcda6abda1de"
UPLOAD_FOLDER = 'renting/static/uploads/'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentaldb.db'
app.config['SECRET_KEY'] = '53a089e23b6255700b33f9fc'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
from renting.models import HouseProperty, Tenant, TenantPayments, User
# db.drop_all()
# db.create_all()
# db.session.commit()


def send_sms_to_all_tenants():
    client = Client(account_sid, auth_token)
    tenObj = Tenant.query.all()
    _date = datetime.today()
    _month = calendar.month_name[_date.month]
    for ten in tenObj:
        message = client.messages \
            .create(
                body=f'NDUGU: {ten.first_name +" "+ ten.surname} UNATAKIWA KULIPA KODI YA NYUMBA YA MWEZI: {_month.upper()}',
                from_='+12542795811',
                to=f'{ten.phone}'
            )

        print(message.sid)
        
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_sms_to_all_tenants, trigger='cron', month='*', year='*', day=1, hour='10')
scheduler.start()
    # Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
    

from renting import routes
#from renting import send_sms