from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.proveedores import Proveedor, TgModeloItem
from src.models.tipo_comprobante import TipoComprobante
from src.models.producto_despiece import StProductoDespiece
from src.models.despiece import StDespiece
from src.models.orden_compra import StOrdenCompraCab,StOrdenCompraDet,StTracking,StPackinglist
from src.models.embarque_bl import StEmbarquesBl, StTrackingBl, StNaviera, StEmbarqueContenedores
from src.models.entities.vt_detalles_orden_general import VtDetallesOrdenGeneral
from src.config.database import db
from src.models.tipo_aforo import StTipoAforo
from src.models.aduana import StAduRegimen
from sqlalchemy import and_, or_, func, tuple_
import datetime
from decimal import Decimal
from datetime import datetime, date
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import requests

bpcustom = Blueprint('routes_custom', __name__)

logger = logging.getLogger(__name__)

#CONSULTAS GET CON PARAMETROS

@bpcustom.route('/productos_param') #sw para mostrar los productos por parametros
@jwt_required()
@cross_origin()
def obtener_productos_param():
    cod_producto = request.args.get('cod_producto', None)
    empresa = request.args.get('empresa', None)
    nombre = request.args.get('nombre', None)

    query = Producto.query()
    if cod_producto:
        query = query.filter(Producto.cod_producto.like(f'%{cod_producto.upper()}%'))
    if empresa:
        query = query.filter(Producto.empresa == empresa)
    if nombre:
        query = query.filter(Producto.nombre.like(f'%{nombre.upper()}%'))

    productos = query.all()

    serialized_detalles = []
    for producto in productos:
        empresa = producto.empresa if producto.empresa else ""
        cod_producto = producto.cod_producto if producto.cod_producto else ""
        tipo_inventario = producto.tipo_inventario if producto.tipo_inventario else ""
        cod_marca = producto.cod_marca if producto.cod_marca else ""
        cod_alterno = producto.cod_alterno if producto.cod_alterno else ""
        nombre = producto.nombre if producto.nombre else ""
        cod_barra = producto.cod_barra if producto.cod_barra else ""
        useridc = producto.useridc if producto.useridc else ""
        presentacion = producto.presentacion if producto.presentacion else ""
        volumen = producto.volumen if producto.volumen else ""
        grado = producto.grado if producto.grado else ""
        costo = producto.costo if producto.costo else ""
        activo = producto.activo if producto.activo else ""
        cod_modelo = producto.cod_modelo if producto.cod_modelo else ""
        cod_item = producto.cod_item if producto.cod_item else ""
        cod_modelo_cat = producto.cod_modelo_cat if producto.cod_modelo_cat else ""
        cod_item_cat = producto.cod_item_cat if producto.cod_item_cat else ""
        serie = producto.serie if producto.serie else ""
        ice = producto.ice if producto.ice else ""
        cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
        serialized_detalles.append({
            'empresa': empresa,
            'cod_producto': cod_producto,
            'tipo_inventario': tipo_inventario,
            'cod_marca': cod_marca,
            'cod_alterno': cod_alterno,
            'nombre': nombre,
            'cod_barra': cod_barra,
            'useridc': useridc,
            'presentacion': presentacion,
            'volumen': volumen,
            'grado': grado,
            'costo': costo,
            'activo': activo,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'cod_modelo_cat': cod_modelo_cat,
            'cod_item_cat': cod_item_cat,
            'serie': serie,
            'ice': ice,
            'cod_producto_modelo': cod_producto_modelo
        })
    return jsonify(serialized_detalles)

@bpcustom.route('/proveedores_param') #sw para mostrar los proveedores con ingreso de parametros de empresa,nombre y cod_proveedor
@jwt_required()
@cross_origin()
def obtener_proveedores_param():

    cod_proveedor = request.args.get('cod_proveedor', None)
    empresa = request.args.get('empresa', None)
    nombre = request.args.get('nombre', None)    

    query = Proveedor.query()
    if cod_proveedor:
        query = query.filter(Proveedor.cod_proveedor == cod_proveedor)
    if empresa:
        query = query.filter(Proveedor.empresa == empresa)
    if nombre:
        query = query.filter(Proveedor.nombre == nombre)

    proveedores = query.all()
    serialized_proveedores = []
    for proveedor in proveedores:
        empresa = proveedor.empresa if proveedor.empresa else ""
        cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
        nombre = proveedor.nombre if proveedor.nombre else ""
        direccion = proveedor.direccion if proveedor.direccion else ""
        telefono = proveedor.telefono if proveedor.telefono else ""
        #cod_proveedores = [cod_proveedor.to_dict() for cod_proveedor in proveedor.cod_proveedores]
        serialized_proveedores.append({
            'empresa': empresa,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'direccion': direccion,
            'telefono': telefono
        })
    return jsonify(serialized_proveedores)

@bpcustom.route('/tipo_comprobante_param')
@jwt_required()
@cross_origin()
def obtener_tipo_comprobante_param():

    empresa = request.args.get('empresa', None)
    nombre = request.args.get('nombre', None)
    cod_sistema = request.args.get('cod_sistema',None)

    query = TipoComprobante.query()
    if empresa:
        query = query.filter(TipoComprobante.empresa == empresa)
    if nombre:
        query = query.filter(TipoComprobante.nombre == nombre)
    if cod_sistema:
        query = query.filter(TipoComprobante.cod_sistema == cod_sistema)
    
    comprobantes = query.all()
    serialized_comprobantes = []
    for comprobante in comprobantes:
        empresa = comprobante.empresa if comprobante.empresa else ""
        tipo = comprobante.tipo if comprobante.tipo else ""
        nombre = comprobante.nombre if comprobante.nombre else ""
        cod_sistema = comprobante.cod_sistema if comprobante.cod_sistema else ""
        serialized_comprobantes.append({
            'empresa': empresa,
            'tipo': tipo,
            'nombre': nombre,
            'cod_sistema': cod_sistema,
        })
    return jsonify(serialized_comprobantes)

