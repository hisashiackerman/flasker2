

from flask import Flask, redirect, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date

from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from forms import NamerForm, UserForm, PasswordForm, PostForm, LoginForm, SearchForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create a flask instance
app = Flask(__name__)
ckeditor = CKEditor(app)
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hhcsbnmhlbbwgj:365da5ba7b23bb688815e2172bf4fadbffd8ac5838e929cd56d1b85789b75a18@ec2-3-224-8-189.compute-1.amazonaws.com:5432/d4g40s9e4diqq6'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Cristiano@2021@localhost/our_users'
app.config['SECRET_KEY'] = "e07e5ecdb25b94b71947500f166ce38e"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # Foreign key to link user
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_anime = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)

    password_hash = db.Column(db.String(128))
    # 1 user can have many posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<Name %r>' % self.name


@app.route('/')
@app.route('/home')
def index():
    first_name = "Tim"
    html_stuff = "I like attack on titan"
    favorite_animes = ["Attack on Titan", "Steins;Gate",
                       "Fate", "Rurouni Kenshin", "SpyxFamily"]
    return render_template('index.html', first_name=first_name, html_stuff=html_stuff, favorite_animes=favorite_animes)

# localhost:5000/user/john


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# Create custom error pages
# Invalid url


@app.route('/test_pw', methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # Query usinhg email id
        pw_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_to_check.password_hash, password)
        flash("Name submitted successfully!")
    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(name=form.name.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash('Login successful!!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password! Try again!')
        else:
            flash("User doesn't exist :(")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out! >__<")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/name', methods=["GET", "POST"])
def namepage():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Name submitted successfully!")
    our_users = Users.query.order_by(Users.date_added)
    # return render_template('add_user.html', form=form, name=name, our_users=our_users, id=id)
    return render_template("namepage.html", name=name, form=form, our_users=our_users, id=id)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(
                form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data,
                         favorite_anime=form.favorite_anime.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_anime.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_anime = request.form['favorite_anime']
        name_to_update.profile_pic = request.files['profile_pic']

        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Saving the image
        saver = request.files['profile_pic']

        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            saver.save(os.path.join(
                app.config['UPLOAD_FOLDER']), pic_name)
            flash("User updated successfully!")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

        except:
            flash("Error! Couldn't update Database :(")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users, id=id)

    except:
        flash("Error in deleting user! :(")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users, id=id)
    return render_template('add_user.html', form=form, name=name, our_users=our_users, id=id)


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    poster = current_user.id
    form.author.data = current_user.name
    if form.validate_on_submit():

        post = Posts(title=form.title.data, poster_id=poster, author=current_user.name,
                     content=form.content.data, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        db.session.add(post)
        db.session.commit()

        flash("Post submitted successfully!!")
    return render_template('add_post.html', form=form, poster=poster)


@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        # return render_template('post.html', post=post)
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster.id:
        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug
        return render_template('edit_post.html', form=form, post=post)
    else:
        flash('You cannot edit this post!!')
        return render_template


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash('Post deleted successfully!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash('Oops! There was a problem :(')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash('You cannot delete that post!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    post.searched = form.searched.data

    posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
    posts = posts.order_by(Posts.title).all()
    if form.validate_on_submit():
        return render_template('search.html', form=form, searched=post.searched, posts=posts)


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash("Only admins can access this page! :(")
        return redirect(url_for('dashboard'))


@app.route('/date')
def get_current_date():
    agents = {
        "jett": "duelist",
        "chamber": "sentinel (lol)",
        "sova": "initiator"
    }
    return agents
    return {"Date": date.today()}


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
