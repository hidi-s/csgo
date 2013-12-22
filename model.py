import config
import bcrypt
from datetime import datetime
import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

# These are imported for uploading files
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

engine = create_engine(config.DB_URI, echo=False)
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))


Base = declarative_base()
Base.query = session.query_property()

class Contribution(Base):
    __tablename__ = "contributions"
    id = Column(Integer, primary_key=True)
    supporter_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    payment_type = Column(String(64), nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password

class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)
    first_name = Column(String(16), nullable=False)
    last_name = Column(String(24), nullable=False)
    description = Column(String(128), nullable=True)
    link = Column(String(128), nullable=True)
    linkedin = Column(String(128), nullable=True)
    github = Column(String(128), nullable=True)
    twitter = Column(String(128), nullable=True)
    img = Column(String(128), default="default.jpg")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    approved = Column(Boolean, default=False)
    campaign = relationship("Campaign", uselist=False)
    kudoses = relationship("Kudoses", uselist=True)
    supporting = relationship("Supporters", uselist=True)
    campaignCreator = Column(Boolean, default=True)
    contributions = relationship("Contribution", uselist=True)
  
    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    video = Column(String(128))
    deadline = Column(DateTime, nullable=False, default=datetime.now)
    #Float for money/bitcoin fractions?
    goal = Column(Integer, nullable=True)
    tagline = Column(String(128), nullable=True)
    description = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    approved = Column(Boolean, default=False)
    kudoses = relationship("Kudoses", uselist=True)
    user = relationship("User", backref="user")
    supporting = relationship("Supporters", uselist=True)
    contributors = relationship("Contribution", uselist=True)

    def time_remaining(self, currentDate):
        remaining = self.deadline - currentDate
        days = remaining.days
        if days <= 0:
            return "Completed"
        return days
        #Fix this later
        # if days == 1:
        #     return [1, remaining.seconds]
        # return [0, days]

    def numKudoses(self):
        return len(self.kudoses)

    def addKudos(self, user_id):
        if user_id == None:
            return False

        for kudos in self.kudoses:
            if kudos.user_id == user_id:
                return False

        newKudos = Kudoses(campaign_id=self.id, user_id=user_id)
        session.add(newKudos)
        session.commit()
        return True

    def hasKudosed(self, user_id):
        if user_id == None:
            return False
        for kudos in self.kudoses:
            if kudos.user_id == user_id:
                return True
        return False

    def removeKudos(self, user_id):
        delKudo = Kudoses.query.filter_by(user_id=user_id).one()
        session.delete(delKudo)
        session.commit()

class Kudoses(Base):
    __tablename__ = "kudoses"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

class Supporters(Base):
    __tablename__ = "supporters"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))

class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(String, nullable=True)
    kudos = Column(Boolean, default=False) 
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    posted_at = Column(DateTime, nullable=True, default=None)
    user = relationship("User", backref="comments")

    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign = relationship("Campaign", backref=backref("comments", uselist=True))

# This creates the tables. drop_all is a hack to delete tables and recreate them. Needs a more permanent solution. 
def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def seed():
    user = User(email="dslevi12@gmail.com", first_name="Danielle", last_name="Levi", 
        linkedin="www.linkedin.com/in/dslevi/", github="https://github.com/dslevi", 
        twitter="https://twitter.com/DaniSLevi", img="danielle.jpg", campaignCreator=True)
    user.set_password('python')
    session.add(user)

    camp = Campaign(video="http://www.youtube.com/watch?feature=player_detailpage&v=0byNU3RHhr8",
        goal=500, tagline="I want to learn how to program", description="I am a super cool programmer.",
        user_id=user.id)

    user.campaign = camp

    session.add(camp)
    session.add(user)
    session.commit()

    supporter1 = User(email="tester1@gmail.com", first_name="Tester", last_name="One", 
        link="www.hackbright.com", img="default.jpg", campaignCreator=False)
    supporter1.set_password('tester')
    session.add(supporter1)

    supporter2 = User(email="tester2@gmail.com", first_name="Tester", last_name="Two", 
        link="www.hackbright.com", img="default.jpg", campaignCreator=False)
    supporter2.set_password('tester')
    session.add(supporter2)

    supporter3 = User(email="tester3@gmail.com", first_name="Tester", last_name="Three", 
        link="www.hackbright.com", img="default.jpg", campaignCreator=False)
    supporter3.set_password('tester')
    session.add(supporter3)

    supporter4 = User(email="tester4@gmail.com", first_name="Tester", last_name="Four", 
        link="www.hackbright.com", img="default.jpg", campaignCreator=False)
    supporter4.set_password('tester')
    session.add(supporter4)

    session.commit()

    print supporter1.id, camp.id
    s1 = Supporters(user_id=supporter1.id, campaign_id=camp.id)
    session.add(s1)

    s2 = Supporters(user_id=supporter2.id, campaign_id=camp.id)
    session.add(s2)

    s3 = Supporters(user_id=supporter3.id, campaign_id=camp.id)
    session.add(s3)

    s4 = Supporters(user_id=supporter4.id, campaign_id=camp.id)
    session.add(s4)

    admin1 = Admin(username="dslevi")
    admin1.set_password('master')

    admin2 = Admin(username="hidi")
    admin2.set_password('hackbright')

    session.add(admin1)
    session.add(admin2)

    session.commit()
 
if __name__ == "__main__":
    create_tables()
    seed()