@bpcustom.route('/prod_despiece_param')
@jwt_required()
@cross_origin()
def obtener_prod_despiece_param():

    empresa = request.args.get('empresa',None)
    cod_producto = request.args.get('cod_producto',None)
    cod_despiece = request.args.get('cod_despiece', None)

    query = StProductoDespiece.query()
    if empresa:
        query = query.filter(StProductoDespiece.empresa == empresa)
    if cod_producto:
        query = query.filter(StProductoDespiece.cod_producto == cod_producto)
    if cod_despiece:
        query = query.filter(StProductoDespiece.cod_despiece == cod_despiece)
    
    prod_despiece = query.all()
    serialized_prodespiece = []
    for prod in prod_despiece:
        cod_despiece = prod.cod_despiece if prod.cod_despiece else ""
        secuencia = prod.secuencia if prod.secuencia else ""
        cod_color = prod.cod_color if prod.cod_color else ""
        empresa = prod.empresa if prod.empresa else ""
        cod_producto = prod.cod_producto if prod.cod_producto else ""
        fecha_creacion = prod.fecha_creacion if prod.fecha_creacion else ""
        serialized_prodespiece.append({
            'cod_despiese': cod_despiece,
            'secuencia': secuencia,
            'cod_color': cod_color,
            'empresa': empresa,
            'cod_producto': cod_producto,
            'fecha_creacion': fecha_creacion,
        })
    return jsonify(serialized_prodespiece)

@bpcustom.route('/nombre_productos_param')
@jwt_required()
@cross_origin()
def obtener_nombre_productos_param():

    empresa = request.args.get('empresa',None)
    cod_despiece = request.args.get('cod_despiece', None)

    query = StDespiece.query()
    if empresa:
        query = query.filter(StDespiece.empresa == empresa)
    if cod_despiece:
        query = query.filter(StDespiece.cod_despiece == cod_despiece)
    
    nom_productos = query.all()
    serialized_nomproductos = []
    for nombres in nom_productos:
        cod_despiece = nombres.cod_despiece if nombres.cod_despiece else ""
        empresa = nombres.empresa if nombres.empresa else ""
        nombre_c = nombres.nombre_c if nombres.nombre_c else ""
        nombre_i = nombres.nombre_i if nombres.nombre_i else ""
        nombre_e = nombres.nombre_e if nombres.nombre_e else ""
        serialized_nomproductos.append({
            'cod_despiece': cod_despiece,
            'empresa': empresa,
            'nombre_c': nombre_c,
            'nombre_i': nombre_i,
            'nombre_e': nombre_e
        })
    return jsonify(serialized_nomproductos)

@bpcustom.route('/estados_param')
@jwt_required()
@cross_origin()
def obtener_estados_param():

    empresa = request.args.get('empresa', None)
    cod_modelo = request.args.get('cod_modelo', None)
    cod_item = request.args.get('cod_item', None)

    query = TgModeloItem.query()
    if empresa:
        query = query.filter(TgModeloItem.empresa == empresa)
    if cod_modelo:
        query = query.filter(TgModeloItem.cod_modelo == cod_modelo)
    if cod_item:
        query = query.filter(TgModeloItem.cod_item == cod_item)

    estados = query.all()
    serialized_estados = []
    for estado in estados:
        empresa = estado.empresa if estado.empresa else ""
        cod_modelo = estado.cod_modelo if estado.cod_modelo else ""
        cod_item = estado.cod_item if estado.cod_item else ""
        nombre = str(estado.nombre) if estado.nombre else ""
        observaciones = str(estado.observaciones) if estado.observaciones else ""
        tipo = str(estado.tipo) if estado.tipo else ""
        orden = estado.orden if estado.orden else ""
        serialized_estados.append({
            'empresa': empresa,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'nombre': nombre,
            'observaciones': observaciones,
            'tipo': tipo,
            'orden': orden
        })
    return jsonify(serialized_estados)

#METODO PARA OBTENER LAS NAVIERAS CON PARAMETROS
@bpcustom.route('/naviera_param')
@jwt_required()
@cross_origin()
def obtener_naviera_param():
    empresa = request.args.get('empresa', None)
    codigo = request.args.get('codigo', None)
    query = StNaviera.query()

    if empresa:
        query = query.filter(StNaviera.empresa == empresa)
    if codigo:
        query = query.filter(StNaviera.codigo == codigo)
    
    navieras = query.all()
    serialized_naviera = []
    for naviera in navieras:
        empresa = naviera.empresa if naviera.empresa else ""
        codigo = naviera.codigo if naviera.codigo else ""
        nombre = naviera.nombre if naviera.nombre else ""
        estado = naviera.estado
        usuario_crea = naviera.usuario_crea if naviera.usuario_crea else ""
        fecha_crea = datetime.strftime(naviera.fecha_crea , "%d%m%Y") if naviera.fecha_crea else ""
        usuario_modifica = naviera.usuario_modifica if naviera.usuario_modifica else ""
        fecha_modifica = datetime.strftime(naviera.fecha_modifica, "%d%m%Y") if naviera.fecha_modifica else ""
        serialized_naviera.append({
            "empresa": empresa,
            "codigo": codigo,
            "nombre" : nombre,
            "estado": estado,
            "usuario_crea": usuario_crea,
            "fecha_crea": fecha_crea,
            "usuario_modifica": usuario_modifica,
            "fecha_modifica": fecha_modifica
        })
    return jsonify(serialized_naviera)

#METODOS GET CUSTOM PARA ORDENES DE COMPRA

