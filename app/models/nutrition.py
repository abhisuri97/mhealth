from .. import db


class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    description = db.Column(db.Text)
    # resources = db.relationship('Resource', backref='nutrition', lazy='dynamic')

    def __init__(self, name, description):
        self.name = name
        self.description = description
