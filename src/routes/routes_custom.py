from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.proveedores import Proveedor, TgModeloItem
from src.models.tipo_comprobante import TipoComprobante
from src.models.producto_despiece import StProductoDespiece
from src.models.despiece import StDespiece
from src.models.formula import StFormula, StFormulaD
from src.models.comprobante import Comprobante, Movimiento
from src.models.orden_compra import StOrdenCompraCab,StOrdenCompraDet,StTracking,StPackinglist
from src.models.embarque_bl import StEmbarquesBl, StTrackingBl, StNaviera, StEmbarqueContenedores
from src.models.entities.vt_detalles_orden_general import VtDetallesOrdenGeneral
from src.config.database import db
from src.models.tipo_aforo import StTipoAforo
from src.models.aduana import StAduRegimen
from src.routes.routes import asigna_cod_comprobante, obtener_secuencia_formule
from src.models.lote import StLote, Sta_Comprobante, Sta_Movimiento
from sqlalchemy import and_, or_, func, tuple_
import datetime
from decimal import Decimal
from datetime import datetime, date
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from src import oracle
from os import getenv
import cx_Oracle

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
    tipos = request.args.getlist('tipos[]', None)

    query = TgModeloItem.query()
    if empresa:
        query = query.filter(TgModeloItem.empresa == empresa)
    if cod_modelo:
        query = query.filter(TgModeloItem.cod_modelo == cod_modelo)
    if cod_item:
        query = query.filter(TgModeloItem.cod_item == cod_item)
    if tipos:
        query = query.filter(TgModeloItem.tipo.in_(tipos))

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

        query2 = TgModeloItem.query().filter(TgModeloItem.empresa == 20).filter(TgModeloItem.cod_modelo == 'BL').filter(TgModeloItem.tipo == 'A')
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
            bl_house_manual = embarque.bl_house_manual if embarque.bl_house_manual else ""
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
                'nro_mrn': nro_mrn,
                'bl_house_manual': bl_house_manual
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
                query.fob = 0
                query.fob_total = 0
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
        fecha_bodega = contenedor.fecha_bodega if contenedor.fecha_bodega else ""
        cod_modelo = contenedor.cod_modelo if contenedor.cod_modelo else ""
        cod_item = contenedor.cod_item if contenedor.cod_item else ""
        es_repuestos = contenedor.es_repuestos if contenedor.es_repuestos else ""
        es_motos = contenedor.es_motos if contenedor.es_motos else ""
        fecha_salida = contenedor.fecha_salida if contenedor.fecha_salida else ""
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
            "observaciones": observaciones,
            "fecha_bodega": fecha_bodega,
            "cod_modelo": cod_modelo,
            "cod_item": cod_item,
            "es_repuestos": es_repuestos,
            "es_motos": es_motos,
            "fecha_salida": fecha_salida
        })
    return jsonify(serialized_contenedores)

@bpcustom.route('/detalles_general')
@jwt_required()
@cross_origin()
def obtener_vt_detalles_general():
    query = VtDetallesOrdenGeneral.query()
    vista = query.all()

    # Diccionario para almacenar los registros agrupados por clave
    grouped_records = {}

    for registro in vista:
        clave = (
            registro.cod_po,
            registro.secuencia,
            registro.cod_producto,
            registro.nombre,
            registro.modelo,
            registro.costo_sistema,
            registro.costo_cotizado,
            registro.cantidad_pedido,
            registro.saldo_producto,
            registro.fob_detalle,
            registro.fob_total,
            registro.proforma,
            registro.proveedor,
            registro.fecha_estimada_produccion,
            registro.fecha_estimada_puerto,
            registro.fecha_estimada_llegada
        )

        if clave not in grouped_records:
            grouped_records[clave] = {
                "cantidad_pedido": registro.cantidad_pedido,
                "cod_po": registro.cod_po,
                "secuencia": registro.secuencia,
                "cod_producto": registro.cod_producto,
                "costo_cotizado": registro.costo_cotizado,
                "costo_sistema": registro.costo_sistema,
                "fecha_estimada_llegada": datetime.strftime(registro.fecha_estimada_llegada,"%d/%m/%Y") if registro.fecha_estimada_llegada else "",
                "fecha_estimada_produccion": datetime.strftime(registro.fecha_estimada_produccion,"%d/%m/%Y") if registro.fecha_estimada_produccion else "",
                "fecha_estimada_puerto": datetime.strftime(registro.fecha_estimada_puerto,"%d/%m/%Y") if registro.fecha_estimada_puerto else "",
                "fob_detalle": registro.fob_detalle,
                "fob_total": registro.fob_total,
                "modelo": registro.modelo,
                "nombre": registro.nombre,
                "proforma": registro.proforma,
                "proveedor": registro.proveedor,
                "saldo_producto": registro.saldo_producto,
                "estado_orden": registro.estado_orden,
                "containers": []
            }

        grouped_records[clave]["containers"].append({
            "nro_contenedor": registro.nro_contenedor,
            "codigo_bl_house": registro.codigo_bl_house,
            "fecha_embarque": datetime.strftime(registro.fecha_embarque,"%d/%m/%Y") if registro.fecha_embarque else "",
            "fecha_llegada": datetime.strftime(registro.fecha_llegada,"%d/%m/%Y") if registro.fecha_llegada else "",
            "fecha_bodega": datetime.strftime(registro.fecha_bodega,"%d/%m/%Y") if registro.fecha_bodega else "",
            "cantidad": registro.total_precio_container,
            "fob": registro.cantidad_container,
            "estado_embarque": registro.estado_embarque
        })

    # Convertir el diccionario en una lista de registros
    serialized = list(grouped_records.values())

    return jsonify(serialized)


