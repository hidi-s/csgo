from flask import Flask, render_template, redirect, request, g, session, url_for, flash, send_from_directory
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.markdown import Markdown
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from flask.ext.mail import Mail, Message 
# import config
# import forms
import model
from model import User, Campaign, Supporters, Comments 

import os 
import random
import string 
from datetime import datetime

from csgo import app

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