@bpcustom.route('/orden_compra_cab_param')
@jwt_required()
@cross_origin()
def obtener_orden_compra_cab_param():

    empresa = request.args.get('empresa', None)
    cod_po = request.args.get('cod_po', None)
    tipo_comprobante = request.args.get('tipo_comprobante', None)
    cod_items = request.args.getlist('cod_items[]', None)
    fecha_inicio = request.args.get('fecha_inicio', None)  # Nueva fecha de inicio
    fecha_fin = request.args.get('fecha_fin', None)  # Nueva fecha de fin
    fecha_estimada_produccion = request.args.get('fecha_estimada_produccion', None)
    fecha_estimada_puerto = request.args.get('fecha_estimada_puerto', None)
    fecha_estimada_llegada = request.args.get('fecha_estimada_llegada', None)
    cod_opago = request.args.get('cod_opago', None)

    query = StOrdenCompraCab.query()
    if empresa:
        query = query.filter(StOrdenCompraCab.empresa == empresa)
    if cod_po:
        query = query.filter(StOrdenCompraCab.cod_po == cod_po)
    if tipo_comprobante:
        query = query.filter(StOrdenCompraCab.tipo_comprobante == tipo_comprobante)
    if fecha_estimada_produccion:
        fecha_estimada_produccion = datetime.strptime(fecha_estimada_produccion, '%d/%m/%Y').date()
        query = query.filter(StOrdenCompraCab.fecha_estimada_produccion == fecha_estimada_produccion)
    if fecha_estimada_puerto:
        fecha_estimada_puerto = datetime.strptime(fecha_estimada_puerto, '%d/%m/%Y').date()
        query = query.filter(StOrdenCompraCab.fecha_estimada_puerto == fecha_estimada_puerto)
    if fecha_estimada_llegada:
        fecha_estimada_llegada = datetime.strptime(fecha_estimada_llegada, '%d/%m/%Y').date()
        query = query.filter(StOrdenCompraCab.fecha_estimada_llegada == fecha_estimada_llegada)
    if cod_opago:
        query = query.filter(StOrdenCompraCab.cod_opago == cod_opago)
    if cod_items:
        query = query.filter(StOrdenCompraCab.cod_item.in_(cod_items))
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y').date()
        fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y').date()
        query = query.filter(StOrdenCompraCab.fecha_crea.between(fecha_inicio, fecha_fin))

    cabeceras = query.all()
    serialized_cabeceras = []
    for cabecera in cabeceras:
        empresa = cabecera.empresa if cabecera.empresa else ""
        cod_po = cabecera.cod_po if cabecera.cod_po else ""
        tipo_comprobante = cabecera.tipo_comprobante if cabecera.tipo_comprobante else ""
        cod_proveedor = cabecera.cod_proveedor if cabecera.cod_proveedor else ""
        nombre = cabecera.nombre if cabecera.nombre else ""
        proforma = cabecera.proforma if cabecera.proforma else ""
        usuario_crea = cabecera.usuario_crea if cabecera.usuario_crea else ""
        fecha_crea = cabecera.fecha_crea.strftime("%d/%m/%Y") if cabecera.fecha_crea else ""
        usuario_modifica = cabecera.usuario_modifica if cabecera.usuario_modifica else ""
        fecha_modifica = cabecera.fecha_modifica.strftime("%d/%m/%Y") if cabecera.fecha_modifica else ""
        cod_modelo = cabecera.cod_modelo if cabecera.cod_modelo else ""
        cod_item = cabecera.cod_item if cabecera.cod_item else ""
        ciudad = cabecera.ciudad if cabecera.ciudad else ""
        fecha_estimada_produccion = cabecera.fecha_estimada_produccion.strftime("%d/%m/%Y") if cabecera.fecha_estimada_produccion else ""
        fecha_estimada_puerto = cabecera.fecha_estimada_puerto.strftime("%d/%m/%Y") if cabecera.fecha_estimada_puerto else ""
        fecha_estimada_llegada = cabecera.fecha_estimada_llegada.strftime("%d/%m/%Y") if cabecera.fecha_estimada_llegada else ""
        serialized_cabeceras.append({
            'empresa': empresa,
            'cod_po': cod_po,
            'tipo_combrobante': tipo_comprobante,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'proforma': proforma,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'ciudad': ciudad,
            'fecha_estimada_produccion': fecha_estimada_produccion,
            'fecha_estimada_puerto': fecha_estimada_puerto,
            'fecha_estimada_llegada': fecha_estimada_llegada
        })
    
    return jsonify(serialized_cabeceras)
    
@bpcustom.route('/orden_compra_det_param')
@jwt_required()
@cross_origin()
def obtener_orden_compra_det_param():

    empresa = request.args.get('empresa', None)
    cod_po = request.args.get('cod_po', None)
    tipo_comprobante = request.args.get('tipo_comprobante', None)

    query = db.session.query(
        StOrdenCompraDet.cod_po,
        StOrdenCompraDet.secuencia,
        StOrdenCompraDet.cod_producto,
        StOrdenCompraDet.nombre,
        StOrdenCompraDet.costo_sistema,
        StOrdenCompraDet.fob,
        StOrdenCompraDet.cantidad_pedido,
        StOrdenCompraDet.saldo_producto,
        StOrdenCompraDet.unidad_medida,
        StOrdenCompraDet.fob_total,
        StOrdenCompraDet.nombre_i,
        StOrdenCompraDet.nombre_c,
        StOrdenCompraDet.exportar,
        StOrdenCompraDet.nombre_mod_prov,
        StOrdenCompraDet.nombre_comercial,
        StOrdenCompraDet.costo_cotizado,
        StOrdenCompraDet.fecha_costo,
        Producto.nombre.label("modelo"),
        StOrdenCompraDet.cod_producto_modelo
    ).filter(
        StOrdenCompraDet.empresa == empresa, StOrdenCompraDet.cod_po == cod_po, StOrdenCompraDet.tipo_comprobante == tipo_comprobante
    ).outerjoin(
        Producto,
        and_(Producto.cod_producto == StOrdenCompraDet.cod_producto_modelo, Producto.empresa == StOrdenCompraDet.empresa, Producto.empresa ==empresa)
    )
    results = query.all()

    serialized_details = [
        {
            "cod_po": result.cod_po,
            "secuencia": result.secuencia,
            "cod_producto": result.cod_producto,
            "nombre": result.nombre,
            "costo_sistema": result.costo_sistema,
            "fob": result.fob,
            "cantidad_pedido": result.cantidad_pedido,
            "saldo_producto": result.saldo_producto,
            "unidad_medida": result.unidad_medida,
            "fob_total": result.fob_total,
            "nombre_i": result.nombre_i,
            "nombre_c": result.nombre_c,
            "exportar": result.exportar,
            "nombre_mod_prov": result.nombre_mod_prov,
            "nombre_comercial": result.nombre_comercial,
            "costo_cotizado": result.costo_cotizado,
            "fecha_costo": result.fecha_costo,
            "modelo": result.modelo,
            "cod_producto_modelo": result.cod_producto_modelo
        }
        for result in results
    ]
    return jsonify(serialized_details)

