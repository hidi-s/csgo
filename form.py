from wtforms import Form, TextField, TextAreaField, PasswordField, validators, RadioField

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])

<<<<<<< HEAD:forms.py
class RegisterForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
=======
class NewPostForm(Form):
    title = TextField("title", [validators.Required()])
    body = TextAreaField("body", [validators.Required()])
>>>>>>> ad0326e64f6d4cedf8f6477c57d833f4ec94454f:form.py
