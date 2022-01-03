from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

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
# from renting.models import HouseProperty, Tenant, TenantPayments, User
# db.drop_all()
# db.create_all()
# db.session.commit()

from renting import routes
#from renting import send_sms