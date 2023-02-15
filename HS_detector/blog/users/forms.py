from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from blog.models import User


#We can create Forms in flaskform using classes, then the classes will convert into html templates

# registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #validate for existing username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first() #check whether username alreadi exists in db
        if user:
            raise ValidationError('That username is already taken. Please choose a different username')

    #validate for existing emails
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() #check whether username alreadi exists in db
        if user:
            raise ValidationError('That email is already taken. Please choose a different email')

# login form
class LoginForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

# Update account form
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('update')

    #validate for existing username
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first() #check whether username alreadi exists in db
            if user:
                raise ValidationError('That username is already taken. Please choose a different username')

    #validate for existing emails
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first() #check whether username alreadi exists in db
            if user:
                raise ValidationError('That email is already taken. Please choose a different email')


# form to request password reset
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    #validate for existing emails
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() #check whether username alreadi exists in db
        if user is None:
            raise ValidationError('There is no account with that email!')

# password reset form
class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# search form
class SearchForm(FlaskForm):
    searched = StringField('search', validators=[DataRequired()])
    submit = SubmitField('Submit')