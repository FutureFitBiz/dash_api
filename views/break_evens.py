import time
import re
import copy

from flask import jsonify, request, render_template, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app import app, bcrypt, settings, db, surveys
from lib.email import send_reset_password_email
import utils as utils
import models as m


@app.route('/be/sankey', methods=['GET'])
@jwt_required
def get_a_sankey():
    """
    ! Currently based on risk profile goals
    """
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    risk_profile = m.RiskProfile.query.filter_by(company_id=user.company.id).first()
    convert_risk = {
        'Unlikely': 0,
        'Low': 1,
        'Moderate': 2,
        'High': 3
    }

    be_nodes = []
    sdg_nodes = []
    links = []

    for goal in risk_profile.goals:
        sdgs = utils.sdg_links[goal.code]

        for sdg in sdgs:
            risk_value = convert_risk[goal.risk]

            if risk_value > 0:
                be_nodes.append(goal.code)
                sdg_nodes.append(sdg)
                sdg_link_text = surveys.sdg_to_be_tooltips[goal.code].get(str(sdg), '')
                links.append({
                    'target': sdg,
                    'source': goal.code,
                    'sdg': sdg,
                    'sdg_text': utils.sdgs[str(sdg)]['title'],
                    'code': goal.code,
                    'be_text': surveys.be_text_lookup['break_evens'][goal.code]['long_name'],
                    'value': risk_value,
                    'risk': goal.risk,
                    'sdg_link_text': sdg_link_text,
                })

    goal_risks = {goal.code: goal.risk for goal in risk_profile.goals}
    be_nodes = list(set(be_nodes))
    sdg_nodes = list(set(sdg_nodes))

    sortings = [
        be_risk_sdg_number(be_nodes, sdg_nodes, copy.deepcopy(links), convert_risk, goal_risks),
        be_number_sdg_number(be_nodes, sdg_nodes, copy.deepcopy(links)),
        be_number_sdg_risk(be_nodes, sdg_nodes, copy.deepcopy(links), convert_risk, goal_risks),
    ]

    return jsonify({
        'sortings': sortings,
        'goal_risks': goal_risks,
    })


def be_risk_sdg_number(be_nodes, sdg_nodes, links, convert_risk, goal_risks):
    be_nodes = sorted(be_nodes, key=lambda x: (convert_risk[goal_risks[x]],), reverse=True)
    sdg_nodes = sorted(sdg_nodes)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even risk (High-Low) / SDG numerical (default)'
    res['id'] = 0
    return res


def be_number_sdg_number(be_nodes, sdg_nodes, links):
    be_nodes = sorted(be_nodes)
    sdg_nodes = sorted(sdg_nodes)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even numerical / SDG numerical'
    res['id'] = 1
    return res


def be_number_sdg_risk(be_nodes, sdg_nodes, links, convert_risk, goal_risks):
    be_nodes = sorted(be_nodes)
    sdg_risks = {}
    for link in links:
        sdg = link['sdg']
        if sdg not in sdg_risks:
            sdg_risks[sdg] = 0
        sdg_risks[sdg] += link['value']

    sdg_nodes = sorted(sdg_nodes, key=lambda x: sdg_risks[x], reverse=True)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even numerical / SDG risk (High-Low)'
    res['id'] = 2
    return res


def finish_linking_nodes(be_nodes, sdg_nodes, links):
    nodes = []
    id = 0
    lookup = {}
    all_nodes = be_nodes + sdg_nodes

    for node in all_nodes:
        nodes.append({'name': node})
        lookup[node] = id
        id += 1

    for link in links:
        source = link['source']
        link['source'] = lookup[source]
        target = link['target']
        link['target'] = lookup[target]

    return {
        'nodes': nodes,
        'links': links
    }
