from flask import Flask, render_template, redirect, request, g, session, url_for, flash, send_from_directory
from model import User, Campaign, Supporters, Comments, Contribution
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
from datetime import datetime, date
from itsdangerous import URLSafeSerializer

app = Flask(__name__)
app.config.from_object(config)
mail = Mail(app)

images = UploadSet('images', IMAGES)
configure_uploads(app, (images))

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#login and logout stuff here
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
@login_required
def logout():
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
            return render_template("login.html")

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
        register_Form = forms.RegisterForm(request.form)
        if not register_Form.validate():
            flash("Invalid email")
            return render_template("login.html")
        email = request.form.get("email")
        if User.query.filter_by(email=email).all():
            flash("User email already exists")         
            return render_template("login.html")
        first_name=request.form.get("first_name")
        last_name=request.form.get("last_name")
        creator = bool(request.form.get("role"))
        if not first_name or not last_name:
            flash("Please enter information in all fields")
            return render_template("login.html")
        password = request.form.get("password")
        verify_password = request.form.get("verify")
        if password != verify_password:
            flash("Passwords do not match")
            return render_template("login.html")
        new_user = User(email=email, first_name=first_name, last_name=last_name, campaignCreator=creator)
        new_user.set_password(password=password)
        model.session.add(new_user)
        model.session.commit()

        session['user_id'] = new_user.id
        if creator:
            return redirect(url_for("create_info"))
        return redirect(url_for("create_supporter"))

    elif request.form['btn'] == "fb_login":
        print "AJAX request data:"
        fb_id = request.form.get('fb_id')
        user = User.query.filter_by(fb_id=fb_id).first()
        # If user's fb id exists in database, log in user 
        if user: 
            login_user(user)
            session["user_id"] = user.id

        elif current_user.is_anonymous():
            # create an account based on their FB data
            print "creating a new user for %s" % request.form.get('first_name')
            #img_url = "https://graph.facebook.com/%s/picture?type=small" % fb_id 
            #print img_url
            user = User(
                email=request.form.get('email'),
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                fb_id=fb_id,
            )
            user.set_password('python')
            model.session.add(user)
            model.session.commit()
            session['user_id'] = new_user.id

        elif not current_user.fb_id:
            # make sure we already have their FB ID stored with their account
            current_user.fb_id = fb_id
            model.session.commit()

        return ""

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

def supporter_list(campaign_id):
    d = {}
    supporters = Supporters.query.filter_by(campaign_id=campaign_id)
    for supporter in supporters:
        user = []
        u = User.query.filter_by(id=supporter.user_id).one()
        user.append(u.first_name)
        user.append(u.last_name)
        d[u.id] = user
    return d

@app.route("/campaign/<int:id>")
def view_profile(id):
    campaign = Campaign.query.get(id)
    if session.get('user_id'):
        user_id = session['user_id']
    else:
        user_id = None
    supporters = supporter_list(id)

    raised = 0.0
    if campaign.contributors:
        contributions = campaign.contributors
        for c in contributions:
            raised += (c.amount/100)

    return render_template("campaign.html", raised=raised, campaign=campaign, now=datetime.today(), user_id=user_id, supporters=supporters)

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

@app.route("/create_supporter")
def create_supporter():
    return render_template("create_supporter.html")

@app.route("/create_supporter", methods=["POST"])
def process_supporter():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    user.tagline = request.form.get("tagline")
    user.description = request.form.get("description")
    user.link = request.form.get("link")

    if not request.form.get("image"):
        user.img = "default.jpg"

    if 'image' in request.files:

        random_string = ''.join(random.sample(string.letters,5))
        image_id = "%s.jpg" %(random_string)
     
        filename = images.save(request.files['image'], folder=None, name=image_id) 
        
        user.img = image_id

    model.session.commit()

    return redirect(url_for("browse"))


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
    # video is the raw link from youtube 
    video = request.form.get("video_url")
    video_link_split = video.split("=")
    video_embed = video_link_split[1]
    tagline = request.form.get("tagline")
    description = request.form.get("description")
    goal = request.form.get("goal")
    if not goal or int(goal) < 0 or int(goal) > 500:
        flash("Please enter an appropriate goal")
        return redirect(url_for("create_info"))
    twitter = request.form.get("twitter")
    github = request.form.get("github")
    linkedin = request.form.get("linkedin")
    deadline = request.form.get("deadline")
    if not deadline:
        flash("Please enter a date")
        return redirect(url_for("create_info"))

    campaign = Campaign(
        video=video,
        video_embed = video_embed, 
        user_id=user_id,
        description=description,
        goal=int(goal),
        deadline=datetime.strptime(deadline, "%Y-%m-%d"),
        )

    model.session.add(campaign)
    model.session.commit()

    user = User.query.get(user_id)

    if not request.form.get("image"):
        user.img = "default.jpg"

    if 'image' in request.files:
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

