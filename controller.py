from flask import Flask, render_template, redirect, request, g, session, url_for, flash, send_from_directory
from model import User, Campaign, Supporters, Comments 
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.markdown import Markdown
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES 
import config
import forms
import model
import os 
import random
import string 


app = Flask(__name__)
app.config.from_object(config)


images = UploadSet('images', IMAGES)
configure_uploads(app, (images))

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#Testing upload functionality 
@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST" and 'image' in request.files:
        print "saving image"
        filename = images.save(request.files['image'])
    elif request.method == "POST" :
        print "no image on request"
    else:
        print "render uploads"
        return render_template("upload.html")
    
    return redirect(url_for("browse"))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADS_DEFAULT_DEST'],
                               filename)

#login and logout stuff here
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def authenticate():
    if request.form['btn'] == "login": 
        form_login = forms.LoginForm(request.form)
        if not form_login.validate():
            flash("Incorrect username or password") 
            return render_template("base.html")

        email = form_login.email.data
        password = form_login.password.data

        user = User.query.filter_by(email=email).first()

        if not user or not user.authenticate(password):
            flash("Incorrect username or password")         
            return render_template("login.html")

        login_user(user)

        return redirect(request.args.get("next", url_for("index")))

    elif request.form['btn'] == "register": 
        password = request.form.get("password")
        email = request.form.get("email")
        first_name=request.form.get("first_name")
        last_name=request.form.get("last_name")
        new_user = User(email=email)
        new_user.set_password(password=password)
        new_user.first_name=first_name
        new_user.last_name=last_name
        model.session.add(new_user)
        model.session.commit()

        return redirect(url_for("browse"))

    elif request.form['btn'] == "fb_login":

        return redirect(url_for("browse"))

@app.route("/")
def index():
    # testvar = request.args.get("arg", "empty")
    # print testvar   
    return render_template("index.html")


@app.route("/about")
def view_about():
    return render_template("about.html")

#Browse displays basic info for all users, including their phot
@app.route("/browse")
def browse():
    print session.keys()
    user_list = User.query.filter_by(approved=False).all()
    return render_template("browse.html", user_list=user_list)

#Profile displays detailed info for one user and displays their video 
#TODO fix links for this from profile
@app.route("/campaign/<int:id>")
def view_profile(id):
    user = User.query.get(id)
    return render_template("campaign.html", user=user)


#Create_info is a form which stores information about a user's campaign
@app.route("/create_info")
def create_info():
    return render_template("create_info2.html")

@app.route("/create_info", methods=["POST"])
def post_create_info():
    # if current_user.is_anonymous == True: 
    user_id = session.get('user_id')
    video = request.form.get("video_url")
    tagline = request.form.get("tagline")
    description = request.form.get("description")
    goal = int(request.form.get("goal"))
    twitter = request.form.get("twitter")
    github = request.form.get("github")
    linkedin = request.form.get("linkedin")
    deadline_date = request.form.get("deadline")
    # strftime for deadline 

    print "user_id", session.get("user_id")

    campaign = Campaign(
        video=video,
        user_id=user_id,
        description=description,
        goal=goal,
        deadline_date=deadline_date,
        tagline=tagline
        )
    print campaign.video 
    model.session.add(campaign)
    model.session.commit()
    print campaign 
    model.session.refresh(campaign)
    print campaign 

    if 'image' in request.files:
        random_string = ''.join(random.sample(string.letters,5))
        image_id = "%s.jpg" % random_string
        print image_id
        filename = images.save(request.files['image'], folder=None, name=image_id) 
        print "saving image"
        print current_user 
           #SAVE THE FILENAME AS THE USER ID. 
        current_user.img_2 = image_id  
        model.session.add(current_user)
        model.session.commit()
        print filename 
        print session.get('user_id')
    else:
        print "no image"

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