@bpcustom.route('/productos_by_cat', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_productos_por_categoria():
    try:
        data = request.get_json()
        empresa = data.get('empresa', None)
        cod_modelo_cat = data.get('cod_modelo_cat', None)
        cod_item_cat = data.get('cod_item_cat', None)
        cod_modelo = data.get('cod_modelo', None)
        cod_item = data.get('cod_item', None)
        cod_modelo_cat1 = data.get('cod_modelo_cat1', None)
        cod_item_cat1 = data.get('cod_item_cat1', None)
        if not cod_modelo_cat or not cod_item_cat or not cod_modelo or not cod_item or not cod_modelo_cat1 or not cod_item_cat1:

            return jsonify({'error': 'Faltan valores por ingresar.'}), 404

        query = Producto.query()

        if empresa:
            query = query.filter(Producto.empresa == empresa)

        query = query.filter(Producto.cod_modelo_cat == cod_modelo_cat, Producto.cod_item_cat == cod_item_cat, Producto.cod_modelo == cod_modelo,
                             Producto.cod_item == cod_item, Producto.cod_modelo_cat1 == cod_modelo_cat1, Producto.cod_item_cat1 == cod_item_cat1)

        productos = query.all()
        serialized_productos = []

        for producto in productos:
            empresa = producto.empresa if producto.empresa else ""
            cod_producto = producto.cod_producto if producto.cod_producto else ""
            tipo_inventario = producto.tipo_inventario if producto.tipo_inventario else ""
            cod_unidad = producto.cod_unidad if producto.cod_unidad else ""
            cod_marca = producto.cod_marca if producto.cod_marca else ""
            cod_alterno = producto.cod_alterno if producto.cod_alterno else ""
            nombre = producto.nombre if producto.nombre else ""
            cod_barra = producto.cod_barra if producto.cod_barra else ""
            useridc = producto.useridc if producto.useridc else ""
            niv_cod_nivel = producto.niv_cod_nivel if producto.niv_cod_nivel else ""
            niv_secuencia = producto.niv_secuencia if producto.niv_secuencia else ""
            niv_cat_emp_empresa = producto.niv_cat_emp_empresa if producto.niv_cat_emp_empresa else ""
            niv_cat_cod_categoria = producto.niv_cat_cod_categoria if producto.niv_cat_cod_categoria else ""
            promedio = producto.promedio if producto.promedio else ""
            presentacion = producto.presentacion if producto.presentacion else ""
            volumen = producto.volumen if producto.volumen else ""
            grado = producto.grado if producto.grado else ""
            iva = producto.iva if producto.iva else ""
            referencia = producto.referencia if producto.referencia else ""
            partida = producto.partida if producto.partida else ""
            minimo = producto.minimo if producto.minimo else ""
            maximo = producto.maximo if producto.maximo else ""
            costo = producto.costo if producto.costo else ""
            dolar = producto.dolar if producto.dolar else ""
            activo = producto.activo if producto.activo else ""
            alcohol = producto.alcohol if producto.alcohol else ""
            cod_unidad_r = producto.cod_unidad_r if producto.cod_unidad_r else ""
            cod_modelo = producto.cod_modelo if producto.cod_modelo else ""
            cod_item = producto.cod_item if producto.cod_item else ""
            es_fabricado = producto.es_fabricado if producto.es_fabricado else ""
            cod_modelo_cat = producto.cod_modelo_cat if producto.cod_modelo_cat else ""
            cod_item_cat = producto.cod_item_cat if producto.cod_item_cat else ""
            cod_unidad_f = producto.cod_unidad_f if producto.cod_unidad_f else ""
            cantidad = producto.cantidad if producto.cantidad else ""
            cantidad_i = producto.cantidad_i if producto.cantidad_i else ""
            serie = producto.serie if producto.serie else ""
            es_express = producto.es_express if producto.es_express else ""
            precio = producto.precio if producto.precio else ""
            cod_modelo_cat1 = producto.cod_modelo_cat1 if producto.cod_modelo_cat1 else ""
            cod_item_cat1 = producto.cod_item_cat1 if producto.cod_item_cat1 else ""
            ice = producto.ice if producto.ice else ""
            control_lote = producto.control_lote if producto.control_lote else ""
            es_grupo_modelo = producto.es_grupo_modelo if producto.es_grupo_modelo else ""
            cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
            serialized_productos.append({
                'empresa': empresa,
                'cod_producto': cod_producto,
                'tipo_inventario': tipo_inventario,
                'cod_marca': cod_marca,
                'cod_unidad': cod_unidad,
                'cod_alterno': cod_alterno,
                'nombre': nombre,
                'cod_barra': cod_barra,
                'useridc': useridc,
                'niv_cod_nivel': niv_cod_nivel,
                'niv_secuencia': niv_secuencia,
                'niv_cat_emp_empresa': niv_cat_emp_empresa,
                'niv_cat_cod_categoria': niv_cat_cod_categoria,
                'promedio': promedio,
                'presentacion': presentacion,
                'volumen': volumen,
                'grado': grado,
                'iva': iva,
                'referencia': referencia,
                'partida': partida,
                'minimo': minimo,
                'maximo': maximo,
                'costo': costo,
                'dolar': dolar,
                'activo': activo,
                'alcohol': alcohol,
                'cod_unidad_r': cod_unidad_r,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'es fabricado': es_fabricado,
                'cod_modelo_cat': cod_modelo_cat,
                'cod_item_cat': cod_item_cat,
                'cod_unidad_f': cod_unidad_f,
                'cantidad': cantidad,
                'cantidad_i': cantidad_i,
                'serie': serie,
                'es_express': es_express,
                'precio': precio,
                'cod_modelo_cat1': cod_modelo_cat1,
                'cod_item_cat1': cod_item_cat1,
                'ice': ice,
                'control_lote': control_lote,
                'es_grupo_modelo': es_grupo_modelo,
                'cod_producto_modelo': cod_producto_modelo
            })
        return jsonify(serialized_productos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500


@bpcustom.route('/productos_by_cod', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_productos_por_codigo():
    try:
        data = request.get_json()
        empresa = data.get('empresa', None)
        cod_producto = data.get('cod_producto', None)
        print(cod_producto)
        if not cod_producto:
            return jsonify({'error': 'Falta ingresar el codigo de producto.'}), 404

        query = Producto.query()

        if empresa:
            query = query.filter(Producto.empresa == empresa)

        query = query.filter(Producto.cod_producto.like(f'%{cod_producto}%'))
        query = query.filter(Producto.activo == 'S')
        query = query.filter(Producto.cod_item_cat.in_(['Z', 'R', 'J', 'L', 'D']))

        productos = query.all()
        serialized_productos = []

        for producto in productos:
            empresa = producto.empresa if producto.empresa else ""
            cod_producto = producto.cod_producto if producto.cod_producto else ""
            tipo_inventario = producto.tipo_inventario if producto.tipo_inventario else ""
            cod_unidad = producto.cod_unidad if producto.cod_unidad else ""
            cod_marca = producto.cod_marca if producto.cod_marca else ""
            cod_alterno = producto.cod_alterno if producto.cod_alterno else ""
            nombre = producto.nombre if producto.nombre else ""
            cod_barra = producto.cod_barra if producto.cod_barra else ""
            useridc = producto.useridc if producto.useridc else ""
            niv_cod_nivel = producto.niv_cod_nivel if producto.niv_cod_nivel else ""
            niv_secuencia = producto.niv_secuencia if producto.niv_secuencia else ""
            niv_cat_emp_empresa = producto.niv_cat_emp_empresa if producto.niv_cat_emp_empresa else ""
            niv_cat_cod_categoria = producto.niv_cat_cod_categoria if producto.niv_cat_cod_categoria else ""
            promedio = producto.promedio if producto.promedio else ""
            presentacion = producto.presentacion if producto.presentacion else ""
            volumen = producto.volumen if producto.volumen else ""
            grado = producto.grado if producto.grado else ""
            iva = producto.iva if producto.iva else ""
            referencia = producto.referencia if producto.referencia else ""
            partida = producto.partida if producto.partida else ""
            minimo = producto.minimo if producto.minimo else ""
            maximo = producto.maximo if producto.maximo else ""
            costo = producto.costo if producto.costo else ""
            dolar = producto.dolar if producto.dolar else ""
            activo = producto.activo if producto.activo else ""
            alcohol = producto.alcohol if producto.alcohol else ""
            cod_unidad_r = producto.cod_unidad_r if producto.cod_unidad_r else ""
            cod_modelo = producto.cod_modelo if producto.cod_modelo else ""
            cod_item = producto.cod_item if producto.cod_item else ""
            es_fabricado = producto.es_fabricado if producto.es_fabricado else ""
            cod_modelo_cat = producto.cod_modelo_cat if producto.cod_modelo_cat else ""
            cod_item_cat = producto.cod_item_cat if producto.cod_item_cat else ""
            cod_unidad_f = producto.cod_unidad_f if producto.cod_unidad_f else ""
            cantidad = producto.cantidad if producto.cantidad else ""
            cantidad_i = producto.cantidad_i if producto.cantidad_i else ""
            serie = producto.serie if producto.serie else ""
            es_express = producto.es_express if producto.es_express else ""
            precio = producto.precio if producto.precio else ""
            cod_modelo_cat1 = producto.cod_modelo_cat1 if producto.cod_modelo_cat1 else ""
            cod_item_cat1 = producto.cod_item_cat1 if producto.cod_item_cat1 else ""
            ice = producto.ice if producto.ice else ""
            control_lote = producto.control_lote if producto.control_lote else ""
            es_grupo_modelo = producto.es_grupo_modelo if producto.es_grupo_modelo else ""
            cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
            serialized_productos.append({
                'empresa': empresa,
                'cod_producto': cod_producto,
                'tipo_inventario': tipo_inventario,
                'cod_marca': cod_marca,
                'cod_unidad': cod_unidad,
                'cod_alterno': cod_alterno,
                'nombre': nombre,
                'cod_barra': cod_barra,
                'useridc': useridc,
                'niv_cod_nivel': niv_cod_nivel,
                'niv_secuencia': niv_secuencia,
                'niv_cat_emp_empresa': niv_cat_emp_empresa,
                'niv_cat_cod_categoria': niv_cat_cod_categoria,
                'promedio': promedio,
                'presentacion': presentacion,
                'volumen': volumen,
                'grado': grado,
                'iva': iva,
                'referencia': referencia,
                'partida': partida,
                'minimo': minimo,
                'maximo': maximo,
                'costo': costo,
                'dolar': dolar,
                'activo': activo,
                'alcohol': alcohol,
                'cod_unidad_r': cod_unidad_r,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'es fabricado': es_fabricado,
                'cod_modelo_cat': cod_modelo_cat,
                'cod_item_cat': cod_item_cat,
                'cod_unidad_f': cod_unidad_f,
                'cantidad': cantidad,
                'cantidad_i': cantidad_i,
                'serie': serie,
                'es_express': es_express,
                'precio': precio,
                'cod_modelo_cat1': cod_modelo_cat1,
                'cod_item_cat1': cod_item_cat1,
                'ice': ice,
                'control_lote': control_lote,
                'es_grupo_modelo': es_grupo_modelo,
                'cod_producto_modelo': cod_producto_modelo
            })
        return jsonify(serialized_productos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        # logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500


@bpcustom.route('/formule', methods=['POST'])
@jwt_required()
@cross_origin()
def formule():
    data = request.get_json()
    empresa = data.get('empresa', None)
    cod_formula = data.get('cod_formula', None)
    cod_producto = data.get('cod_producto', None)

    query = StFormula.query()
    if empresa:
        query = query.filter(StFormula.empresa == empresa)
    if cod_producto:
        query = query.filter(StFormula.cod_producto == cod_producto)
    if cod_formula:
        query = query.filter(StFormula.cod_formula == cod_formula)

    formula = query.all()
    serialized_formula = []
    for form in formula:
        empresa = form.empresa if form.empresa else ""
        cod_formula = form.cod_formula if form.cod_formula else ""
        nombre = form.nombre if form.nombre else ""
        cod_producto = form.cod_producto if form.cod_producto else ""
        cod_unidad = form.cod_unidad if form.cod_unidad else ""
        cantidad_produccion = form.cantidad_produccion if form.cantidad_produccion else ""
        activa = form.activa if form.activa else ""
        mano_obra = form.mano_obra if form.mano_obra else ""
        costo_standard = form.costo_standard if form.costo_standard else ""
        debito_credito = form.debito_credito if form.debito_credito else ""
        serialized_formula.append({
            'empresa': empresa,
            'cod_formula': cod_formula,
            'nombre': nombre,
            'cod_producto': cod_producto,
            'cod_unidad': cod_unidad,
            'cantidad_produccion': cantidad_produccion,
            'activa': activa,
            'mano_obra': mano_obra,
            'costo_standard': costo_standard,
            'debito_credito': debito_credito
        })
    return jsonify(serialized_formula)

@bpcustom.route('/formule_d', methods=['POST'])
@jwt_required()
@cross_origin()
def formule_d():
    data = request.get_json()
    empresa = data.get('empresa', None)
    cod_formula = data.get('cod_formula', None)
    cod_producto_f = data.get('cod_producto_f', None)

    query = StFormulaD.query()
    if empresa:
        query = query.filter(StFormulaD.empresa == empresa)
    if cod_formula:
        query = query.filter(StFormulaD.cod_formula == cod_formula)
    if cod_producto_f:
        query = query.filter(StFormulaD.cod_producto_f == cod_producto_f)

    formulad = query.all()
    serialized_formulad = []
    for form in formulad:
        empresa = form.empresa if form.empresa else ""
        cod_formula = form.cod_formula if form.cod_formula else ""
        secuencia = form.secuencia if form.secuencia else ""
        cod_producto_f = form.cod_producto_f if form.cod_producto_f else ""
        cod_unidad_f = form.cod_unidad_f if form.cod_unidad_f else ""
        cantidad_f = form.cantidad_f if form.cantidad_f else ""
        debito_credito = form.debito_credito if form.debito_credito else ""
        costo_standard = form.costo_standard if form.costo_standard else ""
        serialized_formulad.append({
            'empresa': empresa,
            'cod_formula': cod_formula,
            'secuencia': secuencia,
            'cod_producto_f': cod_producto_f,
            'cod_unidad_f': cod_unidad_f,
            'cantidad_f': cantidad_f,
            'debito_credito': debito_credito,
            'costo_standard': costo_standard
        })

    return jsonify(serialized_formulad)

@bpcustom.route('/formule_d', methods=['DELETE'])
@jwt_required()
@cross_origin()
def formule_d_delete():
    data = request.get_json()
    empresa = data.get('empresa', None)
    cod_formula = data.get('cod_formula', None)
    secuencia = data.get('secuencia', None)

    query = StFormulaD.query()
    if empresa:
        query = query.filter(StFormulaD.empresa == empresa)
    if cod_formula:
        query = query.filter(StFormulaD.cod_formula == cod_formula)
    if secuencia:
        query = query.filter(StFormulaD.secuencia == secuencia)

    formulad = query.first()

    db.session.delete(formulad)

    db.session.commit()

    return jsonify({'Success': 'Detalle de Formula Eliminado'})

@bpcustom.route('/formule_total', methods=['POST'])
@jwt_required()
@cross_origin()
def formule_total():
    data = request.get_json()
    empresa = data['formula']['empresa']
    cod_formula = asigna_cod_comprobante(empresa, 'FD',1)

    query = StFormula.query()
    if empresa:
        query = query.filter(StFormula.empresa == empresa)
    if data['formula']['cod_producto']:
        query = query.filter(StFormula.cod_producto == data['formula']['cod_producto'])
    if data['formula']['debito_credito']:
        query = query.filter(StFormula.debito_credito == data['formula']['debito_credito'])

    existencia = query.first()

    if existencia:
        return jsonify({'error': 'Ya existe formula para: ' + data['formula']['cod_producto']})

    if data['detalles'] is None or data['detalles'] == []:
        return jsonify({'error': 'No hay items ingresados para la formula'})

    formule = StFormula(
        empresa=empresa,
        cod_formula=cod_formula,
        nombre=data['formula']['nombre'],
        cod_producto=data['formula']['cod_producto'],
        cod_unidad='U',
        cantidad_produccion=1,
        activa=data['formula']['activa'],
        mano_obra=data['formula']['mano_obra'],
        costo_standard=data['formula']['costo_standard'],
        debito_credito=data['formula']['debito_credito']
    )
    db.session.add(formule)
    db.session.commit()


    for detalle in data['detalles']:

        detalle_formula = StFormulaD(
            empresa=empresa,
            cod_formula=cod_formula,
            secuencia=obtener_secuencia_formule(cod_formula),
            cod_producto_f=detalle['cod_producto_f'],
            cod_unidad_f='U',
            cantidad_f=detalle['cantidad_f'],
            debito_credito=detalle['debito_credito'],
            costo_standard=detalle['costo_standard'] if detalle['costo_standard'] else 0
        )
        db.session.add(detalle_formula)
        db.session.commit()

    return jsonify({'cod_formula': cod_formula})

@bpcustom.route('/formule_edit', methods=['PUT'])
@jwt_required()
@cross_origin()
def formule_edit():
    try:
        data = request.get_json()
        empresa = data['formula']['empresa']
        cod_formula = data['formula']['cod_formula']
        cod_producto = data['formula']['cod_producto']

        query = StFormula.query()
        if empresa:
            query = query.filter(StFormula.empresa == empresa)
        if cod_producto:
            query = query.filter(StFormula.cod_producto == cod_producto)
        if cod_formula:
            query = query.filter(StFormula.cod_formula == cod_formula)

        formula = query.first()

        if not formula:
            return jsonify({'error': 'No existe la formula'}), 404
        formula.nombre = data['formula']['nombre'] if data['formula']['nombre'] else formula.nombre
        formula.activa = data['formula']['activa']
        formula.debito_credito = data['formula']['debito_credito']
        formula.cod_producto = data['formula']['cod_producto'] if data['formula']['cod_producto'] else formula.cod_producto
        db.session.commit()

        for detalle in data['detalles']:
            if 'secuencia' not in detalle:
                detalle_formula = StFormulaD(
                    empresa=empresa,
                    cod_formula=cod_formula,
                    secuencia=obtener_secuencia_formule(cod_formula),
                    cod_producto_f=detalle['cod_producto_f'],
                    cod_unidad_f='U',
                    cantidad_f=detalle['cantidad_f'],
                    debito_credito=detalle['debito_credito'],
                    costo_standard=0
                )
                db.session.add(detalle_formula)
                db.session.commit()

        return jsonify({'Success': 'Formula correctamente actualizada'})


    except Exception as e:
        logger.exception(f"Error al actualizar Formula: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/validar_existencia', methods=['POST'])
@jwt_required()
@cross_origin()
def validate_existance():

    try:
        data = request.get_json()
        cod_producto = data.get('cod_producto', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db.cursor()
        cursor.execute("""
                    SELECT KS_INVENTARIO.consulta_existencia(
                        :param1,
                        :param2,
                        :param3,
                        :param4,
                        TO_DATE(:param5, 'YYYY/MM/DD'),
                        :param6,
                        :param7,
                        :param8 
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_agencia, param3=cod_producto, param4='U', param5=date.today(), param6=1, param7='Z',
                       param8=1)
        db.close
        result = cursor.fetchone()
        cursor.close()
        return jsonify({'cantidad_inventario': result[0]})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/validar_existencia_disponible', methods=['POST'])
@jwt_required()
@cross_origin()
def validate_available_existance():

    try:
        data = request.get_json()
        cod_formula = data.get('cod_formula', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db.cursor()
        cursor.execute("""
                    SELECT KS_FORMULA_D.consulta_existencia(
                        :param1,
                        :param2,
                        :param3
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_formula, param3=cod_agencia)
        db.close
        result = cursor.fetchone()
        cursor.close()
        return jsonify({'cantidad_inventario_disponible': result[0]})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/generar_combo', methods=['POST'])
@jwt_required()
@cross_origin()
def generate_combo():
    try:
        data = request.get_json()
        cod_formula = data.get('cod_formula', None)
        cantidad = data.get('cantidad', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        usuario = data.get('usuario', None)

        if cantidad <= 0:
            return jsonify({'error': 'Ingrese una cantidad válida'}), 404

        query = StFormula.query()
        if empresa:
            query = query.filter(StFormula.empresa == empresa)
        if cod_formula:
            query = query.filter(StFormula.cod_formula == cod_formula)
        formula = query.first()

        cod_producto = formula.cod_producto
        debito_credito = formula.debito_credito

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        cursor = db1.cursor()
        cursor.execute("""
                    SELECT KS_FORMULA_D.consulta_existencia(
                        :param1,
                        :param2,
                        :param3
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_formula, param3=cod_agencia)
        result = cursor.fetchone()
        cursor.close()

        if result[0] == 0:
            return jsonify({'error': 'No hay inventario para generar '+ formula.nombre}), 404

        if result[0] < cantidad:
            return jsonify({'error': 'Se pueden generar máximo '+ str(result[0]) +' '+ formula.nombre}), 404

        cursor = db1.cursor()
        cursor.execute("""
                            select c.Cod_Tipo_Persona, C.COD_PERSONA, u.useridc
                            from ad_usuarios a,
                                st_vendedor b,
                                persona c,
                                usuario u
                                where a.identificacion=b.cedula
                                and b.empresa=c.empresa
                                and b.cod_tipo_persona=c.cod_tipo_persona
                                and b.cod_vendedor=c.cod_persona
                                and u.usuario_oracle = a.codigo_usuario
                                and u.usuario_oracle = :param1
                                and c.empresa = 20

                        """,
                       param1=usuario)

        result = cursor.fetchone()
        cursor.close()
        if result:
            cod_tipo_persona = result[0]
            cod_persona = result[1]
            useridc = result[2]
        else:
            return jsonify({'error': 'El usuario actual no tiene acceso a st_vendedor'})

        cursor = db1.cursor()
        cursor.execute("""
                    SELECT KS_LIQUIDACION.consulta_cod_liquidacion(
                        :param1,
                        :param2,
                        sysdate                                   
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_agencia)

        result = cursor.fetchone()
        cursor.close()
        if result:
            cod_liquidacion = result[0]
        else:
            return jsonify({'error': 'No existe Liquidacion'})

        ###########################################################ASIGNACION CODIGO COMPROBANTE##################################################################

        query = """
                        DECLARE
                          v_cod_empresa           FLOAT := :1;
                          v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                          v_cod_agencia           FLOAT := :3;
                          v_result                VARCHAR2(50);
                        BEGIN
                          v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                      p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                      p_cod_agencia => v_cod_agencia);
                        :4 := v_result;
                        END;
                        """
        cur = db1.cursor()
        result_var = cur.var(cx_Oracle.STRING)
        cur.execute(query, (empresa, 'IC', cod_agencia, result_var))
        cod_comprobante = result_var.getvalue()
        cur.close()

        ############################################CREACION DE LOTE PARA FORMULA######################################################################

        # query = """
        #                             DECLARE
        #                               v_cod_empresa           FLOAT := :1;
        #                               v_cod_agencia           FLOAT := :2;
        #                               v_tipo_comprobante_lote  VARCHAR2(50) := :3;
        #                               v_tipo_lote             VARCHAR2(3) := :4;
        #                               v_result                VARCHAR2(50);
        #                             BEGIN
        #                               v_result := ks_lote.asigna_codigo(p_empresa => v_cod_empresa,
        #                                                                           p_cod_agencia => v_cod_agencia,
        #                                                                           p_tipo_comprobante_lote => v_tipo_comprobante_lote,
        #                                                                           p_fecha => sysdate,
        #                                                                           P_TIPO_LOTE => v_tipo_lote);
        #                             :5 := v_result;
        #                             END;
        #                             """
        # cur = db1.cursor()
        # result_var = cur.var(cx_Oracle.STRING)
        # cur.execute(query, (empresa, cod_agencia, 'LT', 'IN', result_var))
        # cod_comprobante_lote_formula = result_var.getvalue()
        # cur.close()
        # db1.commit()
        #
        # query = StLote.query()
        # if empresa:
        #     query = query.filter(StLote.empresa == empresa)
        # if cod_agencia:
        #     query = query.filter(StLote.cod_agencia == cod_agencia)
        # if cod_comprobante_lote_formula:
        #     query = query.filter(StLote.cod_comprobante == cod_comprobante_lote_formula)
        #
        # result = query.all()

        lote = StLote(
            empresa=empresa,
            tipo_comprobante='IC',
            cod_comprobante=cod_comprobante,
            fecha=date.today(),
            descripcion='Lote para creacion de combos',
            tipo_lote='IN',
            cod_agencia=cod_agencia,
            usuario_aud=usuario,
            fecha_aud=date.today()
        )
        db.session.add(lote)
        db.session.commit()

        query = """
                                           DECLARE
                                             v_cod_empresa           FLOAT := :1;
                                             v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                                             v_cod_agencia           FLOAT := :3;
                                             v_result                VARCHAR2(50);
                                           BEGIN
                                             v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                                         p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                         p_cod_agencia => v_cod_agencia);
                                           :4 := v_result;
                                           END;
                                           """
        cur = db1.cursor()
        result_var = cur.var(cx_Oracle.STRING)
        cur.execute(query, (empresa, 'TE', cod_agencia, result_var))
        cod_sta_comprobante = result_var.getvalue()
        cur.close()
        db1.commit()

        ###################################GENERACION DE REGISTROS TEMPORALES PARA AGREGAR LOTE PARA PRODUCTO#####################################################

        cursor = db1.cursor()
        cursor.execute("""
                                                    SELECT
                                                    S.Tipo_Comprobante_Lote,
                                                    S.Cod_Comprobante_Lote,
                                                    S.Cantidad,
                                                    L.Fecha_Ingreso
                                                    FROM
                                                        st_inventario_lote S
                                                    JOIN
                                                        ST_Producto_Lote L
                                                    ON
                                                        L.Cod_Producto = S.Cod_Producto
                                                        AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                                        AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                                        AND L.Cod_Tipo_Inventario = 1
                                                        AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                                                    WHERE
                                                        S.Cod_AAMM = 0
                                                        AND S.Cod_Bodega = :param1 
                                                        AND S.Empresa = :param2 
                                                        AND S.Cod_Producto = :param3 
                                                        AND S.Cod_Comprobante_Lote = :param4
                                                    ORDER BY 
                                                        L.Fecha_Ingreso DESC 
                                                                    """,
                       param1=cod_agencia, param2=empresa, param3=cod_producto, param4=cod_comprobante)

        existencia_lote = cursor.fetchall()
        cursor.close()
        if not existencia_lote:
            sta_comprobante = Sta_Comprobante(
                cod_comprobante=cod_sta_comprobante,
                tipo_comprobante='TE',
                empresa=empresa,
                cod_agencia=cod_agencia,
                fecha=date.today(),
                comprobante_manual='INGRESO DE COMBO',
                cod_tipo_persona_a=cod_tipo_persona,
                cod_persona_a=cod_persona,
                cod_tipo_persona_b=cod_tipo_persona,
                cod_persona_b=cod_persona,
                cod_bodega_ingreso=cod_agencia,
                cod_subbodega_ingreso=None,
                cod_bodega_egreso=cod_agencia,
                cod_subbodega_egreso=None,
                cod_liquidacion=cod_liquidacion,
                useridc=useridc,
                es_grabado=0,
                es_anulado=0,
                tipo_transferencia=None,
                tipo_comprobante_pedido=None,
                cod_comprobante_pedido=None,
                cod_estado_producto_egreso=None,
                cod_estado_producto_ingreso=None,
                cod_estado_proceso=None,
                transportador=None,
                placa=None,
                tipo_comprobante_lote='IC',
                cod_comprobante_lote=cod_comprobante,
                cod_comprobante_ingreso=None,
                tipo_comprobante_ingreso=None,
                tipo_identificacion_transporta=None,
                cod_motivo=None,
                ruta=None
            )
            db.session.add(sta_comprobante)

            sta_movimiento = Sta_Movimiento(
                cod_comprobante=cod_sta_comprobante,
                tipo_comprobante='TE',
                empresa=empresa,
                cod_secuencia_mov=1,
                cod_producto=cod_producto,
                cod_unidad='U',
                cantidad=0,
                es_serie=0,
                cod_estado_producto=None,
                ubicacion_bodega=None,
                cod_tipo_lote='LT',
                cod_comprobante_lote=cod_comprobante,
                cod_estado_producto_ing=None,
                cantidad_pedida=None
            )
            db.session.add(sta_movimiento)
            db.session.commit()

            query = """
                                                               DECLARE
                                                                 v_cod_empresa           FLOAT := :1;
                                                                 v_cod_tipo_comprobante  VARCHAR2(2) := :2;
                                                                 v_cod_comprobante       VARCHAR2(10) := :3;
                                                                 v_cod_empresa_g         FLOAT ;
                                                                 v_cod_tipo_comprobante_g VARCHAR2(2) ;
                                                                 v_cod_comprobante_g      VARCHAR2(10) ;
                                                                 v_cod_comprobante_orden  VARCHAR2(10) := :7;
                                                                 v_cod_tipo_comprobante_orden  VARCHAR2(2) := :8;
                                                               BEGIN
                                                                 ksa_comprobante.graba_ni(p_cod_empresa => v_cod_empresa,
                                                                                                             p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                                              p_cod_comprobante => v_cod_comprobante,
                                                                                                              p_cod_empresa_g => v_cod_empresa_g,
                                                                                                              p_cod_tipo_comprobante_g => v_cod_tipo_comprobante_g,
                                                                                                              p_cod_comprobante_g => v_cod_comprobante_g,
                                                                                                              p_cod_comprobante_orden => v_cod_comprobante_orden,
                                                                                                              p_cod_tipo_comprobante_orden => v_cod_tipo_comprobante_orden);
                                                               :4 := v_cod_empresa_g;
                                                               :5 := v_cod_tipo_comprobante_g;
                                                               :6 := v_cod_comprobante_g;
                                                               END;
                                                               """
            cur = db1.cursor()
            result_var0 = cur.var(cx_Oracle.NUMBER)
            result_var1 = cur.var(cx_Oracle.STRING)
            result_var2 = cur.var(cx_Oracle.STRING)
            cur.execute(query, (empresa, 'TE', cod_sta_comprobante, result_var0, result_var1, result_var2, None, None))
            cod_comprobante_ni = result_var2.getvalue()
            cur.close()

            db1.commit()
            print(cod_comprobante_ni)

        ########################################################ADD COMPROBANTE GENERACION DE FORMULA#####################################################

        comprobante = Comprobante(
        empresa = empresa,
        tipo_comprobante = 'IC',
        cod_comprobante = cod_comprobante,
        cod_tipo_persona = cod_tipo_persona,
        cod_persona = cod_persona,
        fecha = date.today(),
        pedido = cod_formula,
        iva = 0,
        valor = 0,
        financiamiento = 0,
        otros = 0,
        descuento = 0,
        tipo_iva = None,
        c_tipo_combrobante = None,
        c_comprobante = None,
        cod_liquidacion = cod_liquidacion,
        useridc = useridc,
        factura_manual = cod_comprobante,
        anulado = 'N',
        guia = cod_formula,
        estado_grabado = None,
        estado_contabilizado = None,
        nombre_persona = None,
        certificado = None,
        secuen_certificado = None,
        orden_compra = None,
        transportador = None,
        placa = None,
        observaciones = None,
        entrada = 0,
        ice = 0,
        cod_agente = cod_persona,
        cod_divisa = 'DOLARES',
        valor_divisa = None,
        cancelada = None,
        saldo = None,
        cod_agencia = cod_agencia,
        forma_pago = None,
        cotizacion = None,
        tipo_comprobante_r = None,
        cod_comprobante_r = None,
        transferencia = None,
        aa_cliente = None,
        codigo_cliente = None,
        estado_comision = None,
        cod_periodo_comision = None,
        linea_contabilidad = None,
        tipo_comprobante_pr = None,
        cod_comprobante_pr = None,
        cod_tipo_persona_gar = None,
        cod_persona_gar = None,
        numero_pagos = 0,
        cuotas_gratis = 0,
        dias_atrazo = 0,
        devolucion_otros = 0,
        valor_alterno = None,
        descuento_promocion = 0,
        cod_bodega_ingreso = cod_agencia,
        cod_subbodega_ingreso = None,
        cod_bodega_egreso = cod_agencia,
        cod_subbodega_egreso = None,
        cod_tarjeta = None,
        num_tarjeta = None,
        num_recap = None,
        num_voucher = None,
        num_autorizacion = None,
        cod_politica = None,
        tipo_comprobante_pedido = None,
        cod_comprobante_pedido = None,
        fecha_ingreso = None,
        rebate = None,
        base_imponible = None,
        base_excenta = None,
        cod_caja = None,
        fecha_vencimiento1 = None,
        por_interes = None,
        aud_fecha = None,
        aud_usuario = None,
        aud_terminal = None,
        cod_tipo_persona_aprob = None,
        cod_persona_aprob = None,
        cod_tipo_persona_verif = None,
        cod_persona_verif = None,
        interes =None
        )

        db.session.add(comprobante)

        ################################################################################################################

        query = StFormulaD.query()
        if empresa:
            query = query.filter(StFormulaD.empresa == empresa)
        if cod_formula:
            query = query.filter(StFormulaD.cod_formula == cod_formula)
        formulaD = query.all()
        total_iteraciones = 2

        ######################################################ADD EGRESOS MOVIMIENTOS POR ITEM##########################
        lotes = []
        costo_formula = 0
        precio_minimo_formula = 0
        precio_maximo_formula = 0
        for item in formulaD:
            cantidad_detalle = item.cantidad_f * cantidad
            print('Detalle: ', item.cod_producto_f, ' ', cantidad_detalle)
            cursor = db1.cursor()
            cursor.execute("""
                            SELECT
                            S.Tipo_Comprobante_Lote,
                            S.Cod_Comprobante_Lote,
                            S.Cantidad,
                            L.Fecha_Ingreso
                            FROM
                                st_inventario_lote S
                            JOIN
                                ST_Producto_Lote L
                            ON
                                L.Cod_Producto = S.Cod_Producto
                                AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                AND L.Cod_Tipo_Inventario = 1
                                AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                            WHERE
                                S.Cod_AAMM = 0
                                AND S.Cod_Bodega = 6
                                AND S.Empresa = 20
                                AND S.Cod_Producto = :param1
                                AND S.Cantidad > 0
                            ORDER BY
                                L.Fecha_Ingreso ASC
                                            """,
                           param1=item.cod_producto_f)
            rows = cursor.fetchall()
            print('Resultados: ', rows)

            for row in rows:
                tipo_comprobante_lote, cod_comprobante_lote, cantidad_lote, fecha_ingreso = row
                print(cod_comprobante_lote, ' ', fecha_ingreso, ' ', cantidad_lote)

                ###################################Obtencion del costo de cada lote para cada producto########################################
                query = """
                DECLARE
                  result NUMBER;
                BEGIN
                  result := ks_producto_lote.obt_costo_valorado_lote(
                    p_cod_empresa => :p_cod_empresa,
                    p_cod_producto => :p_cod_producto,
                    p_cod_comprobante_lote => :p_cod_comprobante_lote,
                    p_tipo_comprobante_lote => :p_tipo_comprobante_lote,
                    p_fecha_final => :p_fecha_final,
                    p_obligatorio => :p_obligatorio
                  );
                  :result := result;
                END;
                """
                cur = db1.cursor()
                result_var = cursor.var(cx_Oracle.NUMBER)

                cur.execute(query, p_cod_empresa=empresa, p_cod_producto=item.cod_producto_f,
                               p_cod_comprobante_lote=cod_comprobante_lote,
                               p_tipo_comprobante_lote=tipo_comprobante_lote, p_fecha_final=date.today(),
                               p_obligatorio=1, result=result_var)

                costo_lote = result_var.getvalue()

                if cantidad_lote <= cantidad_detalle and cantidad_lote:
                    movimiento = Movimiento(
                        empresa=20,
                        tipo_comprobante='IC',
                        cod_comprobante=cod_comprobante,
                        secuencia= total_iteraciones,
                        cod_producto=item.cod_producto_f,
                        cantidad=cantidad_lote,
                        debito_credito=item.debito_credito,
                        cantidad_i=None,
                        precio=costo_lote,
                        descuento=0,
                        costo=float(costo_lote)*int(cantidad_lote),
                        bodega=cod_agencia,
                        iva=0,
                        fecha=date.today(),
                        factura_manual=cod_formula,
                        serie=None,
                        grado=None,
                        cod_subbodega=None,
                        temperatura=None,
                        cod_unidad='U',
                        divisa=0,
                        anulado='N',
                        cantidad_b=None,
                        cantidad_i_b=None,
                        ice=0,
                        lista=None,
                        total_linea=0,
                        porce_descuento=0,
                        valor_alterno=None,
                        es_serie=0,
                        td=None,
                        rebate=None,
                        es_iva=None,
                        cod_estado_producto='A',
                        cod_tipo_inventario=1,
                        cod_promocion=None,
                        ubicacion_bodega=None,
                        cantidad_promocion=None,
                        tipo_comprobante_lote=tipo_comprobante_lote,
                        cod_comprobante_lote=cod_comprobante_lote,
                        descuento_regalo=None,
                        precio_unitario_xml=None,
                        descuento_xml=None,
                        precio_total_sin_impuesto_xml=None,
                        iva_xml=None,
                        ice_xml=None,
                        base_imponible_iva=None,
                        base_imponible_ice=None,
                        cod_producto_xml=None,
                        cod_porcentaje_iva=None
                    )
                    db.session.add(movimiento)
                    total_iteraciones += 1
                    cantidad_detalle = cantidad_detalle - Decimal(str(cantidad_lote))
                    print('Cantidad Detalle actual: ', cantidad_detalle)
                    costo_formula += (float(costo_lote)*int(cantidad_lote))
                else:
                    if Decimal(str(cantidad_lote)) > cantidad_detalle:
                        movimiento = Movimiento(
                            empresa=20,
                            tipo_comprobante='IC',
                            cod_comprobante=cod_comprobante,
                            secuencia=total_iteraciones,
                            cod_producto=item.cod_producto_f,
                            cantidad=cantidad_detalle,
                            debito_credito=item.debito_credito,
                            cantidad_i=None,
                            precio=costo_lote,
                            descuento=0,
                            costo=float(costo_lote)*int(cantidad_detalle),
                            bodega=cod_agencia,
                            iva=0,
                            fecha=date.today(),
                            factura_manual=cod_formula,
                            serie=None,
                            grado=None,
                            cod_subbodega=None,
                            temperatura=None,
                            cod_unidad='U',
                            divisa=0,
                            anulado='N',
                            cantidad_b=None,
                            cantidad_i_b=None,
                            ice=0,
                            lista=None,
                            total_linea=0,
                            porce_descuento=0,
                            valor_alterno=None,
                            es_serie=0,
                            td=None,
                            rebate=None,
                            es_iva=None,
                            cod_estado_producto='A',
                            cod_tipo_inventario=1,
                            cod_promocion=None,
                            ubicacion_bodega=None,
                            cantidad_promocion=None,
                            tipo_comprobante_lote=tipo_comprobante_lote,
                            cod_comprobante_lote=cod_comprobante_lote,
                            descuento_regalo=None,
                            precio_unitario_xml=None,
                            descuento_xml=None,
                            precio_total_sin_impuesto_xml=None,
                            iva_xml=None,
                            ice_xml=None,
                            base_imponible_iva=None,
                            base_imponible_ice=None,
                            cod_producto_xml=None,
                            cod_porcentaje_iva=None
                        )
                        db.session.add(movimiento)
                        print('Ultimo ', cod_comprobante_lote, ' ', fecha_ingreso, ' ', cantidad_lote)
                        costo_formula += (float(costo_lote) * int(cantidad_detalle))
                        total_iteraciones += 1
                        break
            cursor = db1.cursor()

            #Obtener el precio minimo y maximo para cada item
            cursor.execute("""
                            SELECT
                                MAX(precio),
                                MIN(precio)
                            FROM
                                st_lista_precio
                            WHERE
                                empresa = 20
                                AND cod_producto = :param1
                                AND TRUNC(SYSDATE) BETWEEN fecha_inicio AND NVL(fecha_final, TRUNC(SYSDATE))
                           """,
                           param1=item.cod_producto_f)
            result = cursor.fetchone()
            if result[0] is None or result[1] is None:
                return jsonify({'error': 'No existe lista de precios para: ' + item.cod_producto_f })
            max_precio = float(result[0]) * int(item.cantidad_f)
            min_precio = float(result[1]) * int(item.cantidad_f)
            precio_maximo_formula = precio_maximo_formula + max_precio
            precio_minimo_formula = precio_minimo_formula + min_precio
            cursor.close()

            cursor = db1.cursor()
            cursor.execute("""
                            SELECT
                                *
                            FROM
                                st_lista_precio  s
                            WHERE
                                s.cod_producto = :param1
                                AND s.cod_agencia = 6
                                AND TRUNC(SYSDATE) BETWEEN fecha_inicio AND NVL(fecha_final, TRUNC(SYSDATE))
                           """,
                           param1=item.cod_producto_f)

            lista_precios = cursor.fetchall()

            #########################################################ADD MOVIMIENTO INGRESO COMBO################################################################################
            row1 = rows[0]
            if row1:
                lotes.append(row1)
            else:
                return jsonify({'error': 'No existen lotes para el producto ' + row1}), 500

        movimiento = Movimiento(
            empresa=20,
            tipo_comprobante='IC',
            cod_comprobante=cod_comprobante,
            secuencia=1,
            cod_producto=cod_producto,
            cantidad=cantidad,
            debito_credito=debito_credito,
            cantidad_i=None,
            precio=costo_formula,
            descuento=0,
            costo=float(costo_formula),
            bodega=cod_agencia,
            iva=0,
            fecha=date.today(),
            factura_manual=cod_formula,
            serie=None,
            grado=None,
            cod_subbodega=None,
            temperatura=None,
            cod_unidad='U',
            divisa=0,
            anulado='N',
            cantidad_b=None,
            cantidad_i_b=None,
            ice=0,
            lista=None,
            total_linea=0,
            porce_descuento=0,
            valor_alterno=None,
            es_serie=0,
            td=None,
            rebate=None,
            es_iva=None,
            cod_estado_producto='A',
            cod_tipo_inventario=1,
            cod_promocion=None,
            ubicacion_bodega=None,
            cantidad_promocion=None,
            tipo_comprobante_lote='IC',
            cod_comprobante_lote=cod_comprobante,
            descuento_regalo=None,
            precio_unitario_xml=None,
            descuento_xml=None,
            precio_total_sin_impuesto_xml=None,
            iva_xml=None,
            ice_xml=None,
            base_imponible_iva=None,
            base_imponible_ice=None,
            cod_producto_xml=None,
            cod_porcentaje_iva=None
        )
        db.session.add(movimiento)

        cursor.close()

        db1.commit()        ########################################################COMMIT DE SECUENCIAL DE COD COMPROBANTE############################################################

        db.session.commit() #####################################################COMMIT DE COMPROBANTE Y MOVIMIENTOS###################################################################


        ####################################################################OBTENCION DE SECUENCIA#####################################################################################
        cursor = db1.cursor()
        cursor.execute("""
                        SELECT MAX(secuencia)
                        FROM st_gen_lista_precio a
                        WHERE empresa = 20
                        AND a.useridc = 'OHA'
                       """)
        result = cursor.fetchone()
        max_secuencia = int(result[0]) + 1 if result else 0
        cursor.close()

        ###################################################################OBTENCION DE AGENCIAS A ACTUALIZAR LISTA DE PRECIOS DE FORMULA##############################################

        cursor = db1.cursor()

        query_bodegas = """
        SELECT bodega
        FROM sta_seleccion_bodega
        WHERE empresa = 20
        AND usuario = 'JARTEAGA'
        """
        cursor.execute(query_bodegas)
        bodegas = cursor.fetchall()
        cursor.close()
        ########################################################################ACTUALIZACION DE LISTA DE PRECIOS######################################################################

        for row in lista_precios:
            for bodega in bodegas:
                empresa = row[0]
                cod_producto = cod_producto
                cod_modelo_cli = row[2]
                cod_item_cli = row[3]
                cod_modelo_zona = row[4]
                cod_item_zona = row[5]
                cod_agencia_formula = bodega[0]
                cod_unidad = row[7]
                cod_forma_pago = row[8]
                cod_divisa = row[9]
                estado_generacion = row[10]
                fecha_inicio = date.today()
                fecha_final = None
                valor = precio_maximo_formula
                iva = row[14]
                ice = row[15]
                precio = precio_maximo_formula
                cargos = row[17]
                useridc = 'OHA'
                secuencia_generacion = max_secuencia
                estado_vida = row[20]
                valor_alterno = row[21]
                rebate = row[22]
                aud_fecha = row[23]
                aud_usuario = 'JARTEAGA'
                aud_terminal = row[25]

                try:
                    cursor = db1.cursor()
                    cursor.execute("""
                                                   INSERT INTO st_lista_precio (
                                                        empresa, 
                                                        cod_producto, 
                                                        cod_modelo_cli, 
                                                        cod_item_cli, 
                                                        cod_modelo_zona, 
                                                        cod_item_zona, 
                                                        cod_agencia, 
                                                        cod_unidad,
                                                        cod_forma_pago, 
                                                        cod_divisa, 
                                                        estado_generacion, 
                                                        fecha_inicio, 
                                                        fecha_final, 
                                                        valor, 
                                                        iva, 
                                                        ice,
                                                        precio, 
                                                        cargos,
                                                        useridc, 
                                                        secuencia_generacion,
                                                        estado_vida,
                                                        valor_alterno, 
                                                        rebate,
                                                        aud_fecha,
                                                        aud_usuario,
                                                        aud_terminal
                                                   ) VALUES (
                                                        :empresa,
                                                        :cod_producto,
                                                        :cod_modelo_cli,
                                                        :cod_item_cli,
                                                        :cod_modelo_zona,
                                                        :cod_item_zona,
                                                        :cod_agencia,
                                                        :cod_unidad,
                                                        :cod_forma_pago,
                                                        :cod_divisa,
                                                        :estado_generacion,
                                                        :fecha_inicio,
                                                        :fecha_final,
                                                        :valor,
                                                        :iva,
                                                        :ice,
                                                        :precio,
                                                        :cargos,
                                                        :useridc,
                                                        :secuencia_generacion,
                                                        :estado_vida,
                                                        :valor_alterno,
                                                        :rebate,
                                                        :aud_fecha,
                                                        :aud_usuario,
                                                        :aud_terminal

                                                   )
                                                   """,
                                   empresa=empresa,
                                   cod_producto=cod_producto,
                                   cod_modelo_cli=cod_modelo_cli,
                                   cod_item_cli=cod_item_cli,
                                   cod_modelo_zona=cod_modelo_zona,
                                   cod_item_zona=cod_item_zona,
                                   cod_agencia=cod_agencia_formula,
                                   cod_unidad=cod_unidad,
                                   cod_forma_pago=cod_forma_pago,
                                   cod_divisa=cod_divisa,
                                   estado_generacion=estado_generacion,
                                   fecha_inicio=fecha_inicio,
                                   fecha_final=fecha_final,
                                   valor=valor,
                                   iva=iva,
                                   ice=ice,
                                   precio=precio,
                                   cargos=cargos,
                                   useridc=useridc,
                                   secuencia_generacion=secuencia_generacion,
                                   estado_vida=estado_vida,
                                   valor_alterno=valor_alterno,
                                   rebate=rebate,
                                   aud_fecha=aud_fecha,
                                   aud_usuario=aud_usuario,
                                   aud_terminal=aud_terminal
                                   )
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    cursor.close()

                cursor = db1.cursor()
                cursor.execute("""
                    UPDATE st_lista_precio 
                    SET fecha_final = TRUNC(SYSDATE-1) 
                    WHERE cod_producto in (:param1) 
                    AND fecha_inicio < TRUNC(SYSDATE) 
                    AND fecha_final is null
                """, param1=cod_producto)

                cursor.close()
        db1.commit()
        db1.close()
        return jsonify({'success': cod_comprobante})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/desintegrar_combo', methods=['POST'])
@jwt_required()
@cross_origin()
def desintegrate_combo():
    try:
        data = request.get_json()
        cod_formula = data.get('cod_formula', None)
        cantidad = data.get('cantidad', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        usuario = data.get('usuario', None)

        if cantidad <= 0:
            return jsonify({'error': 'Ingrese una cantidad válida'}), 404

        query = StFormula.query()
        if empresa:
            query = query.filter(StFormula.empresa == empresa)
        if cod_formula:
            query = query.filter(StFormula.cod_formula == cod_formula)
        formula = query.first()

        cod_producto = formula.cod_producto
        debito_credito = formula.debito_credito
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        if debito_credito == 1:
            cursor = db1.cursor()
            cursor.execute("""
                                SELECT KS_INVENTARIO.consulta_existencia(
                                    :param1,
                                    :param2,
                                    :param3,
                                    :param4,
                                    sysdate,
                                    :param5

                                ) AS resultado
                                FROM dual
                            """,
                           param1=empresa, param2=cod_agencia, param3=cod_producto, param4='U', param5=1)
            db1.close
            result = cursor.fetchone()
            cursor.close()

            if result[0] == 0:
                return jsonify({'error': 'No hay inventario para desarmar ' + formula.nombre}), 404

            if result[0] < cantidad:
                return jsonify({'error': 'Se pueden desarmar máximo ' + str(result[0]) + ' ' + formula.nombre}), 404

            cursor = db1.cursor()
            cursor.execute("""
                                        select c.Cod_Tipo_Persona, C.COD_PERSONA, u.useridc
                                        from ad_usuarios a,
                                            st_vendedor b,
                                            persona c,
                                            usuario u
                                            where a.identificacion=b.cedula
                                            and b.empresa=c.empresa
                                            and b.cod_tipo_persona=c.cod_tipo_persona
                                            and b.cod_vendedor=c.cod_persona
                                            and u.usuario_oracle = a.codigo_usuario
                                            and u.usuario_oracle = :param1
                                            and c.empresa = 20

                                    """,
                           param1=usuario)
            db1.close
            result = cursor.fetchone()
            cursor.close()

            if result:
                cod_tipo_persona = result[0]
                cod_persona = result[1]
                useridc = result[2]
            else:
                return jsonify({'error': 'El usuario actual no tiene acceso a st_vendedor'})

            cursor = db1.cursor()

            cursor.execute("""
                                SELECT KS_LIQUIDACION.consulta_cod_liquidacion(
                                    :param1,
                                    :param2,
                                    sysdate                                   
                                ) AS resultado
                                FROM dual
                            """,
                           param1=empresa, param2=cod_agencia)
            db1.close
            result = cursor.fetchone()
            cursor.close()
            if result:
                cod_liquidacion = result[0]
            else:
                return jsonify({'error': 'No existe Liquidacion'})

            query = """
                                    DECLARE
                                      v_cod_empresa           FLOAT := :1;
                                      v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                                      v_cod_agencia           FLOAT := :3;
                                      v_result                VARCHAR2(50);
                                    BEGIN
                                      v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                                  p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                  p_cod_agencia => v_cod_agencia);
                                    :4 := v_result;
                                    END;
                                    """
            cur = db1.cursor()
            result_var = cur.var(cx_Oracle.STRING)
            cur.execute(query, (empresa, 'IC', cod_agencia, result_var))
            cod_comprobante = result_var.getvalue()
            cur.close()

            cursor = db1.cursor()
            cursor.execute("""
                                                SELECT Tipo_Comprobante_Lote, Cod_Comprobante_Lote, Fecha_Ingreso
                                                FROM (
                                                  SELECT
                                                    S.Tipo_Comprobante_Lote,
                                                    S.Cod_Comprobante_Lote,
                                                    L.Fecha_Ingreso,
                                                    ROWNUM AS rnum
                                                  FROM
                                                    st_inventario_lote S
                                                  JOIN
                                                    ST_Producto_Lote L
                                                  ON
                                                    L.Cod_Producto = S.Cod_Producto
                                                    AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                                    AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                                    AND L.Cod_Tipo_Inventario = 1
                                                    AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                                                  WHERE
                                                    S.Cod_AAMM = 0
                                                    AND S.Cod_Bodega = 6
                                                    AND S.Empresa = 20
                                                    AND S.Cod_Producto = :param1
                                                    AND S.Cantidad > 0
                                                  ORDER BY
                                                    L.Fecha_Ingreso ASC
                                                )
                                                WHERE
                                                  ROWNUM <= 1
                                            """,
                           param1=cod_producto)
            db1.close

            result = cursor.fetchone()

            if result:
                tipo_comprobante_lote = result[0]
                cod_comprobante_lote = result[1]
            else:
                return jsonify({'error': 'No existe Lote asignado al producto'})

            cursor.close()
            db1.commit()

            comprobante = Comprobante(
                empresa=empresa,
                tipo_comprobante='IC',
                cod_comprobante=cod_comprobante,
                cod_tipo_persona=cod_tipo_persona,
                cod_persona=cod_persona,
                fecha=date.today(),
                pedido=cod_formula,
                iva=0,
                valor=0,
                financiamiento=0,
                otros=0,
                descuento=0,
                tipo_iva=None,
                c_tipo_combrobante=None,
                c_comprobante=None,
                cod_liquidacion=cod_liquidacion,
                useridc=useridc,
                factura_manual=cod_comprobante,
                anulado='N',
                guia=cod_formula,
                estado_grabado=None,
                estado_contabilizado=None,
                nombre_persona=None,
                certificado=None,
                secuen_certificado=None,
                orden_compra=None,
                transportador=None,
                placa=None,
                observaciones=None,
                entrada=0,
                ice=0,
                cod_agente=cod_persona,
                cod_divisa='DOLARES',
                valor_divisa=None,
                cancelada=None,
                saldo=None,
                cod_agencia=cod_agencia,
                forma_pago=None,
                cotizacion=None,
                tipo_comprobante_r=None,
                cod_comprobante_r=None,
                transferencia=None,
                aa_cliente=None,
                codigo_cliente=None,
                estado_comision=None,
                cod_periodo_comision=None,
                linea_contabilidad=None,
                tipo_comprobante_pr=None,
                cod_comprobante_pr=None,
                cod_tipo_persona_gar=None,
                cod_persona_gar=None,
                numero_pagos=0,
                cuotas_gratis=0,
                dias_atrazo=0,
                devolucion_otros=0,
                valor_alterno=None,
                descuento_promocion=0,
                cod_bodega_ingreso=cod_agencia,
                cod_subbodega_ingreso=None,
                cod_bodega_egreso=cod_agencia,
                cod_subbodega_egreso=None,
                cod_tarjeta=None,
                num_tarjeta=None,
                num_recap=None,
                num_voucher=None,
                num_autorizacion=None,
                cod_politica=None,
                tipo_comprobante_pedido=None,
                cod_comprobante_pedido=None,
                fecha_ingreso=None,
                rebate=None,
                base_imponible=None,
                base_excenta=None,
                cod_caja=None,
                fecha_vencimiento1=None,
                por_interes=None,
                aud_fecha=None,
                aud_usuario=None,
                aud_terminal=None,
                cod_tipo_persona_aprob=None,
                cod_persona_aprob=None,
                cod_tipo_persona_verif=None,
                cod_persona_verif=None,
                interes=None
            )

            db.session.add(comprobante)
            db.session.commit()

            query = """
                            DECLARE
                              result NUMBER;
                            BEGIN
                              result := ks_producto_lote.obt_costo_valorado_lote(
                                p_cod_empresa => :p_cod_empresa,
                                p_cod_producto => :p_cod_producto,
                                p_cod_comprobante_lote => :p_cod_comprobante_lote,
                                p_tipo_comprobante_lote => :p_tipo_comprobante_lote,
                                p_fecha_final => :p_fecha_final,
                                p_obligatorio => :p_obligatorio
                              );
                              :result := result;
                            END;
                            """
            cur = db1.cursor()
            result_var = cursor.var(cx_Oracle.NUMBER)

            cur.execute(query, p_cod_empresa=empresa, p_cod_producto=cod_producto,
                        p_cod_comprobante_lote=cod_comprobante_lote,
                        p_tipo_comprobante_lote=tipo_comprobante_lote, p_fecha_final=date.today(),
                        p_obligatorio=1, result=result_var)

            costo_lote = result_var.getvalue()
            cur.close()

            movimiento = Movimiento(
                empresa=20,
                tipo_comprobante='IC',
                cod_comprobante=cod_comprobante,
                secuencia=1,
                cod_producto=cod_producto,
                cantidad=cantidad,
                debito_credito=2,
                cantidad_i=None,
                precio=0,
                descuento=0,
                costo=costo_lote,
                bodega=cod_agencia,
                iva=0,
                fecha=date.today(),
                factura_manual=cod_formula,
                serie=None,
                grado=None,
                cod_subbodega=None,
                temperatura=None,
                cod_unidad='U',
                divisa=0,
                anulado='N',
                cantidad_b=None,
                cantidad_i_b=None,
                ice=0,
                lista=None,
                total_linea=0,
                porce_descuento=0,
                valor_alterno=None,
                es_serie=0,
                td=None,
                rebate=None,
                es_iva=None,
                cod_estado_producto='A',
                cod_tipo_inventario=1,
                cod_promocion=None,
                ubicacion_bodega=None,
                cantidad_promocion=None,
                tipo_comprobante_lote=tipo_comprobante_lote,
                cod_comprobante_lote=cod_comprobante_lote,
                descuento_regalo=None,
                precio_unitario_xml=None,
                descuento_xml=None,
                precio_total_sin_impuesto_xml=None,
                iva_xml=None,
                ice_xml=None,
                base_imponible_iva=None,
                base_imponible_ice=None,
                cod_producto_xml=None,
                cod_porcentaje_iva=None
            )
            db.session.add(movimiento)
            db.session.commit()

            ################################################################################################################

            query = StFormulaD.query()
            if empresa:
                query = query.filter(StFormulaD.empresa == empresa)
            if cod_formula:
                query = query.filter(StFormulaD.cod_formula == cod_formula)
            formulaD = query.all()
            total_iteraciones = 2

            for item in formulaD:
                db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
                cursor = db1.cursor()
                cursor.execute("""
                                        SELECT
                                        S.Tipo_Comprobante_Lote,
                                        S.Cod_Comprobante_Lote,
                                        S.Cantidad,
                                        L.Fecha_Ingreso
                                        FROM
                                            st_inventario_lote S
                                        JOIN
                                            ST_Producto_Lote L
                                        ON
                                            L.Cod_Producto = S.Cod_Producto
                                            AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                            AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                            AND L.Cod_Tipo_Inventario = 1
                                            AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                                        WHERE
                                            S.Cod_AAMM = 0
                                            AND S.Cod_Bodega = 6
                                            AND S.Empresa = 20
                                            AND S.Cod_Producto = :param1
                                            AND S.Cantidad > 0
                                        ORDER BY
                                            L.Fecha_Ingreso ASC
                                                        """,
                               param1=item.cod_producto_f)

                rows = cursor.fetchall()
                if not rows:
                    db1.rollback()
                    db.session.rollback()
                    db1.close()
                    return jsonify({'error': 'No se encontraron lotes de inventario para ' + item.cod_producto_f})

                db1.close

                cantidad_detalle = item.cantidad_f * cantidad
                for row in cursor:
                    tipo_comprobante_lote, cod_comprobante_lote, cantidad_lote, fecha_ingreso = row
                    query = """
                                                                DECLARE
                                                                  result NUMBER;
                                                                BEGIN
                                                                  result := ks_producto_lote.obt_costo_valorado_lote(
                                                                    p_cod_empresa => :p_cod_empresa,
                                                                    p_cod_producto => :p_cod_producto,
                                                                    p_cod_comprobante_lote => :p_cod_comprobante_lote,
                                                                    p_tipo_comprobante_lote => :p_tipo_comprobante_lote,
                                                                    p_fecha_final => :p_fecha_final,
                                                                    p_obligatorio => :p_obligatorio
                                                                  );
                                                                  :result := result;
                                                                END;
                                                                """
                    cur = db1.cursor()
                    result_var = cursor.var(cx_Oracle.NUMBER)

                    cur.execute(query, p_cod_empresa=empresa, p_cod_producto=item.cod_producto_f,
                                p_cod_comprobante_lote=cod_comprobante_lote,
                                p_tipo_comprobante_lote=tipo_comprobante_lote, p_fecha_final=date.today(),
                                p_obligatorio=1, result=result_var)

                    costo_lote = result_var.getvalue()
                    cur.close()
                    if cantidad_lote <= cantidad_detalle:
                        movimiento = Movimiento(
                            empresa=20,
                            tipo_comprobante='IC',
                            cod_comprobante=cod_comprobante,
                            secuencia=total_iteraciones,
                            cod_producto=item.cod_producto_f,
                            cantidad=cantidad_lote,
                            debito_credito=1,
                            cantidad_i=None,
                            precio=0,
                            descuento=0,
                            costo=costo_lote,
                            bodega=cod_agencia,
                            iva=0,
                            fecha=date.today(),
                            factura_manual=cod_formula,
                            serie=None,
                            grado=None,
                            cod_subbodega=None,
                            temperatura=None,
                            cod_unidad='U',
                            divisa=0,
                            anulado='N',
                            cantidad_b=None,
                            cantidad_i_b=None,
                            ice=0,
                            lista=None,
                            total_linea=0,
                            porce_descuento=0,
                            valor_alterno=None,
                            es_serie=0,
                            td=None,
                            rebate=None,
                            es_iva=None,
                            cod_estado_producto='A',
                            cod_tipo_inventario=1,
                            cod_promocion=None,
                            ubicacion_bodega=None,
                            cantidad_promocion=None,
                            tipo_comprobante_lote=tipo_comprobante_lote,
                            cod_comprobante_lote=cod_comprobante_lote,
                            descuento_regalo=None,
                            precio_unitario_xml=None,
                            descuento_xml=None,
                            precio_total_sin_impuesto_xml=None,
                            iva_xml=None,
                            ice_xml=None,
                            base_imponible_iva=None,
                            base_imponible_ice=None,
                            cod_producto_xml=None,
                            cod_porcentaje_iva=None
                        )
                        db.session.add(movimiento)
                        db.session.commit()
                        total_iteraciones += 1
                        cantidad_detalle = cantidad_detalle - Decimal(str(cantidad_lote))
                    else:
                        movimiento = Movimiento(
                            empresa=20,
                            tipo_comprobante='IC',
                            cod_comprobante=cod_comprobante,
                            secuencia=total_iteraciones,
                            cod_producto=item.cod_producto_f,
                            cantidad=cantidad_detalle,
                            debito_credito=1,
                            cantidad_i=None,
                            precio=0,
                            descuento=0,
                            costo=costo_lote,
                            bodega=cod_agencia,
                            iva=0,
                            fecha=date.today(),
                            factura_manual=cod_formula,
                            serie=None,
                            grado=None,
                            cod_subbodega=None,
                            temperatura=None,
                            cod_unidad='U',
                            divisa=0,
                            anulado='N',
                            cantidad_b=None,
                            cantidad_i_b=None,
                            ice=0,
                            lista=None,
                            total_linea=0,
                            porce_descuento=0,
                            valor_alterno=None,
                            es_serie=0,
                            td=None,
                            rebate=None,
                            es_iva=None,
                            cod_estado_producto='A',
                            cod_tipo_inventario=1,
                            cod_promocion=None,
                            ubicacion_bodega=None,
                            cantidad_promocion=None,
                            tipo_comprobante_lote=tipo_comprobante_lote,
                            cod_comprobante_lote=cod_comprobante_lote,
                            descuento_regalo=None,
                            precio_unitario_xml=None,
                            descuento_xml=None,
                            precio_total_sin_impuesto_xml=None,
                            iva_xml=None,
                            ice_xml=None,
                            base_imponible_iva=None,
                            base_imponible_ice=None,
                            cod_producto_xml=None,
                            cod_porcentaje_iva=None
                        )
                        db.session.add(movimiento)
                        db.session.commit()
                        total_iteraciones += 1
                        break

                cursor.close()
                db1.close()
        else:
            if debito_credito == 2:
                print('Desintegrar despiece')
        return jsonify({'success': cod_comprobante})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/lotes_by_prod', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_lotes():
    try:
        data = request.get_json()
        cod_producto = data.get('cod_producto', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        cursor.execute("""
                                            SELECT
                                            S.Tipo_Comprobante_Lote,
                                            S.Cod_Comprobante_Lote,
                                            S.Cantidad,
                                            L.Fecha_Ingreso
                                            FROM
                                                st_inventario_lote S
                                            JOIN
                                                ST_Producto_Lote L
                                            ON
                                                L.Cod_Producto = S.Cod_Producto
                                                AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                                AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                                AND L.Cod_Tipo_Inventario = 1
                                                AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                                            WHERE
                                                S.Cod_AAMM = 0
                                                AND S.Cod_Bodega = :param1 
                                                AND S.Empresa = :param2 
                                                AND S.Cod_Producto = :param3 
                                                AND S.Cantidad > 0 
                                            ORDER BY 
                                                L.Fecha_Ingreso DESC 
                                                            """,
                       param1=cod_agencia, param2=empresa, param3=cod_producto)

        lotes_prod = cursor.fetchall()
        lotes = []

        for lote in lotes_prod:
            lote_dict = {
                'tipo_comprobante_lote': lote[0],
                'cod_comprobante_lote': lote[1],
                'cantidad': lote[2],
                'fecha_ingreso': str(lote[3])
            }
            lotes.append(lote_dict)

        if not lotes:
            return jsonify({'error': 'Se creará un nuevo lote para el producto'}), 500

        return jsonify({'lotes': lotes})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpcustom.route('/generar_despiece', methods=['POST'])
@jwt_required()
@cross_origin()
def generate_despiece():
    try:
        data = request.get_json()
        cod_formula = data.get('cod_formula', None)
        cantidad = data.get('cantidad', None)
        empresa = data.get('empresa', None)
        cod_agencia = data.get('cod_agencia', None)
        cod_comprobante_lote = data.get('cod_comprobante_lote', None)
        fecha_ingreso = data.get('fecha_ingreso', None)
        tipo_comprobante_lote = data.get('tipo_comprobante_lote', None)
        usuario = data.get('usuario', None)
        print(cod_comprobante_lote, ' ', tipo_comprobante_lote)
        if cantidad <= 0:
            return jsonify({'error': 'Ingrese una cantidad válida'}), 404

        query = StFormula.query()
        if empresa:
            query = query.filter(StFormula.empresa == empresa)
        if cod_formula:
            query = query.filter(StFormula.cod_formula == cod_formula)
        formula = query.first()

        cod_producto = formula.cod_producto
        debito_credito = formula.debito_credito

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        cursor = db1.cursor()
        cursor.execute("""
                            SELECT KS_INVENTARIO.consulta_existencia(
                                :param1,
                                :param2,
                                :param3,
                                :param4,
                                TO_DATE(:param5, 'YYYY/MM/DD'),
                                :param6,
                                :param7,
                                :param8 
                            ) AS resultado
                            FROM dual
                        """,
                       param1=empresa, param2=cod_agencia, param3=cod_producto, param4='U', param5=date.today(),
                       param6=1, param7='Z',
                       param8=1)
        result = cursor.fetchone()
        cursor.close()

        if result[0] == 0:
            return jsonify({'error': 'No hay inventario para desintegrar '+ formula.nombre}), 404

        if result[0] < cantidad:
            return jsonify({'error': 'Se pueden desintegrar máximo '+ str(result[0]) +' '+ formula.nombre}), 404

        cursor = db1.cursor()
        cursor.execute("""
                            select c.Cod_Tipo_Persona, C.COD_PERSONA, u.useridc
                            from ad_usuarios a,
                                st_vendedor b,
                                persona c,
                                usuario u
                                where a.identificacion=b.cedula
                                and b.empresa=c.empresa
                                and b.cod_tipo_persona=c.cod_tipo_persona
                                and b.cod_vendedor=c.cod_persona
                                and u.usuario_oracle = a.codigo_usuario
                                and u.usuario_oracle = :param1
                                and c.empresa = 20

                        """,
                       param1=usuario)

        result = cursor.fetchone()
        cursor.close()
        if result:
            cod_tipo_persona = result[0]
            cod_persona = result[1]
            useridc = result[2]
        else:
            return jsonify({'error': 'El usuario actual no tiene acceso a st_vendedor'})

        cursor = db1.cursor()
        cursor.execute("""
                    SELECT KS_LIQUIDACION.consulta_cod_liquidacion(
                        :param1,
                        :param2,
                        sysdate                                   
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_agencia)

        result = cursor.fetchone()
        cursor.close()
        if result:
            cod_liquidacion = result[0]
        else:
            return jsonify({'error': 'No existe Liquidacion'})

        ###########################################################ASIGNACION CODIGO COMPROBANTE##################################################################

        query = """
                        DECLARE
                          v_cod_empresa           FLOAT := :1;
                          v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                          v_cod_agencia           FLOAT := :3;
                          v_result                VARCHAR2(50);
                        BEGIN
                          v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                      p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                      p_cod_agencia => v_cod_agencia);
                        :4 := v_result;
                        END;
                        """
        cur = db1.cursor()
        result_var = cur.var(cx_Oracle.STRING)
        cur.execute(query, (empresa, 'IC', cod_agencia, result_var))
        cod_comprobante = result_var.getvalue()
        cur.close()

        ########################################################OBTENCION DE COSTO VALORADO DE FORMULA####################################################

        query = """
                        DECLARE
                          result NUMBER;
                        BEGIN
                          result := ks_producto_lote.obt_costo_valorado_lote(
                            p_cod_empresa => :p_cod_empresa,
                            p_cod_producto => :p_cod_producto,
                            p_cod_comprobante_lote => :p_cod_comprobante_lote,
                            p_tipo_comprobante_lote => :p_tipo_comprobante_lote,
                            p_fecha_final => :p_fecha_final,
                            p_obligatorio => :p_obligatorio
                          );
                          :result := result;
                        END;
                        """
        cur = db1.cursor()
        result_var = cursor.var(cx_Oracle.NUMBER)

        cur.execute(query, p_cod_empresa=empresa, p_cod_producto=cod_producto,
                    p_cod_comprobante_lote=cod_comprobante_lote,
                    p_tipo_comprobante_lote=tipo_comprobante_lote, p_fecha_final=date.today(),
                    p_obligatorio=1, result=result_var)

        costo_lote = result_var.getvalue()

        ########################################################ADD COMPROBANTE GENERACION DE FORMULA#####################################################

        comprobante = Comprobante(
        empresa = empresa,
        tipo_comprobante = 'IC',
        cod_comprobante = cod_comprobante,
        cod_tipo_persona = cod_tipo_persona,
        cod_persona = cod_persona,
        fecha = date.today(),
        pedido = cod_formula,
        iva = 0,
        valor = 0,
        financiamiento = 0,
        otros = 0,
        descuento = 0,
        tipo_iva = None,
        c_tipo_combrobante = None,
        c_comprobante = None,
        cod_liquidacion = cod_liquidacion,
        useridc = useridc,
        factura_manual = cod_comprobante,
        anulado = 'N',
        guia = cod_formula,
        estado_grabado = None,
        estado_contabilizado = None,
        nombre_persona = None,
        certificado = None,
        secuen_certificado = None,
        orden_compra = None,
        transportador = None,
        placa = None,
        observaciones = None,
        entrada = 0,
        ice = 0,
        cod_agente = cod_persona,
        cod_divisa = 'DOLARES',
        valor_divisa = None,
        cancelada = None,
        saldo = None,
        cod_agencia = cod_agencia,
        forma_pago = None,
        cotizacion = None,
        tipo_comprobante_r = None,
        cod_comprobante_r = None,
        transferencia = None,
        aa_cliente = None,
        codigo_cliente = None,
        estado_comision = None,
        cod_periodo_comision = None,
        linea_contabilidad = None,
        tipo_comprobante_pr = None,
        cod_comprobante_pr = None,
        cod_tipo_persona_gar = None,
        cod_persona_gar = None,
        numero_pagos = 0,
        cuotas_gratis = 0,
        dias_atrazo = 0,
        devolucion_otros = 0,
        valor_alterno = None,
        descuento_promocion = 0,
        cod_bodega_ingreso = cod_agencia,
        cod_subbodega_ingreso = None,
        cod_bodega_egreso = cod_agencia,
        cod_subbodega_egreso = None,
        cod_tarjeta = None,
        num_tarjeta = None,
        num_recap = None,
        num_voucher = None,
        num_autorizacion = None,
        cod_politica = None,
        tipo_comprobante_pedido = None,
        cod_comprobante_pedido = None,
        fecha_ingreso = None,
        rebate = None,
        base_imponible = None,
        base_excenta = None,
        cod_caja = None,
        fecha_vencimiento1 = None,
        por_interes = None,
        aud_fecha = None,
        aud_usuario = None,
        aud_terminal = None,
        cod_tipo_persona_aprob = None,
        cod_persona_aprob = None,
        cod_tipo_persona_verif = None,
        cod_persona_verif = None,
        interes =None
        )

        db.session.add(comprobante)

        movimiento = Movimiento(
            empresa=20,
            tipo_comprobante='IC',
            cod_comprobante=cod_comprobante,
            secuencia=1,
            cod_producto=cod_producto,
            cantidad=cantidad,
            debito_credito=debito_credito,
            cantidad_i=None,
            precio=costo_lote,
            descuento=0,
            costo=float(costo_lote) * int(cantidad),
            bodega=cod_agencia,
            iva=0,
            fecha=date.today(),
            factura_manual=cod_formula,
            serie=None,
            grado=None,
            cod_subbodega=None,
            temperatura=None,
            cod_unidad='U',
            divisa=0,
            anulado='N',
            cantidad_b=None,
            cantidad_i_b=None,
            ice=0,
            lista=None,
            total_linea=0,
            porce_descuento=0,
            valor_alterno=None,
            es_serie=0,
            td=None,
            rebate=None,
            es_iva=None,
            cod_estado_producto='A',
            cod_tipo_inventario=1,
            cod_promocion=None,
            ubicacion_bodega=None,
            cantidad_promocion=None,
            tipo_comprobante_lote=tipo_comprobante_lote,
            cod_comprobante_lote=cod_comprobante_lote,
            descuento_regalo=None,
            precio_unitario_xml=None,
            descuento_xml=None,
            precio_total_sin_impuesto_xml=None,
            iva_xml=None,
            ice_xml=None,
            base_imponible_iva=None,
            base_imponible_ice=None,
            cod_producto_xml=None,
            cod_porcentaje_iva=None
        )
        db.session.add(movimiento)

        query = StFormulaD.query()
        if empresa:
            query = query.filter(StFormulaD.empresa == empresa)
        if cod_formula:
            query = query.filter(StFormulaD.cod_formula == cod_formula)
        formulaD = query.all()
        total_iteraciones = 2

        ######################################################ADD EGRESOS MOVIMIENTOS POR ITEM##########################

        for item in formulaD:
            cantidad_detalle = item.cantidad_f * cantidad
            cursor = db1.cursor()
            cursor.execute("""
                            SELECT
                            S.Tipo_Comprobante_Lote,
                            S.Cod_Comprobante_Lote,
                            S.Cantidad,
                            L.Fecha_Ingreso
                            FROM
                                st_inventario_lote S
                            JOIN
                                ST_Producto_Lote L
                            ON
                                L.Cod_Producto = S.Cod_Producto
                                AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                AND L.Cod_Tipo_Inventario = 1
                                AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                            WHERE
                                S.Cod_AAMM = 0
                                AND S.Cod_Bodega = 6
                                AND S.Empresa = 20
                                AND S.Cod_Producto = :param1
                                AND S.Cantidad > 0
                            ORDER BY
                                L.Fecha_Ingreso DESC
                                            """,
                           param1=item.cod_producto_f)
            rows = cursor.fetchone()
            print('Resultado: ', rows)
            ############################################VALIDACION DE EXISTENCIA DE LOTES#########################################################################
            if rows is None:
                query = """
                                                    DECLARE
                                                      v_cod_empresa           FLOAT := :1;
                                                      v_cod_agencia           FLOAT := :2;
                                                      v_tipo_comprobante_lote  VARCHAR2(50) := :3;
                                                      v_tipo_lote             VARCHAR2(3) := :4;  
                                                      v_result                VARCHAR2(50);
                                                    BEGIN
                                                      v_result := ks_lote.asigna_codigo(p_empresa => v_cod_empresa,
                                                                                                  p_cod_agencia => v_cod_agencia,
                                                                                                  p_tipo_comprobante_lote => v_tipo_comprobante_lote,
                                                                                                  p_fecha => sysdate,
                                                                                                  P_TIPO_LOTE => v_tipo_lote);
                                                    :5 := v_result;
                                                    END;
                                                    """
                cur = db1.cursor()
                result_var = cur.var(cx_Oracle.STRING)
                cur.execute(query, (empresa, cod_agencia, 'LT', 'IN', result_var))
                cod_comprobante_lote = result_var.getvalue()
                tipo_comprobante_lote = 'LT'
                cantidad_lote = 0
                fecha_ingreso = date.today()

                cur.close()
                db1.commit()

                query = StLote.query()
                if empresa:
                    query = query.filter(StLote.empresa == empresa)
                if cod_agencia:
                    query = query.filter(StLote.cod_agencia == cod_agencia)
                if cod_comprobante_lote:
                    query = query.filter(StLote.cod_comprobante == cod_comprobante_lote)

                result = query.all()

                if not result:
                    lote = StLote(
                        empresa=empresa,
                        tipo_comprobante='LT',
                        cod_comprobante=cod_comprobante_lote,
                        fecha=date.today(),
                        descripcion='Lote para desintegracion de combos',
                        tipo_lote='IN',
                        cod_agencia=cod_agencia,
                        usuario_aud=usuario,
                        fecha_aud=date.today()
                    )
                    db.session.add(lote)
                    db.session.commit()

                query = """
                                                          DECLARE
                                                            v_cod_empresa           FLOAT := :1;
                                                            v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                                                            v_cod_agencia           FLOAT := :3;
                                                            v_result                VARCHAR2(50);
                                                          BEGIN
                                                            v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                                                        p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                                        p_cod_agencia => v_cod_agencia);
                                                          :4 := v_result;
                                                          END;
                                                          """
                cur = db1.cursor()
                result_var = cur.var(cx_Oracle.STRING)
                cur.execute(query, (empresa, 'TE', cod_agencia, result_var))
                cod_sta_comprobante_item = result_var.getvalue()
                cur.close()
                db1.commit()

                ###################################GENERACION DE REGISTROS TEMPORALES PARA AGREGAR LOTE PARA PRODUCTO#####################################################

                cursor = db1.cursor()
                cursor.execute("""
                                                                   SELECT
                                                                   S.Tipo_Comprobante_Lote,
                                                                   S.Cod_Comprobante_Lote,
                                                                   S.Cantidad,
                                                                   L.Fecha_Ingreso
                                                                   FROM
                                                                       st_inventario_lote S
                                                                   JOIN
                                                                       ST_Producto_Lote L
                                                                   ON
                                                                       L.Cod_Producto = S.Cod_Producto
                                                                       AND L.Cod_Comprobante_Lote = S.Cod_Comprobante_Lote
                                                                       AND L.Tipo_Comprobante_Lote = S.Tipo_Comprobante_Lote
                                                                       AND L.Cod_Tipo_Inventario = 1
                                                                       AND L.COD_TIPO_INVENTARIO = S.COD_TIPO_INVENTARIO
                                                                   WHERE
                                                                       S.Cod_AAMM = 0
                                                                       AND S.Cod_Bodega = :param1 
                                                                       AND S.Empresa = :param2 
                                                                       AND S.Cod_Producto = :param3 
                                                                       AND S.Cod_Comprobante_Lote = :param4
                                                                   ORDER BY 
                                                                       L.Fecha_Ingreso DESC 
                                                                                   """,
                               param1=cod_agencia, param2=empresa, param3=item.cod_producto_f,
                               param4=cod_comprobante_lote)

                existencia_lote = cursor.fetchall()
                cursor.close()

                if not existencia_lote:
                    sta_comprobante = Sta_Comprobante(
                        cod_comprobante=cod_sta_comprobante_item,
                        tipo_comprobante='TE',
                        empresa=empresa,
                        cod_agencia=cod_agencia,
                        fecha=date.today(),
                        comprobante_manual='DESINTEGRACION DE COMBO',
                        cod_tipo_persona_a=cod_tipo_persona,
                        cod_persona_a=cod_persona,
                        cod_tipo_persona_b=cod_tipo_persona,
                        cod_persona_b=cod_persona,
                        cod_bodega_ingreso=cod_agencia,
                        cod_subbodega_ingreso=None,
                        cod_bodega_egreso=cod_agencia,
                        cod_subbodega_egreso=None,
                        cod_liquidacion=cod_liquidacion,
                        useridc=useridc,
                        es_grabado=0,
                        es_anulado=0,
                        tipo_transferencia=None,
                        tipo_comprobante_pedido=None,
                        cod_comprobante_pedido=None,
                        cod_estado_producto_egreso=None,
                        cod_estado_producto_ingreso=None,
                        cod_estado_proceso=None,
                        transportador=None,
                        placa=None,
                        tipo_comprobante_lote='LT',
                        cod_comprobante_lote=cod_comprobante_lote,
                        cod_comprobante_ingreso=None,
                        tipo_comprobante_ingreso=None,
                        tipo_identificacion_transporta=None,
                        cod_motivo=None,
                        ruta=None
                    )
                    db.session.add(sta_comprobante)

                    sta_movimiento = Sta_Movimiento(
                        cod_comprobante=cod_sta_comprobante_item,
                        tipo_comprobante='TE',
                        empresa=empresa,
                        cod_secuencia_mov=1,
                        cod_producto=item.cod_producto_f,
                        cod_unidad='U',
                        cantidad=0,
                        es_serie=0,
                        cod_estado_producto=None,
                        ubicacion_bodega=None,
                        cod_tipo_lote='LT',
                        cod_comprobante_lote=cod_comprobante_lote,
                        cod_estado_producto_ing=None,
                        cantidad_pedida=None
                    )
                    db.session.add(sta_movimiento)
                    db.session.commit()

                    query = """
                                                                              DECLARE
                                                                                v_cod_empresa           FLOAT := :1;
                                                                                v_cod_tipo_comprobante  VARCHAR2(2) := :2;
                                                                                v_cod_comprobante       VARCHAR2(10) := :3;
                                                                                v_cod_empresa_g         FLOAT ;
                                                                                v_cod_tipo_comprobante_g VARCHAR2(2) ;
                                                                                v_cod_comprobante_g      VARCHAR2(10) ;
                                                                                v_cod_comprobante_orden  VARCHAR2(10) := :7;
                                                                                v_cod_tipo_comprobante_orden  VARCHAR2(2) := :8;
                                                                              BEGIN
                                                                                ksa_comprobante.graba_ni(p_cod_empresa => v_cod_empresa,
                                                                                                                            p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                                                             p_cod_comprobante => v_cod_comprobante,
                                                                                                                             p_cod_empresa_g => v_cod_empresa_g,
                                                                                                                             p_cod_tipo_comprobante_g => v_cod_tipo_comprobante_g,
                                                                                                                             p_cod_comprobante_g => v_cod_comprobante_g,
                                                                                                                             p_cod_comprobante_orden => v_cod_comprobante_orden,
                                                                                                                             p_cod_tipo_comprobante_orden => v_cod_tipo_comprobante_orden);
                                                                              :4 := v_cod_empresa_g;
                                                                              :5 := v_cod_tipo_comprobante_g;
                                                                              :6 := v_cod_comprobante_g;
                                                                              END;
                                                                              """
                    cur = db1.cursor()
                    result_var0 = cur.var(cx_Oracle.NUMBER)
                    result_var1 = cur.var(cx_Oracle.STRING)
                    result_var2 = cur.var(cx_Oracle.STRING)
                    cur.execute(query,
                                (empresa, 'TE', cod_sta_comprobante_item, result_var0, result_var1, result_var2, None, None))
                    cod_comprobante_ni = result_var2.getvalue()
                    cur.close()
                    db1.commit()
            else:
                tipo_comprobante_lote, cod_comprobante_lote, cantidad_lote, fecha_ingreso = rows
            ######################################################################################################################################################

            print(cod_comprobante_lote, ' ', fecha_ingreso, ' ', cantidad_lote)
            movimiento = Movimiento(
                empresa=20,
                tipo_comprobante='IC',
                cod_comprobante=cod_comprobante,
                secuencia= total_iteraciones,
                cod_producto=item.cod_producto_f,
                cantidad=float(item.cantidad_f) * int(cantidad),
                debito_credito=item.debito_credito,
                cantidad_i=None,
                precio=(float(costo_lote) * float(item.costo_standard))/100,
                descuento=0,
                costo=((float(costo_lote) * float(item.costo_standard))/100) * int(cantidad),
                bodega=cod_agencia,
                iva=0,
                fecha=date.today(),
                factura_manual=cod_formula,
                serie=None,
                grado=None,
                cod_subbodega=None,
                temperatura=item.costo_standard,
                cod_unidad='U',
                divisa=0,
                anulado='N',
                cantidad_b=None,
                cantidad_i_b=None,
                ice=0,
                lista=None,
                total_linea=0,
                porce_descuento=0,
                valor_alterno=None,
                es_serie=0,
                td=None,
                rebate=None,
                es_iva=None,
                cod_estado_producto='A',
                cod_tipo_inventario=1,
                cod_promocion=None,
                ubicacion_bodega=None,
                cantidad_promocion=None,
                tipo_comprobante_lote=tipo_comprobante_lote,
                cod_comprobante_lote=cod_comprobante_lote,
                descuento_regalo=None,
                precio_unitario_xml=None,
                descuento_xml=None,
                precio_total_sin_impuesto_xml=None,
                iva_xml=None,
                ice_xml=None,
                base_imponible_iva=None,
                base_imponible_ice=None,
                cod_producto_xml=None,
                cod_porcentaje_iva=None
            )
            db.session.add(movimiento)
            total_iteraciones += 1

            cursor = db1.cursor()

            # Obtener el precio minimo y maximo para cada item
            cursor.execute("""
                                        SELECT
                                            MAX(precio),
                                            MIN(precio)
                                        FROM
                                            st_lista_precio
                                        WHERE
                                            empresa = 20
                                            AND cod_producto = :param1
                                            AND TRUNC(SYSDATE) BETWEEN fecha_inicio AND NVL(fecha_final, TRUNC(SYSDATE))
                                       """,
                           param1=cod_producto)
            result = cursor.fetchone()
            max_precio = result[0]
            min_precio = result[1]
            precio_maximo_item = float(max_precio) * float(item.costo_standard) / 100
            precio_minimo_item = float(min_precio) * float(item.costo_standard) / 100
            cursor.close()

            cursor = db1.cursor()
            cursor.execute("""
                                        SELECT
                                            *
                                        FROM
                                            st_lista_precio  s
                                        WHERE
                                            s.cod_producto = :param1
                                            AND s.cod_agencia = 6
                                            AND TRUNC(SYSDATE) BETWEEN fecha_inicio AND NVL(fecha_final, TRUNC(SYSDATE))
                                       """,
                           param1=cod_producto)

            lista_precios = cursor.fetchall()

            ####################################################################OBTENCION DE SECUENCIA#####################################################################################
            cursor = db1.cursor()
            cursor.execute("""
                                    SELECT MAX(secuencia)
                                    FROM st_gen_lista_precio a
                                    WHERE empresa = 20
                                    AND a.useridc = 'OHA'
                                   """)
            result = cursor.fetchone()
            max_secuencia = int(result[0]) + 1 if result else 0
            cursor.close()

            ###################################################################OBTENCION DE AGENCIAS A ACTUALIZAR LISTA DE PRECIOS DE FORMULA##############################################

            cursor = db1.cursor()

            query_bodegas = """
                    SELECT bodega
                    FROM sta_seleccion_bodega
                    WHERE empresa = 20
                    AND usuario = 'JARTEAGA'
                    """
            cursor.execute(query_bodegas)
            bodegas = cursor.fetchall()

            ########################################################################ACTUALIZACION DE LISTA DE PRECIOS######################################################################

            for row in lista_precios:
                for bodega in bodegas:
                    empresa = row[0]
                    cod_producto_item = item.cod_producto_f
                    cod_modelo_cli = row[2]
                    cod_item_cli = row[3]
                    cod_modelo_zona = row[4]
                    cod_item_zona = row[5]
                    cod_agencia_precio = bodega[0]
                    cod_unidad = row[7]
                    cod_forma_pago = row[8]
                    cod_divisa = row[9]
                    estado_generacion = row[10]
                    fecha_inicio = date.today()
                    fecha_final = None
                    valor = precio_maximo_item
                    iva = row[14]
                    ice = row[15]
                    precio = precio_maximo_item
                    cargos = row[17]
                    useridc = 'OHA'
                    secuencia_generacion = max_secuencia
                    estado_vida = row[20]
                    valor_alterno = row[21]
                    rebate = row[22]
                    aud_fecha = row[23]
                    aud_usuario = 'JARTEAGA'
                    aud_terminal = row[25]

                    try:
                        cursor = db1.cursor()
                        cursor.execute("""
                            INSERT INTO st_lista_precio (
                                empresa, 
                                cod_producto, 
                                cod_modelo_cli, 
                                cod_item_cli, 
                                cod_modelo_zona, 
                                cod_item_zona, 
                                cod_agencia, 
                                cod_unidad,
                                cod_forma_pago, 
                                cod_divisa, 
                                estado_generacion, 
                                fecha_inicio, 
                                fecha_final, 
                                valor, 
                                iva, 
                                ice,
                                precio, 
                                cargos,
                                useridc, 
                                secuencia_generacion,
                                estado_vida,
                                valor_alterno, 
                                rebate,
                                aud_fecha,
                                aud_usuario,
                                aud_terminal
                            ) VALUES (
                                :empresa,
                                :cod_producto,
                                :cod_modelo_cli,
                                :cod_item_cli,
                                :cod_modelo_zona,
                                :cod_item_zona,
                                :cod_agencia,
                                :cod_unidad,
                                :cod_forma_pago,
                                :cod_divisa,
                                :estado_generacion,
                                :fecha_inicio,
                                :fecha_final,
                                :valor,
                                :iva,
                                :ice,
                                :precio,
                                :cargos,
                                :useridc,
                                :secuencia_generacion,
                                :estado_vida,
                                :valor_alterno,
                                :rebate,
                                :aud_fecha,
                                :aud_usuario,
                                :aud_terminal
                            )
                            """,
                                       empresa=empresa,
                                       cod_producto=cod_producto_item,
                                       cod_modelo_cli=cod_modelo_cli,
                                       cod_item_cli=cod_item_cli,
                                       cod_modelo_zona=cod_modelo_zona,
                                       cod_item_zona=cod_item_zona,
                                       cod_agencia=cod_agencia_precio,
                                       cod_unidad=cod_unidad,
                                       cod_forma_pago=cod_forma_pago,
                                       cod_divisa=cod_divisa,
                                       estado_generacion=estado_generacion,
                                       fecha_inicio=fecha_inicio,
                                       fecha_final=fecha_final,
                                       valor=valor,
                                       iva=iva,
                                       ice=ice,
                                       precio=precio,
                                       cargos=cargos,
                                       useridc=useridc,
                                       secuencia_generacion=secuencia_generacion,
                                       estado_vida=estado_vida,
                                       valor_alterno=valor_alterno,
                                       rebate=rebate,
                                       aud_fecha=aud_fecha,
                                       aud_usuario=aud_usuario,
                                       aud_terminal=aud_terminal
                                       )
                    except Exception as e:
                        print('Ya existe lista de precios para: '+ item.cod_producto_f)
                    finally:
                        cursor.close()

            cursor = db1.cursor()
            cursor.execute("""
                               UPDATE st_lista_precio 
                               SET fecha_final = TRUNC(SYSDATE-1) 
                               WHERE cod_producto in (:param1) 
                               AND fecha_inicio < TRUNC(SYSDATE) 
                               AND fecha_final is null
                           """, param1=item.cod_producto_f)

            cursor.close()
        #########################################################ADD MOVIMIENTO INGRESO COMBO################################################################################


        db1.commit()        ########################################################COMMIT DE SECUENCIAL DE COD COMPROBANTE############################################################
        db1.close()
        db.session.commit() #####################################################COMMIT DE COMPROBANTE Y MOVIMIENTOS###################################################################
        return jsonify({'success': cod_comprobante})

    except Exception as e:
        logger.exception(f"Error al obtener : {str(e)}")
        db1.rollback()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bpcustom.route('/create_lote', methods=['POST'])
#@jwt_required()
@cross_origin()
def create_lote():
    db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    data = request.get_json()
    empresa = data['empresa']
    cod_agencia = data['agencia']

    query = """
                            DECLARE
                              v_cod_empresa           FLOAT := :1;
                              v_cod_agencia           FLOAT := :2;
                              v_tipo_comprobante_lote  VARCHAR2(50) := :3;
                              v_tipo_lote             VARCHAR2(3) := :4;  
                              v_result                VARCHAR2(50);
                            BEGIN
                              v_result := ks_lote.asigna_codigo(p_empresa => v_cod_empresa,
                                                                          p_cod_agencia => v_cod_agencia,
                                                                          p_tipo_comprobante_lote => v_tipo_comprobante_lote,
                                                                          p_fecha => sysdate,
                                                                          P_TIPO_LOTE => v_tipo_lote);
                            :5 := v_result;
                            END;
                            """
    cur = db1.cursor()
    result_var = cur.var(cx_Oracle.STRING)
    cur.execute(query, (empresa, cod_agencia, 'LT', 'IN', result_var))
    cod_comprobante_lote = result_var.getvalue()
    cur.close()
    db1.commit()

    query = StLote.query()
    if empresa:
        query = query.filter(StLote.empresa == empresa)
    if cod_agencia:
        query = query.filter(StLote.cod_agencia == cod_agencia)
    if cod_comprobante_lote:
        query = query.filter(StLote.cod_comprobante == cod_comprobante_lote)

    result = query.all()

    if not result:
        lote = StLote(
            empresa=empresa,
            tipo_comprobante='LT',
            cod_comprobante=cod_comprobante_lote,
            fecha=date.today(),
            descripcion='Pruebas desde Backend 2',
            tipo_lote='IN',
            cod_agencia=cod_agencia,
            usuario_aud='DTRELLES',
            fecha_aud=date.today()
        )
        db.session.add(lote)
        db.session.commit()

    query = """
                                   DECLARE
                                     v_cod_empresa           FLOAT := :1;
                                     v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                                     v_cod_agencia           FLOAT := :3;
                                     v_result                VARCHAR2(50);
                                   BEGIN
                                     v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                                 p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                 p_cod_agencia => v_cod_agencia);
                                   :4 := v_result;
                                   END;
                                   """
    cur = db1.cursor()
    result_var = cur.var(cx_Oracle.STRING)
    cur.execute(query, (empresa, 'TE', cod_agencia, result_var))
    cod_sta_comprobante = result_var.getvalue()
    cur.close()
    db1.commit()

    sta_comprobante = Sta_Comprobante(
        cod_comprobante=cod_sta_comprobante,
        tipo_comprobante='TE',
        empresa=empresa,
        cod_agencia=cod_agencia,
        fecha=date.today(),
        comprobante_manual='INGRESO DE COMBO',
        cod_tipo_persona_a='VEN',
        cod_persona_a='022001',
        cod_tipo_persona_b='VEN',
        cod_persona_b='022001',
        cod_bodega_ingreso=cod_agencia,
        cod_subbodega_ingreso=None,
        cod_bodega_egreso=cod_agencia,
        cod_subbodega_egreso=None,
        cod_liquidacion='F1-240613',
        useridc='DTP',
        es_grabado=0,
        es_anulado=0,
        tipo_transferencia=None,
        tipo_comprobante_pedido=None,
        cod_comprobante_pedido=None,
        cod_estado_producto_egreso=None,
        cod_estado_producto_ingreso=None,
        cod_estado_proceso=None,
        transportador=None,
        placa=None,
        tipo_comprobante_lote='LT',
        cod_comprobante_lote=cod_comprobante_lote,
        cod_comprobante_ingreso=None,
        tipo_comprobante_ingreso=None,
        tipo_identificacion_transporta=None,
        cod_motivo=None,
        ruta=None
    )
    db.session.add(sta_comprobante)

    sta_movimiento = Sta_Movimiento(
        cod_comprobante=cod_sta_comprobante,
        tipo_comprobante='TE',
        empresa=empresa,
        cod_secuencia_mov=1,
        cod_producto='R150-000806',
        cod_unidad='U',
        cantidad=0,
        es_serie=0,
        cod_estado_producto=None,
        ubicacion_bodega=None,
        cod_tipo_lote='LT',
        cod_comprobante_lote=cod_comprobante_lote,
        cod_estado_producto_ing=None,
        cantidad_pedida=None
    )
    db.session.add(sta_movimiento)
    db.session.commit()

    query = """
                                           DECLARE
                                             v_cod_empresa           FLOAT := :1;
                                             v_cod_tipo_comprobante  VARCHAR2(2) := :2;
                                             v_cod_comprobante       VARCHAR2(10) := :3;
                                             v_cod_empresa_g         FLOAT ;
                                             v_cod_tipo_comprobante_g VARCHAR2(2) ;
                                             v_cod_comprobante_g      VARCHAR2(10) ;
                                             v_cod_comprobante_orden  VARCHAR2(10) := :7;
                                             v_cod_tipo_comprobante_orden  VARCHAR2(2) := :8;
                                           BEGIN
                                             ksa_comprobante.graba_ni(p_cod_empresa => v_cod_empresa,
                                                                                         p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                                          p_cod_comprobante => v_cod_comprobante,
                                                                                          p_cod_empresa_g => v_cod_empresa_g,
                                                                                          p_cod_tipo_comprobante_g => v_cod_tipo_comprobante_g,
                                                                                          p_cod_comprobante_g => v_cod_comprobante_g,
                                                                                          p_cod_comprobante_orden => v_cod_comprobante_orden,
                                                                                          p_cod_tipo_comprobante_orden => v_cod_tipo_comprobante_orden);
                                           :4 := v_cod_empresa_g;
                                           :5 := v_cod_tipo_comprobante_g;
                                           :6 := v_cod_comprobante_g;
                                           END;
                                           """
    cur = db1.cursor()
    result_var0 = cur.var(cx_Oracle.NUMBER)
    result_var1 = cur.var(cx_Oracle.STRING)
    result_var2 = cur.var(cx_Oracle.STRING)
    cur.execute(query, (empresa, 'TE', cod_sta_comprobante, result_var0, result_var1, result_var2, None, None))
    cod_comprobante_ni = result_var2.getvalue()
    cur.close()

    db1.commit()
    db1.close()
    print(cod_comprobante_ni)

    return jsonify({'cod_formula': cod_comprobante_ni})