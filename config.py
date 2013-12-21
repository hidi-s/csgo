import os

# Config file, put all your keys and passwords and whatnot in here
DB_URI = os.environ.get("DATABASE_URL", "sqlite:///my_app.db")
SECRET_KEY = "this should be a secret"
UPLOADS_DEFAULT_DEST = "./static/"
MAIL_PORT = 465,
MAIL_SERVER = "smtp.googlemail.com",
MAIL_USE_TLS = False,
MAIL_USE_SSL = True,
MAIL_USERNAME = 'dslevi12@gmail.com',
MAIL_PASSWORD = 'lovehina',