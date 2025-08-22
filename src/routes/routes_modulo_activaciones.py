from functools import reduce

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging

from sqlalchemy import text

from src.decorators import validate_json, handle_exceptions
from src.config.database import db
from src.exceptions import validation_error
from src.models.catalogos_bench import Marca, Segmento
from src.models.clientes import cliente_hor, Cliente
from src.models.modulo_activaciones import st_activacion, st_cliente_direccion_guias, rh_empleados, st_promotor_tienda, \
    ad_usuarios, st_encuesta, st_form_promotoria, st_mod_seg_frm_prom, st_mar_seg_frm_prom, st_info_tienda
from src.models.modulo_formulas import validar_empresa, st_modelo_comercial
from src.models.proveedores import TgModeloItem, Proveedor
from src.models.users import Empresa, Usuario, tg_rol_usuario
from src.validations import validar_number, validar_varchar, validar_fecha
from src.validations.alfanumericas import validar_hora

activaciones_b = Blueprint('routes_activaciones', __name__)
logger = logging.getLogger(__name__)

COD_MODELO_CATAL_ACTIV = "ACT"
CODIGOS_MARCAS_PROPIAS = [94, 99]  # 3, 18, 22


def calcular_diferencia_horas_en_minutos(inicio, fin):
    inicio = validar_hora('hora_inicio', inicio, devuelve_string=False)
    fin = validar_hora('hora_fin', fin, devuelve_string=False)
    if inicio >= fin:
        raise validation_error(mensaje='La hora de inicio debe ser menor a la hora de fin')
    return (fin - inicio).total_seconds() / 60


@activaciones_b.route("/promotores/<usuario_oracle>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el promotor")
def get_promotor(usuario_oracle):
    usuario_oracle = validar_varchar('usuario_oracle', usuario_oracle, 20)
    usuario = db.session.get(Usuario, usuario_oracle)
    if not usuario:
        mensaje = 'Usuario {} inexistente'.format(usuario_oracle)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    ad_usuario = db.session.get(ad_usuarios, usuario.usuario_oracle)
    if not ad_usuario:
        mensaje = 'AD usuario {} inexistente'.format(usuario_oracle)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    promotor = db.session.get(rh_empleados, ad_usuario.identificacion)
    if not promotor:
        mensaje = 'Promotor {} inexistente'.format(ad_usuario.identificacion)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(promotor.to_dict())


@activaciones_b.route("/promotores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los promotores")
def get_promotores():
    sql = text("""
                SELECT
                    e.identificacion,
                    e.apellido_paterno,
                    e.apellido_materno,
                    e.nombres
                FROM
                    rh_empleados e
                WHERE
                    e.activo = 'S' AND
                    EXISTS (
                        SELECT 1
                        FROM st_promotor_tienda p
                        WHERE p.cod_promotor = e.identificacion
                    )
                ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres
                """)
    rows = db.session.execute(sql).fetchall()
    result = [{"identificacion": row[0], "apellido_paterno": row[1], "apellido_materno": row[2], "nombres": row[3]} for
              row in rows]
    return jsonify(result)


