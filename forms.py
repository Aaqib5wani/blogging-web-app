from flask_wtf import FlaskForm
from wtforms import Form,validators,StringField,SubmitField,PasswordField,TextField,TextAreaField
from wtforms.validators import DataRequired,length,Email,EqualTo,email_validator



class Register(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),length(max=20,min=2)])
    name = StringField('Name', validators=[DataRequired(), length(max=40, min=2)])
    email = StringField('Email', validators=[DataRequired(), length(max=50, min=2),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm_password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Submit')




class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), length(max=50, min=2),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Submit')

class Enter_post(FlaskForm):
    title = StringField('title',validators=[DataRequired(),length(max=100,min=5)])
    subtitle = StringField('subtitle', validators=[DataRequired(), length(max=50, min=2)])
    content = TextAreaField('content', validators=[DataRequired(), length(max=10000, min=10)])
    submit=SubmitField('Submit')