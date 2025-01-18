import datetime
from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from . import bp, login_manager, mail, avatars # Assuming your main app file is your_app.py
from ..forms import LoginForm, RegistrationForm, PasswordResetRequestForm, ResetPasswordForm # Assuming your forms are in your_app/forms.py
from ..models import User, db
import hashlib
from flask_mail import Message


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_verification_email(user):
    user.verify_token = user.get_verify_token()
    user.verify_token_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.session.commit()

    msg = Message('Verify Your Email', sender='noreply@example.com', recipients=[user.email])
    msg.body = f'''
            To verify your email, visit the following link: {url_for('auth.verify_email', token=user.verify_token, _external=True)}

            If you did not make this request, simply ignore this email.
            '''
    mail.send(msg)

def send_password_reset_email(user):
    user.reset_token = user.get_reset_token()
    user.reset_token_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.session.commit()

    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
            {url_for('auth.reset_password_with_token', token=user.reset_token, _external=True)}

            If you did not make this request, simply ignore this email and no changes will be made.
            '''
    mail.send(msg)

def create_user_from_registration_form(form):
    new_user = User(
        username=form.username.data,
        email=form.email.data,
        icon=avatars.gravatar(size=30, hash=hashlib.md5(form.email.data.lower().encode('utf-8')).hexdigest())
    )
    new_user.set_password(form.password.data)
    db.session.add(new_user)
    db.session.commit()
    return new_user

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect if already logged in
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.verified:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=form.remember.data)

                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    return redirect(url_for('main.index'))  # Replace 'main.index' with your main page

                return redirect(next_page)

            else:
                send_verification_email(user)
                flash('A verification email has been sent to your email address. Please verify your account.',
                      category='info')
                return redirect(url_for('auth.login'))
        else:
            flash('Incorrect email or password.', category='error')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirect if already logged in
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            print(f"user_failed {form.email.data}")
            flash('Email already exists.', category='error')
        else:
            user = create_user_from_registration_form(form)
            send_verification_email(user)
            flash('Account created! Please check your email to verify your account.', category='success')
            print(f"user_created {form.email.data}")
            return redirect(url_for('auth.login'))
    return render_template('registration.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Replace 'main.index' with your main page
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password.', category='info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', form=form)

@bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    user = User.verify_user_token(token)
    if user:
        if user.verify_token_expiration is None or user.verify_token_expiration > datetime.datetime.utcnow():
            user.verified = True
            user.verify_token = None
            user.verify_token_expiration = None
            db.session.commit()
            flash('Your email has been verified. You can now log in.', category='success')
        else:
            flash('The verification link has expired. Please request a new one.', category='warning')
    else:
        flash('Invalid verification link.', category='error')
    return redirect(url_for('auth.login'))

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    user = User.verify_reset_token(token)
    if user:
        if user.reset_token_expiration is None or user.reset_token_expiration > datetime.datetime.utcnow():
            form = ResetPasswordForm()
            if form.validate_on_submit():
                user.set_password(form.password.data)
                user.reset_token = None
                user.reset_token_expiration = None
                db.session.commit()
                flash('Your password has been reset. You can now log in.', category='success')
                return redirect(url_for('auth.login'))
            return render_template('reset_password.html', form=form)
        else:
            flash('The reset link has expired. Please request a new one.', category='warning')
            return redirect(url_for('auth.reset_password_request'))
    else:
        flash('Invalid reset link.', category='error')
        return redirect(url_for('auth.reset_password_request'))


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password_request.html', form=form)