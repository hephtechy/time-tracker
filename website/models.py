from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import pytz



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    sign_in_time = db.Column(db.String(10), nullable=True)#, server_default=func.now())
    sign_out_time = db.Column(db.String(10), nullable=True)
    date = db.Column(db.DateTime(), nullable=True)
    sign_in_status = db.Column(db.Boolean, nullable=True)
    interval = db.Column(db.Interval, nullable=True)
