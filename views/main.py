import time
import re
import datetime
import json

from flask import jsonify, request, render_template, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app import app, bcrypt, settings, db, excel_files
from lib.email import send_reset_password_email
import utils as utils
import models as m
import config.settings as settings

if settings.DEBUG:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/check', methods=['GET'])
def check_route():
    res = excel_files.goal_risk_defaults
    res = excel_files.valueweb
    res = excel_files.risk_questions['product']
    res = excel_files.risk_question_sections
    return jsonify(res)


@app.route('/bug', methods=['POST'])
@jwt_required
def save_a_bug():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    bug = m.Bug()
    bug.text = request.json.get('text')
    bug.user_id = user.id
    db.session.add(bug)
    db.session.commit()
    return jsonify('saved')


@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"message": "Missing username/password"})

    app_name = request.json.get('app', '').lower()
    user = m.User.query.filter_by(email=email).first()
    benchmark_id = user.current_benchmark_id

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username/password"})

    company = None
    if user.company:
        company = user.company
    else:
        return jsonify({'status': 'error', 'message': 'user has no company'})

    if not benchmark_id:
        b = m.Benchmark()
        now = datetime.datetime.now()
        iso_date = now.isoformat()
        start_month = iso_date[:10]
        year = iso_date[:4]
        iso_date_next_year = (now + datetime.timedelta(weeks=52)).isoformat()

        b.company_id = company.id
        b.start_month = start_month
        b.end_month = iso_date_next_year[:10]
        b.year = year
        db.session.add(b)
        db.session.commit()
        #todo, redo
        user.current_benchmark_id = b.id
        benchmark_id = b.id
        print('--new benchmark')
        db.session.commit()

    assessment = m.RiskAssessment.query.filter_by(benchmark_id=benchmark_id).first()
    if not assessment:
        # print('creating risk assessment')
        ass = m.RiskAssessment()
        ass.benchmark_id = benchmark_id
        db.session.add(ass)
        db.session.commit()

    goal_infos = m.GoalInfo.query.filter_by(benchmark_id=benchmark_id).all()

    if not goal_infos:
        for code in utils.break_evens:
            gi = m.GoalInfo()
            gi.benchmark_id = benchmark_id
            gi.code = code
            db.session.add(gi)

        db.session.commit()

    res = {
        'token': create_access_token(identity=email),
        'user': {
            'onboarding_complete': user.onboarding_complete,
            'be_onboarding_complete': user.be_onboarding_complete,
            'pp_onboarding_complete': user.pp_onboarding_complete,
            'email': user.email,
            'first': user.first,
            'last': user.last,
        },
        'company': {
            'business_activity': company.business_activity,
            'name': company.name,
            'description': company.description,
            'id': company.id,
        }
    }

    return jsonify(res)


@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    password = request.json.get('password')
    company_name = request.json.get('company_name')
    duplicate = m.User.query.filter_by(email=email).first()
    if duplicate:
        return jsonify({'status': 'error', "message": "Email already in use"})

    company = m.Company()
    company.name = company_name
    db.session.add(company)

    user = m.User()
    user.email = email
    user.password = utils.new_bcrypt_password(password)
    user.company = company
    db.session.add(user)
    db.session.commit()

    b = m.Benchmark()
    now = datetime.datetime.now()
    iso_date = now.isoformat()
    start_month = iso_date[:10]
    year = iso_date[:4]
    iso_date_next_year = (now + datetime.timedelta(weeks=52)).isoformat()

    b.company_id = company.id
    b.start_month = start_month
    b.end_month = iso_date_next_year[:10]
    b.year = year
    db.session.add(b)
    db.session.commit()
    user.current_benchmark_id = b.id
    benchmark_id = b.id

    ass = m.RiskAssessment()
    ass.benchmark_id = benchmark_id
    db.session.add(ass)

    for code in utils.break_evens:
        gi = m.GoalInfo()
        gi.benchmark_id = benchmark_id
        gi.code = code
        db.session.add(gi)

    db.session.commit()

    res = {
        'token': create_access_token(identity=email),
        'new_user': True,
        'user': {
            'onboarding_complete': False,
            'be_onboarding_complete': False,
            'pp_onboarding_complete': False,
            'email': email,
            'first': '',
            'last': '',
        },
        'company': {
            'business_activity': company.business_activity,
            'name': company.name,
            'description': '',
            'id': '',
        }
    }

    return jsonify(res)


