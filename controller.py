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
from datetime import datetime


app = Flask(__name__)
app.config.from_object(config)


images = UploadSet('images', IMAGES)
configure_uploads(app, (images))

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#Testing upload functionality 
# @app.route("/upload", methods=["POST", "GET"])
# def upload():
#     if request.method == "POST" and 'image' in request.files:
#         print "saving image"
#         filename = images.save(request.files['image'])
#     elif request.method == "POST" :
#         print "no image on request"
#     else:
#         print "render uploads"
#         return render_template("upload.html")
    
#     return redirect(url_for("browse"))


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOADS_DEFAULT_DEST'],
#                                filename)

#login and logout stuff here
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
    #What does logout user do?
    logout_user()
    session.clear()
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
            return render_template("create_info")

        email = form_login.email.data
        password = form_login.password.data

        user = User.query.filter_by(email=email).first()

        if not user or not user.authenticate(password):
            flash("Incorrect username or password")         
            return render_template("login.html")

        login_user(user)
        session["user_id"] = user.id
        return redirect(request.args.get("next", url_for("browse")))

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

        session['user_id'] = new_user.id
        return redirect(url_for("browse"))

    elif request.form['btn'] == "fb_login":
        fb_name = request.form.get("name")
        if current_user.is_anonymous == False:
            current_user.fb_id = fb_id
            current_user.fb_img_url = "https://graph.facebook.com/%s/picture?type=small" % fb_id 
            print current_user.fb_img_url 
            model.session.commit()
            model.session.refresh()
        return redirect(url_for("browse"))

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def view_about():
    return render_template("about.html")

#Browse displays basic info for all users, including their photo
#users are not displayed in a consistent order
@app.route("/browse")
def browse():
    user_list = User.query.all()
    return render_template("browse.html", user_list=user_list)

#Users only allowed to have one campaign? Using user.id instead of campaign.id
#(perhaps hash campaign number for privacy)
#Created this way, user and campaign must be created at same time in order, if you just switch to campaign.id
#Need to query for this user's campaign

@app.route("/campaign/<int:id>")
def view_profile(id):
    campaign = Campaign.query.get(id)
    if session.get('user_id'):
        user_id = session['user_id']
    else:
        user_id = None
    return render_template("campaign.html", campaign=campaign, now=datetime.today(), user_id=user_id)

#Change this into an AJAX call
#Really weird bug, changes font size after kudosing
@app.route("/campaign/<int:id>/kudos", methods=["POST"])
def give_kudos(id):
    if session.get('user_id'):
        campaign = Campaign.query.get(id)
        action = request.form.get("kudos_button")
        if action == "Give Kudos":
            campaign.addKudos(session['user_id'])
        else:
            campaign.removeKudos(session['user_id'])
        model.session.commit()
    return redirect(url_for("view_profile", id=id))

#Create_info is a form which stores information about a user's campaign
@app.route("/create_info")
def create_info():
    return render_template("create_info2.html")

@app.route("/create_info", methods=["POST", "GET"])
def post_create_info():
    if not session.get('user_id'):
        flash("Please sign in to create a campaign")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    video = request.form.get("video_url")
    tagline = request.form.get("tagline")
    description = request.form.get("description")
    goal = int(request.form.get("goal"))
    twitter = request.form.get("twitter")
    github = request.form.get("github")
    linkedin = request.form.get("linkedin")
    deadline = request.form.get("deadline")
 
    campaign = Campaign(
        video=video,
        user_id=user_id,
        description=description,
        goal=goal,
        deadline=datetime.strptime(deadline, "%Y-%m-%d"),
        )

    model.session.add(campaign)
    model.session.commit()

    user = User.query.get(user_id)

    if 'image' in request.files:
        random_string = ''.join(random.sample(string.letters,5))
        image_id = "%s.jpg" %(random_string)
     
        filename = images.save(request.files['image'], folder=None, name=image_id) 
        print "saving image"
        
        user.img = image_id

    user.tagline=tagline
    user.twitter=twitter
    user.github=github
    user.linkedin=linkedin
    model.session.commit()

    return redirect(url_for("browse"))

   
if __name__ == "__main__":
    app.run(debug=True, port=5001)
