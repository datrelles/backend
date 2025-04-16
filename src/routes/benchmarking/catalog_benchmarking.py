import logging
from datetime import datetime

from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.config.database import db
from src.models.catalogos_bench import Chasis, DimensionPeso, ElectronicaOtros

bench = Blueprint('routes_bench', __name__)
logger = logging.getLogger(__name__)

@bench.route('/insert_chasis', methods=["POST"])
@jwt_required()
def insert_chasis():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = Chasis(
            aros_rueda_posterior=data.get("aros_rueda_posterior"),
            neumatico_delantero=data.get("neumatico_delantero"),
            neumatico_trasero=data.get("neumatico_trasero"),
            suspension_delantera=data.get("suspension_delantera"),
            suspension_trasera=data.get("suspension_trasera"),
            frenos_delanteros=data.get("frenos_delanteros"),
            frenos_traseros=data.get("frenos_traseros"),
            aros_rueda_delantera=data.get("aros_rueda_delantera"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"message": "Chasis insertado correctamente", "codigo_chasis": nuevo.codigo_chasis})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_dimension', methods=["POST"])
@jwt_required()
def insert_dimension():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = DimensionPeso(
            altura_total=data.get("altura_total"),
            longitud_total=data.get("longitud_total"),
            ancho_total=data.get("ancho_total"),
            peso_seco=data.get("peso_seco"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Dimensión/Peso insertado", "codigo_dim_peso": nuevo.codigo_dim_peso})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_electronica_otros', methods=["POST"])
@jwt_required()
def insert_electronica_otros():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = ElectronicaOtros(
            capacidad_combustible=data.get("capacidad_combustible"),
            tablero=data.get("tablero"),
            luces_delanteras=data.get("luces_delanteras"),
            luces_posteriores=data.get("luces_posteriores"),
            garantia=data.get("garantia"),
            velocidad_maxima=data.get("velocidad_maxima"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Elementos de electronica/otros insertados", "codigo_electronica": nuevo.codigo_electronica})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500