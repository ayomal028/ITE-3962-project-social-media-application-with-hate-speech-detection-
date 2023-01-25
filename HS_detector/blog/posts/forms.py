from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', widget=TextArea())
    picture = FileField('browse', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')