from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import PasswordField, StringField, SubmitField, FileField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from wtforms.widgets import TextArea

from .. import db
from ..models import Role, User, Exercise, Medication, Nutrition, Plan


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

class ChangePlanForm(Form):
    plan = QuerySelectField(
        'New plan type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Plan).order_by('name'))
    submit = SubmitField('Update plan')

class InviteUserForm(Form):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    plan = QuerySelectField(
        'Plan type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Plan).order_by('name'))
    # first_name = StringField(
        # 'First name', validators=[InputRequired(), Length(1, 64)])
    # last_name = StringField(
        # 'Last name', validators=[InputRequired(), Length(1, 64)])
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
    days = SelectMultipleField('Day(s) of the week to do this exercise', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
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
    url_list = StringField(
        'URL List', validators=[Length(0, 10000)],
        widget=TextArea())
    days = SelectMultipleField('Day(s) of the week to do this exercise', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
    submit = SubmitField('Save Exercise')


class MedicationForm(Form):
    name = StringField(
        'Medication Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Medication Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    dosage = StringField(
        'Medication Dosage', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    days = SelectMultipleField('Day(s) of the week to take medication', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
    submit = SubmitField('Add Medication')


class EditMedicationForm(Form):
    name = StringField(
        'Medication Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Medication Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    dosage = StringField(
        'Medication Dosage', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    days = SelectMultipleField('Day(s) of the week to take medication', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
    submit = SubmitField('Edit Exercise')


class NutritionForm(Form):
    name = StringField(
        'Food Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Food Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    days = SelectMultipleField('Day(s) of the week to eat this food', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
    submit = SubmitField('Add Food')


class EditNutritionForm(Form):
    name = StringField(
        'Nutrition Name', validators=[InputRequired(), Length(1, 1000)])
    description = StringField(
        'Nutrition Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    files = FileField()
    url_list = StringField(
        'URL List', validators=[Length(0, 10000)],
        widget=TextArea())
    days = SelectMultipleField('Day(s) of the week to eat this food', validators=[InputRequired()],
            choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday'),
                ('S', 'Saturday'), ('U', 'Sunday')])
    submit = SubmitField('Save Food')


class PlanForm(Form):
    name = StringField(
            'Plan Name', validators=[InputRequired(), Length(1, 64)])
    exercise_description = StringField(
        'Exercise Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    exercise_link = StringField(
        'Exercise Survey Link', validators=[Length(1, 1000)])
    exercise_components = QuerySelectMultipleField(
        'Exercise Components',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Exercise).order_by('name'))
    medication_description = StringField(
        'Medication Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    medication_link = StringField(
        'Medication Survey Link', validators=[Length(1, 1000)])
    medication_components = QuerySelectMultipleField(
        'Medication Components',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Medication).order_by('name'))
    nutrition_description = StringField(
        'Nutrition Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    nutrition_link = StringField(
        'Nutrition Survey Link', validators=[Length(1, 1000)])
    nutrition_components = QuerySelectMultipleField(
        'Nutrition Components',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Nutrition).order_by('name'))
    pain_description = StringField(
        'Pain Survey Description', validators=[InputRequired(), Length(1, 10000)],
        widget=TextArea())
    pain_link = StringField(
        'Pain Survey Link', validators=[InputRequired(), Length(1, 1000)])
    submit = SubmitField('Add Plan')
