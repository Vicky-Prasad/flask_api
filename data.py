"""Routines associated with the application data.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.parser import parse
from run import app
import json
from os import path
from flask_marshmallow import Marshmallow


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course.db'
app.config['SECRET_KEY'] = '4bd76bdfadeec1257a781426'
db = SQLAlchemy(app)
ma = Marshmallow(app)

courses = {}

class Course(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow())
    description = db.Column(db.String(length=255))
    discount_price = db.Column(db.Numeric(10, 1))
    image_path = db.Column(db.String(length=100))
    on_discount = db.Column(db.Boolean(), nullable=False)
    price = db.Column(db.Numeric(10, 1), nullable=False)
    title = db.Column(db.String(length=100),db.CheckConstraint("LENGTH(title) > 4") , nullable=False)

    #def __repr__(self):
    #    return f'Course ID: {self.id}'
    #def get_url(self):
    #   return url_for('get_customer', id=self.id, _external=True)


class CourseSchema(ma.ModelSchema):
    class Meta:
        model = Course

def load_data():
    """Load the data from the json file.
    """

    if path.exists('course.db'):
        if len(Course.query.all()) != 0:
            return None

    print("ADDING DATA")
    db.create_all()
    
    f = open('Json/course.json')
    data = json.load(f)

    for item in range(len(data)):

        r = Course(id=int(data[item]['id']), date_created=parse(data[item]['date_created']), date_updated=parse(data[item]['date_updated']),
                   description=data[item]['description'], discount_price=data[item]['discount_price'],
                   image_path=data[item]['image_path'], on_discount=data[item]['on_discount'],
                   price=data[item]['price'], title=data[item]['title'])

        db.session.add(r)

    db.session.commit()
    f.close()