@bpcustom.route('/orden_compra_track_param')
@jwt_required()
@cross_origin()
def obtener_orden_compra_track_param():
    cod_po = request.args.get('cod_po', None)
    subquery = (db.session.query(StTracking.cod_item,func.max(StTracking.secuencia).label("max_secuencia")).filter(StTracking.cod_po == cod_po).group_by(StTracking.cod_item).subquery())
    query = (db.session.query(StTracking.cod_item,StTracking.fecha,StTracking.secuencia).filter(StTracking.cod_po == cod_po).filter(tuple_(StTracking.cod_item, StTracking.secuencia).in_(subquery.select())).all())

    query2 = TgModeloItem.query().filter(TgModeloItem.empresa == 20).filter(TgModeloItem.cod_modelo == 'IMPR')
    estados = query2.all()
    serialized_estados = []

    for estado in estados:
        cod_item = estado.cod_item if estado.cod_item else ""
        serialized_estados.append({
            'cod': cod_item
        })

    serialized_seguimientos = []
    for seguimiento in query:
        secuencia = seguimiento.secuencia if seguimiento.secuencia else ""
        cod_item = seguimiento.cod_item if seguimiento.cod_item else ""
        fecha = datetime.strftime(seguimiento.fecha, "%d/%m/%Y") if seguimiento.fecha else ""
        serialized_seguimientos.append({
            'secuencia': secuencia,
            'cod': cod_item,
            'fecha': fecha,
        })
    serialized_seguimientos_ordenados = sorted(serialized_seguimientos, key=lambda x: x['cod'])

    codigos_existentes = set(item['cod'] for item in serialized_seguimientos_ordenados)

    for codigo in serialized_estados:
        cod = codigo['cod']
        if cod not in codigos_existentes:
            # Si el código no existe, agregamos un diccionario con secuencia y fecha a None
            serialized_seguimientos_ordenados.append({'secuencia': None, 'cod': cod, 'fecha': None})

    return sorted(serialized_seguimientos_ordenados, key=lambda x: x['cod'])

@bpcustom.route('/tracking_bl_param')
@jwt_required()
@cross_origin()
def obtener_tracking_bl_param():
    try:
        cod_bl_house = request.args.get('cod_bl_house', None)
        empresa = request.args.get('empresa', None)
        secuencial = request.args.get('secuencial', None)

        subquery = (db.session.query(StTrackingBl.cod_item, func.max(StTrackingBl.secuencial).label("max_secuencia")).filter(
            StTrackingBl.cod_bl_house == cod_bl_house).group_by(StTrackingBl.cod_item).subquery())
        query = (db.session.query(StTrackingBl.cod_bl_house, StTrackingBl.cod_item, StTrackingBl.fecha, StTrackingBl.secuencial).filter(
            StTrackingBl.cod_bl_house == cod_bl_house).filter(
            tuple_(StTrackingBl.cod_item, StTrackingBl.secuencial).in_(subquery.select())).all())

        serialized_bls = []

        query2 = TgModeloItem.query().filter(TgModeloItem.empresa == 20).filter(TgModeloItem.cod_modelo == 'BL')
        estados = query2.all()
        serialized_estados = []

        for estado in estados:
            cod_item = estado.cod_item if estado.cod_item else ""
            serialized_estados.append({
                'cod_item': cod_item
            })

        for bl in query:

            secuencial = bl.secuencial if bl.secuencial else ""
            fecha = datetime.strftime(bl.fecha,"%d/%m/%Y") if bl.fecha else ""
            cod_item = bl.cod_item if bl.cod_item else ""
            serialized_bls.append({
                'secuencial': secuencial,
                'fecha': fecha,
                'cod_item': cod_item,
            })
        codigos_existentes = set(item['cod_item'] for item in serialized_bls)

        for codigo in serialized_estados:
            cod = codigo['cod_item']
            if cod not in codigos_existentes:
                # Si el código no existe, agregamos un diccionario con secuencia y fecha a None
                serialized_bls.append({'secuencia': None, 'cod_item': cod, 'fecha': None})

        return sorted(serialized_bls, key=lambda x: x['cod_item'])
        
    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500    

