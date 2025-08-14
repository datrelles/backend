from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
import os
import logging
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from src.routes.module_order.db_connection import get_oracle_connection
import dotenv
dotenv.load_dotenv()

pdf_s3 = Blueprint('pdf_s3', __name__)
logger = logging.getLogger(__name__)

BUCKET_NAME = "shineray-images-benchmarking"  # Cambia por tu bucket de PDFs

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-1'
)

@pdf_s3.route('/upload-pdf', methods=['POST'])
@jwt_required()
def upload_pdf():
    try:
        user = get_jwt_identity()
        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo PDF"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "El archivo no tiene nombre"}), 400

        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.pdf'):
            return jsonify({"error": "Solo se permiten archivos PDF"}), 400

        # Normalizar el nombre del archivo (sin espacios, mayúsculas)
        filename_normalized = filename.replace(' ', '_').upper()
        nombre_base = Path(filename_normalized).stem.strip().upper()

        # Buscar y eliminar PDFs previos con el mismo nombre base (ignorar extensión)
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        for item in response.get('Contents', []):
            key = item['Key']
            key_base = Path(key).stem.strip().upper()
            if key_base == nombre_base and key != filename_normalized:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
                logger.info(f"Archivo duplicado eliminado: {key}")

        # Subir el nuevo archivo PDF
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            filename_normalized,
            ExtraArgs={'ContentType': 'application/pdf'}
        )

        public_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename_normalized}"
        logger.info(f"Usuario {user} subió PDF: {filename_normalized}")

        return jsonify({"url": public_url, "message": "Archivo PDF subido correctamente"})

    except Exception as e:
        logger.error(f"Error subiendo PDF: {str(e)}")
        return jsonify({"error": f"Error subiendo PDF: {str(e)}"}), 500


# 2. SUBIDA DE PDF + REGISTRO EN BD
@pdf_s3.route('/upload_pdf_detail', methods=['POST'])
@jwt_required()
def upload_pdf_with_regiter():
    c = None
    try:
        user = request.form.get('userShineray')
        empresa = request.form.get('empresa')
        agencia = request.form.get('systemShineray')
        nombre_s3 = request.form.get('nombre_s3')  # <-- Nuevo parámetro opcional

        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo PDF"}), 400
        if not empresa or not agencia:
            return jsonify({"error": "Faltan parámetros: empresa y agencia"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "El archivo no tiene nombre"}), 400

        # Determinar el nombre final para S3
        if nombre_s3:
            # Normaliza el nombre y fuerza la extensión
            nombre_s3 = secure_filename(nombre_s3).replace(' ', '_').upper()
            if not nombre_s3.lower().endswith('.pdf'):
                nombre_s3 += '.PDF'
            filename_normalized = nombre_s3
        else:
            # Si no se envía, nombre por default
            filename_normalized = "PDF_CATALOGO_MAYOREO_CURRENT.PDF"

        nombre_base = Path(filename_normalized).stem.strip().upper()

        # Elimina PDFs previos con el mismo nombre base (ignorando extensión)
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        for item in response.get('Contents', []):
            key = item['Key']
            key_base = Path(key).stem.strip().upper()
            if key_base == nombre_base and key != filename_normalized:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
                logger.info(f"Archivo duplicado eliminado: {key}")

        # Subir el nuevo PDF
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            filename_normalized,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        public_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{filename_normalized}"

        # REGISTRO EN BASE DE DATOS
        ahora = datetime.now()

        c = get_oracle_connection()
        cur = c.cursor()

        # Verifica si existe un registro previo (misma empresa, nombre_pdf y agencia)
        select_sql = """
        SELECT COUNT(*) FROM TG_PDF_UPLOADS
        WHERE empresa = :empresa AND nombre_pdf = :nombre_pdf AND agencia = :agencia
        """
        cur.execute(select_sql, empresa=int(empresa), nombre_pdf=filename_normalized, agencia=agencia)
        exists = cur.fetchone()[0]

        if exists:
            update_sql = """
            UPDATE TG_PDF_UPLOADS
            SET usuario_ultima_modificacion = :usuario,
                fecha_ultima_modificacion   = :fecha
            WHERE empresa   = :empresa
              AND nombre_pdf = :nombre_pdf
              AND agencia    = :agencia
            """
            cur.execute(update_sql, usuario=user, fecha=ahora,
                        empresa=int(empresa), nombre_pdf=filename_normalized, agencia=agencia)
        else:
            insert_sql = """
            INSERT INTO TG_PDF_UPLOADS (
                empresa, nombre_pdf, agencia, usuario_ultima_modificacion, fecha_ultima_modificacion
            ) VALUES (
                :empresa, :nombre_pdf, :agencia, :usuario, :fecha
            )
            """
            cur.execute(insert_sql, empresa=int(empresa), nombre_pdf=filename_normalized, agencia=agencia,
                        usuario=user, fecha=ahora)

        c.commit()

        # Obtén los detalles para la respuesta
        cur.execute("""
        SELECT empresa, nombre_pdf, agencia, usuario_ultima_modificacion, fecha_ultima_modificacion
        FROM TG_PDF_UPLOADS
        WHERE empresa = :empresa AND nombre_pdf = :nombre_pdf AND agencia = :agencia
        """, empresa=int(empresa), nombre_pdf=filename_normalized, agencia=agencia)
        row = cur.fetchone()
        cur.close()

        response_data = {
            "url": public_url,
            "empresa": row[0],
            "nombre_pdf": row[1],
            "agencia": row[2],
            "usuario_ultima_modificacion": row[3],
            "fecha_ultima_modificacion": row[4].strftime('%Y-%m-%d %H:%M:%S'),
            "message": "Archivo PDF subido y registrado correctamente"
        }
        return jsonify(response_data)

    except Exception as ex:
        if c:
            c.rollback()
        logger.error(f"Error subiendo PDF: {str(ex)}")
        return jsonify({"error": f"Error subiendo PDF: {str(ex)}"}), 500
    finally:
        if c:
            c.close()


