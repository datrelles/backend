from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from src.config.database import db
from src.models.proveedores import tc_coa_tipo_contribuyente, st_banco, tc_instituciones_multicash, tc_prov_cta_multicash
import logging
from datetime import datetime
rmc = Blueprint('routes_module_contabilidad', __name__)

@rmc.route('/get_tipo_contribuyente', methods=['GET'])
@jwt_required()
def get_tipo_contribuyente():
    try:
        # Query all record from the table
        tipos_contribuyentes = db.session.query(tc_coa_tipo_contribuyente).all()

        # Serialyze the data into a JSON-compatible format

        result = [
            {
                "cod_tipo_contribuyente": tipo.cod_tipo_contribuyente,
                "descripcion": tipo.descripcion
            }
            for tipo in tipos_contribuyentes
        ]

        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error al obtener los tipos de contribuyente: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@rmc.route('/get_bancos', methods=['GET'])
@jwt_required()
def get_bancos():
    try:
        # Consultar todos los registros de la tabla st_banco
        bancos = st_banco.query().filter(st_banco.es_multicash == 1).all()

        # Serializar los datos en un formato compatible con JSON
        result = [
            {
                "cod_banco": banco.cod_banco,
                "nombre": banco.nombre
            }
            for banco in bancos
        ]

        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error al obtener los bancos: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@rmc.route('/get_instituciones_multicash', methods=['GET'])
@jwt_required()
def get_instituciones_multicash():
    try:
        # Obtener el parámetro cod_banco de la solicitud
        cod_banco = request.args.get('cod_banco')

        # Verificar si se proporcionó el filtro
        if not cod_banco:
            return jsonify({"error": "El parámetro 'cod_banco' es obligatorio"}), 400

        # Consultar las instituciones filtradas por cod_banco
        instituciones = tc_instituciones_multicash.query().filter(tc_instituciones_multicash.cod_banco == cod_banco).all()

        # Serializar los datos en un formato compatible con JSON
        result = [
            {
                "codigo": institucion.codigo,
                "nombre": institucion.nombre,
                "cod_banco": institucion.cod_banco
            }
            for institucion in instituciones
        ]

        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error al obtener las instituciones multicash: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@rmc.route('/get_prov_cta_multicash', methods=['GET'])
@jwt_required()
def get_prov_cta_multicash():
    try:
        # Obtener el parámetro ruc de la solicitud
        ruc = request.args.get('ruc')

        # Verificar si se proporcionó el filtro
        if not ruc:
            return jsonify({"error": "El parámetro 'ruc' es obligatorio"}), 400

        # Consultar las cuentas filtradas por ruc
        cuentas = tc_prov_cta_multicash.query().filter(tc_prov_cta_multicash.ruc == ruc).all()

        # Serializar los datos en un formato compatible con JSON
        result = [
            {
                "empresa": cuenta.empresa,
                "ruc": cuenta.ruc,
                "codigo_institucion": cuenta.codigo_institucion,
                "num_cuenta": cuenta.num_cuenta,
                "tipo_cuenta": cuenta.tipo_cuenta,
                "nombre_banco": cuenta.nombre_banco,
                "tipo_identificacion": cuenta.tipo_identificacion,
                "identificacion_titular": cuenta.identificacion_titular,
                "nombre_titular": cuenta.nombre_titular,
                "cod_banco": cuenta.cod_banco
            }
            for cuenta in cuentas
        ]

        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error al obtener las cuentas multicash: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
