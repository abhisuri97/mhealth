from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from wtforms.widgets import TextArea

from .. import db
from ..models import Role, User, Exercise


class ChangeUserEmailForm(Form):
    email = EmailField(
        'New email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(Form):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(), EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class ExerciseForm(Form):
    name = StringField(
        'Exercise Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Exercise Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    submit = SubmitField('Add Exercise')

    def validate_name(self, field):
        if Exercise.query.filter_by(name=field.data).first():
            raise ValidationError('Exercise name already registered.')

class EditExerciseForm(Form):
    name = StringField(
        'Exercise Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Exercise Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    files = FileField()
    submit = SubmitField('Edit Exercise')