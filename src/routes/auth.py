from src.function_jwt import validate_token, write_token
from flask import request, jsonify, Blueprint
from src import oracle


auth = Blueprint("auth2", __name__)


@auth.route("/get-token", methods=["POST"])
def get_token():
    data = request.get_json()
    usuario = data['username'].upper()
    password = data['password']
    if oracle.connection_test(usuario, password):
        return write_token(data=request.get_json())
    else:
        response = jsonify({"message": "Users or Password  is not correct"})
        response.status_code = 404
        return response


@auth.route("/verify-token")
def verify():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token, output=True)