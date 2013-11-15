from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Post
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flask.ext.markdown import Markdown
import config
import forms
import model

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    # testvar = request.args.get("arg", "empty")
    posts = Post.query.all()
    # print testvar   
    return render_template("index.html", posts=posts)

@app.route("/post/<int:id>")
def view_post(id):
    post = Post.query.get(id)
    return render_template("post.html", post=post)

@app.route("/post/new")
@login_required
def new_post():
    return render_template("new_post.html")

@app.route("/post/new", methods=["POST"])
@login_required
def create_post():
    form = forms.NewPostForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_post.html")

    post = Post(title=form.title.data, body=form.body.data)
    current_user.posts.append(post) 
    
    model.session.commit()
    model.session.refresh(post)

    return redirect(url_for("view_post", id=post.id))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def authenticate():
    form = forms.LoginForm(request.form)
    if not form.validate():
        flash("Incorrect username or password") 
        return render_template("login.html")

    email = form.email.data
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("login.html")

    login_user(user)
    return redirect(request.args.get("next", url_for("index")))

@app.route("/about")
def view_about():
    return render_template("about.html")

@app.route("/browse")
def browse():
    return render_template("browse.html")

@app.route("/create_profile")
def create_profile():
    return render_template("create_profile.html")

@app.route("/create_profile", methods=["POST"])
def post_create_profile():
    password = request.form.get("password")
    email = request.form.get("email")
     # def add_user(email, password):
    new_user = User(email=email)
    new_user.set_password(password=password)
    model.session.add(new_user)
    model.session.commit()
    print password
    print email
    return redirect(url_for("index"))

@app.route("/create_info")
def create_info():
    return render_template("create_info.html")

@app.route("/create_info", methods=["POST"])
def post_create_info():
    age = request.form.get("age")
    description = request.form.get("description")
    program = request.form.get("program")
    print age
    print description 
    print program 
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
