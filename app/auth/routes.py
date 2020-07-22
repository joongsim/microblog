from datetime import datetime

from flask import flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_babel import _, get_locale
from guess_language import guess_language
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import (EditProfileForm, EmptyForm, LoginForm, PostForm,
    RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm)
from app.models import Post, User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Return user to index if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Query users with matching username
        # Using first() because usernames are unique
        user = User.query.filter_by(username=form.username.data).first()
        # If user does not exist or password is incorrect, flash error
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # next page redirect
        # get next page url from user request
        next_page = request.args.get('next')
        # redirect to index if not set or set to full URL with domain name
        # second case necessary to prevent attackers from redirecting to
        # malicious site
        # url_parse() returns tuple including netloc (eg example.com)
        # if netloc is not empty, redirect to index
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for instructions on resetting your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
        title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())
