from flask import abort, flash, redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_rq import get_queue
from app import csrf
from datetime import datetime
import time
import json
import pytz
from pytz import timezone
from datetime import datetime, timedelta
import ast
from . import participant
from .. import db
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, EditableHTML, Plan, PlanComponent, Exercise, Resource, Medication, Nutrition, PlanTodo, UsageStats

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




@participant.route('/todo/<int:plan_id>/<string:type>')
@csrf.exempt
def mark_todo(plan_id, type):
    n = PlanTodo(plan_component_id=plan_id, user_id=current_user.id, status=(True if type == 'complete' else False), last_updated=datetime.now())
    db.session.add(n)
    db.session.commit()
    return jsonify({'success' : 'true'})


@participant.route('/stats/<int:user_id>/<string:page_type>/<int:time>', methods=['GET', 'POST'])
@csrf.exempt
def usage_stats(user_id, page_type, time):
    n = UsageStats(user_id = user_id, page = page_type, time=datetime.now(), length=time)
    db.session.add(n)
    db.session.commit()
    return jsonify({'success' : 'true'})


@participant.route('/exercises')
@login_required
def exercise_index():
    """Participant Dashboard"""
    (exercises, resources, todo, todo_resources)  = get_resources(current_user, 'exercise')
    return render_template('participant/plan-indexes.html', title='Exercise', items=exercises, resources=resources,
            description=get_description('exercise'), form_link=get_form_link('exercise'), todo=todo, todo_resources=todo_resources)


def get_resources(current_user, type):
    days = ['M','T','W','R','F','S','U']
    eastern = timezone('US/Eastern')
    day = days[datetime.now(eastern).weekday()]
    print(day)
    rs = []
    todo = []
    for x in current_user.plan.plan_components:
        print(x.fk_table)
        if x.fk_table == type:
            rs+= [(e, x.id) for e in db.session.query(db.Model.metadata.tables[type]).filter_by(id=x.fk_id).all()]
    print(rs)
    for (e, id) in rs:
        arr_days = ast.literal_eval(e.days)
        for d in arr_days:
            if d == day:
                status = PlanTodo.query.filter_by(plan_component_id=id, user_id=current_user.id).order_by('id desc').first()
                if status != None and days[status.last_updated.weekday()] != day:
                    status = False
                todo.append((e, status, id))

    resources = [Resource.query.filter_by(fk_id=x.id).filter_by(fk_table=type).all() for (x, _) in rs]
    todo_resources = [Resource.query.filter_by(fk_id=x.id).filter_by(fk_table=type).all() for (x,_, _) in todo]
    return (rs, resources, todo, todo_resources)


@participant.route('/medication')
@login_required
def medication_index():
    """Participant Dashboard"""
    (medications, resources, todo, todo_resources)  = get_resources(current_user, 'medication')
    return render_template('participant/plan-indexes.html', title='Medication', items=medications, resources=resources, description=get_description('medication'), form_link=get_form_link('medication'), todo=todo, todo_resources=todo_resources)



@participant.route('/nutrition')
@login_required
def nutrition_index():
    (nutrition, resources, todo, todo_resources)  = get_resources(current_user, 'nutrition')
    return render_template('participant/plan-indexes.html', title='Nutrition', items=nutrition, resources=resources, description=get_description('nutrition'), form_link=get_form_link('nutrition'), todo=todo, todo_resources=todo_resources)


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