@bpcustom.route('/packinglist_param')
@jwt_required()
@cross_origin()
def obtener_packinglist_param():
    empresa = request.args.get('empresa', None)
    secuencia = request.args.get('secuencia', None)
    cod_po = request.args.get('cod_po', None)
    
    query = StPackinglist.query()
    if empresa:
        query = query.filter(StPackinglist.empresa == empresa)
    if secuencia:
        query = query.filter(StPackinglist.secuencia == secuencia)
    if cod_po:
        query = query.filter(StPackinglist.cod_po == cod_po)
    
    packings = query.all()
    serialized_packings = []

    for packing in packings:
        nro_contenedor = packing.nro_contenedor if packing.nro_contenedor else ""
        secuencia = packing.secuencia if packing.secuencia else ""
        cod_po = packing.cod_po if packing.cod_po else ""
        tipo_comprobante = packing.tipo_comprobante if packing.tipo_comprobante else ""
        empresa = packing.empresa if packing.empresa else ""
        secuencia = packing.secuencia if packing.secuencia else ""
        cod_producto = packing.cod_producto if packing.cod_producto else ""
        cantidad = packing.cantidad if packing.cantidad else ""
        fob = packing.fob if packing.fob else ""
        unidad_medida = packing.unidad_medida if packing.unidad_medida else ""
        cod_liquidacion = packing.cod_liquidacion if packing.cod_liquidacion else ""
        cod_tipo_liquidacion = packing.cod_tipo_liquidacion if packing.cod_tipo_liquidacion else ""
        usuario_crea = packing.usuario_crea if packing.usuario_crea else ""
        fecha_crea = datetime.strftime(packing.fecha_crea,"%d/%m/%Y") if packing.fecha_crea else ""
        usuario_modifica = packing.usuario_modifica if packing.usuario_modifica else ""
        fecha_modifica = datetime.strftime(packing.fecha_modifica,"%d/%m/%Y") if packing.fecha_modifica else ""
        serialized_packings.append({
            'cod_po': cod_po,
            'tipo_comprobante': tipo_comprobante,
            'nro_contenedor': nro_contenedor,
            'empresa': empresa,
            'secuencia': secuencia,
            'cod_producto': cod_producto,
            'cantidad': cantidad,
            'fob': fob,
            'unidad_medida': unidad_medida,
            'cod_liquidacion': cod_liquidacion,
            'cod_tipo_liquidacion': cod_tipo_liquidacion,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica
        })
    return jsonify(serialized_packings)


@bpcustom.route('/packinglist_param_by_container')
@jwt_required()
@cross_origin()
def obtener_packinglist_param_by_container():
    nro_contenedor = request.args.get('nro_contenedor', None)
    empresa = request.args.get('empresa', None)

    query = db.session.query(
        StPackinglist.nro_contenedor,
        StPackinglist.secuencia,
        StPackinglist.cod_po,
        StPackinglist.tipo_comprobante,
        StPackinglist.empresa,
        StPackinglist.cod_producto,
        StPackinglist.cantidad,
        StPackinglist.fob,
        StPackinglist.unidad_medida,
        StPackinglist.cod_liquidacion,
        StPackinglist.cod_tipo_liquidacion,
        StPackinglist.usuario_crea,
        func.to_char(StPackinglist.fecha_crea, "DD/MM/YYYY").label("fecha_crea"),
        StPackinglist.usuario_modifica,
        func.to_char(StPackinglist.fecha_modifica, "DD/MM/YYYY").label("fecha_modifica"),
        StOrdenCompraCab.proforma.label("proforma"),
        Producto.nombre.label("producto")
    ).filter(
        StPackinglist.empresa == empresa, StPackinglist.nro_contenedor == nro_contenedor
    ).outerjoin(
        StOrdenCompraCab,
        and_(StOrdenCompraCab.cod_po == StPackinglist.cod_po, StOrdenCompraCab.empresa == StPackinglist.empresa)
    ).outerjoin(
        Producto,
        and_(Producto.cod_producto == StPackinglist.cod_producto, Producto.empresa == StPackinglist.empresa)
    )
    results = query.all()

    serialized_packings = [
        {
            "proforma": result.proforma,
            "producto": result.producto,
            "cod_po": result.cod_po,
            "tipo_comprobante": result.tipo_comprobante,
            "empresa": result.empresa,
            "nro_contenedor": result.nro_contenedor,
            "secuencia": result.secuencia,
            "cod_producto": result.cod_producto,
            "cantidad": result.cantidad,
            "fob": result.fob,
            "unidad_medida": result.unidad_medida,
            "cod_liquidacion": result.cod_liquidacion,
            "cod_tipo_liquidacion": result.cod_tipo_liquidacion,
            "usuario_crea": result.usuario_crea,
            "fecha_crea": result.fecha_crea,
            "usuario_modifica": result.usuario_modifica,
            "fecha_modifica": result.fecha_modifica,
        }
        for result in results
    ]


    return jsonify(serialized_packings)
#METODO CUSTOM PARA ELIMINAR TODA LA ORDEN DE COMPRA

@bpcustom.route('/eliminar_orden_compra_total/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra(cod_po, empresa, tipo_comprobante):
    try:
        orden_cab = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).first()
        if not orden_cab:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        # Eliminar registros en StOrdenCompraDet
        db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).delete()

        # Eliminar registros en StOrdenCompraTracking
        db.session.query(StTracking).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).delete()

        # Eliminar registros en StPackinglist
        db.session.query(StPackinglist).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).delete()

        # Eliminar registro en StOrdenCompraCab
        db.session.delete(orden_cab)

        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra eliminada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500    
    
@bpcustom.route('/producto_modelo')
@jwt_required()
@cross_origin()
def obtener_producto_modelo():
    query = db.session.query(Producto).filter(
        and_(
            Producto.empresa == 20,
            Producto.es_grupo_modelo == 1,
            Producto.activo == "S"
        )
    )
    productos = query.all()
    serialized_producto = []
    for producto in productos:
        cod_producto = producto.cod_producto if producto.cod_producto else ""
        nombre = producto.nombre if producto.nombre else ""
        cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
        serialized_producto.append({
            'cod_producto': cod_producto,
            'nombre': nombre,
            'cod_producto_modelo': cod_producto_modelo
        })
    return jsonify(serialized_producto)

