import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from social_site.db import db_session
from social_site.models import User

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

ph = PasswordHasher()

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    print(request.form)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        password_hash = ph.hash(password)

        error = None

        if not username:
            error = 'Username is required.'
        elif not display_name:
            error = 'Display name is required.'
        elif not email:
            error = 'Please provide an email address.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db_session.add(User(username, display_name, email, password_hash))
                db_session.commit()
            except IntegrityError as e:
                db_session.rollback()

                message = str(e.orig)

                if "user.username" in message:
                    error = "That username is already registered."
                elif "user.email" in message:
                    error = "That email address is already registered."
                else:
                    error = "The user could not be registered."
            except SQLAlchemyError as e:
                print("[ERR] [DB]", e.__cause__)
                error = "Sorry, something went wrong."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

def check_password(user: User, password: str) -> bool:
    try:
        ph.verify(user.password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    
    if ph.check_needs_rehash(user.password_hash):
        try:
            user.password_hash = ph.hash(password)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
            raise

    return True

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db_session.query(User).filter(User.username == username).first()

        if user is None:
            flash("Incorrect username.")
            return render_template("auth/login.html")

        # Verify password is correct
        if not check_password(user, password):
            flash("Incorrect password.")
            return render_template("auth/login.html")

        # Update session
        session.clear()
        session["user_id"] = user.id

        return redirect(url_for("index"))

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Set the user for every session 
# (before_app_request applies it not only to this blueprint but the entire site)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db_session.query(User).filter(User.id == user_id).first()

# Wrapper for views that make them require auth or redirect to login
# So many type: ignore, but there's no docs on what types these take
def login_required(view): # type: ignore
    @functools.wraps(view) # type: ignore
    def wrapped_view(**kwargs): # type: ignore
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs) # type: ignore

    return wrapped_view # type: ignore