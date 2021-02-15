import json, time
from models import Investments, Withdrawal, db, app, User, Admin_tasks, Confirm_mail, Reset_password, current_user
# from mailing_server import mail_folks, Message, mail
from passlib.hash import md5_crypt
from flask import url_for, request, render_template, redirect, flash, send_from_directory, send_file, jsonify, Response
import boto3, os, botocore
from forms import passwordResetForm, passwordReset
import io
from forms import MyForm, LoginForm, TestimonyForm 
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Admin_tasks, db.session))
admin.add_view(ModelView(Investments, db.session))
admin.add_view(ModelView(Withdrawal, db.session))
admin.add_view(ModelView(Reset_password, db.session))
admin.add_view(ModelView(Confirm_mail, db.session))
# Reset_password
# @app.route("/signup", methds=[o"GET", "POST"])
# def signup():
# # def authenticate_mail():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
    
#     form = MyForm()
#     if request.method == "POST" and form.validate_on_submit():
#         name = form.name.data
#         email = form.email.data
#         phone = form.phone.data
#         password = form.password.data
#         password = md5_crypt.hash(password)
#         user_info = json.dumps({
#             "name": name,
#             "email": email,
#             "phone": phone,
#             "password": password
#         })
#         random_generated = uuid.uuid4()
#         expired_token = time.time() + (int(app.config['TOKEN_EXPIRY_TIME']) * 60 )
#         print((int(app.config['TOKEN_EXPIRY_TIME']) * 60 ))
#         # msg = Message('Hello', sender = 'wisefexinvestment11@gmail.com', recipients = [email])
#         # msg.body = f"Hello Flask message sent from Flask-Mail, the token is {random_generated}, it expires in {expired_token / 60} hours "
#         # mail.send(msg)
        
#         confirm_user = Confirm_mail(user_details=user_info, token=random_generated, mail=email, dateTime=expired_token )
#         db.session.add(confirm_user)
#         db.session.commit()
        
#         return redirect(url_for("enter_token"))

#     return render_template("sign_up.html", form=form)


# @app.route("/enter-token", methods=["GET", "POST"])
# # def confirm_mail():
# def enter_token():
#     if request.method == "POST":
#         token_value = request.form.get("token")
#         verify_token = Confirm_mail.query.filter_by(token=token_value).first()
#         if verify_token:
#             current_time = time.time()
#             if current_time >= verify_token.dateTime:
#                 db.session.delete(verify_token)
#                 db.session.commit()
#                 flash("token has expired, try again")
#                 return redirect(url_for("confirm_mail"))
                
#             else:
#                 # success msg
#                 user_data = json.loads(verify_token.user_details)
#                 user_name = user_data.get("name")
#                 password = user_data.get("password")
#                 email = user_data.get("email")
#                 phone = user_data.get("phone")
    
#                 password = md5_crypt.hash(password)
                
#                 user = User(username=user_name, password=password, phone=phone, email=email)
#                 db.session.add(user)

#                 delete_confirm = Confirm_mail.query.filter_by(mail=email).all()
#                 for each_delete_confirm in delete_confirm:
#                     db.session.delete(each_delete_confirm)
#                 db.session.commit()
                
@app.route("/enter-token", methods=["GET", "POST"])
# def confirm_mail():
def enter_token():
    if request.method == "POST":
        token_value = request.form.get("token")
        print(token_value)
        verify_token = Confirm_mail.query.filter_by(token=token_value).first()
        if verify_token:
            current_time = time.time()
            print(current_time, verify_token.dateTime)
            if current_time >= float(verify_token.dateTime):
                db.session.delete(verify_token)
                db.session.commit()
                flash("token has expired, try again")
                return redirect(url_for("sign_up"))
                
            else:
                # success msg
                user_data = json.loads(verify_token.user_details)
                user_name = user_data.get("username")
                password = user_data.get("password")
                email = user_data.get("email")
                mobile_number = user_data.get("mobile_number")
                bitcoin_wallet = user_data.get("bitcoin_wallet")
                account_name = user_data.get("account_name")
                bank_name = user_data.get("bank_name")
                account_number = user_data.get("account_number")
                country = user_data.get("country")
                referral = user_data.get("referral")
    
                password = md5_crypt.hash(password)
                
                check_for_first_user = len(User.query.all())
                if not check_for_first_user:
                    user = User(username=user_name, referral=referral, is_admin=True, password=password, country=country, account_number=account_number, account_name=account_name, bitcoin_addr=bitcoin_wallet, bank_name=bank_name, mobile_number=mobile_number, email=email)
                else:
                    user = User(username=user_name, referral=referral, is_admin=False, password=password, country=country, account_number=account_number, account_name=account_name, bitcoin_addr=bitcoin_wallet, bank_name=bank_name, mobile_number=mobile_number, email=email)
                
                db.session.add(user)

                delete_confirm = Confirm_mail.query.filter_by(mail=email).all()
                for each_delete_confirm in delete_confirm:
                    db.session.delete(each_delete_confirm)
                db.session.commit()
                

                flash("your account has been verified successfully, you can now login")
                return redirect(url_for("login"))
            print(verify_token.token)
        else:
            flash("token does not exist")
            return redirect(url_for("enter_token"))
    else:
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template("enter_token.html", context=context)
        

    #             flash("your account has been verified successfully, you can now login")
    #             return redirect(url_for("login"))
    #         print(verify_token.token)
    #     else:
    #         flash("token does not exist")
    #         return redirect(url_for("enter_token"))
    # else:
    #     context = {}
    #     all_tasks = Admin_tasks.query.all()
    #     for task in all_tasks:
    #         context[f"{task.key}"] = task.value
    #     return render_template("enter_token.html", context=context)
        
