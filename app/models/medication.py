from .. import db


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    description = db.Column(db.Text)
    dosage = db.Column(db.Text)

    def __init__(self, name, description, dosage):
        self.name = name
        self.description = description
        self.dosage = dosage
