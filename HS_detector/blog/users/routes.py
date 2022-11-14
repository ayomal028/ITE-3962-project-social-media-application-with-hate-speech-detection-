from flask import render_template, url_for, flash, redirect, request, Blueprint
from blog import  db, bcrypt
from blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from blog.users.utils import save_picture, send_reset_email
from flask_mail import Mail

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #adding a user to db throgh reg form
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #hashing the pw
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        #check if the user exists in db
        user = User.query.filter_by(email=form.email.data).first()
        #if user exists check whether the entered password match with the one in the db. if exists, login. else, error
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            #redirect to the next page if next page exists.(get() will fetch the value from next parameter in URL)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required #to access the account, a user has to be logged in
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file #change the picture name to the one defined in the save_picture function
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account information have been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET': #current user info should be displayed on the account page
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form = form)

    
#show all posts of a single user
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)#pagination and post order
    return render_template('user_posts.html', posts=posts, user=user)



#request a email to reset the password
@users.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Password Reset', form=form)

#actual reset password
@users.route("/reset_password/<token>", methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        #adding a user to db throgh reg form
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #hashing the pw
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you can login now', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Password Reset', form=form)