#METODO PARA OBTENER EL REGIMEN ADUANA SOLO ACTIVOS
@bpcustom.route('/regimen_aduana')
@jwt_required()
@cross_origin()
def obtener_regimen_aduana():
    try:
        query = db.session.query(StAduRegimen).filter(
                StAduRegimen.es_activo == 1
        )
        regimenes = query.all()
        serialized_regimen = []
        for regimen in regimenes:
            cod_regimen = regimen.cod_regimen
            descripcion= regimen.descripcion
            serialized_regimen.append({
                'cod_regimen': cod_regimen,
                'descripcion' : descripcion
            })
        return jsonify(serialized_regimen)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
#METODO CUSTOM PARA EMBARQUES DE ORDENES DE COMPRA

@bpcustom.route('/embarque_param')
@jwt_required()
@cross_origin()
def obtener_embarques_param():
    try:
        empresa = request.args.get('empresa', None)
        codigo_bl_house = request.args.get('codigo_bl_house', None)
        fecha_inicio = request.args.get('fecha_inicio', None)  # Nueva fecha de inicio
        fecha_fin = request.args.get('fecha_fin', None)  # Nueva fecha de fin
        
        query = StEmbarquesBl.query()
        if empresa:
            query = query.filter(StEmbarquesBl.empresa == empresa)
        if codigo_bl_house:
            query = query.filter(StEmbarquesBl.codigo_bl_house == codigo_bl_house)
        if fecha_inicio and fecha_fin:
            fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y').date()
            fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y').date()
            query = query.filter(StEmbarquesBl.fecha_adicion.between(fecha_inicio, fecha_fin))
        
        embarques = query.all()
        serialized_embarques = []

        for embarque in embarques:
            empresa = embarque.empresa if embarque.empresa else ""
            codigo_bl_master = embarque.codigo_bl_master if embarque.codigo_bl_master else ""
            codigo_bl_house = embarque.codigo_bl_house if embarque.codigo_bl_house else ""
            cod_proveedor = embarque.cod_proveedor if embarque.cod_proveedor else ""
            fecha_embarque = datetime.strftime(embarque.fecha_embarque,"%d/%m/%Y") if embarque.fecha_embarque else ""
            fecha_llegada = datetime.strftime(embarque.fecha_llegada,"%d/%m/%Y") if embarque.fecha_llegada else ""
            fecha_bodega = datetime.strftime(embarque.fecha_bodega,"%d/%m/%Y") if embarque.fecha_bodega else ""
            numero_tracking = embarque.numero_tracking if embarque.numero_tracking else ""
            naviera = embarque.naviera if embarque.naviera else ""
            agente = embarque.agente if embarque.agente else ""
            estado = embarque.estado if embarque.estado else ""
            buque = embarque.buque if embarque.buque else ""
            cod_puerto_embarque = embarque.cod_puerto_embarque if embarque.cod_puerto_embarque else ""
            cod_puerto_desembarque = embarque.cod_puerto_desembarque if embarque.cod_puerto_desembarque else ""
            costo_contenedor = embarque.costo_contenedor if embarque.costo_contenedor else ""
            descripcion = embarque.descripcion if embarque.descripcion else ""
            tipo_flete = embarque.tipo_flete if embarque.tipo_flete else ""
            adicionado_por = embarque.adicionado_por if embarque.adicionado_por else ""
            fecha_adicion = datetime.strftime(embarque.fecha_adicion,"%d/%m/%Y") if embarque.fecha_adicion else ""
            modificado_por = embarque.modificado_por if embarque.modificado_por else ""
            fecha_modificacion = datetime.strftime(embarque.fecha_modificacion,"%d/%m/%Y") if embarque.fecha_modificacion else ""
            cod_modelo = embarque.cod_modelo if embarque.cod_modelo else ""
            cod_item = embarque.cod_item if embarque.cod_item else ""
            cod_aforo = embarque.cod_aforo
            cod_regimen = embarque.cod_regimen
            nro_mrn = embarque.nro_mrn if embarque.nro_mrn else ""
            serialized_embarques.append({
                'empresa': empresa,
                'codigo_bl_master': codigo_bl_master,
                'codigo_bl_house': codigo_bl_house,
                'cod_proveedor': cod_proveedor,
                'fecha_embarque': fecha_embarque,
                'fecha_llegada': fecha_llegada,
                'fecha_bodega': fecha_bodega,
                'numero_tracking': numero_tracking,
                'naviera': naviera,
                'agente': agente,
                'estado': estado,
                'buque': buque,
                'cod_puerto_embarque': cod_puerto_embarque,
                'cod_puerto_desembarque': cod_puerto_desembarque,
                'costo_contenedor': costo_contenedor,
                'descripcion': descripcion,
                'tipo_flete': tipo_flete,
                'adicionado_por': adicionado_por,
                'fecha_adicion': fecha_adicion,
                'modificado_por': modificado_por,
                'fecha_modificacion': fecha_modificacion,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'cod_aforo': cod_aforo,
                'cod_regimen': cod_regimen,
                'nro_mrn': nro_mrn
            })
        return jsonify(serialized_embarques)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500

