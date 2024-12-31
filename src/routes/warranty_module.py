from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request

#here modules

import logging

rmwa = Blueprint('routes_module_warranty', __name__)