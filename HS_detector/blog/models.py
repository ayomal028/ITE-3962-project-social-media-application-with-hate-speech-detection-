# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import abort
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from datetime import datetime, timedelta
from blog import db, login_manager, app
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

#reloading a user from the session 
#decorated function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

admin = Admin(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) 
    #posts attribute sets the relationship with the Post table(1 to many)
    comments = db.relationship('Comment', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)

    #setting a secret key with an expiration time and returing a token 
    def get_reset_token(self, expires_sec=1800):
         s= Serializer(app.config['SECRET_KEY'], expires_sec)
         return s.dumps({'user_id':self.id}).decode('utf-8')

    #verify the pw reset token and creates a serializer and load the token and returns the user id
    @staticmethod
    def verify_reset_token(token):
        s= Serializer(app.config['SECRET_KEY'])
        #using try/catch because if the user with this token does not exist, it will crash the server. we dont want that to happen
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    post_image = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    is_offensive = db.Column(db.Boolean, default=False)
    is_clean = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_liked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin == True:
                return current_user.is_authenticated
            else:
                return abort(404)
        else:
            return abort(404)
    def not_auth(self):
        return "You are not autherized to proceed further!"


admin.add_view(Controller(User, db.session))
admin.add_view(Controller(Post, db.session))
admin.add_view(Controller(Comment, db.session))
admin.add_view(Controller(Like, db.session))