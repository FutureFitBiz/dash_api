import time
import math

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, settings, db, excel_files
import utils as utils
import models as m
import lib.goal_stats as goal_stats
import lib.common_utils as common_utils


@app.route('/risk-profile/delete', methods=['GET'])
@jwt_required
def get_risk_assessment_delete():
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()

    return 'ok'


@app.route('/risk-profile/status', methods=['GET'])
@jwt_required
def get_risk_assessment_status():
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()
    answer_groups = [a.group for a in answers]
    groups = {}
    saved_count = 0
    product_type = None
    finished = True
    total = 0
    total_finished = 0
    started = assessment.is_product is not None
    if started:
        product_type = 'product' if assessment.is_product else 'non_product'

    groups = {
        'intro': {
            'order': 1,
            'name': 'Introduction',
            'disabled': False,
            'show_intro': False,
        },
        'basic_info': {
            'name': 'Basic Info',
            'saved': started,
            'count': 1 if started else 0,
            'max': 1,
            'order': 2,
            'finished': started,
            'disabled': False,
            'show_intro': True,
        },
        'results': {
            'order': 99,
            'name': 'Results',
            'show_intro': False,
            'disabled': False
        }
    }
    order = 3

    for key in excel_files.valueweb.keys():
        saved = key in answer_groups
        order += 1

        if not saved:
            finished = False

        max = 0
        if started:
            max = excel_files.risk_questions['counts'][key][product_type]
            total += max

        groups[key] = {
            'saved': saved,
            'name': excel_files.valueweb[key]['name'],
            'description': excel_files.valueweb[key]['description'],
            'max': max,
            'count': 0,
            'order': order,
            'finished': False,
            'show_intro': True,
            'disabled': assessment.is_product is None
        }

        if saved:
            saved_count += 1

    for a in answers:
        if a.group not in groups:
            print('error - api/statuses/ no group', a.id, a)
        if a.value is not None:
            groups[a.group]['count'] += 1
            total_finished += 1

            if groups[a.group]['count'] == groups[a.group]['max']:
                groups[a.group]['finished'] = True

    res = {
        'items': groups,
        'is_product': assessment.is_product,
        'started': started,
        'finished': (total > 0) and (total_finished == total),
        'remaining_count': total - total_finished,
    }
    return jsonify(res)


@app.route('/risk-profile/questions/<group>', methods=['GET'])
@jwt_required
def get_risk_assessment_part2(group):
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id, group=group).all()
    answers_lookup = {a.code: a for a in answers}
    res = []
    product_type = 'product' if assessment.is_product else 'non_product'
    template_questions = excel_files.risk_questions[product_type]

    if group == 'basic_info':
        res = [{
            'title': 'Do you manufacture or sell physical goods?',
            'value': assessment.is_product,
            'order': 1,
        }]
    else:
        for key in template_questions[group]['items']:
            question = template_questions[group]['items'][key]
            answer = answers_lookup.get(question['code'])
            question['value'] = answer.value if answer else None
            res.append(question)


        res = sorted(res, key=lambda k: (k['order']))

        group_titles = excel_files.risk_question_sections[product_type][group]
        added_codes = []
        for q in res:
            if q['code'] in group_titles and q['code'] not in added_codes:
                added_codes.append(q['code'])
                q['group_title'] = group_titles[q['code']]


    return jsonify(res)


@app.route('/risk-profile/questions/<group>', methods=['POST'])
@jwt_required
def save_risk_assessment_questions(group):
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    answers = request.json

    if group == 'basic_info':
        all_answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()
        for previous_answer in all_answers:
            db.session.delete(previous_answer)

        assessment.is_product = answers[0]['value']
    else:
        previous_answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id, group=group).all()

        for previous_answer in previous_answers:
            db.session.delete(previous_answer)

        for answer in answers:
            if answer['value'] is not None:
                a = m.RiskAssessmentAnswer()
                a.benchmark_id = benchmark_id
                a.code = answer['code']
                a.group = group
                a.risk = answer['risk']
                a.value = answer['value']
                db.session.add(a)

    set_goal_risks(benchmark_id)
    db.session.commit()

    return jsonify({'status': 'success'})


def set_goal_risks(benchmark_id):
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    all_answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()
    goal_infos = m.GoalInfo.query.filter_by(benchmark_id=benchmark_id).all()
    product_type = 'product' if assessment.is_product else 'non_product'
    answer_lookup = {a.code: a for a in all_answers}

    for goal in goal_infos:
        current_risk = ''
        for id in excel_files.risk_questions['question_ids_by_goal'][goal.code][product_type]:
            if id not in answer_lookup:
                current_risk = common_utils.HIGHEST_RISK
            else:
                answer = answer_lookup[id]

                if answer.value is True:
                    if not current_risk:
                        current_risk = answer.risk
                    elif utils.risk_priority[answer.risk] > utils.risk_priority[current_risk]:
                        current_risk = answer.risk

        if not current_risk:
            goal.is_default_risk = True
            goal.risk = excel_files.goal_risk_defaults[goal.code][product_type]
        else:
            goal.is_default_risk = False
            goal.risk = current_risk


