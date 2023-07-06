from flask import Blueprint, jsonify, request
from models.productos import Producto
from models.proveedores import Proveedor, TgModeloItem
from models.tipo_comprobante import TipoComprobante
from models.producto_despiece import StProductoDespiece
from models.despiece import StDespiece
from models.orden_compra import StOrdenCompraCab,StOrdenCompraDet,StTracking,StPackinglist
from models.embarque_bl import StEmbarquesBl
from config.database import db
from sqlalchemy import and_
import datetime
from datetime import datetime
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin

bpcustom = Blueprint('routes_custom', __name__)

logger = logging.getLogger(__name__)

#CONSULTAS GET CON PARAMETROS

@bpcustom.route('/productos_param') #sw para mostrar los productos por parametros
@jwt_required()
@cross_origin()
def obtener_productos_param():
    cod_producto = request.args.get('cod_producto', None)
    empresa = request.args.get('empresa', None)
    cod_barra = request.args.get('cod_barra', None)

    query = Producto.query()
    if cod_producto:
        query = query.filter(Producto.cod_producto == cod_producto)
    if empresa:
        query = query.filter(Producto.empresa == empresa)
    if cod_barra:
        query = query.filter(Producto.cod_barra == cod_barra)

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
            'ciudad': ciudad
        })
    
    return jsonify(serialized_cabeceras)
    
