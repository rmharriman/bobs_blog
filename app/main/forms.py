from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, Email
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Two forms are required for editing user profiles as the one for admins includes more fields
class EditProfileForm(FlaskForm):
    name = StringField("Real name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")
    
class EditProfileAdminForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField("Username", validators=[
        DataRequired(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
                                    "Usernames must have only letters, numbers, dots or underscores")])
    confirmed = BooleanField("Confirmed")
    # SelectField is a wrapper for HTML Select form control (implements dropdown list)
    # Default storage type is string
    role = SelectField("Role", coerce=int)
    name = StringField("Real name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")    
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # An instance of a SelectField must set the choices attribute with all options
        ## List of tuples: (id, text to display)
        self.role.choices = [(role.id, role.name) 
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    # Validation must detect changes to the fields (unlike when user registers)
    def validate_email(self, field):
        if field.data != self.user.email and \
               User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if field.data != self.user.username and \
               User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")
