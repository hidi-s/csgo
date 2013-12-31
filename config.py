import os

# Config file, put all your keys and passwords and whatnot in here
DB_URI = os.environ.get("DATABASE_URL", "sqlite:///my_app.db")
SECRET_KEY = "this should be a secret"
UPLOADS_DEFAULT_DEST = "./static/"
MAIL_PORT = 465
MAIL_SERVER = "smtp.googlemail.com"
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'hello.hackerbees@gmail.com'
MAIL_PASSWORD = 'hackbright'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
