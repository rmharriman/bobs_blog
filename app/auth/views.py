from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
                   PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..email import send_email


@auth.before_app_request
def before_request():
    # intercepts users who have not confirmed but can log in, does nothing otherwise
    if current_user.is_authenticated:
        # This intercepts all requests, so good place to call ping and update last seen
        current_user.ping()
        if not current_user.confirmed \
           and request.endpoint != "static" \
           and request.endpoint[:5] != "auth.":
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect("main.index")
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    # Executes on a properly submitted form (POST)
    if form.validate_on_submit():
        # begin authentication by trying to load user by email
        user = User.query.filter_by(email=form.email.data).first()
        # if user is not found or password check fails, the user is not logged in 
        if user is not None and user.verify_password(form.password.data):
            # Records user as logged in for the user session
            # A True (or checked remember me) causes a long term cookie to be set in the client browser
            # A False value will have the user log in again if the window is closed
            login_user(user, form.remember_me.data)
            # 2 destinations for a logged in user
            # if form was presented bc the user tried to access a protected url:
            #### Flask-login stores the url in the next query string arg, else to the main page
            return redirect(request.args.get("next") or url_for("main.index"))
        # incorrect password attempt renders a message and presents the form for the user to retry
        flash("Invalid username or password")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    # Removes and resets the user's session
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        # Need to manually commit as users are only assigned an id after committing
        db.session.commit()
        # Generate token is a user method because it needs access to the ID
        # in order to encrypt it in the token itself
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account", "auth/email/confirm", user=user, token=token)
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
    

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    # Current user is provided by the flask-login via the login_required decorator
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirm Your Account", "auth/email/confirm", user=current_user, token=token)
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Your password has been updated")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Reset Your Password",
                       "auth/email/reset_password",
                       user=user, token=token,
                       next=request.args.get("next"))
        flash("An email with instructions to reset your password has been sent to you.")
    return render_template("auth/reset_password.html", form=form)
            
            
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
    
    
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
    