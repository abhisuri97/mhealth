from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from flask_rq import get_queue

from . import participant
from .. import db
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, EditableHTML, Plan, PlanComponent, Exercise, Resource, Medication, Nutrition

@participant.route('/')
@login_required
def index():
    """Participant Dashboard"""
    return render_template('participant/index.html')

def get_description(table):
    ret = []
    l = current_user.plan.plan_descriptions
    for x in l:
        if x.type == table:
            return x.description


def get_form_link(table):
    ret = []
    l = current_user.plan.plan_descriptions
    for x in l:
        if x.type == table:
            return x.form_link



@participant.route('/exercises')
@login_required
def exercise_index():
    """Participant Dashboard"""
    exercises = []
    for x in current_user.plan.plan_components:
        if x.fk_table == 'exercise':
            exercises += Exercise.query.filter_by(id=x.fk_id).all()

    resources = [Resource.query.filter_by(fk_id=x.id).filter_by(fk_table='exercise').all() for x in exercises] 
    print(len(exercises))
    print(len(resources))
    return render_template('participant/plan-indexes.html', title='Exercise', items=exercises, resources=resources,
            description=get_description('exercise'), form_link=get_form_link('exercise'))

@participant.route('/medication')
@login_required
def medication_index():
    """Participant Dashboard"""
    medications = [Medication.query.filter_by(id=x.fk_id).first() for x in current_user.plan.plan_components if x.fk_table == 'medication']
    resources = [[]]
    return render_template('participant/plan-indexes.html', title="Medication", items=medications, resources=resources, description=get_description('medication'), form_link=get_form_link('medication'))


@participant.route('/nutrition')
@login_required
def nutrition_index():
    nutritions = [Nutrition.query.filter_by(id=x.fk_id).first() for x in current_user.plan.plan_components if x.fk_table == 'nutrition']
    resources = [Resource.query.filter_by(fk_id=x.id).filter_by(fk_table='nutrition').all() for x in nutritions] 
    return render_template('participant/plan-indexes.html', title="Nutrition", items=nutritions, resources=resources, description=get_description('nutrition'), form_link=get_form_link('nutrition'))


@participant.route('/journal')
@login_required
def journal_index():
    """Participant Dashboard"""
    return render_template('participant/index.html')

@participant.route('/pain')
@login_required
def pain_index():
    link = get_form_link('pain')
    return render_template('participant/pain.html', desscription=get_description('pain'), link=link)
