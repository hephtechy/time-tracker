import pytz
import os
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timezone, timedelta
from flask_mail import Mail, Message
from twilio.rest import Client


auth = Blueprint('auth', __name__)


def newest_day():
    '''A function that returns the latest sign_in date if there have been sign_ins over
       a couple of days or None if the curent sign in is the first.'''

    users = User.query.all()

    # aggregating the sign_in dates
    sign_in_dates = []

    if users:
        for user in users:
            date = user.date
            sign_in_dates.append(date)

        # arbitrarily assigning the first date to newest_day
        latest_date = sign_in_dates[0]

        for date in sign_in_dates:
            if date > latest_date:
                latest_date = date

        return latest_date

    else:
        return None

def the_time():
    dateNtime = datetime.now(pytz.utc)
    minute = list(str(dateNtime.minute))
    if len(minute) == 1:
        hour, minute = str(dateNtime.hour+1), list(str(dateNtime.minute))
        new_minute = []
        new_minute.append(0)
        new_minute.append(int(minute[0]))
        minute = str(new_minute[0]) + str(new_minute[1])
        the_time = str(hour) + ":" + minute
    else:
        hour, minute = str(dateNtime.hour+1), str(dateNtime.minute)
        the_time = hour + ":" + minute
    return the_time

def mail_HR(user):
    if user.sign_in_status == True:
        msg = Message('Office Attendance', sender = 'temiseese23@gmail.com', recipients = ['adekimisimi@gmail.com', 'emanueloyekanmi@gmail.com'])
        msg.body = "Good day HR Mgr \n{} {} just signed in!!!".format(user.first_name, user.last_name)
        mail.send(msg)
    else:
        msg = Message('Office Attendance', sender = 'temiseese23@gmail.com', recipients = ['adekimisimi@gmail.com', 'emanueloyekanmi@gmail.com'])
        msg.body = "Good day HR Mgr \n{} {} just signed out!!!".format(user.first_name, user.last_name)
        mail.send(msg)
    return "HR mailed!!!"

def chat_HR(user):
    account_sid = os.environ.get("ACCOUNT_SID")
    auth_token = os.environ.get("AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    if user.sign_in_status == True:
        message = client.messages.create(
        from_='whatsapp:+14155238886',
        body="Good day HR Mgr \n{} {} just signed in!!!".format(user.first_name, user.last_name),
        to='whatsapp:+2347037006829'
        )
    else:
        message = client.messages.create(
                                     from_='whatsapp:+14155238886',
                                     body="Good day HR Mgr \n{} {} just signed out!!!".format(user.first_name, user.last_name),
                                     to='whatsapp:+2347037006829'
                                 )
    return "HR chatted!!!"


@auth.route('/login', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                user.date = datetime.now()
                user.sign_in_time = the_time()
                user.sign_in_status = True
                db.session.add(user)
                db.session.commit()

                # mailing and whatsapp reporting
                mail_HR(user=user)
                chat_HR(user=user)

                users = User.query.all()

                new_date = newest_day()
                if new_date != None:
                    return render_template('report.html', users=users, new_date=new_date)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("sign_in.html", user=current_user)


@auth.route('/sign_out', methods=['GET', 'POST'])
@login_required
def sign_out():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.sign_in_status == False:
                flash('You have signed out already.', category='error')
            else:
                if check_password_hash(user.password, password):
                    flash('Logged out successfully!', category='success')

                    user.sign_out_time = the_time()
                    user.sign_in_status = False
                    db.session.add(user)
                    db.session.commit()

                    # mailing and whatsapp reporting
                    mail_HR(user=user)
                    chat_HR(user=user)

                    users = User.query.all()

                    new_date = newest_day()
                    if new_date != None:
                        return render_template('report.html', users=users, new_date=new_date)
                else:
                    flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("sign_out.html", user=current_user)

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Please use another one.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, \
            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            #login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.sign_in'))
    return render_template("sign_up.html")