@app.route('/user/info', methods=['POST'])
@jwt_required
def save_user_info():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    company_name = request.json.get('company_name')
    business_activity = request.json.get('business_activity')
    password = request.json.get('password')
    email = request.json.get('email')
    reset_risks = request.json.get('reset_risks')

    if company_name:
        user.company.name = company_name
    if business_activity:
        user.company.business_activity = business_activity
    if password:
        user.password = utils.new_bcrypt_password(password)
    if email:
        user.email = email

    if reset_risks:
        risk_profile = m.RiskProfile.query.filter_by(company_id=user.company.id).first()
        utils.apply_heatmap_answers(risk_profile, user.company)
        utils.score_goals(risk_profile)

    db.session.commit()

    return jsonify({
        'email': user.email,
        'company_name': user.company.name,
        'business_activity': user.company.business_activity,
    })


@app.route('/user/intro', methods=['POST'])
@jwt_required
def save_user_intro():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    company = user.company
    company.name = request.json.get('company_name')
    company.business_activity = request.json.get('heatmap')
    user.onboarding_complete = True
    db.session.commit()

    risk_profile = m.RiskProfile.query.filter_by(company_id=company.id).first()
    utils.apply_heatmap_answers(risk_profile, company)
    utils.score_goals(risk_profile)

    return jsonify({
        'heatmap': company.business_activity,
        'company_name': company.name,
    })


@app.route('/test/email/<type>')
def test_email(type):
    res = 'unknown'
    if type == 'welcome':
        res = render_template('emails/welcome.html', password='testpassword', email='test@test.com')
    if type == 'reset':
        res = render_template('emails/reset_password.html', password='testpassword')
    return res


@app.route('/reset/password', methods=['POST'])
def reset_password():
    email = request.json.get('email')
    user = m.User.query.filter_by(email=email).first()
    data = {'status': 'success'}

    if user:
        try:
            new_password = utils.random_uuid_code()
            send_reset_password_email(email, new_password)
            user.password = utils.new_bcrypt_password(new_password)
            db.session.commit()
            data['message'] = 'email sent'
        except Exception as e:
            time.sleep(2)
            data = {'status': 'error', 'message': 'error sending email'}
            print(e)
    else:
        time.sleep(2)
        data = {'status': 'error', 'message': 'email not found'}

    return jsonify(data)


@app.route('/user/profile', methods=['POST'])
@jwt_required
def post_update_profile():
    email = get_jwt_identity()
    data = request.json.get('data')
    user = m.User.query.filter_by(email=email).first()
    user.email = data['email']
    user.first = data.get('first')
    user.last = data.get('last')

    pw = data.get('password')
    new_pw = data.get('new_password')
    if pw and new_pw:
        if bcrypt.check_password_hash(user.password, pw):
            user.password = utils.new_bcrypt_password(new_pw)
        else:
            return jsonify({'status': 'error', 'message': 'Wrong password'})

    db.session.commit()
    return jsonify({'message': 'profile updated'})


@app.route('/layout/<name>', methods=['GET'])
@jwt_required
def get_action_survey(name):
    lookup = {
        'impact': surveys.pp_action,
        'facets': surveys.facets,
        'properties': surveys.properties,
        'add_edit_product': surveys.add_edit_product,
        'business_activity_questions': surveys.business_activity_questions,
        'heatmap_template_questions': surveys.heatmap_template_questions,
    }
    return jsonify(lookup.get(name))
