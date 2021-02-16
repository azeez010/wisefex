from flask_wtf import FlaskForm
from models import User
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email
from wtforms import StringField, HiddenField, IntegerField, PasswordField, SubmitField, TextAreaField
import re
# from flask import request, jsonify, send_from_directory, render_template, flash, redirect, url_for
# import wtforms

# print(dir(wtforms))

class MyForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    bank_name = StringField('Bank name')
    account_name = StringField('Account Name')
    account_number = StringField('Account number')
    bank_name = StringField('Bank name')
    bitcoin_wallet = StringField('Bitcoin wallet')
    email = StringField('email', validators=[DataRequired(), Email()])
    mobile_number = StringField('Mobile number', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField("Sign up")
    referral = HiddenField()

    def validate_password(self, password):
        print(self.referral.data)
        if len(password.data) < 7 or len(password.data) > 15:
            raise ValidationError("password must be greater 7 and less than 15")
    
    def validate_confirm_password(self, confirm_password):
        print(self.confirm_password.data, self.password.data)
        if self.confirm_password.data != self.password.data:
            raise ValidationError("password and confirm password must be the same")
    
    def validate_mobile_number(self, mobile_number):
        all_number = len(re.findall("[0-9]", mobile_number.data))
        if len(mobile_number.data) != all_number:
            raise ValidationError("Mobile number must be digits or numbers")

        if len(mobile_number.data) != 11:
            raise ValidationError("Mobile number must be 11 digits")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail already exists")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists")


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Log in")
    
class RequestForm(FlaskForm):
    request = TextAreaField('Make requests', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class TestimonyForm(FlaskForm):
    testimony = TextAreaField('Testimony', validators=[DataRequired()])
    submit = SubmitField("Submit")

class passwordResetForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if not user:
            raise ValidationError("E-mail doesn't exist, create an account instead")

class passwordReset(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])
    token = PasswordField('Password Recovery Token', validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_password(self, password):
        if len(password.data) < 7 or len(password.data) > 15:
            raise ValidationError("password must be greater 7 and less than 15")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail already exists")


# class AdminSettings(FlaskForm):
#     account_name = StringField('account_name', validators=[DataRequired()])
#     account_name = StringField('account_name', validators=[DataRequired()])
#     account_name = StringField('account_name', validators=[DataRequired()])
#     account_name = StringField('account_name', validators=[DataRequired()])
#     account_name = StringField('account_name', validators=[DataRequired()])
    
    
#     email = StringField('email', validators=[DataRequired(), Email()])
#     password = PasswordField('password', validators=[DataRequired()])
#     submit = SubmitField("Sign up")
    
#     def validate_password(self, password):
#         if len(password.data) < 7 or len(password.data) > 15:
#             raise ValidationError("password must be greater 7 and less than 15")
    
#     # def validate_phone(self, phone):
#     #     all_number = len(re.findall("[0-9]", phone.data))
#     #     if len(phone.data) != all_number:
#     #         raise ValidationError("Phone must be digits or numbers")

#     #     if len(phone.data) != 11:
#     #         raise ValidationError("Phone must be 11 digits")

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user:
#             raise ValidationError("E-mail already exists")

#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError("Username already exists")
