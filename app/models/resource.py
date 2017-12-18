from .. import db


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aws_url = db.Column(db.String(10000))
    description = db.Column(db.Text)
    fk_id = db.Column(db.Integer)
    fk_table = db.Column(db.String(64), nullable=True)

    def get_resource_name(self):
        a = db.session.query(db.Model.metadata.tables[self.fk_table]).filter_by(id=self.fk_id).first()
        if a is not None:
            return a.name

    def get_resource_description(self):
        a = db.session.query(db.Model.metadata.tables[self.fk_table]).filter_by(id=self.fk_id).first()
        if a is not None:
            return a.description

    @staticmethod
    def add_resource(table, urls, fk_id):
        Resource.query.filter_by(fk_table=table).filter_by(fk_id=fk_id).delete()
        db.session.commit()
        for x in urls:
            if len(x) > 0:
                url, desc = x.split(';')[0], ''.join(x.split(';')[1:])
                r_new = Resource(aws_url=url, fk_id=fk_id, fk_table=table, description=desc)
                db.session.add(r_new)
        db.session.commit()

    # @staticmethod
    # def add_exercises(urls, ex_id):
        # Resource.query.filter_by(exercise_id=ex_id).delete()
        # db.session.commit()
        # for x in urls:
            # if len(x) > 0:
                # url, desc = x.split(';')[0], ''.join(x.split(';')[1:])
                # r_new = Resource(aws_url=url, exercise_id=ex_id, description=desc)
                # db.session.add(r_new)
        # db.session.commit()
# 
    # @staticmethod
    # def add_nutritions(urls, ex_id):
        # Resource.query.filter_by(nutrition_id=ex_id).delete()
        # db.session.commit()
        # for x in urls:
            # if len(x) > 0:
                # url, desc = x.split(';')[0], ''.join(x.split(';')[1:])
                # r_new = Resource(aws_url=url, nutrition_id=ex_id, description=desc)
                # db.session.add(r_new)
        # db.session.commit()