@activaciones_b.route("/promotores/<cod_promotor>/clientes", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los clientes del promotor")
def get_clientes_por_promotor(cod_promotor):
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    sql = text("""
                SELECT
                    DISTINCT(p.cod_cliente) AS cod_cliente,
                    ch.cod_tipo_clienteh,
                    SUBSTR(c.nombre, 1) AS nombre
                FROM
                    ST_PROMOTOR_TIENDA p
                INNER JOIN
                    CLIENTE_HOR ch
                    ON
                    ch.empresah = p.empresa AND
                    ch.cod_clienteh = p.cod_cliente
                INNER JOIN
                    CLIENTE c
                    ON
                    c.empresa = ch.empresah AND
                    c.cod_cliente = ch.cod_clienteh
                WHERE
                    p.cod_promotor = :cod_promotor
                ORDER BY
                    nombre
                """)
    rows = db.session.execute(sql, {"cod_promotor": cod_promotor}).fetchall()
    result = [{"cod_cliente": row[0], "cod_tipo_clienteh": row[1], "nombre": row[2]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/promotores/<cod_promotor>/clientes/<cod_cliente>/direcciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las tiendas del promotor por cliente")
def get_direcciones_por_promotor_y_cliente(cod_promotor, cod_cliente):
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    sql = text("""
                SELECT
                   g.cod_direccion,
                   SUBSTR(g.ciudad, 1) AS ciudad,
                   SUBSTR(CASE
                     WHEN b.nombre IS NULL THEN
                       CASE
                         WHEN g.nombre IS NOT NULL THEN g.nombre
                         ELSE 'SIN NOMBRE'
                       END
                     ELSE b.nombre
                   END, 1) AS nombre,
                   SUBSTR(g.direccion, 1) AS direccion
                FROM
                   ST_PROMOTOR_TIENDA p
                INNER JOIN
                   ST_CLIENTE_DIRECCION_GUIAS g
                   ON
                   g.empresa = p.empresa AND
                   g.cod_cliente = p.cod_cliente AND
                   g.cod_direccion = p.cod_direccion_guia
                LEFT JOIN
                   ST_BODEGA_CONSIGNACION b
                   ON
                   b.empresa = g.empresa AND
                   b.ruc_cliente = g.cod_cliente AND
                   b.cod_direccion = g.cod_direccion
                WHERE
                  g.es_activo = 1 AND
                  p.cod_promotor = :cod_promotor AND
                  p.cod_cliente = :cod_cliente
                """)
    rows = db.session.execute(sql, {"cod_promotor": cod_promotor, "cod_cliente": cod_cliente}).fetchall()
    result = [{"cod_direccion": row[0], "ciudad": row[1], "nombre": row[2], "direccion": row[3]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/proveedores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los proveedores")
def get_proveedores(empresa):
    empresa = validar_empresa('empresa', empresa)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = text("""
                SELECT
                    p.cod_proveedor,
                    REPLACE(TRIM(p.nombre), CHR(9), '') AS nombre
                FROM
                    proveedor p
                WHERE
                    p.empresa = :empresa
                ORDER BY p.nombre
                """)
    rows = db.session.execute(sql, {"empresa": empresa}).fetchall()
    result = [{"cod_proveedor": row[0], "nombre": row[1]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/tipos-activacion", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los tipos de activación")
def get_tipos_activacion(empresa):
    empresa = validar_empresa('empresa', empresa)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = text("""
                SELECT
                    m.cod_modelo,
                    m.cod_item,
                    m.nombre
                FROM
                    tg_modelo_item m
                WHERE
                    m.empresa = :empresa AND
                    m.cod_modelo = :cod_modelo
                ORDER BY m.nombre
                """)
    rows = db.session.execute(sql, {"empresa": empresa, "cod_modelo": COD_MODELO_CATAL_ACTIV}).fetchall()
    result = [{"cod_modelo": row[0], "cod_item": row[1], "nombre": row[2]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/activaciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las activaciones")
def get_activaciones_por_promotor(empresa):
    empresa = validar_number('empresa', empresa, 2)
    cod_promotor = validar_varchar('cod_promotor', request.args.get('cod_promotor'), 20, False)
    cod_cliente = validar_varchar('cod_cliente', request.args.get("cod_cliente"), 14, False)
    fecha_inicio = validar_fecha('fecha_inicio', request.args.get("fecha_inicio"), False)
    fecha_fin = validar_fecha('fecha_fin', request.args.get("fecha_fin"), False)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if (fecha_inicio and not fecha_fin) or (not fecha_inicio and fecha_fin):
        mensaje = 'Debes proveer las fechas de inicio y fin para filtrar por ese parámetro'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 400
    query = st_activacion.query()
    activaciones = query.filter(st_activacion.empresa == empresa)
    if cod_promotor:
        if not db.session.get(rh_empleados, cod_promotor):
            mensaje = 'Promotor {} inexistente'.format(cod_promotor)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        activaciones = activaciones.filter(st_activacion.cod_promotor == cod_promotor)
    if cod_cliente:
        if not db.session.get(cliente_hor, (empresa, cod_cliente)):
            mensaje = 'Cliente {} inexistente'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        activaciones = activaciones.filter(st_activacion.cod_cliente == cod_cliente)
    if fecha_inicio and fecha_fin:
        if fecha_inicio >= fecha_fin:
            mensaje = 'La fecha de inicio debe ser menor a la de fin'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        activaciones = activaciones.filter(st_activacion.audit_fecha_ing.between(fecha_inicio, fecha_fin))
    activaciones = activaciones.all()
    return jsonify(
        st_activacion.to_list(activaciones, ["promotor", "cliente", "cliente_hor", "tienda", "bodega", "proveedor"]))


@activaciones_b.route("/empresas/<empresa>/activaciones", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la activación")
def post_activacion(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    activacion = st_activacion(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(rh_empleados, data['cod_promotor']):
        mensaje = 'Promotor {} inexistente'.format(data['cod_promotor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, data['cod_cliente'])):
        mensaje = 'Cliente {} inexistente'.format(data['cod_cliente'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_cliente_direccion_guias, (empresa, data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Tienda {} inexistente'.format(data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_promotor_tienda,
                          (data['empresa'], data['cod_promotor'], data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Promotor {} no vinculado a la tienda {}'.format(data['cod_promotor'], data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 403
    if not db.session.get(Proveedor, (empresa, data['cod_proveedor'])):
        mensaje = 'Proveedor {} inexistente'.format(data['cod_proveedor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(TgModeloItem, (empresa, data['cod_modelo_act'], data['cod_item_act'])):
        mensaje = 'Tipo de activación {} inexistente'.format(data['cod_item_act'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    activacion.total_minutos = calcular_diferencia_horas_en_minutos(activacion.hora_inicio, activacion.hora_fin)
    db.session.add(activacion)
    db.session.commit()
    mensaje = 'Se registró la activación {}'.format(activacion.cod_activacion)
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@activaciones_b.route("/activaciones/<cod_activacion>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar la activación")
def put_activacion(cod_activacion, data):
    cod_activacion = validar_number('cod_activacion', cod_activacion, 22)
    activacion = db.session.get(st_activacion, cod_activacion)
    if not activacion:
        mensaje = 'Activación {} inexistente'.format(cod_activacion)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    data = {**data, 'cod_activacion': cod_activacion, 'empresa': activacion.empresa,
            'cod_promotor': activacion.cod_promotor}
    st_activacion(**data)
    if not db.session.get(Cliente, (data['empresa'], data['cod_cliente'])):
        mensaje = 'Cliente {} inexistente'.format(data['cod_cliente'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_cliente_direccion_guias, (data['empresa'], data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Tienda {} inexistente'.format(data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_promotor_tienda,
                          (data['empresa'], data['cod_promotor'], data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Promotor {} no vinculado a la tienda {}'.format(data['cod_promotor'], data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 403
    if not db.session.get(Proveedor, (data['empresa'], data['cod_proveedor'])):
        mensaje = 'Proveedor {} inexistente'.format(data['cod_proveedor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(TgModeloItem, (data['empresa'], data['cod_modelo_act'], data['cod_item_act'])):
        mensaje = 'Tipo de activación {} inexistente'.format(data['cod_item_act'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    activacion.cod_cliente = data['cod_cliente']
    activacion.cod_tienda = data['cod_tienda']
    activacion.cod_proveedor = data['cod_proveedor']
    activacion.cod_modelo_act = data['cod_modelo_act']
    activacion.cod_item_act = data['cod_item_act']
    activacion.animadora = data['animadora']
    activacion.fecha_act = data['fecha_act']
    activacion.hora_inicio = data['hora_inicio']
    activacion.hora_fin = data['hora_fin']
    activacion.total_minutos = calcular_diferencia_horas_en_minutos(activacion.hora_inicio, activacion.hora_fin)
    activacion.num_exhi_motos = data['num_exhi_motos']
    activacion.audit_usuario_mod = text('user')
    activacion.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = 'Se actualizó la activación {}'.format(activacion.cod_activacion)
    logger.info(mensaje)
    return '', 204


@activaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/direcciones-guia/<cod_direccion>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar la dirección guia")
def put_direccion_guia(empresa, cod_cliente, cod_direccion, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    cod_direccion = validar_number('cod_direccion', cod_direccion, 3)
    data = {'empresa': empresa, 'cod_cliente': cod_cliente, 'cod_direccion': cod_direccion, **data}
    st_cliente_direccion_guias(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, cod_cliente)):
        mensaje = 'Cliente {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    direccion_guia = db.session.get(st_cliente_direccion_guias, (empresa, cod_cliente, cod_direccion))
    if not direccion_guia:
        mensaje = 'Dirección guía {} inexistente'.format(cod_direccion)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    direccion_guia.ciudad = data['ciudad']
    direccion_guia.direccion = data.get('direccion')
    direccion_guia.direccion_larga = data.get('direccion_larga')
    direccion_guia.cod_zona_ciudad = data.get('cod_zona_ciudad')
    direccion_guia.es_activo = data['es_activo']
    nombre = data.get('nombre')
    if nombre:
        direccion_guia.nombre = nombre
    db.session.commit()
    mensaje = 'Se actualizó la dirección guía {}'.format(direccion_guia.cod_direccion)
    logger.info(mensaje)
    return '', 204


@activaciones_b.route("/canal-promotor/<usuario_oracle>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el canal del promotor")
def get_canal_promotor(usuario_oracle):
    usuario_oracle = validar_varchar('usuario_oracle', usuario_oracle, 20)
    usuario = db.session.get(Usuario, usuario_oracle)
    if not usuario:
        mensaje = 'Usuario {} inexistente'.format(usuario_oracle)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    rol = tg_rol_usuario.query().filter(tg_rol_usuario.empresa == usuario.empresa_actual,
                                        tg_rol_usuario.usuario == usuario.usuario_oracle,
                                        tg_rol_usuario.activo == 1).first()
    if not rol:
        mensaje = 'El usuario {} no tiene ningún rol activo asignado'.format(usuario_oracle)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify({'canal': rol.cod_rol})


@activaciones_b.route("/empresas/<empresa>/encuestas", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las encuestas")
def get_encuestas(empresa):
    empresa = validar_number('empresa', empresa, 2)
    cod_promotor = validar_varchar('cod_promotor', request.args.get('cod_promotor'), 20, False)
    cod_cliente = validar_varchar('cod_cliente', request.args.get("cod_cliente"), 14, False)
    fecha_inicio = validar_fecha('fecha_inicio', request.args.get("fecha_inicio"), False)
    fecha_fin = validar_fecha('fecha_fin', request.args.get("fecha_fin"), False)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if (fecha_inicio and not fecha_fin) or (not fecha_inicio and fecha_fin):
        mensaje = 'Debes proveer las fechas de inicio y fin para filtrar por ese parámetro'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 400
    query = st_encuesta.query()
    encuestas = query.filter(st_encuesta.empresa == empresa)
    if cod_promotor:
        if not db.session.get(rh_empleados, cod_promotor):
            mensaje = 'Promotor {} inexistente'.format(cod_promotor)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        encuestas = encuestas.filter(st_encuesta.cod_promotor == cod_promotor)
    if cod_cliente:
        if not db.session.get(cliente_hor, (empresa, cod_cliente)):
            mensaje = 'Cliente {} inexistente'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        encuestas = encuestas.filter(st_encuesta.cod_cliente == cod_cliente)
    if fecha_inicio and fecha_fin:
        if fecha_inicio >= fecha_fin:
            mensaje = 'La fecha de inicio debe ser menor a la de fin'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        encuestas = encuestas.filter(st_encuesta.audit_fecha_ing.between(fecha_inicio, fecha_fin))
    encuestas = encuestas.all()
    return jsonify(
        st_encuesta.to_list(encuestas, ["promotor", "cliente", "cliente_hor", "tienda", "bodega"]))


@activaciones_b.route("/empresas/<empresa>/encuestas", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la encuesta")
def post_encuesta(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    encuesta = st_encuesta(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(rh_empleados, data['cod_promotor']):
        mensaje = 'Promotor {} inexistente'.format(data['cod_promotor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, data['cod_cliente'])):
        mensaje = 'Cliente {} inexistente'.format(data['cod_cliente'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_cliente_direccion_guias, (empresa, data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Tienda {} inexistente'.format(data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_promotor_tienda,
                          (data['empresa'], data['cod_promotor'], data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Promotor {} no vinculado a la tienda {}'.format(data['cod_promotor'], data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 403
    ad_usuario = ad_usuarios.query().filter(ad_usuarios.identificacion == data['cod_promotor']).first()
    if not ad_usuario:
        mensaje = 'AD usuario del promotor {} inexistente'.format(data['cod_promotor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    rol = tg_rol_usuario.query().filter(tg_rol_usuario.usuario == ad_usuario.codigo_usuario,
                                        tg_rol_usuario.activo == 1).first()
    if not rol:
        mensaje = 'El usuario {} no tiene ningún rol activo asignado'.format(ad_usuario.codigo_usuario)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if rol.cod_rol != 'PROM_RET' and data.get('prec_vis_corr'):
        mensaje = "Solo los promotores de retail pueden responder a la pregunta de 'precios visibles y correctos'"
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    if data.get('estado_publi') != 0 and data.get('estado_publi_obs'):
        mensaje = "Solo si la respuesta del estado de publicidad de la marca es no, debe existir observación al respecto"
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    if data.get('confor_compe') is None and data.get('confor_compe_obs'):
        mensaje = "Si la conformidad del incentivo actual de la competencia no aplica, no debe existir observación al respecto"
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(encuesta)
    db.session.commit()
    mensaje = 'Se registró la encuesta {}'.format(encuesta.cod_encuesta)
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@activaciones_b.route("/catalogo-segmentos", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el catálogo de segmentos")
def get_catalogo_segmentos():
    sql = text("""
                SELECT
                    DISTINCT(s.nombre_segmento)
                FROM
                    st_segmento s
                ORDER BY
                    s.nombre_segmento
                """)
    rows = db.session.execute(sql).fetchall()
    result = [{"nombre_segmento": row[0]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/segmentos", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los segmentos")
def get_segmentos():
    sql = text("""
                SELECT
                    s.codigo_segmento,
                    s.codigo_linea,
                    s.codigo_modelo_comercial,
                    s.nombre_segmento,
                    m.codigo_marca,
                    m.nombre_modelo
                FROM st_segmento s
                INNER JOIN
                    st_modelo_comercial m
                ON
                    s.codigo_modelo_comercial = m.codigo_modelo_comercial AND
                    s.codigo_marca = m.codigo_marca
                WHERE
                    s.estado_segmento = 1 AND
                    m.codigo_marca IN (""" + ','.join(map(str, CODIGOS_MARCAS_PROPIAS)) + """)
                ORDER BY s.nombre_segmento, m.nombre_modelo
                """)
    rows = db.session.execute(sql).fetchall()
    result = [
        {"codigo_segmento": row[0], "codigo_linea": row[1], "codigo_modelo_comercial": row[2],
         "nombre_segmento": row[3], "codigo_marca": row[4],
         "nombre_modelo": row[5]} for
        row in rows]
    return jsonify(result)


@activaciones_b.route("/marcas", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las marcas")
def get_marcas():
    marcas = db.session.query(Marca).filter(Marca.estado_marca == 1).order_by(Marca.nombre_marca).all()
    result = [{"codigo_marca": marca.codigo_marca, "nombre_marca": marca.nombre_marca} for marca in marcas]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/tiendas/<cod_tienda>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar información de la tienda")
def get_info_tienda(empresa, cod_cliente, cod_tienda):
    empresa = validar_number('empresa', empresa, 2)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    cod_tienda = validar_number('cod_tienda', cod_tienda, 3)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, cod_cliente)):
        mensaje = 'Cliente {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    info_tienda = db.session.get(st_info_tienda, (empresa, cod_cliente, cod_tienda))
    if not info_tienda:
        mensaje = 'No existe información de la tienda {}'.format(cod_tienda)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(info_tienda.to_dict(['cliente', 'cliente_hor', 'tienda', 'bodega']))


@activaciones_b.route("/empresas/<empresa>/tiendas", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar información de las tiendas")
def get_info_tiendas(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_info_tienda.query()
    info_tiendas = query.filter(st_info_tienda.empresa == empresa)
    return jsonify(st_info_tienda.to_list(info_tiendas, ['cliente', 'cliente_hor', 'tienda', 'bodega']))


@activaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/tiendas/<cod_tienda>", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar información de la tienda")
def post_info_tienda(empresa, cod_cliente, cod_tienda, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    cod_tienda = validar_number('cod_tienda', cod_tienda, 3)
    data = {'empresa': empresa, 'cod_cliente': cod_cliente, 'cod_tienda': cod_tienda, **data}
    info_tienda = st_info_tienda(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, cod_cliente)):
        mensaje = 'Cliente {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_info_tienda, (empresa, cod_cliente, cod_tienda)):
        mensaje = 'La información de la tienda {} ya existe'.format(cod_tienda)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(info_tienda)
    db.session.commit()
    mensaje = 'Se registró la información de la tienda {}'.format(info_tienda.cod_tienda)
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@activaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/tiendas/<cod_tienda>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar la información de la tienda")
def put_info_tienda(empresa, cod_cliente, cod_tienda, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    cod_tienda = validar_number('cod_tienda', cod_tienda, 3)
    data = {'empresa': empresa, 'cod_cliente': cod_cliente, 'cod_tienda': cod_tienda, **data}
    st_info_tienda(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, cod_cliente)):
        mensaje = 'Cliente {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    info_tienda = db.session.get(st_info_tienda, (empresa, cod_cliente, cod_tienda))
    if not info_tienda:
        mensaje = 'Información de la tienda {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    info_tienda.correo_tienda = data['correo_tienda']
    info_tienda.prom_venta_tienda = data['prom_venta_tienda']
    info_tienda.nom_jefe_tienda = data['nom_jefe_tienda']
    info_tienda.cel_jefe_tienda = data['cel_jefe_tienda']
    info_tienda.audit_usuario_mod = text('user')
    info_tienda.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = 'Se actualizó la información de la tienda {}'.format(info_tienda.cod_tienda)
    logger.info(mensaje)
    return '', 204


@activaciones_b.route("/empresas/<empresa>/formularios-promotoria", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los formularios de promotoría")
def get_forms_promotoria(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_form_promotoria.query()
    formularios = query.filter(st_form_promotoria.empresa == empresa)
    return jsonify(st_form_promotoria.to_list(formularios,
                                              ['cliente', 'cliente_hor', 'tienda', 'bodega', 'modelos_segmento',
                                               'marcas_segmento']))


@activaciones_b.route("/empresas/<empresa>/formularios-promotoria", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar el formulario de promotoría")
def post_form_promotoria(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    modelos_segmento = data.pop("modelos_segmento", [])
    marcas_segmento = data.pop("marcas_segmento", [])
    data = {'empresa': empresa, **data}
    if data.get('total_motos_shi') is not None:
        raise validation_error(no_requeridos=['total_motos_shi'])
    if data.get('total_motos_piso') is not None:
        raise validation_error(no_requeridos=['total_motos_piso'])
    data['total_motos_shi'] = 0
    data['total_motos_piso'] = 0
    formulario = st_form_promotoria(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(rh_empleados, data['cod_promotor']):
        mensaje = 'Promotor {} inexistente'.format(data['cod_promotor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Cliente, (empresa, data['cod_cliente'])):
        mensaje = 'Cliente {} inexistente'.format(data['cod_cliente'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_cliente_direccion_guias, (empresa, data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Tienda {} inexistente'.format(data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_promotor_tienda,
                          (data['empresa'], data['cod_promotor'], data['cod_cliente'], data['cod_tienda'])):
        mensaje = 'Promotor {} no vinculado a la tienda {}'.format(data['cod_promotor'], data['cod_tienda'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 403
    for modelo in modelos_segmento:
        if not db.session.get(Segmento, (
                modelo['cod_segmento'], modelo['cod_linea'], modelo['cod_modelo_comercial'], modelo['cod_marca'])):
            mensaje = 'Segmento {} inexistente'.format(modelo['cod_segmento'])
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
    for marca in marcas_segmento:
        if not db.session.get(Marca, marca['cod_marca']):
            mensaje = 'Marca {} inexistente'.format(marca['cod_marca'])
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
    formulario.total_motos_shi = reduce(lambda total, item: total + item['cantidad'], modelos_segmento, 0)
    formulario.total_motos_piso = formulario.total_motos_shi + reduce(lambda total, item: total + item['cantidad'],
                                                                      marcas_segmento, 0)
    db.session.add(formulario)
    db.session.flush()
    db.session.refresh(formulario)
    if modelos_segmento:
        formulario.modelos_segmento = [st_mod_seg_frm_prom(**{**item, "cod_form": formulario.cod_form}) for item in
                                       modelos_segmento]
    if marcas_segmento:
        formulario.marcas_segmento = [st_mar_seg_frm_prom(**{**item, "cod_form": formulario.cod_form}) for item in
                                      marcas_segmento]
    db.session.commit()
    mensaje = 'Se registró el formulario {}'.format(formulario.cod_form)
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201
