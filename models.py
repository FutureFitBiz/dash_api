from app import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    business_activity = db.Column(db.String(120), nullable=True)
    risk_profile = db.relationship('RiskProfile', backref='company', cascade="delete", lazy=True)
    benchmarks = db.relationship('Benchmark', backref='company', cascade="all,delete", lazy=True)
    users = db.relationship('User', backref='company', lazy=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    current_benchmark_id = db.Column(db.Integer, nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first = db.Column(db.String(120), nullable=True)
    last = db.Column(db.String(120), nullable=True)
    admin = db.Column(db.Boolean, nullable=True, default=False)
    investor = db.Column(db.Boolean, nullable=True, default=False)
    onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)
    be_onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)
    pp_onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)
    testing = db.Column(db.Boolean, nullable=True, default=False)


class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class RiskProfile(db.Model):
    """the inital assessment, so you can be assigned a risk per BE"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status = db.Column(db.String(40), nullable=True)

    goals = db.relationship('RiskProfileGoal', backref="risk_profile", cascade="all,delete", lazy='subquery')


class RiskProfileGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    risk_profile_id = db.Column(db.Integer, db.ForeignKey('risk_profile.id'))
    risk = db.Column(db.String(12), nullable=True)
    code = db.Column(db.String(6), nullable=True)
    saved = db.Column(db.Boolean, nullable=True, default=False)
    answers = db.relationship('RiskProfileAnswer', backref="risk_profile_goal", cascade="all,delete", lazy='subquery')


class RiskProfileAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('risk_profile_goal.id'))
    code = db.Column(db.String(20), nullable=True)  # question code
    value = db.Column(db.Boolean, nullable=True)


class Benchmark(db.Model):
    """ """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status = db.Column(db.String(40), nullable=True)
    start_month = db.Column(db.String(180), nullable=True)
    end_month = db.Column(db.String(180), nullable=True)
    year = db.Column(db.String(180), nullable=False)
    note = db.Column(db.String(180), nullable=True)


class Site(db.Model):
    """ """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey('benchmark.id'))

    # not used atm
    status = db.Column(db.String(40), nullable=True)
    active = db.Column(db.Boolean, default=True)

    employees = db.Column(db.Integer, nullable=True)

    name = db.Column(db.String(180), nullable=False)
    country = db.Column(db.String(180), nullable=True)
    note = db.Column(db.String(180), nullable=True)


class Purchase(db.Model):
    """ """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey('benchmark.id'))
    status = db.Column(db.String(40), nullable=True)
    name = db.Column(db.String(180), nullable=False)
    type = db.Column(db.String(180), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    traceable = db.Column(db.Boolean, default=True)


class NaturalResource(db.Model):
    """ """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(180), nullable=False)
    status = db.Column(db.String(40), nullable=True)
    type = db.Column(db.String(180), nullable=False)
    benchmark_id = db.Column(db.Integer, db.ForeignKey('benchmark.id'))
    country = db.Column(db.String(180), nullable=False)
    value = db.Column(db.Float, nullable=True)


class GoalInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(5), nullable=True)
    goal_type = db.Column(db.String(120), nullable=True)
    progress = db.Column(db.Float, nullable=True)
    risk = db.Column(db.String(120), nullable=True)
    is_default_risk = db.Column(db.Boolean, default=False)
    uses_units = db.Column(db.Boolean, default=True)
    unit = db.Column(db.String(120), nullable=True)


class GoalAnswer(db.Model):
    """ """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    input_id = db.Column(db.Integer, nullable=False)
    goal_type = db.Column(db.String(120), nullable=True)
    goal_code = db.Column(db.String(5), nullable=True)
    question_code = db.Column(db.String(120), nullable=True)
    type = db.Column(db.String(180), nullable=True)

    value_bool = db.Column(db.Boolean, default=True)
    value_text = db.Column(db.String(180), nullable=True)
    value_number = db.Column(db.Float, nullable=True)


class RiskAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, nullable=False)
    is_product = db.Column(db.Boolean, nullable=True)


class RiskAssessmentAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    benchmark_id = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(20), nullable=True)
    risk = db.Column(db.String(20), nullable=True)
    group = db.Column(db.String(120), nullable=True)
    value = db.Column(db.Boolean, default=None)
