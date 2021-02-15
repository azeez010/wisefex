from flask import Flask, request, jsonify, send_from_directory, render_template, flash, redirect, url_for
from passlib.hash import md5_crypt
from forms import MyForm, LoginForm, TestimonyForm 
from models import User, Confirm_mail, Admin_tasks, Withdrawal, Investments, app, db, LoginManager, login_required, login_user, logout_user, current_user, current_user
from is_safe_url import is_safe_url
from schema import user_schema
from flask_humanize import Humanize
from datetime import datetime
from mailing_server import mail_folks
import boto3, botocore, time, hashlib, hmac, json, os, shutil, mailing_server, basic_auth, string, random
from time import time
from math import ceil
import requests, uuid
from mailing_server import mail_folks, Message, mail
from blockcypher import get_transaction_details

humanize = Humanize(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "please login"
login_manager.login_message_category = "info"

# confirm_payment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Redirect / to home
@app.route("/", methods=["GET"])
def no_route():
    return redirect(url_for("home"))
    
@app.route("/home", methods=["GET"])
def home():
    context = {}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    return render_template("home.html", context=context)


@app.route("/search-admin", methods=["GET"])
@login_required
def search():
    name = request.args.get("q")
    users = User.query.filter(User.username.like(f"%{name}%")).all()
    users_list = user_schema.dump(users)
    return {"users": users_list}

@app.route("/my-admin", methods=["GET"])
@login_required
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users)
    
@app.route("/user-settings", methods=["GET", "POST"])
@login_required
def user_settings():
    if request.method == "POST":
        user = User.query.filter_by(username=current_user.username).first()
        account_name = request.form.get("account_name")
        account_number = request.form.get("account_number")
        bank_name = request.form.get("bank_name")
        mobile_number = request.form.get("mobile_number")
        country = request.form.get("country")
        bitcoin_addr = request.form.get("bitcoin_addr")
        user.account_name = account_name
        user.account_number = account_number
        user.bank_name = bank_name
        user.mobile_number = mobile_number
        user.bitcoin_addr = bitcoin_addr
        
        db.session.commit()
        
        flash("You have successfully updated your account details")
        return redirect(url_for('user_settings'))
    else:
        username = request.args.get("username")
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template("user_settings.html", context=context)


