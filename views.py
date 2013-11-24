from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Post
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.markdown import Markdown
import config
import forms
import model
import os 

UPLOAD_FOLDER = './static/img/UPLOADS'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
   
    
# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


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
        return render_template("base_template.html")

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
    user_list = User.query.all()
    return render_template("browse.html", users=user_list)

@app.route("/profile")
def view_profile():
    user_list = User.query.all()
    return render_template("profile.html", users=user_list)

@app.route("/create_profile")
def create_profile():
    return render_template("create_profile.html")

@app.route("/create_profile", methods=["POST"])
def post_create_profile():
    password = request.form.get("password")
    email = request.form.get("email")
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    print password
    print email    
    print first_name
    print last_name                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    new_user = User(email=email)
    new_user.set_password(password=password)
    new_user.first_name=first_name
    new_user.last_name=last_name
    model.session.add(new_user)
    model.session.commit()

    model.session.refresh(new_user)
    return redirect(url_for("create_info"))

@app.route("/create_info")
def create_info():
    return render_template("create_info2.html")

@app.route("/create_info", methods=["POST"])
def post_create_info():
    # if current_user.is_anonymous == True: 
    user_id = session.get('user_id')
    current_user.video = request.form.get("video_url")
    current_user.tagline = request.form.get("tagline")
    current_user.description = request.form.get("description")
    current_user.goal = request.form.get("goal")
    current_user.twitter = request.form.get("twitter")
    current_user.github = request.form.get("github")
    current_user.linkedin = request.form.get("linkedin")
    current_user.deadline_date = request.form.get("deadline")
    model.session.add(current_user)
    model.session.commit()
    model.session.refresh(current_user)

    return redirect(url_for("browse"))


    # else: 
        # return render_template(url_for("create_profile")
    # print request.form.get("video_url")
    # print request.form.get("tagline")
    # print request.form.get("description")
    # print request.form.get("goal")
    # print request.form.get("twitter")
    # print request.form.get("github")
    # print request.form.get("linkedin")
    # print request.form.get("deadline")
    # print request.form.get("img_1")




   
if __name__ == "__main__":
    app.run(debug=True)
