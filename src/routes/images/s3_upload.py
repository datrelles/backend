import dotenv
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
import os
from datetime import datetime
import logging
from src.config.database import db
from src.models.catalogos_bench import Imagenes

dotenv.load_dotenv()

s3 = Blueprint('routes_s3', __name__)
logger = logging.getLogger(__name__)

# Configuración de boto3 con credenciales y región
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-2'
)


#print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
#print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))


BUCKET_NAME = "shineray-imagenes-benchmarking"

@s3.route("/generate-upload-url", methods=["POST"])
@jwt_required()
@cross_origin()
def generate_upload_url():
    try:
        data = request.get_json()
        filename = data.get("filename")
        content_type = data.get("contentType")

        if not filename or not content_type:
            return jsonify({"error": "Parámetros faltantes: filename o contentType"}), 400

        # Generar URL firmada para carga
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': filename,
                'ContentType': content_type
            },
            ExpiresIn=300  # 5 minutos
        )

        # URL pública para visualización
        public_url = f"https://{BUCKET_NAME}.s3.us-east-2.amazonaws.com/{filename}"

        logger.info(f"Usuario {get_jwt_identity()} generó URL de carga para {filename}")
        return jsonify({
            "uploadUrl": presigned_url,
            "publicUrl": public_url
        })

    except Exception as e:
        logger.error(f"Error generando URL de carga firmada: {str(e)}")
        return jsonify({"error": "Error generando la URL"}), 500


@s3.route("/guardar-imagen", methods=["POST"])
@jwt_required()
@cross_origin()
def guardar_imagen_url():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        url = data.get("url")
        descripcion = data.get("descripcion")

        if not url:
            return jsonify({"error": "Falta la URL de la imagen"}), 400

        imagen = Imagenes(
            path_imagen=url,
            descripcion_imagen=descripcion or "Insertado desde carga masiva",
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(imagen)
        db.session.commit()

        return jsonify({"message": "Imagen registrada exitosamente"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error guardando URL de imagen: {str(e)}")
        return jsonify({"error": "Error guardando la URL de la imagen"}), 500


@s3.route('/insert_path_imagen', methods=["POST"])
@jwt_required()
@cross_origin()
def insert_path_imagen():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        nuevo = Imagenes(
            path_imagen=data.get("path_imagen"),
            descripcion_imagen=data.get("descripcion_imagen"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"message": "Imagen registrada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@s3.route('/eliminar-imagen', methods=["DELETE"])
@jwt_required()
def eliminar_imagen():
    try:
        data = request.get_json()
        path_imagen = data.get("path_imagen")

        if not path_imagen:
            return jsonify({"error": "Falta path_imagen"}), 400

        # Obtener el nombre del archivo desde la URL completa
        filename = path_imagen.split("/")[-1]

        # 1. Borrar en S3
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)

        # 2. Borrar en la base de datos
        imagen = db.session.query(Imagenes).filter_by(path_imagen=path_imagen).first()
        if imagen:
            db.session.delete(imagen)
            db.session.commit()
        else:
            return jsonify({"error": "Imagen no encontrada en base"}), 404

        return jsonify({"message": "Imagen eliminada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
