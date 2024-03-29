from flask import render_template, url_for, flash, redirect, request,abort,Blueprint
from blog import db
from blog.posts.forms import PostForm
from blog.models import Post, Reports
from flask_login import current_user,login_required
from blog.posts.utils import save_picture, get_picture_path
from flask_mail import Message
from blog.finalmodel import get_predictions, ocr
from PIL import Image
import cv2
import numpy as np



posts = Blueprint('posts', __name__)

#route for new post
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            checktitle = get_predictions(request.form['title'])
            checkcontent = get_predictions(request.form['content'])
            
            # picture_path = get_picture_path(form.picture.data)
            # pictureText = ocr(picture_path)
            # checkImage = get_predictions(pictureText)

            if(checktitle == 0 or checkcontent == 0 ):
                flash("It looks like you are trying to submit hateful content. We are strictly against online hate speech", 'danger')
            elif(checktitle == 1 or checkcontent == 1 ):
                flash("We strongly recommend not to post offensive content to our platform", 'warning')
                post = Post(title=form.title.data, content=form.content.data, post_image=picture_file, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
            else:
                post = Post(title=form.title.data, content=form.content.data, post_image=picture_file, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
        else:
            checktitle = get_predictions(request.form['title'])
            checkcontent = get_predictions(request.form['content'])

            if(checktitle == 0 or checkcontent == 0):
                flash("It looks like you are trying to submit hateful content. We are strictly against online hate speech", 'danger')
            elif(checktitle == 1 or checkcontent == 1):
                flash("We strongly recommend not to post offensive content to our platform", 'warning')
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
            else:
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
            
        
    #photo = url_for('static', filename = 'post_images/' + post.post_image)
    return render_template('create_post.html',legend="Post Something on BlogWELL", title="Create a New Post", form=form)

#route for view post
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#update post
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            checktitle = get_predictions(request.form['title'])
            checkcontent = get_predictions(request.form['content'])
            
            # picture_path = get_picture_path(form.picture.data)
            # pictureText = ocr(picture_path)
            # checkImage = get_predictions(pictureText)

            if(checktitle == 0 or checkcontent == 0 ):
                flash("It looks like you are trying to submit hateful content. We are strictly against online hate speech", 'danger')
            elif(checktitle == 1 or checkcontent == 1 ):
                flash("We strongly recommend not to post offensive content to our platform", 'warning')
                post = Post(title=form.title.data, content=form.content.data, post_image=picture_file, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
            else:
                post = Post(title=form.title.data, content=form.content.data, post_image=picture_file, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
        else:
            checktitle = get_predictions(request.form['title'])
            checkcontent = get_predictions(request.form['content'])

            if(checktitle == 0 or checkcontent == 0):
                flash("It looks like you are trying to submit hateful content. We are strictly against online hate speech", 'danger')
            elif(checktitle == 1 or checkcontent == 1):
                flash("We strongly recommend not to post offensive content to our platform", 'warning')
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
            else:
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    # if form.validate_on_submit():
    #     post.title = form.title.data
    #     post.content = form.content.data
    #     post.post_image = save_picture(form.picture.data)
    #     db.session.commit()
    #     flash('Your post has been updated', 'success')
    #     return redirect(url_for('posts.post', post_id=post.id))
    # elif request.method == 'GET':
    #     form.title.data = post.title
    #     form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Edit Your Post')
    
#delete post
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))

@posts.route('/post/<int:post_id>/report', methods=['GET', 'POST'])
@login_required
def report_post(post_id):
    post = Post.query.get_or_404(post_id)
    reason = request.form.get('reason')
    description = request.form.get('description')

    if post:
        report = Reports(author=current_user, post_id=post_id, reason=reason, description=description)
        db.session.add(report)
        db.session.commit()
        flash('Your report was sent successfully. We will take the necessary action', 'success')
    else:
        flash('post does not exist', category='error')
    
    return redirect(url_for('posts.post', post_id=post_id))