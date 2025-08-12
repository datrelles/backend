from flask import Blueprint, jsonify, request, abort
import logging
import datetime
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import requests
from os import getenv
from msal import ConfidentialClientApplication


bi = Blueprint('routes_bi', __name__)

logger = logging.getLogger(__name__)

CLIENT_ID = getenv("CLIENT_ID_BI")
CLIENT_SECRET = getenv("CLIENT_SECRET_BI")
TENANT_ID = getenv("TENANT_ID")
GROUP_ID = getenv("GROUP_ID")
REPORT_ID = getenv("REPORT_ID")

if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID, GROUP_ID, REPORT_ID]):
    raise RuntimeError("Faltan variables de entorno requeridas para BI")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

def get_service_principal_token():

    app_msal = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    token_response = app_msal.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in token_response:

        logging.error("MSAL error: %s", token_response)
        abort(500, description="No se pudo obtener access_token desde Azure AD.")

    return token_response["access_token"]

def compute_cedula_vendedor(username: str) -> str:

    if not username or len(username) < 2:
        return username
    return f"{username[:-1]}-{username[-1]}"

@bi.route('/embed-token/<id>', methods=["POST"])
@jwt_required()
@cross_origin()
def get_embed_token(id):
    user = id
    access_token = get_service_principal_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "accessLevel": "View"
    }

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{REPORT_ID}/GenerateToken"

    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    if resp.status_code != 200:
        logging.error("Power BI GenerateToken error %s: %s", resp.status_code, resp.text)
        abort(resp.status_code, description="Fallo al generar embed token de Power BI.")

    embed = resp.json()

    embed_url = f"https://app.powerbi.com/reportEmbed?reportId={REPORT_ID}&groupId={GROUP_ID}"

    return jsonify({
        "token": embed.get("token"),
        "tokenId": embed.get("tokenId"),
        "expiration": embed.get("expiration"),
        "embedUrl": embed_url,
        "reportId": REPORT_ID,
        "cedula_vendedor": user,
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }), 200

