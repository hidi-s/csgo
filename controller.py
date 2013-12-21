from flask import Flask, render_template, redirect, request, g, session, url_for, flash, send_from_directory
from model import User, Campaign, Supporters, Comments 
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.markdown import Markdown
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from flask.ext.mail import Mail, Message 
import config
import forms
import model
import os 
import random
import string 
from datetime import datetime


app = Flask(__name__)
app.config.from_object(config)
mail = Mail(app)

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
        creator = bool(request.form.get("role"))
        new_user.campaignCreator=creator
        model.session.add(new_user)
        model.session.commit()

        session['user_id'] = new_user.id
        if creator:
            return redirect(url_for("create_info"))
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
@app.route("/browse")
def browse():
    user_list = User.query.filter_by(campaignCreator=True).all()
    return render_template("browse.html", user_list=user_list)

@app.route("/campaign/<int:id>")
def view_profile(id):
    campaign = Campaign.query.get(id)
    if session.get('user_id'):
        user_id = session['user_id']
    else:
        user_id = None
    return render_template("campaign.html", campaign=campaign, now=datetime.today(), user_id=user_id)

#Change this into an AJAX call
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

@app.route("/create_info", methods=["POST"])
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

        print request.files['image']

        random_string = ''.join(random.sample(string.letters,5))
        image_id = "%s.jpg" %(random_string)
     
        filename = images.save(request.files['image'], folder=None, name=image_id) 
        
        user.img = image_id

    user.tagline=tagline
    user.twitter=twitter
    user.github=github
    user.linkedin=linkedin
    model.session.commit()

    return redirect(url_for("browse"))

@app.route("/forgotpassword")
def forgotPassword():
    return render_template("recoverPassword.html")

@app.route("/recovery", methods=["POST"])
def recoverPassword():
    email = request.form.get("email")
    if email == "":
        #fix flash formatting, so its centered
        flash("Please enter email address")
        return redirect(url_for("forgotPassword"))
    valid = User.query.filter_by(email=email).all()
    if not valid:
        flash("Sorry, that email is not registered.")
        return redirect(url_for("forgotPassword"))
    user = valid[0]
    msg = Message("Reset CS:Go Password",
        sender= ("CS:Go", "dslevi12@gmail.com"),
        recipients=[email])
    msg.body = """Hi %s,\n
        Forgot your password?\n
        Please click on this link to reset it.\n
        Love,\n
        CS:Go""" % (user.first_name)
    msg.html = 'body'
    with app.app_context():
        mail.send(msg)
    flash("Please check your inbox for instructions to reset your password.")
    return redirect(url_for("login"))

@app.route("/browseSupporters")
def browseSupporters():
    supporters = User.query.filter_by(campaignCreator=False)
    return render_template("browseSupporters.html", supporters=supporters)

@app.route("/supporter/<supporter_id>")
def display_supporter(supporter_id):
    supporter = User.query.filter_by(id=supporter_id).one()
    return render_template("supporters.html", supporter=supporter)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
