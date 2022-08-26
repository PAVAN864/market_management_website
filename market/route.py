from market import app
from flask import render_template, redirect,url_for,flash, request
from market.models import Item, User
from market.forms import Register,Login,Purchase,Sell
from market import db
from flask_login import login_user, login_required , logout_user, current_user

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')
#About Page
@app.route('/about/<name>')
def about(name):
    return render_template('about.html')+name

#Market Page
@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    purchase= Purchase()
    item = Item()
    if request.method == 'POST':
        purchased_item=request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name= purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(item):
                p_item_object.buy(current_user)
                flash(f'Congratulations! You purchased {p_item_object.name} for {p_item_object.price}',category='success')
            else:
                flash(f'Unfortunately, You dont have enough money to buy {p_item_object.name}',category='danger')
    #return redirect(url_for('home'))
    if request.method=='GET':
        items = Item.query.filter_by(owner=None)
        return render_template('market.html',items= items,purchase= purchase)

@app.route('/templates/register',methods=['GET','POST'])
def register_page():
    forms= Register()
    if forms.validate_on_submit():
        user_to_create = User(username=forms.username.data,email=forms.email.data,password=forms.password.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username[1]}",category='success')
        return redirect(url_for('market_page'))
    if(forms.errors!={}):
        for err_msg in forms.errors.values():
            flash(f'There was an error with creating user: {err_msg}',category='danger')
    return render_template('register.html',form=forms)

@app.route('/templates/login',methods=['GET','POST'])
def login_page():
    form = Login()
    if form.validate_on_submit():
        attempted_user= User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
            login_user(attempted_user)
            flash(f'Successfully logged in as {attempted_user.username}',category="success")
            return redirect(url_for('market_page'))
        else:
            flash('Username and Password do not match',category='failure')

    return render_template('login.html',form=form)

@app.route('/templates/logout',methods=['GET','POST'])
def logout_page():
    logout_user()
    flash("Successfully logged out!!",category='info')
    return redirect(url_for('home'))
