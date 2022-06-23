import email
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms.widgets import TextArea
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class NamerForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("Enter your email", validators=[
                        DataRequired(), Email()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    favorite_anime = StringField("Favorite Anime", validators=[
                                 Length(min=0, max=20)])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo(
        'password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField(
        "Confirm Password", validators=[DataRequired()])
    profile_pic = FileField("Profile pic")
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
