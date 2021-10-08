import time

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, settings, db, excel_files
import utils as utils
import models as m



@app.route('/progress_summary', methods=['GET'])
@jwt_required
def get_progress_summary():
    goals = []

    return jsonify({
        'goals': goals
    })
