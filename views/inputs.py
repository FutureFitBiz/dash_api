import time

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, settings, db, excel_files
import utils as utils
import models as m
import lib.inputs as input_stats


DEFAULT_ERROR_MESSAGE = 'Missing required information'


@app.route('/inputs/<type>', methods=['GET'])
@jwt_required
def get_sites(type):
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    items = []

    if type == 'sites':
        items = input_stats.get_sites(user.current_benchmark_id)
    elif type == 'purchases':
        items = input_stats.get_purchases(user.current_benchmark_id)
    elif type == 'natural_resources':
        items = input_stats.get_natural_resources(user.current_benchmark_id)

    return jsonify(items)


@app.route('/inputs/delete/<type>/<int:id>', methods=['GET'])
@jwt_required
def delete_input(type, id):
    status = 'success'
    message = 'Site deleted'
    item = None

    if type == 'sites':
        item = m.Site.query.get(id)
    if type == 'purchases':
        item = m.Purchase.query.get(id)
    if type == 'natural_resources':
        item = m.NaturalResource.query.get(id)

    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        status = 'error'
        message = 'No matching item'

    return jsonify({'status': status, 'message': message})


@app.route('/inputs/sites', methods=['POST'])
@jwt_required
def update_site():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    id = request.json.get('id')
    name = request.json.get('name')
    country = request.json.get('country')
    employees = request.json.get('employees')

    if not name or not country:
        return jsonify({'status': 'error', 'message': DEFAULT_ERROR_MESSAGE})

    if employees == '':
        employees = None

    if id:
        item = m.Site.query.filter_by(id=id).first()
    else:
        item = m.Site()
        item.benchmark_id = user.current_benchmark_id
        db.session.add(item)

    item.name = name
    item.country = country
    item.employees = employees
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'saved'})


@app.route('/inputs/purchases', methods=['POST'])
@jwt_required
def post_purchase():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    id = request.json.get('id')
    name = request.json.get('name')
    type = request.json.get('type')
    cost = request.json.get('cost')
    traceable = request.json.get('traceable', False)

    if not name or not type or not cost:
        return jsonify({'status': 'error', 'message': DEFAULT_ERROR_MESSAGE})

    if id:
        item = m.Purchase.query.filter_by(id=id).first()
    else:
        item = m.Purchase()
        item.benchmark_id = user.current_benchmark_id
        db.session.add(item)

    item.traceable = traceable
    item.cost = cost
    item.type = type
    item.name = name

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'saved'})


@app.route('/inputs/natural_resources', methods=['POST'])
@jwt_required
def post_natural_resource():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    id = request.json.get('id')
    type = request.json.get('type')
    name = request.json.get('name')
    country = request.json.get('country')
    value = request.json.get('value')

    if not name or not type or not value:
        return jsonify({'status': 'error', 'message': DEFAULT_ERROR_MESSAGE})

    if id:
        item = m.NaturalResource.query.filter_by(id=id).first()
    else:
        item = m.NaturalResource()
        item.benchmark_id = user.current_benchmark_id
        db.session.add(item)

    item.type = type
    item.value = value
    item.country = country
    item.name = name

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'saved'})
