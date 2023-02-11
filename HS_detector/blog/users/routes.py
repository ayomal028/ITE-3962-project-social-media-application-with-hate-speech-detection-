from blog import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from blog import  db, bcrypt
from blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, SearchForm
from blog.models import User, Post, Comment, Like
from flask_login import login_user, current_user, logout_user, login_required
from blog.users.utils import save_picture, send_reset_email
from sqlalchemy import or_, and_
from flask_mail import Mail
from blog.finalmodel import get_predictions

users = Blueprint('users', __name__)

#route for user registration
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

#Create an Admin account
@users.route("/create_admin", methods=['GET', 'POST'])
def create_admin():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #hashing the pw
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=True)
        db.session.add(user)
        db.session.commit()
        flash(f'Admin account has been created! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('admin_register.html', form=form)

#login route
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


#route for account page and update account
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

#show all posts of the current user
@users.route("/user/<string:username>")
def my_posts(current_user):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)#pagination and post order
    return render_template('my_content.html', posts=posts, user=user)

#request a email to reset the password
@users.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #hashing the pw
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you can login now', 'success')
        return redirect(url_for('users.login'))
    return render_template('change_password.html', title='Password Reset', form=form)


# #search
# @users.route('/search', methods=['POST'])
# def search():
#     form = SearchForm()
#     posts = Post.query
#     if form.validate_on_submit():
#         searched = form.searched.data
#         #query the database for posts
#         posts = posts.filter(Post.content.like('%' + searched + '%'))
#         posts = posts.order_by(Post.title).all()
#         return render_template("search.html", form=form, searched=searched, posts=posts)

#search function
@users.route('/search', methods=['POST'])
def search():
    form = SearchForm()

    if form.validate_on_submit():
        search_query = form.searched.data
        posts = Post.query.filter(
            or_(
                Post.title.like('%' + search_query + '%'), Post.content.like('%' + search_query + '%')
            )
        )
        users = User.query.filter(
            User.username.like('%' + search_query + '%')
        )
        return render_template('search.html', form=form, posts=posts, users=users, search_query=search_query)

@app.context_processor
def home():
    form = SearchForm()
    return dict(form=form)


#add comments
@users.route("/comment/<post_id>", methods =["POST"])
@login_required
def comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('there seems to be no comment typed', category='error')
    else:
        post = Post.query.filter_by(id = post_id)
        if post:
            comment_txt = get_predictions(text)
            if comment_txt == 0:
                flash("It looks like you are trying to submit hateful content. We are strictly against online hate speech", 'danger')
            elif comment_txt == 1:
                flash("We strongly recommend not to post offensive content to our platform", 'warning')
                comment = Comment(text = text, author=current_user, post_id=post_id)
                db.session.add(comment)
                db.session.commit()
            else:
                comment = Comment(text = text, author=current_user, post_id=post_id)
                db.session.add(comment)
                db.session.commit()
        else:
            flash('Post does not exist', category='error')    
    
    return redirect(url_for('main.home'))

#delete comments
@users.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('there is no such comment', category='error')
    elif current_user.id != comment.user_id and current_user.id != comment.post.post_id:
        flash('you do not have permission to delete comments', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
    
    return redirect(url_for('main.home'))

#Like posts
# @users.route("/like-post/<post_id>", methods =["GET"] )
# @login_required
# def like(post_id):
#     post = Post.query.filter_by(id=post_id)
#     like = Like.query.filter_by(author=current_user, post_id=post_id).first()

#     if not post:
#         flash('Post does not exists', 'warning')
#     elif like:
#         db.session.delete(like)
#         db.session.commit()
#     else:
#         like = Like(author=current_user, post_id=post_id)
#         db.session.add(like)
#         db.session.commit()

#     return redirect(url_for('main.home'))

@users.route("/like-post/<post_id>", methods =["POST"] )
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'post does not exist'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes":len(post.likes), "liked":current_user in map(lambda x: x.author, post.likes)})





