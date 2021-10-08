import time
import math

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, settings, db, excel_files
import utils as utils
import models as m
import lib.goal_stats as goal_stats


@app.route('/BE/unit/<goal_code>/<goal_type>/<unit>', methods=['POST'])
@jwt_required
def post_goal_unit(goal_code, goal_type, unit):
    print(goal_code, unit)
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    goal_info = m.GoalInfo.query.filter_by(code=goal_code, benchmark_id=user.current_benchmark_id).first()
    goal_info.unit = unit
    db.session.commit()
    res = {'status': 'success', 'message': 'saved'}
    return jsonify(res)


@app.route('/BE/v2/<goal_code>/<goal_type>', methods=['GET'])
@jwt_required
def get_be_simple_v2(goal_code, goal_type=None):
    data = {}
    if goal_type == 'undefined':
        goal_type = None

    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    id = user.current_benchmark_id
    if goal_code in ['BE01', 'BE02', 'BE05', 'BE12']:
        data = goal_stats.get_site_bes(id, goal_code, goal_type)

    return jsonify(data)


@app.route('/BE/v2/<goal_code>/<goal_type>', methods=['POST'])
@jwt_required
def post_be_simple_v2(goal_code, goal_type=None):
    answers = request.json
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    benchmark_id = user.current_benchmark_id

    previous = m.GoalAnswer.query.filter_by(goal_code=goal_code, benchmark_id=benchmark_id, goal_type=goal_type).all()

    for answer in previous:
        db.session.delete(answer)

    for key in answers:
        for input_id in answers[key]:
            new_values = answers[key][input_id]
            number = new_values.get('value_number')
            if number == '':
                number = None

            answer = m.GoalAnswer()
            answer.goal_code = goal_code
            answer.goal_type = new_values.get('goal_type')
            answer.active = new_values.get('active')
            answer.question_code = key
            answer.benchmark_id = benchmark_id
            answer.input_id = input_id
            answer.value_number = number
            answer.value_text = new_values.get('value_text')
            answer.value_bool = new_values.get('value_bool')
            answer.type = new_values['type']
            db.session.add(answer)
    db.session.commit()

    if goal_code == 'BE12':
        calculate_progress_be12(goal_code, goal_type, answers, benchmark_id)

    return jsonify({'status': 'success', 'message': 'saved'})


def calculate_progress_be12(goal_code, goal_type, answers, benchmark_id):
    inputs = m.Site.query.filter_by(benchmark_id=benchmark_id).all()
    total_sites = len(inputs)
    total_inactive = 0
    res = {}
    goal_info = m.GoalInfo.query.filter_by(code=goal_code, benchmark_id=benchmark_id).first()

    if not goal_info:
        goal_info = m.GoalInfo()
        goal_info.benchmark_id = benchmark_id
        goal_info.code = goal_code
        db.session.add(goal_info)

    total_points = 0
    points = 0

    for site in inputs:
        if not site.active:
            total_inactive += 1
            continue

        total_points += 6 * site.employees

        for key in answers:
            answer = answers[key][str(site.id)].get('value_number', 0)
            if answer:
                points += int(answer)

    score = round((points / total_points) * 100)
    active_sites = total_sites = total_inactive

    goal_info.progress = score
    db.session.commit()


@app.route('/BE/<goal>', methods=['GET'])
@app.route('/BE/<goal>/<type>', methods=['GET'])
@jwt_required
def get_be_simple(goal, type=None):
    data = {}
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    id = user.current_benchmark_id
    if goal == 'BE01':
        data = goal_info.get_be01(id)
    if goal == 'BE02':
        data = goal_info.get_be02(id, type)

    return jsonify(data)


@app.route('/BE/<int:goal_id>', methods=['POST'])
@jwt_required
def post_be_simple(goal_id):
    """the goal entry has already been created in the GET, so there will always be an id"""
    be = m.Goal.query.get(goal_id)
    answers = request.json.get('answers')
    previous = m.GoalAnswer.query.filter_by(goal_id=be.id).all()
    for _answer in previous:
        db.session.delete(_answer)

    be.is_relevant = request.json.get('is_relevant')
    be.has_data = request.json.get('has_data')
    save_answers(be, answers)
    return jsonify({'status': 'success', 'message': 'saved'})


def save_answers(be, answers):
    for key in answers.keys():
        answer = m.GoalAnswer()
        answer.goal_id = be.id
        answer.goal_code = key
        type = answers[key]['type']

        if type == goal_info.NUMBER:
            answer.value_number = answers[key]['value_number']
        if type == goal_info.TEXT:
            answer.value_text = answers[key]['value_text']
        if type == goal_info.BOOL:
            answer.value_bool = answers[key]['value_bool']

        db.session.add(answer)
    db.session.commit()
