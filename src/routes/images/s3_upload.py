from pathlib import Path
import dotenv
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
import os
from datetime import datetime
import logging
from sqlalchemy import func
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
    region_name='us-east-1'
)

#print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
#print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))


BUCKET_NAME = "shineray-images-benchmarking"

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

        nombre_base = Path(filename).stem.strip().upper()
        filename_normalizado = filename.strip().replace(" ", "_").upper()

        # Eliminar duplicados en S3 que tengan mismo nombre base
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        for item in response.get('Contents', []):
            key = item['Key']
            key_base = Path(key).stem.strip().upper()
            if key_base == nombre_base and key != filename_normalizado:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)

        # Generar URL firmada
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': filename_normalizado,
                'ContentType': content_type
            },
            ExpiresIn=300
        )

        # URL pública para visualización
        public_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename}"

        logger.info(f"Usuario {get_jwt_identity()} generó URL para: {filename_normalizado}")

        return jsonify({
            "uploadUrl": presigned_url,
            "publicUrl": public_url
        })

    except Exception as e:
        logger.error(f"Error generando URL firmada: {str(e)}")
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

        if not url or not descripcion:
            return jsonify({"error": "Faltan parámetros obligatorios"}), 400

        nombre_base = Path(descripcion).stem.strip().upper()
        nuevo_nombre_archivo = Path(url).name.strip()

        # Eliminar duplicados en S3 con mismo nombre base pero distinta extensión
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        for item in response.get('Contents', []):
            key = item['Key']
            key_base = Path(key).stem.strip().upper()

            if key_base == nombre_base and key != nuevo_nombre_archivo:
                print(f"Eliminando duplicado en S3: {key}")
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)

        # Buscar en base de datos
        imagen_por_nombre = db.session.query(Imagenes).filter(
            func.upper(func.trim(func.regexp_replace(Imagenes.descripcion_imagen, r'\.[^.]+$', ''))) == nombre_base
        ).first()

        if imagen_por_nombre:
            imagen_por_nombre.path_imagen = url
            imagen_por_nombre.descripcion_imagen = descripcion
            imagen_por_nombre.usuario_modifica = user
            imagen_por_nombre.fecha_modificacion = datetime.now()
            mensaje = "Imagen actualizada con nuevo archivo."
        else:
            nueva = Imagenes(
                path_imagen=url,
                descripcion_imagen=descripcion,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nueva)
            mensaje = "Imagen registrada exitosamente."

        db.session.commit()
        return jsonify({"message": mensaje})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error guardando imagen: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

def obtener_nombre_base(nombre_archivo):
    return os.path.splitext(nombre_archivo)[0].strip().lower()

@s3.route('/insert_path_imagen', methods=["POST"])
@jwt_required()
@cross_origin()
def insert_path_imagen():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        path_imagen = data.get("path_imagen")
        descripcion = data.get("descripcion_imagen")

        if not path_imagen or not descripcion:
            return jsonify({"error": "Faltan datos"}), 400

        nombre_base = obtener_nombre_base(descripcion)

        # Buscar imagen existente por nombre base (ignorando extensión)
        imagen_existente = db.session.query(Imagenes).filter(
            func.lower(func.trim(func.regexp_replace(Imagenes.descripcion_imagen, r'\.[^.]+$', ''))) == nombre_base
        ).first()

        if imagen_existente:
            imagen_existente.path_imagen = path_imagen
            imagen_existente.descripcion_imagen = descripcion
            imagen_existente.usuario_modifica = user
            imagen_existente.fecha_modificacion = datetime.now()
            mensaje = "Imagen actualizada correctamente"
        else:
            nueva_imagen = Imagenes(
                path_imagen=path_imagen,
                descripcion_imagen=descripcion,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nueva_imagen)
            mensaje = "Imagen registrada correctamente"

        db.session.commit()
        return jsonify({"message": mensaje})

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

#---------------------------------------------------------
#---------------------- OBTIENE IMAGEN PARA BENCH REPUESTOS

@s3.route('/repuesto-url', methods=['GET'])
def get_repuesto_url():
    cod_producto = request.args.get("cod_producto")
    if not cod_producto:
        return jsonify({"error": "Código de repuesto no especificado"}), 400

    object_key = f"repuestos/{cod_producto}.jpg"
    public_url = f"https://shineray-public.s3.amazonaws.com/{object_key}"

    return jsonify({"url": public_url})