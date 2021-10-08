import time
import math

import utils as utils
import models as m
from app import app, settings, db, excel_files
from lib.goal_units import goal_units

NUMBER = 'number'
BOOL = 'bool'
TEXT = 'text'


goal_defaults = {
    'BE01': {
        'goal': 'BE01',
        'group': 'Business inputs',
        'description': utils.be_heading_text['BE01'],
        'goal_text': 'All energy is from renewable sources',
        'progress_indicator_text': 'Energy',
        'input_type': 'Site',
        'input_type_plural': 'Sites',
        'answer_header': 'Electricity consumed'
    },
    'BE02': {
        'goal': 'BE02',
        'group': 'Business inputs',
        'description': utils.be_heading_text['BE02'],
        'goal_text': 'Water use is environmentally responsible and socially equitable',
        'input_type': 'Site',
        'input_type_plural': 'Sites',
        'answer_header': 'Liquid volume'
    },
    'BE03': {
        'goal': 'BE03',
    },
    'BE04': {
        'goal': 'BE04',
    },
    'BE05': {
        'goal': 'BE05',
        'group': 'Operations',
        'description': utils.be_heading_text['BE05'],
        'goal_text': 'Operational emissions do not harm people or the environment',
        'input_type': 'Site',
        'input_type_plural': 'Sites',
    },
    'BE06': {
        'goal': 'BE06',
    },
    'BE12': {
        'goal': 'BE12',
        'group': 'Employees',
        'description': utils.be_heading_text['BE12'],
        'goal_text': 'Employees are subject to fair employment terms',
        'input_type': 'Site',
        'input_type_plural': 'Sites',
        'answer_header': 'Employees covered'
    },
}


def get_site_bes(benchmark_id, goal_code, goal_type=None):
    """
    energy / site
    """

    items = []
    employee_goals = ['BE10', 'BE11', 'BE12', 'BE13', 'BE14', 'BE20']
    inputs = m.Site.query.filter_by(benchmark_id=benchmark_id).all()
    input_ids = [s.id for s in inputs]

    if goal_type:
        questions = excel_files.be_questions[goal_code][goal_type]
    else:
        questions = excel_files.be_questions[goal_code]

    answers = {}
    search_items = []
    total_inputs = len(inputs)
    active_inputs = 0
    hidden_sites = []
    goal_info = m.GoalInfo.query.filter_by(code=goal_code, goal_type=goal_type, benchmark_id=benchmark_id).first()

    for input_obj in inputs:
        hidden = False
        if goal_code in employee_goals and (not input_obj.employees or input_obj.employees == 0):
            hidden_sites.append(input_obj.name)
            hidden = True

        search_items.append(input_obj.name)
        if input_obj.active:
            active_inputs += 1

        for key in questions:
            if key not in answers:
                answers[key] = {}

            answers[key][input_obj.id] = {
                'type': questions[key]['type'],
                'unit': goal_info.unit if goal_info else '',
                # 'unit': questions[key]['unit'],
                'input_id': input_obj.id,
                'input_name': input_obj.name,
                'input_status': input_obj.status,
                'active': True,
                'max': input_obj.employees,
                'country': input_obj.country,
                'value_bool': None,
                'value_text': None,
                'value_number': None,
                'hidden': hidden,
            }

    db_answers = m.GoalAnswer.query.filter(
        m.GoalAnswer.goal_code == goal_code,
        m.GoalAnswer.goal_type == goal_type,
        m.GoalAnswer.input_id.in_(input_ids)).all()


    for answer in db_answers:
        if answer.question_code in answers:
            answers[answer.question_code][answer.input_id].update({
                'value_bool': answer.value_bool,
                'value_text': answer.value_text,
                'value_number': answer.value_number,
                'active': answer.active,
                'id': answer.id,
            })

    answer_header = goal_defaults[goal_code].get('answer_header', 'Answer')

    headers = [
        {'text': 'Site', 'value': 'input_name', 'align': 'start', },
        {'text': answer_header, 'value': 'id', },
        {'text': 'Unit', 'value': 'unit',  'sortable': False},
    ]



    res = goal_defaults[goal_code]
    res.update({
        'questions': questions,
        'answers': answers,
        'headers': headers,
        'search_items': search_items,
        'progress': goal_info.progress if goal_info else 0,
        'total_inputs': total_inputs,
        'hidden_sites': hidden_sites,
        'unit': goal_info.unit if goal_info else False,
        'units': goal_units,
        'has_units': goal_info.uses_units if goal_info else False,

    })

    return res


def get_json_answers(goal_id, questions, goal_type=None):
    answers = m.GoalAnswer.query.filter_by(goal_code=goal_id).all()
    answer_lookup = {a.goal_code: a for a in answers}
    json_answers = {}

    keys = questions[goal_type].keys() if goal_type else questions.keys()

    for code in keys:
        question = questions[goal_type][code] if goal_type else questions[code]

        json_answers[code] = {
            'code': code,
            'type': question['type'],
            'text': question['text'],
            'value_bool': None,
            'value_text': None,
            'value_number': None,
        }
        if code in answer_lookup:
            json_answers[code]['value_number'] = answer_lookup[code].value_number
            json_answers[code]['value_text'] = answer_lookup[code].value_text
            json_answers[code]['value_bool'] = answer_lookup[code].value_bool

    return json_answers


def add_new_goal(input_id, goal_code, goal_type=None):
    print('adding new {}'.format(goal_code))
    be = m.Goal()
    be.input_id = input.id
    be.goal = goal_code
    if goal_type:
        be.type = goal_type
    db.session.add(be)
    db.session.commit()
    return be