@app.route("/admin-settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    if request.method == "POST":
        print(request.form)
        all_data = request.form
        for data in all_data:
            value = request.form.get(data)
            print(data, value)
            admin_task = Admin_tasks.query.filter_by(key=data).first()
            admin_task.value = value

        db.session.commit()
        
        flash("You have successfully updated your Administrative Capabilities")
        return redirect(url_for('admin_settings'))
        # return redirect(url_for('user_settings'))
    else:
        admin_abilities = Admin_tasks.query.all()
        if not admin_abilities:
            init_admin_abilities()

        username = request.args.get("username")
        user = User.query.filter_by(username=username)
        
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value

        # theme = Admin_tasks.query.filter_by(key="theme").first()
        # print(context)

        # account_name = user.account_name
        # account_number = user.account_number
        # bank_name = user.account_number
        return render_template("admin_settings.html", context=context)

def init_admin_abilities():
    abilities = [["theme", "blue"], ["account_number", ""], ["account_name", ""], ["bank_name", ""], ["bitcoin_addr", ""], ["ref_bonus", "2"], ["invest_percent", "35"], ["min_naira", "10000"], ["max_naira", "500000"], ["min_bitcoin", "50"], ["max_bitcoin", "1000"], ["min_ref_withdraw", "2000"], ["no_concurrent_invest", "2"], ["lock_invest_time", ""], ["lock_invest_hours", "24"], ["no_of_invest_day", "10"], ["name_of_invest", ""], ["url_of_invest", "" ]]
    for ability in abilities:
        admin_task = Admin_tasks(key=f"{ability[0]}", value=f"{ability[1]}")
        db.session.add(admin_task)
    db.session.commit()


@app.route("/manage-user", methods=["GET", "POST"])
@login_required
def manage_user():
    id =  request.args.get("id")
    user = User.query.get(id)
    if request.method == "POST":
        update_pay = request.form.get("pay")
        update_admin = request.form.get("admin")
        update_building = request.form.get("building")
        user.is_admin = bool(update_admin)
            
        db.session.commit()

        flash(f"You have successfully update {user.username}'s ability")
        return redirect(f"/manage-user?id={user.id}")

    return render_template("manage_user.html", user=user)

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    your_investments = Investments.query.filter_by(user_id=current_user.id).order_by(Investments.date.desc())
    # lock investment
    lock_investment = False
    lock_invest_time = Admin_tasks.query.filter_by(key="lock_invest_time").first()
    
    context = {"your_investments": your_investments }
    
    if lock_invest_time.value:
        if time() >= float(lock_invest_time.value):
            lock_investment = False
        else:
            date = datetime.fromtimestamp(int(float(lock_invest_time.value)))
            lock_investment = True
            print(date)
            context['date'] = date
            context['lock_investment'] = lock_investment

    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    context['min_ref_withdraw'] = int(context['min_ref_withdraw'])
    context['bonus_wallet'] = int(current_user.bonus_wallet)


    return render_template("dashboard.html", context=context)


@app.route("/confirm-payment", methods=["POST"])
@login_required
def confirm_payment():
    if request.method == "POST":
        db.session.commit()
        # print(request.form, request.files)
        # print(current_user.username)
        investment_id = request.form.get("investment_id")
        print(investment_id)
        description = request.form.get("description")
        investment = Investments.query.filter_by(id=investment_id).first()
        amount = investment.capital
        cur_type = request.form.get("cur_type")
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        
        if cur_type == "naira":
            if int(context["min_naira"]) > int(amount):
                flash(f"#{amount}, You are trying to invest is too low, the minimum is {context['min_naira']}")
                return redirect(url_for('pending_deposit'))     
            elif int(context["max_naira"]) < int(amount):
                flash(f"#{amount}, You are trying to invest is too high, the maximum is {context['max_naira']}")
                return redirect(url_for('pending_deposit'))     
            
            # expected_return = (int(context['invest_percent']) / 100 * int(amount)) + int(amount)
            # investment = Investments(paid=True, invest_type="naira", user_id=current_user.id, capital=amount, expected_return=expected_return)
            
            # db.session.commit()
            
            proof = request.files.get('proof')
            if proof:
                filename = proof.filename
                file_ext = filename.split('.')[1]
                storage_key = os.environ.get("aws_key")
                storage_secret = os.environ.get("aws_secret")
                storage_bucket = "wisefex"
                conn = boto3.client(
                    's3',
                    aws_access_key_id=storage_key,
                    aws_secret_access_key=storage_secret
                    )

                key = f'wisefex/{filename}'
                params={'Bucket': storage_bucket, 'Key': key}
                investment.proof = conn.generate_presigned_url(ClientMethod="get_object", Params=params, ExpiresIn="80000")
                investment.proof_key = key
                conn.upload_fileobj(proof, storage_bucket, key)
                
            investment.pending = False
            investment.paid = True
            investment.description = description
            db.session.commit()
        
        elif cur_type == "bitcoin":
            if int(context["min_bitcoin"]) > int(amount):
                flash(f"#{amount}, You are trying to invest is too low, the minimum is {context['min_bitcoin']}")
                return redirect(url_for('pending_deposit'))     
            elif int(context["max_bitcoin"]) < int(amount):
                flash(f"#{amount}, You are trying to invest is too high, the maximum is {context['max_bitcoin']}")
                return redirect(url_for('pending_deposit'))     
                    
            proof = request.form.get("proof")
            try:
                verify_transaction = get_transaction_details(f'{proof}')
                print(verify_transaction)
            except Exception as exc:
                print(exc)

            if verify_transaction.get("block_hash"):    
                # investment = Investments(paid=True, invest_type="bitcoin", user_id=current_user.id, capital=amount, expected_return=expected_return)
                cur_time = time()
                no_of_invest_day = int(context['no_of_invest_day'])
                no_of_invest_day *= 86400
                return_date = cur_time + no_of_invest_day
                investment.date = cur_time 
                investment.approved = True
                investment.return_date = return_date
            
                db.session.add(investment)
                db.session.commit()
                flash("Your Paid Claim has successfully been submit, wait for admin's Claim")
            else:
                flash("The transaction ID you input is invalid")
        # , currency=cur_type, amount=amount
        return redirect(url_for('pending_deposit')) 
    # context = {} dataslid
    # all_tasks = Admin_tasks.query.all()
    # for task in all_tasks:
    #     context[f"{task.key}"] = task.value
    
    # return render_template("dashboard.html", context=context)

@app.route("/invest", methods=["GET", "POST"])
@login_required
def investment():
    cur_type = request.args.get("currency") 
    amount = request.args.get("amount") 
    
    context = {"cur_type": cur_type, "amount": amount}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    invest_by_user = Investments.query.filter_by(user_id=current_user.id).all()
    no_invest_by_user = len(invest_by_user)

    if no_invest_by_user >= int(context["no_concurrent_invest"]):
        flash(f"The maximum number of investment you can have at a time is {context['no_concurrent_invest']}")
        return redirect(url_for('dashboard'))
    
    if cur_type == "naira":
        if int(context["min_naira"]) > int(amount):
            flash(f"#{amount}, You are trying to invest is too low, the minimum is {context['min_naira']}")
            return redirect(url_for('dashboard'))     
        elif int(context["max_naira"]) < int(amount):
            flash(f"#{amount}, You are trying to invest is too high, the maximum is {context['max_naira']}")
            return redirect(url_for('dashboard'))     
        
        expected_return = (int(context['invest_percent']) / 100 * int(amount)) + int(amount)
        investment = Investments(pending=True, reject=False, invest_type="naira", user_id=current_user.id, capital=amount, expected_return=expected_return)
            
        print(investment.id)
        db.session.add(investment)
        db.session.commit()
        investment_id = investment.id
        print(investment_id)
        context["investment_id"] = investment_id 

    
    elif cur_type == "bitcoin":
        if int(context["min_bitcoin"]) > int(amount):
            flash(f"#{amount}, You are trying to invest is too low, the minimum is {context['min_bitcoin']}")
            return redirect(url_for('dashboard'))     
        elif int(context["max_bitcoin"]) < int(amount):
            flash(f"#{amount}, You are trying to invest is too high, the maximum is {context['max_bitcoin']}")
            return redirect(url_for('dashboard'))     
        
        expected_return = (int(context['invest_percent']) / 100 * int(amount)) + int(amount)
        investment = Investments(pending=True, reject=False, invest_type="bitcoin", user_id=current_user.id, capital=amount, expected_return=expected_return)
            
        print(investment.id)
        db.session.add(investment)
        db.session.commit()
        investment_id = investment.id
        print(investment_id)
        context["investment_id"] = investment_id 



    return render_template("investment.html", context=context, amount=amount, cur_type=cur_type)

@app.route("/my-investment", methods=["GET", "POST"])
@login_required
def my_investment():
    # user_id = current_user.user_id
    investment_id = request.args.get("id") 
    my_invest = Investments.query.get(investment_id)
    if my_invest.return_date:
        time_left = ceil((int(my_invest.return_date) - time()) / 86400)# - 9
        time_left_in_perc = time_left * 10
        # print(time_left, int(my_invest.return_date) - int(my_invest.date), int(my_invest.return_date), int(my_invest.date))
        day_what = 100 - time_left_in_perc
        context = { "my_invest": my_invest, "time_left": time_left_in_perc, "day_what_perc": day_what, "day_what": int(day_what / 10) }
    else:
        context = { "my_invest": my_invest}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    context["invest_day"] = int(context["no_of_invest_day"])
    context["capital"] = int(my_invest.capital)
    context["expected_return"] = int(my_invest.expected_return)
    flash("withdraw buttons will appear when the time has reached")
    return render_template("investment_page.html", context=context )

@app.route("/deposit-admin-approval", methods=["GET", "POST"])
@login_required
def deposit_admin_approval():
    if request.method == "POST":
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        
        date = request.form.get('date')
        invest_id = request.form.get('id') 
        user_id = current_user.id
        print(user_id)
        
        if request.form.get('choice') == "True":
            cur_time = time()
            no_of_invest_day = int(context['no_of_invest_day'])
            no_of_invest_day *= 86400
            return_date = cur_time + no_of_invest_day
            investment = Investments.query.filter_by(id=invest_id).first()
            # print(invest)
            investment.reject = False
            investment.approved = True            
            investment.date = cur_time
            investment.return_date = return_date
            # Give bonus to owners
            bonus = investment.capital * (int(context["ref_bonus"]) / 100)
            investor = User.query.get(user_id)
            ref_name = investor.referral
            referral = User.query.filter_by(username=ref_name).first()
            print(referral)
            if referral:
                prev_wallet_val = int(referral.bonus_wallet)
                referral.bonus_wallet = prev_wallet_val + bonus
                print(prev_wallet_val, bonus, bonus + prev_wallet_val, ref_name)

            # print()
            db.session.commit()
             
        elif request.form.get('choice') == "False":
            investment = Investments.query.filter_by(date=date, user_id=user_id).first()
            investment.reject = True
            investment.approve = False
            investment.date = time()
            db.session.commit()

        group_chat_id = "-1001318559427"
        token = os.getenv("tele_api")
        tele_text = f'Hello {investor.username},\nYour N{investor.capital} DEPOSIT is confirmed.\n\nCONGRATULATIONS IN ADVANCE!\n\nTHANK YOU FOR INVESTING WITH US.'
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={group_chat_id}&text={tele_text}")
       
        return redirect(url_for('deposit_admin_approval'))
    else:
        unapproved = Investments.query.filter_by(paid=True, approved=False, reject=False) 
        context = {"unapproved": unapproved}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        

        return render_template("admin_unapproved.html", context=context)


@app.route("/withdraw-investment", methods=["GET", "POST"])
@login_required
def withdraw_investment():
    invest_id = request.form.get("invest_id")
    invest_type = request.form.get("type")
    
    context = {}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
        
    invest = Investments.query.get(invest_id)
    if invest_type == "profit":
        funds = invest.expected_return - invest.capital  
        withdraw = Withdrawal(investment_id=invest.id, amount=funds, withdraw_type=invest_type)
        invest.profit_withdraw = True
        print(invest.profit_withdraw)
        db.session.add(withdraw)
        db.session.commit()
            
        flash(f'You have successfully request to withdraw your profit which is #{funds}, You will be credited anytime soon')
        return redirect(url_for('my_investment', id=invest.id))
        
    elif invest_type == "capital":
        funds = invest.capital
        withdraw = Withdrawal(investment_id=invest.id, amount=funds, withdraw_type=invest_type)
        invest.capital_withdraw = True
        db.session.add(withdraw)
        db.session.commit()
        flash(f'You have successfully request to withdraw your profit which is #{funds}, You will be credited anytime soon')
        return redirect(url_for('my_investment', id=invest.id))

    elif invest_type == "bonus":
        funds = current_user.bonus_wallet
        if int(funds) >= int(context["min_ref_withdraw"]):
            funds = current_user.bonus_wallet
            withdraw = Withdrawal(investment_id=1, amount=funds, withdraw_type="bonus")
            current_user.bonus_wallet = "0"
            db.session.add(withdraw)
            db.session.commit()
            flash(f'You have successfully request to withdraw your bonus which is #{funds}, You will be credited anytime soon')
            return redirect(url_for('dashboard'))        
        else:
            flash(f"You don't have up to #{context['min_ref_withdraw']} Refer enough people to have above #{context['min_ref_withdraw']} in your bonus wallet")
            return redirect(url_for('dashboard'))        
    

@app.route("/withdraw-admin-approval", methods=["GET", "POST"])
@login_required
def withdraw_admin_approval():
    if request.method == "POST":
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        
        date = request.form.get('date')
        user_id = request.form.get('id') 
        invest_id = request.form.get('invest_id') 
        withdraw = Withdrawal.query.filter_by(investment_id = invest_id).first()

        if request.form.get('choice') == "True":
            withdraw.paid = True            
            db.session.commit()
            flash(f"You have successfully confirmed that {withdraw.investment.user.username}'s withdrawal")
            if withdraw.withdraw_type == "capital" or withdraw.withdraw_type == "profit":
                group_chat_id = "-1001318559427"
                token = os.getenv("tele_api")
                tele_text = f'CONGRATULATIONS {withdraw.investment.user.account_name}, Your (₦{int(withdraw.amount):,}.00) WITHDRAWAL HAS BEEN PROCESSED AND SENT TO YOUR REGISTERED {withdraw.investment.user.bank_name} ACCOUNT\n\nTHANK YOU FOR INVESTING WITH US.'
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={group_chat_id}&text={tele_text}")
            
            elif withdraw.withdraw_type == "bonus":
                group_chat_id = "-1001318559427"
                token = os.getenv("tele_api")
                tele_text = f'HELLO {withdraw.investment.user.account_name.upper()}, YOUR REFERRAL PAYMENT OF ₦{int(withdraw.amount):,} HAS BEEN PAID TO YOUR ACCOUNT.'
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={group_chat_id}&text={tele_text}")

            else:
                group_chat_id = "-1001318559427"
                token = os.getenv("tele_api")
                tele_text = f'CONGRATULATIONS {withdraw.investment.user.account_name}, Your (${int(withdraw.amount):,}) WITHDRAWAL HAS BEEN PROCESSED AND SENT TO YOUR REGISTERED BTC WALLET\n\nTHANK YOU FOR INVESTING WITH US.'
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={group_chat_id}&text={tele_text}")
       
            return redirect(url_for('withdraw_admin_approval'))
        
        elif request.form.get('choice') == "False":

            flash(f"You have successfully declined {withdraw.investment.user.username}'s withdrawal")
            return redirect(url_for('withdraw_admin_approval'))
    else:
        unpaid_withdraw = Withdrawal.query.filter_by(paid=False).order_by(Withdrawal.time.desc())
        context = {"unpaid": unpaid_withdraw}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        

        return render_template("admin_withdrawal.html", context=context)


@app.route("/admin-stats-and-lock", methods=["GET", "POST"])
@login_required
def admin_stats_and_lock():
    if request.method == "POST":
        if request.form.get("type") == 'lock':
            lock_time = Admin_tasks.query.filter_by(key="lock_invest_hours").first().value
            lock_invest_time = Admin_tasks.query.filter_by(key="lock_invest_time").first()
            new_lock_time = time() + (float(lock_time) * 3600)
            lock_invest_time.value = new_lock_time
            db.session.commit()
            flash(f'You have successfully locked this platform for {lock_time} hours')
            return redirect(url_for('admin_stats_and_lock'))
        elif request.form.get('type') == "unlock":
            lock_invest_time = Admin_tasks.query.filter_by(key="lock_invest_time").first()
            lock_invest_time.value = ""
            db.session.commit()
            
            flash(f'You have successfully unlocked this platform for fresh investments')
            return redirect(url_for('admin_stats_and_lock'))
    else:
        all_user = len(User.query.all())
        all_deposit = len(Investments.query.all())
        all_withdrawal = len(Withdrawal.query.all())
        all_money_made = Investments.query.filter_by(paid=True)
        all_money_paid_bonus = Withdrawal.query.filter_by(paid=True, withdraw_type="bonus")
        all_money_paid_capital = Withdrawal.query.filter_by(paid=True, withdraw_type="capital")
        all_money_paid_profit = Withdrawal.query.filter_by(paid=True, withdraw_type="profit")
        money_made = 0
        money_paid_bonus = 0
        money_paid_capital = 0
        money_paid_profit = 0
        # Total deposits
        for each_invest in all_money_made:
            money_made += int(each_invest.capital) 
        # Total withdraw bonus
        for each_paid_bonus in all_money_paid_bonus:
            money_paid_bonus += int(each_paid_bonus.amount) 
        # Total withdraw capital
        for each_paid_capital in all_money_paid_capital:
            money_paid_capital += int(each_paid_capital.amount)
        # Total withdraw profit
        for each_paid_profit in all_money_paid_profit:
            money_paid_profit += int(each_paid_profit.amount)

        # lock investment
        lock_investment = False
        lock_invest_time = Admin_tasks.query.filter_by(key="lock_invest_time").first()
        theme = Admin_tasks.query.filter_by(key="theme").first().value
        if lock_invest_time.value:
            if time() >= float(lock_invest_time.value):
                lock_investment = False
            else:
                lock_investment = True

        
        total_cash_paid = money_paid_bonus + money_paid_capital + money_paid_profit
        context = {
            "total_cash_paid": total_cash_paid,
            "money_made": money_made,
            "money_paid_capital": money_paid_capital,
            "money_paid_bonus": money_paid_bonus,
            "money_paid_profit": money_paid_profit,
            "all_user": all_user,
            "all_deposit": all_deposit,
            "all_withdrawal": all_withdrawal,
            "lock_investment": lock_investment,
            "theme": theme
        }
        
        return render_template("admin_lock_and_stats.html", context=context)
   

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and md5_crypt.verify(password, user.password):
            login_user(user)
            next_page = request.args.get("next")
            is_safe_url(next_page, request.url)
            if is_safe_url(next_page, request.url):
                return redirect(next_page)
            return redirect("/dashboard") 
        else:
            flash("e-mail or password is incorrect")
            return redirect("/login")
    else:
        context = {}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template("login.html", form=form, context=context)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = MyForm()
    if request.method == "POST" and form.validate_on_submit():
        referral = request.form.get('ref')
        email = form.email.data
        password = form.password.data
        username = form.username.data
        bank_name = form.bank_name.data
        account_name = form.account_name.data
        account_number = form.account_number.data
        bitcoin_wallet = form.bitcoin_wallet.data
        mobile_number = form.mobile_number.data
        country = request.form.get("country")

        # password = md5_crypt.hash(password)
        user_info = json.dumps({
            "username": username,
            "email": email,
            "password": password,
            "bank_name": bank_name,
            "account_name": account_name,
            "account_number": account_number,
            "mobile_number": mobile_number,
            "bitcoin_wallet": bitcoin_wallet,
            "country": country,
            "referral": referral
        })

        random_generated = uuid.uuid4()
        expired_token = time() + (int(app.config['TOKEN_EXPIRY_TIME']) * 60 )
        # print((int(app.config['TOKEN_EXPIRY_TIME']) * 60 ))
        
        msg = Message('Confirmation code from wisefex', sender = 'wisefexinvestment11@gmail.com', recipients = [email])
        msg.body = f"the confirmation code is {random_generated}"
        mail.send(msg)
        
        confirm_user = Confirm_mail(user_details=user_info, token=random_generated, mail=email, dateTime=expired_token )
        db.session.add(confirm_user)
        db.session.commit()
        
        return redirect(url_for("enter_token"))
        # password = form.password.data
        # username = form.username.data
        # email = form.email.data
        # referral = request.form.get('ref')
        # # phone = form.phone.data
        # password = md5_crypt.hash(password)
        # check_for_first_user = len(User.query.all())
        # if not check_for_first_user:
        #     user = User(username=username, is_admin=True, email=email, password=password, referral=referral)
        # else:
        #     user = User(username=username, is_admin=False, email=email, password=password, referral=referral)
        
        # db.session.add(user)
        # db.session.commit()
        
        # flash("You have signed up successfully")    
        # return redirect('/login')
    else:
        ref = request.args.get("ref")
        context = {"ref": ref}
        all_tasks = Admin_tasks.query.all()
        for task in all_tasks:
            context[f"{task.key}"] = task.value
        return render_template("sign_up.html", form=form, context=context)

@app.route("/logout")
def logout():
    logout_user()
    flash("You've logged out successfully, do visit soon")
    return redirect(url_for("login"))


# @app.context_processor
# def context_processor():
#     request_alert = Make_request.query.filter_by(not_seen=True).all()
#     alert = False
#     if request_alert:
#         alert = True
#     return dict(alert=alert)

@app.route("/pending-deposit", methods=["GET", "POST"])
@login_required
def pending_deposit():
    pending_deposit = Investments.query.filter_by(user_id=current_user.id, reject=False).order_by(Investments.date.desc()).all()
    # pending=True,
    context = {"pending": pending_deposit}
    # print(len(pending_deposit))
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    return render_template("pending_deposit.html", context=context)

@app.route("/pending-withdraw", methods=["GET", "POST"])
@login_required
def pending_withdraw():
    pending_withdrawal = Withdrawal.query.order_by(Withdrawal.time.desc()).all()
    your_withdraw = []
    print(len(pending_withdrawal))
    for your_pending_withdraw in pending_withdrawal:
        if your_pending_withdraw.investment.user.id == current_user.id:
            your_withdraw.append(your_pending_withdraw)
        print(your_pending_withdraw.investment.user.id)
        print(current_user.id)
    
    context = {"pending": your_withdraw}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    return render_template("pending_withdrawals.html", context=context)

@app.route("/your-referrals", methods=["GET", "POST"])
@login_required
def your_referrals():
    your_referral = User.query.filter_by(referral=current_user.username).all()
    print(len(your_referral))
    context = {"referrals": your_referral}
    all_tasks = Admin_tasks.query.all()
    for task in all_tasks:
        context[f"{task.key}"] = task.value
    
    return render_template("referrals.html", context=context)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        email = request.form.get("email")
        message = request.form.get("message")
        
        msg = Message('Mail from Wisefex User', sender = 'wisefexinvestment11@gmail.com', recipients = [email])
        msg.body = message
        mail.send(msg)

if __name__  == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")