@app.route("/browseSupporters")
def browseSupporters():
    supporters = User.query.filter_by(campaignCreator=False)
    return render_template("browseSupporters.html", supporters=supporters)

def supported_list(user):
    l =[]
    supporting = user.supporting
    for supported in supporting:
        camp = []
        c = Campaign.query.filter_by(id=supported.campaign_id).one()
        u = User.query.get(c.user_id)
        camp.append(c)
        camp.append(u)
        l.append(camp)
    return l

@app.route("/supporter/<supporter_id>")
def display_supporter(supporter_id):
    supporter = User.query.filter_by(id=supporter_id).one()
    supported = supported_list(supporter)
    return render_template("supporters.html", supporter=supporter, supported=supported)

@app.route("/callback", methods=["POST"])
def callback():
    # The request.json is sent from Coinbase to the callback url specified in the merchant settings. 
    coinbase_req = request.json
    order_id = coinbase_req["order"]["id"] 
    # Order status should be "completed" unless something went wrong
    order_status = coinbase_req["order"]["status"]
    # total btc is in satoshis. 
    total_btc = coinbase_req["order"]["total_btc"]["cents"]
    currency = coinbase_req["order"]["total_btc"]["currency_iso"]
    # total native currency in cents. I think this will always be $ for us. 
    total_native_currency = coinbase_req["order"]["total_native"]["cents"]
    native_currency_type = coinbase_req["order"]["total_native"]["currency_iso"]
    # custom_id ties to the code I've put in the html button, which sends the current user id and campaign id. 
    # If a user is not logged in, no user id would be sent, only a campaign id. 
    custom_id= coinbase_req["order"]["custom"]
    custom_id_split = custom_id.split(";")
    campaign_id = custom_id_split[0] 
    user_id = custom_id_split[1]

    contribution = Contribution(
        supporter_id=user_id, 
        campaign_id=campaign_id, 
        payment_type="coinbase", 
        amount=total_native_currency, 
        order_id=order_id, 
        total_btc=total_btc, 
        order_status=order_status)
    model.session.add(contribution)
    model.session.commit() 
    return ""


@app.route("/forgotpassword")
def forgotPassword():
    return render_template("recoverPassword.html")

def create_reset_link(user):
    l = "http://localhost:5001/reset/"
    s = URLSafeSerializer("hacker-bees")
    token = s.dumps(user.id)
    l += token
    user.reset_time = datetime.today()
    return l

@app.route("/recovery", methods=["POST"])
def recoverPassword():
    email = request.form.get("email")
    if email == "":
        flash("Please enter email address")
        return redirect(url_for("forgotPassword"))
    valid = User.query.filter_by(email=email).all()
    if not valid:
        flash("Sorry, that email is not registered.")
        return redirect(url_for("forgotPassword"))
    user = valid[0]
    reset_link = create_reset_link(user)
    msg = Message("Reset HackerBees Password",
        sender= ("HackerBees", "hello.hackerbees@gmail.com"),
        recipients=[email])
    msg.html = """\tHi %s,<br><br>
        Forgot your password? Please click on this link to reset it:<br>
        <a href="%s">Reset HackerBees password</a><br><br>
        Love,<br>
        HackerBees""" % (user.first_name, reset_link)
    with app.app_context():
        mail.send(msg)
    flash("Please check your inbox for instructions to reset your password.")
    return redirect(url_for("login"))

@app.route("/reset/<token>")
def reset_password(token):
    s = URLSafeSerializer("hacker-bees")
    user_id = s.loads(token)
    user = User.query.get(int(user_id))
    expired = datetime.today() - user.reset_time
    if expired.days > 1:
        flash("Password reset link has expired")
        return redirect(url_for("login"))
    return render_template("reset.html", token=token)

@app.route("/reset/<token>", methods=["POST"])
def resetting(token):
    s = URLSafeSerializer("hacker-bees")
    user_id = s.loads(token)
    new = request.form.get("new")
    verify = request.form.get("verify")
    if new != verify:
        flash("Passwords do not match")
        return redirect(url_for("reset_password", token=token))
    user = User.query.get(user_id)
    user.set_password(new)
    user.reset_time = date(2000, 11, 24)

    model.session.commit()
    print user.reset_time
    flash("Password reset")
    return redirect(url_for("login"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
