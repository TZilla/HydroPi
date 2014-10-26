from flask.ext.wtf import Form
from WebServer import mongo
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, SelectField,BooleanField
from wtforms import widgets
from wtforms import validators,ValidationError
import hashlib, uuid
    
class ContactForm(Form):
    name = TextField("Name",  [validators.Required("Please enter your name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."),validators.Email("Please enter your email address.")])
    subject = TextField("Subject",  [validators.Required("Please enter a subject.")])
    message = TextAreaField("Message",  [validators.Required("Please enter a message.")])
    submit = SubmitField("Send")
    
class NewListForm(Form):
    name = TextField("List Name",  [validators.Required("Please enter a list name.")])
    public = BooleanField("Public",  [])
    description = TextField("Description",  [])
    elements = TextAreaField("Elements",  [validators.Required("Please enter list elements, separated by commas")])
    submit = SubmitField("Create")
        
class NewEventForm(Form):
    name = TextField("Event Name",  [validators.Required("Please enter an event name.")])
    description = TextField("Description",  [])
    submit = SubmitField("Create") 

class EditEventForm(Form):
    name = TextField("Event Name",  [validators.Required("Please enter an event name.")])
    description = TextField("Description",  [])
    list=SelectField("List", [validators.Required("Please select a list")])
    submit = SubmitField("Create")  
        
class EditListForm(Form):
    name = TextField("List Name",  [validators.Required("Please enter a list name.")])
    public = BooleanField("Public",  [])
    description = TextField("Description",  [])
    elements = TextAreaField("Elements",  [validators.Required("Please enter list elements, separated by commas")])
    submit = SubmitField("Save")
    
class RegistrationForm(Form):
    username = TextField("Username",  [validators.Required("Please enter a Username name.")])
    firstname = TextField("First name",  [validators.Required("Please enter your First name.")])
    lastname = TextField("Last name",  [validators.Required("Please enter your Last name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."),validators.Email("Please enter your email address.")])
    password = PasswordField("Password",  [validators.Required("Please enter a password.")])
    password1 = PasswordField("Password",  [validators.Required("Please validate the password")])
    submit = SubmitField("Create Account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
 
    def validate(self):
        
        if not Form.validate(self):
            return False
        valid=True #assume success
        email = mongo.db.users.find({'email':self.email.data.lower()}).count()
        username = mongo.db.users.find({'username':self.username.data.lower()}).count()

        if email>0:
            self.email.errors.append("That email is already taken")
            valid=False
        if username>0:
            self.username.errors.append("That username is already taken")
            valid=False
        if(len(self.password.data)<8):
            self.password.errors.append("Passwords must be at least 8 characters long")
            self.password1.errors.append("")
            valid=False
        else:
            self.salt = uuid.uuid4().bytes
            self.password.data = hashlib.sha512(self.password.data.encode('utf-8') + self.salt).digest()
            self.password1.data = hashlib.sha512(self.password1.data.encode('utf-8') + self.salt).digest()
        if(self.password.data!=self.password1.data):
            self.password.errors.append("The passwords do not match")
            self.password1.errors.append("")
            valid=False
        return valid
            
class SignInForm(Form):
    username = TextField("Username",  [validators.Required("Please enter your name.")])
    password = PasswordField("Password",  [validators.Required("Please enter your password.")])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
 
    def validate(self):
        
        if not Form.validate(self):
            return False
        valid=True #assume success
        user = mongo.db.users.find_one({'username':self.username.data.lower()})
        
        if not user:
            self.username.errors.append("That user does not exist")
            valid=False
        else:
            salt=user['salt']
            password=hashlib.sha512(self.password.data.encode('utf-8')+salt).digest()
            if(password!=user['password']):
                self.username.errors.append("Invalid password")
                valid=False
        return valid
    
class ProfileEdit(Form):
    name = TextField("Name",  [])
    image = TextField("Image",  [])
    submit = SubmitField("Send")