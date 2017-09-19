from .. import db


class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    description = db.Column(db.Text)
    resources = db.relationship('Resource', backref='resource', lazy='dynamic')
