from wtforms import Form, TextField, TextAreaField, PasswordField, validators, RadioField

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])

class RegisterForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])