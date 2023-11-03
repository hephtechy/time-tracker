from . import app
# from flask import Flask

from flask_mail import Mail, Message
# app = Flask(__name__)

mails = Blueprint('mails', __name__)

mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'temiseese23@gmail.com'
app.config['MAIL_PASSWORD'] = 'pwqf pipn qobe biha'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route("/mail")
def index():
    msg = Message('Trying Text Formatting', sender = 'temiseese23@gmail.com', recipients = ['emanueloyekanmi@gmail.com'])
    msg.body = "Good morning Daddy \nEmmanuel Oyekanmi just signed in!!!"
    mail.send(msg)
    return "Sent"
