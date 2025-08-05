from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging

from sqlalchemy import text

from src.decorators import validate_json, handle_exceptions
from src.config.database import db
from src.models.users import Empresa
from src.validations import validar_number

activaciones_b = Blueprint('routes_activaciones', __name__)
logger = logging.getLogger(__name__)


@activaciones_b.route("/promotores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los promotores")
def get_proceso():
    sql = text("""
                SELECT e.identificacion,
                    e.apellido_paterno,
                    e.apellido_materno,
                    e.nombres
                FROM rh_empleados e
                WHERE e.activo = 'S'
                ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres
                """)
    rows = db.session.execute(sql).fetchall()
    result = [{"identificacion": row[0], "apellido_paterno": row[1], "apellido_materno": row[2], "nombres": row[3]} for
              row in rows]
    return jsonify(result)