@bpcustom.route('/orden_compra_det_param')
@jwt_required()
@cross_origin()
def obtener_orden_comrpa_det_param():

    empresa = request.args.get('empresa', None)
    cod_po = request.args.get('cod_po', None)
    tipo_comprobante = request.args.get('tipo_comprobante', None)

    query = StOrdenCompraDet.query()
    if empresa :
        query = query.filter(StOrdenCompraDet.empresa == empresa)
    if cod_po:
        query = query.filter(StOrdenCompraDet.cod_po == cod_po)
    if tipo_comprobante:
        query = query.filter(StOrdenCompraDet.tipo_comprobante == tipo_comprobante)

    detalles = query.all()
    serialized_detalles = []
    for detalle in detalles:
        cod_po = detalle.cod_po if detalle.cod_po else ""
        tipo_comprobante = detalle.tipo_comprobante if detalle.tipo_comprobante else ""
        secuencia = detalle.secuencia if detalle.secuencia else ""
        empresa = detalle.empresa if detalle.empresa else ""
        cod_producto = detalle.cod_producto if detalle.cod_producto else ""
        cod_producto_modelo = detalle.cod_producto_modelo if detalle.cod_producto_modelo else ""
        nombre = detalle.nombre if detalle.nombre else ""
        nombre_i = detalle.nombre_i if detalle.nombre_i else ""
        nombre_c = detalle.nombre_c if detalle.nombre_c else ""
        nombre_mod_prov = detalle.nombre_mod_prov if detalle.nombre_mod_prov else ""
        nombre_comercial = detalle.nombre_comercial if detalle.nombre_comercial else ""
        costo_sistema = detalle.costo_sistema if detalle.costo_sistema else ""
        costo_cotizado = detalle.costo_cotizado if detalle.costo_cotizado else ""
        fecha_costo = detalle.fecha_costo if detalle.fecha_costo else ""
        fob = detalle.fob if detalle.fob else ""
        cantidad_pedido = detalle.cantidad_pedido if detalle.cantidad_pedido else ""
        if fob and cantidad_pedido:
            fob_total = fob * cantidad_pedido
        else:
            fob_total = None
        saldo_producto = detalle.saldo_producto if detalle.saldo_producto else ""
        unidad_medida = detalle.unidad_medida if detalle.unidad_medida else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = detalle.fecha_crea.strftime("%d/%m/%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = detalle.fecha_modifica.strftime("%d/%m/%Y") if detalle.fecha_modifica else ""
        serialized_detalles.append({
            'cod_po': cod_po,
            'tipo_comprobante': tipo_comprobante,
            'secuencia': secuencia,
            'empresa': empresa,
            'cod_producto': cod_producto,
            'cod_producto_modelo': cod_producto_modelo,
            'nombre': nombre,
            'nombre_ingles': nombre_i,
            'nombre_china': nombre_c,
            'nombre_mod_prov': nombre_mod_prov,
            'nombre_comercial': nombre_comercial,
            'costo_sistema': costo_sistema,
            'costo_cotizado': costo_cotizado,
            'fecha_costo': fecha_costo,
            'fob': fob,
            'fob_total': fob_total,
            'cantidad_pedido': cantidad_pedido,
            'saldo_producto': saldo_producto,
            'unidad_medida': unidad_medida,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
        })
    return jsonify(serialized_detalles)

@bpcustom.route('/orden_compra_track_param')
@jwt_required()
@cross_origin()
def obtener_orden_compra_track_param():

    empresa = request.args.get('empresa', None)
    cod_po = request.args.get('cod_po', None)
    tipo_comprobante = request.args.get('tipo_comprobante', None)
    secuencia = request.args.get('secuencia', None)

    query = StTracking.query()
    if empresa:
        query = query.filter(StTracking.empresa == empresa)
    if cod_po:
        query = query.filter(StTracking.cod_po == cod_po)
    if tipo_comprobante:
        query = query.filter(StTracking.tipo_comprobante == tipo_comprobante)
    if secuencia:
        query = query.filter(StTracking.secuencia == secuencia)

    seguimientos = query.all()
    serialized_seguimientos = []
    for seguimiento in seguimientos:
        cod_po = seguimiento.cod_po if seguimiento.cod_po else ""
        tipo_comprobante = seguimiento.tipo_comprobante if seguimiento.tipo_comprobante else ""
        empresa = seguimiento.empresa if seguimiento.empresa else ""
        secuencia = seguimiento.secuencia if seguimiento.secuencia else ""
        observaciones = seguimiento.observaciones if seguimiento.observaciones else ""
        cod_modelo = seguimiento.cod_modelo if seguimiento.cod_modelo else ""
        cod_item = seguimiento.cod_modelo if seguimiento.cod_modelo else ""
        fecha = datetime.strftime(seguimiento.fecha,"%d/%m/%Y") if seguimiento else ""
        usuario_crea = seguimiento.usuario_crea if seguimiento.usuario_crea else ""
        fecha_crea = datetime.strftime(seguimiento.fecha_crea,"%d/%m/%Y") if seguimiento.fecha_crea else ""
        usuario_modifica = seguimiento.usuario_modifica if seguimiento.usuario_modifica else ""
        fecha_modifica = datetime.strftime(seguimiento.fecha_modifica,"%d/%m/%Y") if seguimiento.fecha_modifica else ""
        serialized_seguimientos.append({
            'cod_po': cod_po,
            'tipo_comprobante': tipo_comprobante,
            'empresa': empresa,
            'secuencia': secuencia,
            'observaciones': observaciones,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'fecha': fecha,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
        })
    return jsonify(serialized_seguimientos)

@bpcustom.route('/packinglist_param')
@jwt_required()
@cross_origin()
def obtener_packinglist_param():
    empresa = request.args.get('empresa', None)
    codigo_bl_house = request.args.get('cod_bl_house', None)
    secuencia = request.args.get('secuencia', None)
    
    query = StPackinglist.query()
    if empresa:
        query = query.filter(StPackinglist.empresa == empresa)
    if codigo_bl_house:
        query = query.filter(StPackinglist.codigo_bl_house == codigo_bl_house)
    if secuencia:
        query = query.filter(StPackinglist.secuencia == secuencia)
    
    packings = query.all()
    serialized_packings = []

    for packing in packings:
        codigo_bl_house = packing.codigo_bl_house if packing.codigo_bl_house else ""
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
            'codigo_bl_house': codigo_bl_house,
            'cod_po': cod_po,
            'tipo_comprobante': tipo_comprobante,
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

#METODO CUSTOM PARA EMBARQUES DE ORDENES DE COMPRA

@bpcustom.route('/embarque_param')
@jwt_required()
@cross_origin()
def obtener_embarques_param():
    try:
        empresa = request.args.get('empresa', None)
        codigo_bl_house = request.args.get('cod_bl_house', None)
        
        query = StEmbarquesBl.query()
        if empresa:
            query = query.filter(StEmbarquesBl.empresa == empresa)
        if codigo_bl_house:
            query = query.filter(StEmbarquesBl.codigo_bl_house == codigo_bl_house)
        
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
            cod_aforo = embarque.cod_aforo if embarque.cod_aforo else ""
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
                'cod_aforo': cod_aforo
            })
        return jsonify(serialized_embarques)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
