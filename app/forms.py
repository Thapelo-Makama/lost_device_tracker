from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                    TextAreaField, SelectField, DateTimeField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    id_number = StringField('SA ID Number', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, f):
        if User.query.filter_by(username=f.data).first():
            raise ValidationError('Username taken.')
    def validate_email(self, f):
        if User.query.filter_by(email=f.data).first():
            raise ValidationError('Email already registered.')

class DeviceForm(FlaskForm):
    device_name = StringField('Device Name', validators=[DataRequired()])
    device_type = SelectField('Device Type', choices=[
        ('smartphone','Smartphone'),('laptop','Laptop'),('tablet','Tablet'),
        ('smartwatch','Smartwatch'),('camera','Camera'),('gaming_console','Gaming Console'),
        ('headphones','Headphones'),('other','Other')], validators=[DataRequired()])
    imei_number = StringField('IMEI Number (for phones)')
    serial_number = StringField('Serial Number')
    brand = StringField('Brand')
    model = StringField('Model')
    color = StringField('Color')
    description = TextAreaField('Description')
    lost_date = DateTimeField('Date Lost', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    lost_location = StringField('Location Lost')
    is_lost = BooleanField('Mark as Lost')
    submit = SubmitField('Register Device')

class EvidenceForm(FlaskForm):
    evidence_type = SelectField('Evidence Type', choices=[
        ('affidavit','Affidavit of Ownership'),
        ('receipt','Purchase Receipt'),
        ('photo','Photo of Device'),
        ('id_document','ID Document'),
        ('warranty','Warranty Card'),
        ('other','Other')], validators=[DataRequired()])
    file = FileField('Upload File', validators=[
        FileRequired(),
        FileAllowed(['pdf','png','jpg','jpeg','doc','docx','mp4','mov'], 'File type not allowed')])
    description = TextAreaField('Description')
    submit = SubmitField('Upload Evidence')

class MessageForm(FlaskForm):
    subject = StringField('Subject')
    content = TextAreaField('Message', validators=[DataRequired()])
    is_private = BooleanField('Private Message', default=True)
    recipient_id = SelectField('Recipient', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ReportForm(FlaskForm):
    description = TextAreaField('Description of Incident', validators=[DataRequired()])
    police_station = StringField('Police Station')
    police_report_number = StringField('Police Report Number')
    officer_name = StringField('Officer Name')
    officer_contact = StringField('Officer Contact')
    submit = SubmitField('File Report')

class AdminEvidenceForm(FlaskForm):
    is_verified = BooleanField('Verified')
    admin_notes = TextAreaField('Admin Notes')
    submit = SubmitField('Update')
