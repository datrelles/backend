from src.function_jwt import validate_token, write_token
from flask import request, jsonify, Blueprint
from src import oracle


auth = Blueprint("auth", __name__)


@auth.route("/get-token", methods=["POST"])
def get_token():
    data = request.get_json()
    usuario = data['username'].upper()
    array = oracle.execute_sql('select USERNAME from all_users u where u.USERNAME = ' + "'"+usuario+"'",'stock', 'stock')
    if array:
        if array[0][0] == usuario:
            return write_token(data=request.get_json())
    else:
        response = jsonify({"message": "User not found"})
        response.status_code = 404
        return response


@auth.route("/verify-token")
def verify():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token, output=True)