@app.route('/risk-profile/results', methods=['GET'])
@jwt_required
def get_risk_assessment_results():
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()

    if not assessment:
        assessment = m.RiskAssessment()
        assessment.benchmark_id = benchmark_id
        db.session.add(assessment)
        db.session.commit()

    goal_infos = m.GoalInfo.query.filter_by(benchmark_id=benchmark_id).all()
    goal_lookup = {goal.code: goal for goal in goal_infos}
    product_type = 'product' if assessment.is_product else 'non_product'

    counts = [
        len([x for x in goal_infos if x.risk == common_utils.HIGH_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.MODERATE_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.LOW_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.UNLIKELY_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.HIGHEST_RISK]),
    ]

    items = []

    for key in excel_files.valueweb:
        item = {
            'name': excel_files.valueweb[key]['name'],
            'order': excel_files.valueweb[key]['order'],
            'description': excel_files.valueweb[key]['description_short'],
            'items': []
        }
        for goal_code in excel_files.valueweb[key]['goals']:
            goal = goal_lookup[goal_code]
            item['items'].append({
                'goal': goal.code,
                'goal_short_name': excel_files.be_lookup[goal.code]['short_name'],
                'risk': goal.risk,
                'default': goal.is_default_risk,
            })

        items.append(item)

    all_answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()
    answer_lookup = {a.code: a for a in all_answers}
    goal_questions = {}
    template_questions = excel_files.risk_questions[product_type]

    for goal in utils.break_evens:
        questions = []
        codes = excel_files.risk_questions['question_ids_by_goal'][goal][product_type]

        for code in codes:
            if code in answer_lookup and answer_lookup[code].value == True:
                answer = answer_lookup[code]

                for valueweb_key in excel_files.valueweb:
                    for question_code in template_questions[valueweb_key]['items']:
                        if question_code == code:
                            questions.append(template_questions[valueweb_key]['items'][question_code])

        if not questions:
            questions = ['default']
        goal_questions[goal] = questions

    for index, item in enumerate(items):
        for goal_index, goal_item in enumerate(item['items']):
            items[index]['items'][goal_index]['questions'] = goal_questions[goal_item['goal']]

    return jsonify({
        'items': items,
        'counts': counts,
        'labels': ["High", "Moderate", "Low", "Unlikely"],
    })


@app.route('/risk-profile/results/goals', methods=['GET'])
@jwt_required
def get_risk_assessment_results_as_goals():
    benchmark_id = m.User.query.filter_by(email=get_jwt_identity()).first().current_benchmark_id
    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()

    if not assessment:
        assessment = m.RiskAssessment()
        assessment.benchmark_id = benchmark_id
        db.session.add(assessment)
        db.session.commit()

    goal_infos = m.GoalInfo.query.filter_by(benchmark_id=benchmark_id).all()
    goal_lookup = {goal.code: goal for goal in goal_infos}
    product_type = 'product' if assessment.is_product else 'non_product'

    counts = [
        len([x for x in goal_infos if x.risk == common_utils.HIGH_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.MODERATE_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.LOW_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.UNLIKELY_RISK]),
        len([x for x in goal_infos if x.risk == common_utils.HIGHEST_RISK]),
    ]

    items = []

    for goal_code in utils.break_evens:
        valuweb_name = ''
        for key in excel_files.valueweb:
            if goal_code in excel_files.valueweb[key]['goals']:
                valuweb_name = excel_files.valueweb[key]['name']

        goal = goal_lookup[goal_code]
        item = {
            'goal': goal.code,
            'goal_short_name': excel_files.be_lookup[goal.code]['short_name'],
            'risk': goal.risk,
            'valueweb': valuweb_name,
            'default': goal.is_default_risk,
            'default_title': excel_files.goal_risk_defaults[goal.code][product_type + '_title']
        }

        items.append(item)

    all_answers = m.RiskAssessmentAnswer.query.filter_by(benchmark_id=benchmark_id).all()
    answer_lookup = {a.code: a for a in all_answers}
    goal_questions = {}
    template_questions = excel_files.risk_questions[product_type]

    for goal_code in utils.break_evens:
        questions = []
        codes = excel_files.risk_questions['question_ids_by_goal'][goal_code][product_type]

        for code in codes:
            if code in answer_lookup and answer_lookup[code].value == True:
                answer = answer_lookup[code]

                for valueweb_key in excel_files.valueweb:
                    for question_code in template_questions[valueweb_key]['items']:
                        if question_code == code:
                            questions.append(template_questions[valueweb_key]['items'][question_code])

        if not questions:
            questions = ['default']

        for index, goal in enumerate(items):
            if goal['goal'] == goal_code:
                items[index]['questions'] = questions

    return jsonify({
        'items': items,
        'counts': counts,
        'valuewebs': [excel_files.valueweb[key]['name'] for key in excel_files.valueweb],
        'labels': ["High", "Moderate", "Low", "Unlikely"],
    })