@app.route('/enter-reset-password', methods=["GET", "POST"])
def enter_reset_password():
    form = passwordReset()
    if request.method == "POST" and form.validate_on_submit():
        token_value = request.form.get("token")
        verify_token = Reset_password.query.filter_by(token=token_value).first()
        if verify_token:
            current_time = time.time()
            if current_time >= verify_token.dateTime:
                db.session.delete(verify_token)
                db.session.commit()
                # error message
                flash("token has expired, try again")
                return redirect(f"/enter-reset-password?token={token_value}")
            else:
                # success msg
                password = request.form.get("password")
                password = md5_crypt.hash(password)
                user_id = request.args.get("i")
                user = User.query.filter_by(id=user_id).first()
                user.password = password
                delete_confirm = Reset_password.query.filter_by(mail=user.email).all()
                for each_delete_confirm in delete_confirm:
                    db.session.delete(each_delete_confirm)
                db.session.commit()
                
                flash("You have successfully changed your password")
                return redirect(url_for("login"))
        else:
            flash("token does not exist")
            return redirect(url_for("enter_reset_password"))
    else:
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template('enter_reset_password.html', form=form, context=context)


@app.route('/reset-password', methods=["GET", "POST"])
def reset_password():
    # form = passwordResetForm()
    # print(form.validate_on_submit())
    # and form.validate_on_submit()
    if request.method == "POST":
        # email = request.form.get("email")
        email = request.json.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            random_generated = uuid.uuid4()
            Reset_password.query.filter_by(user_id=user.id).delete()
            
            expired_token = time.time() + (int(app.config['TOKEN_EXPIRY_TIME']) * 60 )
            resetPass = Reset_password(token=random_generated, mail=email, dateTime=expired_token, user_id=user.id)
            db.session.add(resetPass)
            db.session.commit()
            try:
                message = f"Here is the password reset token {random_generated}, Use it to change your password"
                msg = Message("Reset password from wisefex investment", sender = 'wisefexinvestment11@gmail.com', recipients = [email])
                msg.body = message
                mail.send(msg)
            except Exception as exc:
                # print(str(exc))
                return jsonify({"ok": '', "msg": 'Oops! mail failed to send sue to Network issues'})

            flash("The token has been sent to your mail successfully")
            return jsonify({"ok": 'true', "msg": "The token has been sent to your mail successfully"})
        else:
            return jsonify({'ok': '', 'msg': "E-mail doesn't exist, create an account instead"})
    else:
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template("reset_password.html", context=context)

@app.route('/reset-password-confirm')
def confirm_reset_password():
    verify_token = Reset_password.query.filter_by(token=token_value).first()
    if verify_token:
        current_time = time.time()
        if current_time >= verify_token.dateTime:
            db.session.delete(verify_token)
            db.session.commit()
            # error message
            confirm_message = { "failure": "token has expired, try again" }
            return confirm_message

        else:
            confirm_message = { "success": "your account has been verified successfully, you can now change password" }
            return confirm_message

# @app.route('/reset-password-confirm')
# def confirm_reset_password():   
#     form = MyForm()
#     if request.method == "POST" and form.validate_on_submit():
#         password = form.password.data
#         name = form.name.data
#         email = form.email.data
#         phone = form.email.data
#         password = md5_crypt.hash(password)
#         check_for_first_user = len(User.query.all())
#         if not check_for_first_user:
#             user = User(username=name, is_admin=True, email=email, phone=phone, password=password)
#         else:
#             user = User(username=name, is_admin=False, email=email, phone=phone, password=password)
#         db.session.add(user)
#         db.session.commit()
#         flash("You have signed up successfully", "success")    
#         return redirect('/login')
#     else:
#         print("HAAAAA")
#     return render_template("sign_up.html", form=form)

