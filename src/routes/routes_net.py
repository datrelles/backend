from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from datetime import datetime, timedelta
from src.config.database import db
from flask_cors import cross_origin
from src.models.auth2.autorizacion import TiOpenAuthorization
from src.models.users import Usuario
from flask_mail import Message
import logging
from os import getenv
from src.models.entities.User import User
import secrets
import string
import requests
from src.apis.netsuite import rest_services
import requests
from flask import Flask, jsonify, request


net = Blueprint('routes_net', __name__)
logger = logging.getLogger(__name__)
NESTJS_CONSULTAR_URL = "http://localhost:5118/api-netsuite-dev/clientes/consultar"

@net.route('/get_costumer_list/')
@jwt_required()
@cross_origin()
def get_costumer_list():
    from src.app import generate_netsuite_token

    try:
        jwt_response = generate_netsuite_token()
        jwt_token = jwt_response.json.get("access_token")
        API_URL = rest_services + "/record/v1/customer/"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "No se pudo obtener la información"}), response.status_code

        return jsonify({'costumer_list': 'Otro caso diferente a 200'})

    except Exception as e:
        logger.exception(f"Error al editar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@net.route('/get_costumer/<id>')
@jwt_required()
@cross_origin()
def get_costumer(id):
    from src.app import generate_netsuite_token

    try:
        jwt_response = generate_netsuite_token()
        jwt_token = jwt_response.json.get("access_token")
        API_URL = rest_services + "/record/v1/customer/"+id

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "No se pudo obtener la información"}), response.status_code

        return jsonify({'costumer_list': 'Otro caso diferente a 200'})

    except Exception as e:
        logger.exception(f"Error al editar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500


@net.route('/create_costumer', methods=['POST'])
@jwt_required()
@cross_origin()
def create_cliente():
    from src.app import generate_netsuite_token

    try:
        jwt_response = generate_netsuite_token()
        jwt_token = jwt_response.json.get("access_token")
        API_URL = rest_services + "/record/v1/customer/"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        data = request.get_json()

        print(data)

        # Validación básica de campos requeridos
        required_fields = ["externalId", "isperson", "companyname", "salesrep", "comments", "email", "phone",
                           "altphone", "homephone", "subsidiary", "custentity_bit_lt_entitydocument",
                           "custentity_bit_lt_ei_commercial_name", "custentity_bit_lt_ei_company_name",
                           "custentity_bit_lt_ei_first_name", "custentity_bit_lt_ei_last_name",
                           "custentity_bit_lt_ei_other_name", "custentity_bit_lt_ei_second_name", "accountnumber",
                           "isinactive", "territory", "startdate", "reminderDays", "currency", "terms", "creditlimit",
                           "addressBook"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"El campo {field} es requerido"}), 400

        response = requests.post(API_URL, json=data, headers=headers)

        if response.status_code == 201:
            return jsonify(response.json()), 201
        else:
            return jsonify({"error": "No se pudo crear el cliente"}), response.status_code

    except Exception as e:
        logger.exception(f"Error al crear cliente: {str(e)}")
        return jsonify({'error': str(e)}), 500

@net.route('/get_item/', defaults={'id': None})
@net.route('/get_item/<id>')
@jwt_required()
@cross_origin()
def get_item(id):
    from src.app import generate_netsuite_token

    try:
        jwt_response = generate_netsuite_token()
        jwt_token = jwt_response.json.get("access_token")
        API_URL = rest_services + "/query/v1/suiteql?limit=10&offset=0"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "text/plain",
            "Prefer": "transient"
        }

        base_query = """
                SELECT item.externalid, item.ID, item.itemid, item.fullname as displayname, 
                       item.description as salesdescription, item.itemtype, item.CLASS, 
                       item.cseg_jm_marcas, item.isinactive, 
                       item.custitem_fte_item_l_itemcode as custitem_fte_item_l_itemcode_id, 
                       CUSTOMRECORD_FTE_ITEMCODE.name as custitem_fte_item_l_itemcode, 
                       item.custitem_jm_costo_precio, 
                       BUILTIN.CURRENCY(item.custitem_jm_costo_precio) custitem_jm_costo_precio, 
                       item.lastmodifieddate 
                FROM item, CUSTOMRECORD_FTE_ITEMCODE 
                WHERE item.custitem_fte_item_l_itemcode = CUSTOMRECORD_FTE_ITEMCODE.ID(+)
            """

        if id is not None and id != '':
            base_query += f" AND item.id = {id}"

        base_query += " ORDER BY item.externalid DESC"

        body = {
            "q": base_query
        }

        response = requests.post(API_URL, headers=headers, json=body)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "No se pudo obtener la información",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

    except Exception as e:
        logger.exception(f"Error al obtener item: {str(e)}")
        return jsonify({'error': str(e)}), 500


@net.route('/get_costumer', methods=['POST'])
# @jwt_required()
@cross_origin()
def consultar_cliente():
    from src.app import gen_api_token
    try:
        data = request.get_json()
        id_cliente_core = data.get("idClienteCore")

        if id_cliente_core is None:
            return jsonify({"error": "idClienteCore es obligatorio"}), 400

        try:
            id_cliente_core = int(id_cliente_core)
        except (ValueError, TypeError):
            return jsonify({"error": "idClienteCore debe ser un número válido"}), 400

        jwt_token = gen_api_token()
        token = jwt_token.json.get("token")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f"{getenv('NESTJS_URL')}clientes/consultar?idClienteCore={id_cliente_core}"

        response = requests.get(url, headers=headers)

        if response.status_code not in [200, 201]:
            return jsonify({
                "error": "Error al consultar al backend NestJS",
                "detalle": response.text
            }), 500

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@net.route('/create_customer', methods=['POST'])
#@jwt_required()
@cross_origin()
def crear_cliente():
    from src.app import gen_api_token
    data = request.get_json()
    url = f"{getenv('NESTJS_URL')}clientes/crear"
    jwt_token = gen_api_token()
    token = jwt_token.json.get("token")

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Fallo al conectarse con la API: {str(e)}")