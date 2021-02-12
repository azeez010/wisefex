from models import app, User
from flask import request, render_template, jsonify
from flask_mail import Mail, Message
from os import environ
	
app.config['MAIL_SERVER'] = "email-smtp.us-east-1.amazonaws.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = environ.get("email_key")
app.config['MAIL_PASSWORD'] = environ.get("email_secret") 
app.config['MAIL_USE_SSL'] = True

# print(environ.get("email_key"),environ.get("email_secret"), environ.get("smtp")  )

mail = Mail(app)

@app.route("/mail-users", methods=["POST"])
def mail_user():
    sender_email = environ.get("email")
    recipient = request.json.get("user")
    message = request.json.get("mail")
    subject = request.json.get("subject")
    try:
        if recipient == "all":
            all_users = User.query.all()
            for user in all_users:
                msg = Message(subject, sender = sender_email, recipients = [user.email])
                msg.body = message
                msg.html = render_template('mail_template.html', message=message)
                mail.send(msg)
        else:
            msg = Message(subject, sender = sender_email, recipients = [recipient])
            msg.body = message
            msg.html = render_template('mail_template.html', message=message)
            mail.send(msg)
        return jsonify({"ok": "true"})
    except Exception as exc:
        return jsonify({"ok": ""})

def mail_folks(recipient, subject, message):
    sender_email = environ.get("email")
    try:
        msg = Message(subject, sender = sender_email, recipients = [recipient])
        msg.body = message
        msg.html = render_template('mail_template.html', message=message)
        mail.send(msg)
        return {"ok": "true"}
    except Exception as exc:
        print(f"fail... {str(exc)}")
        return {"ok": "", "msg": str(exc)}