@pdf_s3.route('/consulta_pdf', methods=['GET'])
@jwt_required()
def consulta_pdf():
    c = None
    try:
        nombre_pdf = request.args.get('nombre_pdf')
        timestamp_str = request.args.get('fecha')

        if not nombre_pdf or not timestamp_str:
            return jsonify({"error": "Parámetros requeridos: nombre_pdf y fecha (timestamp en segundos)"}), 400

        try:
            timestamp = float(timestamp_str)
        except Exception as e:
            return jsonify({"error": f"Formato de fecha inválido (se esperaba timestamp): {e}"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        # Consulta universal y robusta para Oracle:
        sql_latest = """
        SELECT empresa, nombre_pdf, agencia, usuario_ultima_modificacion, fecha_ultima_modificacion
        FROM TG_PDF_UPLOADS
        WHERE nombre_pdf = :nombre_pdf
        AND fecha_ultima_modificacion = (
            SELECT MAX(fecha_ultima_modificacion)
            FROM TG_PDF_UPLOADS
            WHERE nombre_pdf = :nombre_pdf
        )
        """

        cur.execute(sql_latest, nombre_pdf=nombre_pdf)
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "No se encontró registro"}), 404

        fecha_ultima_modificacion = row[4]
        timestamp_bd = int(fecha_ultima_modificacion.timestamp())

        if int(timestamp) == timestamp_bd:
            return jsonify({"pdf_current": True})
        else:
            bucket_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{nombre_pdf}"
            result = {
                "empresa": row[0],
                "nombre_pdf": row[1],
                "agencia": row[2],
                "usuario_ultima_modificacion": row[3],
                "fecha_ultima_modificacion": fecha_ultima_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_timestamp": timestamp_bd,
                "pdf_current": False,
                "url": bucket_url
            }
            return jsonify(result)

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@pdf_s3.route('/consulta_pdf_lasted', methods=['GET'])
@jwt_required()
def consulta_pdf_lasted():
    c = None
    try:
        nombre_pdf = request.args.get('nombre_pdf')
        timestamp_str = request.args.get('fecha')

        c = get_oracle_connection()
        cur = c.cursor()

        # --- LISTAR ÚLTIMOS POR (empresa, nombre_pdf) CUANDO NO HAY PARÁMETROS ---
        if not nombre_pdf and not timestamp_str:
            sql_all = """
                SELECT empresa, nombre_pdf, agencia, usuario_ultima_modificacion, fecha_ultima_modificacion, descripcion
                FROM (
                    SELECT t.*,
                           ROW_NUMBER() OVER (
                               PARTITION BY t.empresa, t.nombre_pdf
                               ORDER BY t.fecha_ultima_modificacion DESC
                           ) AS rn
                    FROM TG_PDF_UPLOADS t
                )
                WHERE rn = 1
                ORDER BY fecha_ultima_modificacion DESC
            """
            cur.execute(sql_all)
            rows = cur.fetchall()
            cur.close()

            data = [{
                "empresa": r[0],
                "key": r[1],
                "agencia": r[2],
                "usuario_ultima_modificacion": r[3],
                "fecha_ultima_modificacion": r[4].strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_timestamp": int(r[4].timestamp()),
                "label": r[5]

            } for r in rows]

            return jsonify(data)

        # --- LÓGICA EXISTENTE PARA CUANDO SE PASAN PARÁMETROS ---
        if not nombre_pdf or not timestamp_str:
            return jsonify({"error": "Parámetros requeridos: nombre_pdf y fecha (timestamp en segundos)"}), 400

        try:
            timestamp = float(timestamp_str)
        except Exception as e:
            return jsonify({"error": f"Formato de fecha inválido (se esperaba timestamp): {e}"}), 400

        sql_latest = """
        SELECT empresa, nombre_pdf, agencia, usuario_ultima_modificacion, fecha_ultima_modificacion
        FROM TG_PDF_UPLOADS
        WHERE nombre_pdf = :nombre_pdf
        AND fecha_ultima_modificacion = (
            SELECT MAX(fecha_ultima_modificacion)
            FROM TG_PDF_UPLOADS
            WHERE nombre_pdf = :nombre_pdf
        )
        """
        cur.execute(sql_latest, nombre_pdf=nombre_pdf)
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "No se encontró registro"}), 404

        fecha_ultima_modificacion = row[4]
        timestamp_bd = int(fecha_ultima_modificacion.timestamp())

        if int(timestamp) == timestamp_bd:
            return jsonify({"pdf_current": True})
        else:
            bucket_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{nombre_pdf}"
            return jsonify({
                "empresa": row[0],
                "nombre_pdf": row[1],
                "agencia": row[2],
                "usuario_ultima_modificacion": row[3],
                "fecha_ultima_modificacion": fecha_ultima_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                "fecha_timestamp": timestamp_bd,
                "pdf_current": False,
                "url": bucket_url
            })

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()
