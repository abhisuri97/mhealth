from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from flask_rq import get_queue

from . import participant
from .. import db
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, EditableHTML

@participant.route('/')
@login_required
def index():
    """Participant Dashboard"""
    return render_template('participant/index.html')