#RUTA PARA CREACION DE WIZARD PARA BUSQUEDA DE PRODUCTOS
@bpcustom.route('/wizard_productos') #sw para mostrar los productos por parametros
@jwt_required()
@cross_origin()
def obtener_wizard_productos():
    try:
        cod_producto = request.args.get('cod_producto' , None)
        empresa = request.args.get('empresa' , None)
        nombre = request.args.get('nombre' , None)

        query = Producto.query()

        if nombre or cod_producto:
            query = db.session.query(Producto).filter(or_(Producto.cod_producto.like(f'%{cod_producto.upper()}%'),
                                                    Producto.nombre.like(f'%{nombre.upper()}%')))
            
        if empresa:
            query = query.filter(Producto.empresa == empresa)

        productos = query.all()

        serialized_productos = []
        for producto in productos:
            empresa = producto.empresa if producto.empresa else ""
            cod_producto = producto.cod_producto if producto.cod_producto else ""
            tipo_inventario = producto.tipo_inventario if producto.tipo_inventario else ""
            cod_marca = producto.cod_marca if producto.cod_marca else ""
            cod_alterno = producto.cod_alterno if producto.cod_alterno else ""
            nombre = producto.nombre if producto.nombre else ""
            cod_barra = producto.cod_barra if producto.cod_barra else ""
            useridc = producto.useridc if producto.useridc else ""
            presentacion = producto.presentacion if producto.presentacion else ""
            volumen = producto.volumen if producto.volumen else ""
            grado = producto.grado if producto.grado else ""
            costo = producto.costo if producto.costo else ""
            activo = producto.activo if producto.activo else ""
            cod_modelo = producto.cod_modelo if producto.cod_modelo else ""
            cod_item = producto.cod_item if producto.cod_item else ""
            cod_modelo_cat = producto.cod_modelo_cat if producto.cod_modelo_cat else ""
            cod_item_cat = producto.cod_item_cat if producto.cod_item_cat else ""
            serie = producto.serie if producto.serie else ""
            ice = producto.ice if producto.ice else ""
            cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
            serialized_productos.append({
                'empresa': empresa,
                'cod_producto': cod_producto,
                'tipo_inventario': tipo_inventario,
                'cod_marca': cod_marca,
                'cod_alterno': cod_alterno,
                'nombre': nombre,
                'cod_barra': cod_barra,
                'useridc': useridc,
                'presentacion': presentacion,
                'volumen': volumen,
                'grado': grado,
                'costo': costo,
                'activo': activo,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'cod_modelo_cat': cod_modelo_cat,
                'cod_item_cat': cod_item_cat,
                'serie': serie,
                "ice": ice,
                'cod_producto_modelo': cod_producto_modelo
            })
        return jsonify(serialized_productos)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
