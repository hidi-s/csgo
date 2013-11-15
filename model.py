import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URI, echo=False)
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

# Validation lives here. The user table contains email and password info. 
class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)

    posts = relationship("Post", uselist=True)
    profile = relationship("Profile", uselist=True)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password

# The user profile lives here. Eventually I may want to break out the program info and followers/funders to a different table. 
class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(16), nullable=True)
    last_name = Column(String(24), nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String(24), nullable=True)
    tagline = Column(String(128), nullable=True)
    profile_description = Column(String(1024), nullable=True)
    program_type = Column(String(128), nullable=True)
    program = Column(String(128), nullable=True)
    program_cost = Column(Integer, nullable=True)
    interests = Column(String(128), nullable=True)
    aspirations = Column(String(128), nullable=True)
    twitter = Column(String(128))
    github = Column(String(128))
    fb_link = Column(String(128))
    linkedin = Column(String(128))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")

# Once I break out my tables further I will put them here. 
# class Program(Base): 
# class Status(Base):

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    posted_at = Column(DateTime, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")


def create_tables():
    Base.metadata.create_all(engine)
    u = User(email="test@test.com")
    u.set_password("unicorn")
    session.add(u)
    p = Post(title="This is a test post", body="This is the body of a test post.")
    u.posts.append(p)
    session.commit()


    # def add_user(email, password):
    # new_user = User(email=email)
    # new_user.set_password(password=password)
    # session.add(new_user)
    # session.commit()

if __name__ == "__main__":
    create_tables()