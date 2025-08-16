#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return 'Camping Fun'

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    campers = Camper.query.all()
    camper_list = [camper.to_dict(only=('id', 'name', 'age')) for camper in campers]

    if not campers:
        return make_response({"error": "Campers not found"}, 404)

    if request.method == 'GET':
        
        return make_response(jsonify(camper_list), 200)
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_camper = Camper(
                name=data.get('name'),
                age=data.get('age'),
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict()), 201)
        
        except:
            
            return make_response({ "errors": ["validation errors"] }, 400)

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter_by(id=id).first()

    if not camper:
        return make_response({"error": "Camper not found"}, 404)

    if request.method == 'GET':
        return make_response((jsonify(camper.to_dict()), 200))
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            for attr, value in data.items():
                setattr(camper, attr, value)

            db.session.commit()

            return make_response(jsonify(camper.to_dict(only=('id','name','age'))), 202)
        
        except:
            return make_response({ "errors": ["validation errors"] }, 400)
    
@app.route('/activities', methods=['GET'])
def activities():
        activities = Activity.query.all()
        activities_list = [activity.to_dict() for activity in activities]
        return make_response((jsonify(activities_list), 200))

@app.route('/activities/<int:id>', methods=['GET', 'DELETE'])
def delete_activities(id):
    activity = Activity.query.filter_by(id=id).first()

    if not activity:
        return make_response({"error": "Activity not found"}, 404)
    
    db.session.delete(activity)
    db.session.commit()

    return make_response('', 204)

@app.route('/signups', methods=['GET', 'POST'])
def new_signup():

    if request.method == 'GET':
        signups = Signup.query.all()
        signup_list = [signup.to_dict() for signup in signups]
        return make_response(jsonify(signup_list), 200)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id=data.get('camper_id'),
                activity_id=data.get('activity_id'),
                time=data.get('time'),
            ) 
            db.session.add(new_signup)
            db.session.commit()
            return make_response(jsonify(new_signup.to_dict()), 201)
        
        except:
            return make_response({ "errors": ["validation errors"] }, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
