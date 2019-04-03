from flask import render_template, flash, redirect, url_for, request
from web_app import app, db
from web_app.emails import send_email
from web_app.forms import LoginForm, RegistrationForm
from web_app.models import User
from web_app.token import generate_confirmation_token, confirm_token
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from decorators import check_confirmed
from pika_init import *

_DELIVERY_MODE_PERSISTENT = 2

@app.route('/')
@app.route('/index')
@login_required
@check_confirmed
def index():
    user = {'username': 'Miguel'}
    posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }]
    return render_template('index.html', user=user, title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, confirmed=False)
        user.set_password(form.password.data)

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        message_body = user.email + ';' + confirm_url
        q = get_welcome_queue()
        q.basic_publish(
            exchange = '',
            routing_key = 'email-queue',
            body = message_body,
            properties = pika.BasicProperties(
                delivery_mode = _DELIVERY_MODE_PERSISTENT
            )
        )

        flash('A confirmation email has been sent via email.')

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('unconfirmed'))
    return render_template('register.html', title='Register', form=form)

@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('index'))

@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('index')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')
