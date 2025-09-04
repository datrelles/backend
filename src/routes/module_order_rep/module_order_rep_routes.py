from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.routes.module_order.db_connection import get_oracle_connection
from datetime import datetime
import uuid

rmorep= Blueprint('routes_module_order_rep', __name__)


