import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from src.config.database import db
from src.models.catalogos_bench import ModeloVersionRepuesto

bench_rep = Blueprint('routes_bench_rep', __name__)
logger = logging.getLogger(__name__)


@bench_rep.route("/comparar_modelo_repuesto", methods=["POST"])
@jwt_required()
def comparar_modelo_repuesto():
    data = request.get_json()
    modelo_id = data.get("modelo_version")
    repuestos = data.get("repuestos", [])

    if not modelo_id or not repuestos:
        return jsonify({"error": "Faltan datos"}), 400

    compatibles = db.session.query(ModeloVersionRepuesto.codigo_prod_externo) \
        .filter(ModeloVersionRepuesto.codigo_mod_vers_repuesto == modelo_id) \
        .all()

    compatibles_set = {r[0] for r in compatibles}

    resultado = []
    for rep in repuestos:
        resultado.append({
            "codigo_prod_externo": rep,
            "compatible": rep in compatibles_set
        })

    return jsonify(resultado)
