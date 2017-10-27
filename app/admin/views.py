from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from flask_rq import get_queue

from .forms import (ChangeAccountTypeForm, ChangeUserEmailForm, ChangePlanForm, InviteUserForm,
                    NewUserForm, ExerciseForm, EditExerciseForm, MedicationForm,
                    EditMedicationForm, NutritionForm, EditNutritionForm, PlanForm)
from . import admin
from .. import db
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, EditableHTML, Exercise, Resource, Medication, Nutrition, Plan, PlanComponent, PlanDescription


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            # first_name=form.first_name.data,
            # last_name=form.last_name.data,
            email=form.email.data,
            plan=form.plan.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.user_anon_id),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            # first_name=form.first_name.data,
            # last_name=form.last_name.data,
            plan=form.plan.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link, )
        flash('User {} successfully invited'.format(user.user_anon_id),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-plan-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_plan_type(user_id):
    """Change a user's plan type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangePlanForm()
    if form.validate_on_submit():
        user.plan = form.plan.data
        db.session.add(user)
        db.session.commit()
        flash('Plan for user {} successfully changed to {}.'
              .format(user.full_name(), user.plan.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200

# Exercises

@admin.route('/add-exercise', methods=['GET', 'POST'])
@login_required
@admin_required
def add_exercise():
    """Create a new user."""
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(
            name=form.name.data,
            description=form.description.data)
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise {} successfully created'.format(exercise.name),
              'form-success')
    return render_template('admin/add_exercise.html', form=form)

@admin.route('/all-exercises')
@login_required
@admin_required
def exercises():
    """View all registered users."""
    exercises = Exercise.query.all()
    return render_template(
        'admin/exercises.html', exercises=exercises)

@admin.route('/exercise/<int:exercise_id>')
@admin.route('/exercise/<int:exercise_id>/info')
@login_required
@admin_required
def exercise_info(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if exercise is None:
        abort(404)
    return render_template('admin/manage_exercise.html', exercise=exercise)

@admin.route('/exercise/<int:exercise_id>/change-info', methods=['GET', 'POST'])
@login_required
@admin_required
def change_exercise_info(exercise_id):
    """Change a user's email."""
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if exercise is None:
        abort(404)
    form = EditExerciseForm()

    if form.validate_on_submit():
        exercise.name = form.name.data
        exercise.description = form.description.data
        url_list = form.url_list.data.split(',')
        Resource.add_resource('exercise', url_list, exercise_id)
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise successfully edited.', 'form-success')
    elif form.is_submitted() is False:
        form.name.data = exercise.name
        form.description.data = exercise.description
        form.url_list.data = ','.join([r.aws_url + ';' + r.description for r in Resource.query.filter_by(fk_table='exercise').filter_by(fk_id=exercise_id).all()])
    return render_template('admin/manage_exercise.html', exercise=exercise,
                           form=form)


@admin.route('/exercise/<int:exercise_id>/delete')
@login_required
@admin_required
def delete_exercise_request(exercise_id):
    """Request deletion of a user's account."""
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if exercise is None:
        abort(404)
    return render_template('admin/manage_exercise.html', exercise=exercise)


@admin.route('/exercise/<int:exercise_id>/_delete')
@login_required
@admin_required
def delete_exercise(exercise_id):
    """Delete an exercise."""
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    db.session.delete(exercise)
    db.session.commit()
    flash('Successfully deleted exercise', 'success')
    return redirect(url_for('admin.exercises'))

# Medication

@admin.route('/add-medication', methods=['GET', 'POST'])
@login_required
@admin_required
def add_medication():
    """Create a new medicine."""
    form = MedicationForm()
    if form.validate_on_submit():
        exercise = Medication(
            name=form.name.data,
            description=form.description.data,
            dosage=form.dosage.data)
        db.session.add(exercise)
        db.session.commit()
        flash('Medication {} successfully created'.format(exercise.name),
              'form-success')
    return render_template('admin/add_medication.html', form=form)

@admin.route('/all-medications')
@login_required
@admin_required
def medications():
    """View all medications."""
    medications = Medication.query.all()
    return render_template(
        'admin/medications.html', medications=medications)

@admin.route('/medication/<int:medication_id>')
@admin.route('/medication/<int:medication_id>/info')
@login_required
@admin_required
def medication_info(medication_id):
    medication = Medication.query.filter_by(id=medication_id).first()
    if medication is None:
        abort(404)
    return render_template('admin/manage_medication.html', medication=medication)

@admin.route('/medication/<int:medication_id>/change-info', methods=['GET', 'POST'])
@login_required
@admin_required
def change_medication_info(medication_id):
    """Change a user's email."""
    medication = Medication.query.filter_by(id=medication_id).first()
    if medication is None:
        abort(404)
    form = EditMedicationForm()

    if form.validate_on_submit():
        medication.name = form.name.data
        medication.description = form.description.data
        medication.dosage = form.dosage.data
        db.session.add(medication)
        db.session.commit()
        flash('Exercise successfully edited.', 'form-success')
    elif form.is_submitted() is False:
        medication.name = form.name.data
        medication.description = form.description.data
        medication.dosage = form.dosage.data

    return render_template('admin/manage_medication.html', medication=medication,
                           form=form)


@admin.route('/medication/<int:medication_id>/delete')
@login_required
@admin_required
def delete_medication_request(medication_id):
    """Request deletion of a user's account."""
    medication = Medication.query.filter_by(id=medication_id).first()
    if medication is None:
        abort(404)
    return render_template('admin/manage_medication.html', medication=medication)


@admin.route('/medication/<int:medication_id>/_delete')
@login_required
@admin_required
def delete_medication(medication_id):
    """Delete an exercise."""
    medication = Medication.query.filter_by(id=medication_id).first()
    db.session.delete(medication)
    db.session.commit()
    flash('Successfully deleted medication', 'success')
    return redirect(url_for('admin.medications'))


# nutritions

@admin.route('/add-nutrition', methods=['GET', 'POST'])
@login_required
@admin_required
def add_nutrition():
    """Create a new user."""
    form = NutritionForm()
    if form.validate_on_submit():
        nutrition = Nutrition(
            name=form.name.data,
            description=form.description.data)
        db.session.add(nutrition)
        db.session.commit()
        flash('nutrition {} successfully created'.format(nutrition.name),
              'form-success')
    return render_template('admin/add_nutrition.html', form=form)

@admin.route('/all-nutritions')
@login_required
@admin_required
def nutritions():
    """View all registered users."""
    nutritions = Nutrition.query.all()
    return render_template(
        'admin/nutritions.html', nutritions=nutritions)

@admin.route('/nutrition/<int:nutrition_id>')
@admin.route('/nutrition/<int:nutrition_id>/info')
@login_required
@admin_required
def nutrition_info(nutrition_id):
    nutrition = Nutrition.query.filter_by(id=nutrition_id).first()
    if nutrition is None:
        abort(404)
    return render_template('admin/manage_nutrition.html', nutrition=nutrition)

@admin.route('/nutrition/<int:nutrition_id>/change-info', methods=['GET', 'POST'])
@login_required
@admin_required
def change_nutrition_info(nutrition_id):
    """Change a user's email."""
    nutrition = Nutrition.query.filter_by(id=nutrition_id).first()
    if nutrition is None:
        abort(404)
    form = EditNutritionForm()

    if form.validate_on_submit():
        nutrition.name = form.name.data
        nutrition.description = form.description.data
        url_list = form.url_list.data.split(',')
        Resource.add_resource('nutrition', url_list, nutrition_id)
        db.session.add(nutrition)
        db.session.commit()
        flash('nutrition successfully edited.', 'form-success')
    elif form.is_submitted() is False:
        form.name.data = nutrition.name
        form.description.data = nutrition.description
        form.url_list.data = ','.join([r.aws_url + ';' + r.description for r in Resource.query.filter_by(fk_table='nutrition').filter_by(fk_id=nutrition_id).all()])
    return render_template('admin/manage_nutrition.html', nutrition=nutrition,
                           form=form)


@admin.route('/nutrition/<int:nutrition_id>/delete')
@login_required
@admin_required
def delete_nutrition_request(nutrition_id):
    """Request deletion of a user's account."""
    nutrition = Nutrition.query.filter_by(id=nutrition_id).first()
    if nutrition is None:
        abort(404)
    return render_template('admin/manage_nutrition.html', nutrition=nutrition)


@admin.route('/nutrition/<int:nutrition_id>/_delete')
@login_required
@admin_required
def delete_nutrition(nutrition_id):
    """Delete an nutrition."""
    nutrition = Nutrition.query.filter_by(id=nutrition_id).first()
    db.session.delete(nutrition)
    db.session.commit()
    flash('Successfully deleted nutrition', 'success')
    return redirect(url_for('admin.nutritions'))

# Plans

@admin.route('/add-plan', methods=['GET', 'POST'])
@login_required
@admin_required
def add_plan():
    """Create a new user."""
    form = PlanForm()
    if form.validate_on_submit():
        plan = Plan(
            name=form.name.data)
        db.session.add(plan)
        db.session.commit()
        PlanComponent.add_plan_component('exercise', form.exercise_components.data, plan.id)
        PlanComponent.add_plan_component('medication', form.medication_components.data, plan.id)
        PlanComponent.add_plan_component('nutrition', form.nutrition_components.data, plan.id)
        PlanDescription.add_plan_description('exercise', form.exercise_description.data, form.exercise_link.data, plan.id)
        PlanDescription.add_plan_description('medication', form.medication_description.data, form.medication_link.data,  plan.id)
        PlanDescription.add_plan_description('nutrition', form.nutrition_description.data, form.nutrition_link.data, plan.id)
        PlanDescription.add_plan_description('pain', form.pain_description.data, form.pain_link.data, plan.id)
        flash('plan {} successfully created'.format(plan.name),
              'form-success')
    return render_template('admin/add_plan.html', form=form)

@admin.route('/all-plans')
@login_required
@admin_required
def plans():
    """View all registered users."""
    plans = Plan.query.all()
    return render_template(
        'admin/plans.html', plans=plans)

@admin.route('/plan/<int:plan_id>')
@admin.route('/plan/<int:plan_id>/info')
@login_required
@admin_required
def plan_info(plan_id):
    plan = Plan.query.filter_by(id=plan_id).first()
    exercises = [Exercise.query.filter_by(id=x.fk_id).first() for x in plan.plan_components if x.fk_table=='exercise']
    exercises_link = [x.form_link for x in plan.plan_descriptions if x if x.type=='exercise']
    exercises_description = [x.description for x in plan.plan_descriptions if x.type=='exercise']
    medications = [Exercise.query.filter_by(id=x.fk_id).first() for x in plan.plan_components if x.fk_table=='medication']
    medications_link = [x.form_link for x in plan.plan_descriptions if x.type=='medication']
    medications_description = [x.description for x in plan.plan_descriptions if x.type=='medication']
    nutritions = [Exercise.query.filter_by(id=x.fk_id).first() for x in plan.plan_components if x.fk_table=='nutrition']
    nutritions_link = [x.form_link for x in plan.plan_descriptions if x.type=='nutrition']
    nutritions_description = [x.description for x in plan.plan_descriptions if x.type=='nutrition']

    if plan is None:
        abort(404)
    return render_template('admin/manage_plan.html', plan=plan, exercises=exercises, exercises_link=exercises_link, exercises_description=exercises_description,
            nutritions=nutritions, nutritions_link=nutritions_link, nutritions_description=nutritions_description,
            medications=medications, medications_link=medications_link, medications_description=medications_description)

@admin.route('/plan/<int:plan_id>/change-info', methods=['GET', 'POST'])
@login_required
@admin_required
def change_plan_info(plan_id):
    """Change a user's email."""
    plan = Plan.query.filter_by(id=plan_id).first()
    if plan is None:
        abort(404)
    form = PlanForm()

    if form.validate_on_submit():
        PlanComponent.add_plan_component('exercise', form.exercise_components.data, plan.id)
        PlanComponent.add_plan_component('medication', form.medication_components.data, plan.id)
        PlanComponent.add_plan_component('nutrition', form.nutrition_components.data, plan.id)
        PlanDescription.add_plan_description('exercise', form.exercise_description.data, form.exercise_link.data, plan.id)
        PlanDescription.add_plan_description('medication', form.medication_description.data, form.medication_link.data,  plan.id)
        PlanDescription.add_plan_description('nutrition', form.nutrition_description.data, form.nutrition_link.data, plan.id)
        flash('plan {} successfully updated'.format(plan.name),
              'form-success')
    elif form.is_submitted() is False:
        form.name.data = plan.name

    return render_template('admin/manage_plan.html', plan=plan,
                           form=form)


@admin.route('/plan/<int:plan_id>/delete')
@login_required
@admin_required
def delete_plan_request(plan_id):
    """Request deletion of a user's account."""
    plan = Plan.query.filter_by(id=plan_id).first()
    if plan is None:
        abort(404)
    return render_template('admin/manage_plan.html', plan=plan)


@admin.route('/plan/<int:plan_id>/_delete')
@login_required
@admin_required
def delete_plan(plan_id):
    """Delete an plan."""
    plan = Plan.query.filter_by(id=plan_id).first()
    db.session.delete(plan)
    db.session.commit()
    flash('Successfully deleted plan', 'success')
    return redirect(url_for('admin.plans'))
