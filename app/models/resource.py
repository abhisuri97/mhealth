from .. import db


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    aws_url = db.Column(db.String(10000))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'))
