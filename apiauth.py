from flask import request, jsonify
# Flask,  
# from flask_sqlalchemy import SQLAlchemy
from os import environ, path
from passlib.hash import md5_crypt
import uuid, time, json
from random import randrange

from flask_mail import Mail, Message

class Api_auth():
    def __init__(self, conf, db, mail, user_schema):
        self.conf = conf
        self.user = conf.config['USER_TABLE']
        self.db = db
        self.user_schema = user_schema
        self.create_database(self.db)
        # set expiry default time this are in minutes
        self.confirm_mail_expiry_time = 5
        self.reset_password_expiry_time = 5
        self.configuration()
        # if mail is present set mail
        if mail:
            self.mail = mail

    def create_database(self, db):
        class Token(db.Model):
            __tablename__ = 'token'
            id = db.Column(db.Integer, primary_key=True)
            user  = db.relationship(self.user, backref='token', lazy=True)
            token = db.Column(db.String(50))            
            user_id = db.Column(db.Integer(), db.ForeignKey(self.user.id))
            dateTime = db.Column(db.Integer)

        class Reset_password(db.Model):
            __tablename__ = 'reset_password'
            id = db.Column(db.Integer, primary_key=True)
            user  = db.relationship(self.user, backref='reset_password', lazy=True)
            mail = db.Column(db.String(100))
            user_id = db.Column(db.Integer(), db.ForeignKey(self.user.id))
            dateTime = db.Column(db.Integer)
            token = db.Column(db.String(150))
            
        class Confirm_mail(db.Model):
            __tablename__ = 'confirm_mail'
            id = db.Column(db.Integer, primary_key=True)
            mail = db.Column(db.String(100))
            user_details = db.Column(db.String(500))
            dateTime = db.Column(db.Integer)
            token = db.Column(db.String(150))
        
        self.token = Token
        self.confirmMail =  Confirm_mail
        self.resetPass = Reset_password

    def configuration(self):
        conf = self.conf
        if 'USER_TABLE' in conf.config:
            self.user_table = conf.config['USER_TABLE']
        else:
            raise Exception('USER_TABLE is required, make sure you initial user_table to your user"s table')
        # This is in minutes
        if 'TOKEN_EXPIRY_TIME' in conf.config:
            # token expiry time is in minutes 
            self.token_expiry_time = int(conf.config['TOKEN_EXPIRY_TIME']) * 60
        else:
            self.token_expiry_time = 60 * 2

        if 'CONFIRM_USER_MAIL' in conf.config:
            # i.e if confirm user mail is set to True
            if conf.config['CONFIRM_USER_MAIL']:
                if 'CONFIRM_USER_MAIL_EXPIRY_TIME' in conf.config:
                    self.confirm_mail_expiry_time = int(conf.config['CONFIRM_USER_MAIL_EXPIRY_TIME']) * 60

        if 'RESET_PASSWORD_EXPIRY_TIME' in conf.config:
            self.confirm_mail_expiry_time = int(conf.config['RESET_PASSWORD_EXPIRY_TIME']) * 60 

    def reset_password(self, resetFunction):
        def reset(id):
            random_generated = randrange(99999, 9999999)
            id = resetFunction(id)

            self.resetPass.query.filter_by(user_id=id).delete()
            self.db.session.commit()
            
            user = self.user.query.get(id)

            expired_token = time.time() + self.reset_password_expiry_time
            print(self.confirm_mail_expiry_time)
            resetPass = self.resetPass(token=random_generated, mail="voodeo", dateTime=expired_token, user_id=user.id)
            self.db.session.add(resetPass)
            self.db.session.commit()
            
            print(f'your token is {random_generated}')
            return f'your token is {random_generated}'
        return reset

    def confirm_reset_password(self, confirm_reset_data):
        def confirm_token():
            token = confirm_reset_data()
            print(token)
            token_value = token['token']
            print(token['token'])

            verify_token = self.resetPass.query.filter_by(token=token_value).first()
            if verify_token:
                current_time = time.time()
                if current_time >= verify_token.dateTime:
                    self.db.session.delete(verify_token)
                    self.db.session.commit()
                    # error message
                    confirm_message = { "failure": "token has expired, try again" }
                    return confirm_message
                    
                else:
                    # success msg
                    confirm_message = { "success": "your account has been verified successfully, you can now change password" }
                    # confirm_message = { "success": "your account has been verified successfully" }
                    return confirm_message
                print(verify_token.token)
            return token
        
        return confirm_token
        
    def confirmedSignUp(self, token_data):
        def confirm_signup_token():
            token = token_data()
            print(token)
            token_value = token['token']
            print(token['token'])

            verify_token = self.confirmMail.query.filter_by(token=token_value).first()
            if verify_token:
                current_time = time.time()
                if current_time >= verify_token.dateTime:
                    self.db.session.delete(verify_token)
                    self.db.session.commit()
                    # error message
                    confirm_message = { "failure": "token has expired, try again" }
                    return confirm_message
                    
                else:
                    # success msg
                    print(verify_token.user_details)
                    print(type(verify_token.user_details))
                    user_data = json.loads(verify_token.user_details)
                    credentials = []
            
                    for value in user_data.values():
                        credentials.append(value)
                    
                    user_name, password, *misc = credentials
                    password = md5_crypt.hash(password)
                    
                    user = self.user(username=user_name, password=password)
                    self.db.session.add(user)
                    self.db.session.commit()
                    confirm_message = { "success": "your account has been verified successfully, you can now change password" }
                    # confirm_message = { "success": "your account has been verified successfully" }
                    return confirm_message
                print(verify_token.token)
            else:
                confirm_message = {"failure": "token does not exist"}
                # print("token does not exist")
            return confirm_message
        
        return confirm_signup_token
    def comfirm_sign_up(self, sign_up_json):
        # generate_ = randrange(99999, 999999)
        def comfirm_mail_wrapper():
            random_generated = randrange(99999, 9999999)
            sign_up_data = sign_up_json()
            email = sign_up_data['email']
            user_info = json.dumps(sign_up_data)
            expired_token = time.time() + self.confirm_mail_expiry_time

            confirm_user = self.confirmMail(user_details=user_info, token=random_generated, mail=email, dateTime=expired_token )
            self.db.session.add(confirm_user)
            self.db.session.commit()
            # msg = Message('Hello', sender = 'dataslid@gmail.com', recipients = [email])
            # msg.body = f"Hello Flask message sent from Flask-Mail, the token is {random_generated} "
            # self.mail.send(msg)
            signup_message = {'success': 'a mail has been sent to your e-mail, use the token sent to complete your registration'}
            return signup_message
        #     self.db.session.commit()
        #     credentials = []
            
        #     for value in sign_up_data.values():
        #         credentials.append(value)
            
        #     user_name, password = credentials
        #     password = md5_crypt.hash(password)
            
        #     user = self.user(username=user_name, password=password)
        #     self.db.session.add(user)
        #     self.db.session.commit()
            
        #     signup_message = '{"sucess": "you have sign up successfully"}'
        #     return signup_message
        return comfirm_mail_wrapper
  

    def login(self, loginfunc):
        def wrapper():
            login_data = loginfunc()
            credentials = []
            for value in login_data.values():
                credentials.append(value)       
            email, password = credentials
            get_user = self.user.query.filter_by(email=email).first()
            if get_user:
                hashed_password = get_user.password
                if md5_crypt.verify(password, hashed_password):
                    # login
                    auth_token = uuid.uuid4()
                    token = self.token(token=auth_token, user_id = get_user.id, dateTime=time.time())
                    self.db.session.add(token)
                    get_user.pin_trial = 5
                    self.db.session.add(get_user)
                    self.db.session.commit()
                    login_message = { "success": "you have logged in successfully" , "token": token.token }
                else:
                    login_message = { "failure": "wrong email address or password" }    
            else:
                login_message = { "failure": "wrong email address or password" }
            return login_message
            
        return wrapper
    

    def verify_pin(self, pin, email ):
        get_user = self.user.query.filter_by(email=email, pin=pin).first()
        if get_user:
            if get_user.pin_trial > 0:
                get_user.pin_trial = 5
                self.db.session.add(get_user)
                self.db.session.commit()
                login_message = { "success": "pin correct" }
            else:
                login_message = { "failure": "You have exceed 5 times pin trial, please reset your pin" }

        else:
            reduce_user_pin = self.user.query.filter_by(email=email).first()
            if reduce_user_pin.pin_trial > 0:
                reduce_user_pin.pin_trial -= 1
                self.db.session.add(reduce_user_pin)
                self.db.session.commit()
                login_message = { "failure": f"Wrong pin, you pin trial remains {reduce_user_pin.pin_trial}" }
            else:
                login_message = { "failure": "You have exceed 5 times pin trial, login please reset your pin" }

        print(login_message)
        return login_message
        


    def pin_login(self, pinfunc):
        def pin_wrapper():
            pin_data = pinfunc()
            pin = pin_data["pin"]
            email = pin_data["email"]

            get_user = self.user.query.filter_by(email=email, pin=pin).first()
            if get_user:
                # login
                if get_user.pin_trial > 0:
                    auth_token = uuid.uuid4()
                    token = self.token(token=auth_token, user_id = get_user.id, dateTime=time.time())
                    self.db.session.add(token)
                    get_user.pin_trial = 5
                    self.db.session.add(get_user)
                    self.db.session.commit()
                    login_message = { "success": "you have logged in successfully" , "token": token.token }
                else:
                    login_message = { "failure": "You have exceed 5 times pin trial, login with email and password" }

            else:
                reduce_user_pin = self.user.query.filter_by(email=email).first()
                if reduce_user_pin.pin_trial > 0:
                    reduce_user_pin.pin_trial -= 1
                    self.db.session.add(reduce_user_pin)
                    self.db.session.commit()
                    login_message = { "failure": f"Wrong pin, you pin trial remains {reduce_user_pin.pin_trial}" }
                else:
                    login_message = { "failure": "You have exceed 5 times pin trial, login with email and password" }

            return jsonify(login_message)
            
        return pin_wrapper

    def sign_up(self, sign_up_data):
        def signup():
            signup_data = sign_up_data()
            user_name = signup_data['username'] 
            password = signup_data['password']
            phone = signup_data['phone'] 
            email = signup_data['email']
            check_if_user_exist = self.user.query.filter_by(email=email).all()
            if len(check_if_user_exist) > 0:
                signup_message = {"failure": "The email you are trying use already exist"}
            else:
                password = md5_crypt.hash(password)
                check_for_first_user = len(self.user.query.all())
                if not check_for_first_user:
                    user = self.user(username=user_name, is_admin=True, phone=phone, email=email, password=password)
                else:
                    user = self.user(username=user_name, is_admin=False, phone=phone, email=email, password=password)

                self.db.session.add(user)
                self.db.session.commit()
                
                signup_message = {"success": "you have sign up successfully"}
            return jsonify(signup_message)
        return signup

    def authenticate(self):
        if 'Auth' in request.headers:
            token = request.headers['Auth']
            # print(request.headers)
            # print(token)
            check = self.db.session.query(self.token).filter_by(token=token).first()
            if check:
                is_token_active = (check.dateTime + self.token_expiry_time) > time.time()
                # print(is_token_active)
                # print(self.token_expiry_time)
                # print(check.dateTime + self.token_expiry_time)
                # print(time.time())
                if is_token_active:
                    user_response = self.user_schema.dump(check.user)
                    auth_message = {"success": "you have sign up successfully", "user_response": user_response}
                else:
                    self.db.session.delete(check)
                    self.db.session.commit()
                    auth_message = {"failure": "please login or signup"}
            else:
                auth_message = {"failure": "please login or signup"}
        else:
            auth_message = {"failure": "please login or signup"}
        return auth_message
        