#RUTA CUSTOM PARA TIPOS DE AFORO
@bpcustom.route('/tipo_aforo_param')
@jwt_required()
@cross_origin()
def obtener_tipo_aforo_param():
    try:
        empresa = request.args.get('empresa', None)
        cod_aforo = request.args.get('cod_aforo', None)

        query = StTipoAforo.query()
        if empresa:
            query = query.filter(StTipoAforo.empresa  == empresa)
        if cod_aforo:
            query = query.filter(StTipoAforo.cod_aforo == cod_aforo)

        aforos = query.all()
        serialized_aforos = []

        for aforo in aforos:
            empresa = aforo.empresa if aforo.empresa else ""
            cod_aforo = aforo.cod_aforo
            nombre = aforo.nombre if aforo.nombre else ""
            valor = aforo.valor
            observacion = aforo.observacion if aforo.observacion else ""
            usuario_crea = aforo.usuario_crea if aforo.usuario_crea else ""
            fecha_crea = datetime.strftime(aforo.fecha_crea,"%d/%m/%Y") if aforo.fecha_crea else ""
            usuario_modifica = aforo.usuario_modifica if aforo.usuario_modifica else ""
            fecha_modifica = datetime.strftime(aforo.fecha_modifica,"%d/%m/%Y") if aforo.fecha_modifica else ""
            serialized_aforos.append({
                'empresa': empresa,
                'cod_aforo': cod_aforo,
                'nombre': nombre,
                'valor': valor,
                'observacion': observacion,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modificia': fecha_modifica 
            })
        return jsonify(serialized_aforos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
#RUTA CUSTOM PARA ACTUALIZAR UN REGISTRO DE PACKINGLIST
@bpcustom.route('/actualizar_packinglist/<empresa>/<cod_po>/<codigo_bl_house>/<secuencia>', methods = ['PUT'])
@jwt_required()
@cross_origin()
def actualizar_registro_packinglist(empresa, cod_po, codigo_bl_house, secuencia):
    try:
        registro = db.session.query(StPackinglist).filter_by(empresa = empresa, cod_po = cod_po, codigo_bl_house = codigo_bl_house, secuencia = secuencia).first()
        if not registro:
            return jsonify({'mensaje': 'El registro no existe en el packinglist'}), 404
        
        data = request.get_json()
        registro.cod_producto = data.get('cod_producto', registro.cod_producto)
        registro.cantidad = data.get('cantidad', registro.cantidad)
        registro.fob = data.get('fob', registro.fob)
        registro.unidad_medida = data.get('unidad_medida', registro.unidad_medida).upper()
        registro.cod_liquidacion = data.get('cod_liquidacion', registro.cod_liquidacion)
        registro.cod_tipo_liquidacion = data.get('cod_tipo_liquidacion', registro.cod_tipo_liquidacion)
        registro.usuario_modifica = data.get('usuario_modifica', registro.usuario_modifica).upper()
        registro.fecha_modifica = date.today()

        # Actualizar campo saldo_pedido en StOrdenCompraDet
        orden_det = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa, cod_producto=registro.cod_producto).first()
        if orden_det:
            saldo_producto = orden_det.cantidad_pedido - registro.cantidad
            orden_det.saldo_producto = saldo_producto
            orden_det.fecha_modifica = date.today()
            orden_det.usuario_modifica = data.get('usuario_modifica', orden_det.usuario_modifica).upper()

        db.session.commit()

        return jsonify({'mensaje': 'Registro de packinglist actualizado exitosamente'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/orden_compra_packinglist_by_container', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_packinglist_por_contenedor():
    try:
        nro_contenedor = request.args.get('nro_contenedor')
        empresa = request.args.get('empresa')

        if not nro_contenedor:
            return jsonify({'error': 'Se debe proporcionar numero de contenedor para eliminar.'}), 400

        packing_query = db.session.query(StPackinglist)
        if nro_contenedor:
            packing_query = packing_query.filter_by(nro_contenedor=nro_contenedor)
        if empresa:
            packing_query = packing_query.filter_by(empresa=empresa)

        packings_to_delete = packing_query.all()

        if not packings_to_delete:
            return jsonify({'mensaje': 'No se encontraron registros para eliminar.'}), 404

        for packing in packings_to_delete:
            query = StOrdenCompraDet.query().filter_by(cod_po=packing.cod_po, cod_producto=packing.cod_producto, empresa=empresa).first()
            if query:
                query.saldo_producto = query.saldo_producto + Decimal(str(packing.cantidad))
                if query.cantidad_pedido == 0:
                    db.session.delete(query)
            db.session.delete(packing)
        db.session.commit()

        return jsonify({'mensaje': 'Registro de Packinglists de orden de compra eliminado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/container_by_nro')
@jwt_required()
@cross_origin()
def obtener_container_por_nro():
    nro_contenedor = request.args.get('nro_contenedor', None)
    cod_bl_house = request.args.get('cod_bl_house', None)
    query = StEmbarqueContenedores.query()
    if nro_contenedor:
        query = query.filter(StEmbarqueContenedores.nro_contenedor == nro_contenedor)

    if cod_bl_house:
        query = query.filter(StEmbarqueContenedores.codigo_bl_house == cod_bl_house)

    contenedores = query.all()
    serialized_contenedores = []
    for contenedor in contenedores:
        empresa = contenedor.empresa if contenedor.empresa else ""
        codigo_bl_house = contenedor.codigo_bl_house if contenedor.codigo_bl_house else ""
        nro_contenedor = contenedor.nro_contenedor if contenedor.nro_contenedor else ""
        cod_tipo_contenedor = contenedor.cod_tipo_contenedor
        peso = contenedor.peso if contenedor.peso else ""
        volumen = contenedor.volumen if contenedor.volumen else ""
        line_seal = contenedor.line_seal if contenedor.line_seal else ""
        shipper_seal = contenedor.shipper_seal if contenedor.shipper_seal else ""
        es_carga_suelta = contenedor.es_carga_suelta if contenedor.es_carga_suelta is not None else 0
        observaciones = contenedor.observaciones if contenedor.observaciones else ""
        serialized_contenedores.append({
            "empresa": empresa,
            "codigo_bl_house": codigo_bl_house,
            "nro_contenedor": nro_contenedor,
            "cod_tipo_contenedor": cod_tipo_contenedor,
            "peso": peso,
            "volumen": volumen,
            "line_seal": line_seal,
            "shipper_seal": shipper_seal,
            "es_carga_suelta": es_carga_suelta,
            "observaciones": observaciones
        })
    return jsonify(serialized_contenedores)

@bpcustom.route('/detalles_general')
@jwt_required()
@cross_origin()
def obtener_vt_detalles_general():
    query = VtDetallesOrdenGeneral.query()
    vista = query.all()
    serialized = []
    for registro in vista:
        cod_po = registro.cod_po if registro.cod_po else ""
        cod_producto = registro.cod_producto if registro.cod_producto else ""
        nombre = registro.nombre if registro.nombre else ""
        modelo = registro.modelo if registro.modelo else ""
        costo_sistema = registro.costo_sistema if registro.costo_sistema else ""
        cantidad_pedido = registro.cantidad_pedido if registro.cantidad_pedido else ""
        saldo_producto = registro.saldo_producto if registro.saldo_producto else ""
        fob_detalle = registro.fob_detalle if registro.fob_detalle else ""
        fob_total = registro.fob_total if registro.fob_total else ""
        proforma = registro.proforma if registro.proforma else ""
        proveedor = registro.proveedor if registro.proveedor else ""
        fecha_estimada_produccion = datetime.strftime(registro.fecha_estimada_produccion,"%d/%m/%Y") if registro.fecha_estimada_produccion else ""
        fecha_estimada_puerto = datetime.strftime(registro.fecha_estimada_puerto,"%d/%m/%Y") if registro.fecha_estimada_puerto else ""
        fecha_estimada_llegada = datetime.strftime(registro.fecha_estimada_llegada,"%d/%m/%Y") if registro.fecha_estimada_llegada else ""
        nro_contenedor = registro.nro_contenedor if registro.nro_contenedor else ""
        codigo_bl_house = registro.codigo_bl_house if registro.codigo_bl_house else ""
        fecha_embarque = datetime.strftime(registro.fecha_embarque,
                                                      "%d/%m/%Y") if registro.fecha_embarque else ""
        fecha_llegada = datetime.strftime(registro.fecha_llegada,
                                           "%d/%m/%Y") if registro.fecha_llegada else ""
        fecha_bodega = datetime.strftime(registro.fecha_bodega,
                                           "%d/%m/%Y") if registro.fecha_bodega else ""
        cantidad = registro.cantidad if registro.cantidad else ""
        fob = registro.fob if registro.fob else ""
        estado_embarque = registro.estado_embarque if registro.estado_embarque else ""
        estado_orden = registro.estado_orden if registro.estado_orden else ""

        serialized.append({
            "cod_po": cod_po,
            "cod_producto": cod_producto,
            "nombre": nombre,
            "modelo": modelo,
            "costo_sistema": costo_sistema,
            "cantidad_pedido": cantidad_pedido,
            "saldo_producto": saldo_producto,
            "fob_detalle": fob_detalle,
            "fob_total": fob_total,
            "proforma": proforma,
            "proveedor": proveedor,
            "fecha_estimada_produccion": fecha_estimada_produccion,
            "fecha_estimada_puerto": fecha_estimada_puerto,
            "fecha_estimada_llegada": fecha_estimada_llegada,
            "nro_contenedor": nro_contenedor,
            "codigo_bl_house": codigo_bl_house,
            "fecha_embarque": fecha_embarque,
            "fecha_llegada": fecha_llegada,
            "fecha_bodega": fecha_bodega,
            "cantidad": cantidad,
            "fob": fob,
            "estado_embarque": estado_embarque,
            "estado_orden": estado_orden


        })
    return jsonify(serialized)