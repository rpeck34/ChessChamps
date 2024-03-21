from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
#super useful module below
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                #remember=True makes it so the site remembers that this
                #particular user is logged in until they clear their
                #browser history/cache, or until the Flask server is reset
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


#the login_required decorator makes it so user must be logged in
#to reach the page
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        #if user already in database (based on their email)
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        #my own addition, if username is taken
        elif User.query.filter_by(username=username).first():
            flash('username is taken', category='error')
        else:
            #all checks passed, add user to database
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            username=username, password=generate_password_hash(
                            password1, method='scrypt', salt_length=16), num_champs = 0,
                            elo_low = 400, elo_high = 600, selected_champ = '')
            #the above line creates new User instance from models
            #the below line actually adds that User to the database
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
            #after adding User to db, redirict to home page

    return render_template("sign_up.html", user=current_user)
