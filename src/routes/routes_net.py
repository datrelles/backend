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
from src.models.entities.User import User
import secrets
import string
import requests
from src.apis.netsuite import rest_services


net = Blueprint('routes_net', __name__)
logger = logging.getLogger(__name__)
from flask_jwt_extended import create_access_token

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
