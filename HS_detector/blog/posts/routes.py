from flask import render_template, url_for, flash, redirect, request,abort,Blueprint
from blog import db
from blog.posts.forms import PostForm
from blog.models import Post
from flask_login import current_user,login_required
from blog.posts.utils import save_picture
from flask_mail import Message
from blog.finalmodel import get_predictions



posts = Blueprint('posts', __name__)

#route for new post
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post = Post(title=form.title.data, content= form.content.data, post_image=picture_file, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))
        else:
            checktitle = get_predictions(request.form['title'])
            checkcontent = get_predictions(request.form['content'])

            if(checktitle == "Hate speech" or checkcontent == "Hate speech"):
                flash("hate!!")
            elif(checktitle == "Offensive Language" or checkcontent == "Offensive Language"):
                flash("offensive!")
                post = Post(checktitle, checkcontent, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
            else:
                flash("clean")
                post = Post(title=form.title.data, content=form.content.data, author=current_user)
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
            # post = Post(title=form.title.data, content=form.content.data, author=current_user)
            # db.session.add(post)
            # db.session.commit()
            # flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))
    #photo = url_for('static', filename = 'post_images/' + post.post_image)
    return render_template('create_post.html',legend="New Post", title="Create a New Post", form=form)

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
        post.title = form.title.data
        post.content = form.content.data
        #post.post_image = form.picture.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
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