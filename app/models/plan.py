from .. import db


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    plan_components = db.relationship('PlanComponent', backref='plan', lazy=True)
    plan_descriptions = db.relationship('PlanDescription', backref='plan', lazy=True)
    plan_users = db.relationship('User', backref='plan', lazy='dynamic')



class PlanComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_table = db.Column(db.String(64), nullable=True)
    fk_id = db.Column(db.Integer, nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)

    @staticmethod
    def add_plan_component(table, objs, plan_id):
        for x in objs:
            p = PlanComponent(fk_table=table, fk_id=x.id, plan_id=plan_id)
            db.session.add(p)
        db.session.commit()



class PlanDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    form_link = db.Column(db.Text, nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)

    @staticmethod
    def add_plan_description(type, desc, link, plan_id):
        p = PlanDescription(type=type, description=desc, plan_id=plan_id, form_link=link)
        db.session.add(p)
        db.session.commit()
