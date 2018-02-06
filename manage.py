#!/usr/bin/env python
import os
import ast
import subprocess
from flask_rq import get_queue
from app.email import send_email
from config import Config
import logging
logging.basicConfig()
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from redis import Redis
from rq import Connection, Queue, Worker

from app import create_app, db
from app.models import Role, User, Resource, Plan, Exercise, Medication, Nutrition, PlanComponent, PlanDescription

from datetime import datetime
import time
import pytz
from pytz import timezone
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BlockingScheduler

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Number of each model type to create',
    dest='number_users')
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email=Config.ADMIN_EMAIL).first() is None:
            user = User(
                first_name='Admin',
                last_name='Account',
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL)
            db.session.add(user)
            db.session.commit()
            print('Added administrator {}'.format(user.full_name()))


@manager.command
def run_worker():
    """Initializes a slim rq task queue."""
    listen = ['default']
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD'])

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


def tick():
    days = ['M','T','W','R','F','S','U']
    eastern = timezone('US/Eastern')
    day = days[datetime.now(eastern).weekday()]
    with app.app_context():
        print(app.config['EMAIL_SENDER'])
        try:
            for p in Plan.query.all():
                users = p.plan_users.all()
                notifs = []
                for c in p.plan_components:
                    table = c.fk_table
                    id = c.fk_id
                    resource = db.session.query(db.Model.metadata.tables[table]).filter_by(id=id).first()
                    arr_days = ast.literal_eval(resource.days)
                    for d in arr_days:
                        if d == day:
                            notifs.append('Name {}, Description: {}'.format(resource.name, resource.description))
                            print('added resource {}'.format(resource.name))
                if len(notifs) > 0:
                    for u in users:
                        get_queue().enqueue(
                            send_email,
                            recipient=u.email,
                            subject='Transplant App Reminder',
                            template='account/email/reminder',
                            user=u,
                            notifs=notifs)
                        print('Send email to {}'.format(u.email))
        except Exception as e:
            print("Error {}".format(e))


@manager.command
def run_clock():
    scheduler = BlockingScheduler()
    start_time = datetime.now(pytz.timezone('US/Eastern')).replace(hour=6, minute=30, second=0)
    scheduler.add_job(tick, 'interval', start_date=start_time, seconds=10)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    scheduler.start()


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == '__main__':
    manager.run()
