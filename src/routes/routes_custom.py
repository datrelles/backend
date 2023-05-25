from flask import Blueprint, jsonify, request
from models.productos import Producto
from models.proveedores import Proveedor, TgModeloItem
from models.tipo_comprobante import TipoComprobante
from models.producto_despiece import StProductoDespiece
from models.despiece import StDespiece
from models.orden_compra import StOrdenCompraCab,StOrdenCompraDet,StOrdenCompraTracking,StPackinglist
from config.database import db
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

    query=StOrdenCompraCab.query()
    if empresa:
        query = query.filter(StOrdenCompraCab.empresa == empresa)
    if cod_po:
        query = query.filter(StOrdenCompraCab.cod_po == cod_po)

    cabeceras = query.all()
    serialized_cabeceras = []
    for cabecera in cabeceras:
        empresa = cabecera.empresa if cabecera.empresa else ""
        cod_po = cabecera.cod_po if cabecera.cod_po else ""
        tipo_comprobante = cabecera.tipo_comprobante if cabecera.tipo_comprobante else ""
        cod_proveedor = cabecera.cod_proveedor if cabecera.cod_proveedor else ""
        nombre = cabecera.nombre if cabecera.nombre else ""
        proforma = cabecera.proforma if cabecera.proforma else ""
        invoice = cabecera.invoice if cabecera.invoice else ""
        bl_no = cabecera.bl_no if cabecera.bl_no else ""
        cod_po_padre = cabecera.cod_po_padre if cabecera.cod_po_padre else ""
        usuario_crea = cabecera.usuario_crea if cabecera.usuario_crea else ""
        fecha_crea = cabecera.fecha_crea.strftime("%d/%m/%Y") if cabecera.fecha_crea else ""
        usuario_modifica = cabecera.usuario_modifica if cabecera.usuario_modifica else ""
        fecha_modifica = cabecera.fecha_modifica.strftime("%d/%m/%Y") if cabecera.fecha_modifica else ""
        cod_modelo = cabecera.cod_modelo if cabecera.cod_modelo else ""
        cod_item = cabecera.cod_item if cabecera.cod_item else ""
        ciudad = cabecera.ciudad if cabecera.ciudad else ""
        estado = cabecera.estado if cabecera.estado else ""
        serialized_cabeceras.append({
            'empresa': empresa,
            'cod_po': cod_po,
            'tipo_combrobante': tipo_comprobante,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'proforma': proforma,
            'invoice': invoice,
            'bl_no': bl_no,
            'cod_po_padre': cod_po_padre,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'ciudad': ciudad,
            'estado': estado
        })
    
    return jsonify(serialized_cabeceras)
    
@bpcustom.route('/orden_compra_det_param')
@jwt_required()
@cross_origin()
def obtener_orden_comrpa_det_param():

    empresa = request.args.get('empresa', None)
    cod_po = request.args.get('cod_po', None)

    query = StOrdenCompraDet.query()
    if empresa :
        query = query.filter(StOrdenCompraDet.empresa == empresa)
    if cod_po:
        query = query.filter(StOrdenCompraDet.cod_po == cod_po)

    detalles = query.all()
    serialized_detalles = []
    for detalle in detalles:
        cod_po = detalle.cod_po if detalle.cod_po else ""
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
        fob = detalle.fob if detalle.fob else ""
        cantidad_pedido = detalle.cantidad_pedido if detalle.cantidad_pedido else ""
        fob_total = fob * cantidad_pedido
        saldo_producto = detalle.saldo_producto if detalle.saldo_producto else ""
        unidad_medida = detalle.unidad_medida if detalle.unidad_medida else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = detalle.fecha_crea.strftime("%d/%m/%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = detalle.fecha_modifica.strftime("%d/%m/%Y") if detalle.fecha_modifica else ""
        serialized_detalles.append({
            'cod_po': cod_po,
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

    query = StOrdenCompraTracking.query()
    if empresa:
        query = query.filter(StOrdenCompraTracking.empresa == empresa)
    if cod_po:
        query = query.filter(StOrdenCompraTracking.cod_po == cod_po)

    seguimientos = query.all()
    serialized_seguimientos = []
    for seguimiento in seguimientos:
        cod_po = seguimiento.cod_po if seguimiento.cod_po else ""
        empresa = seguimiento.empresa if seguimiento.empresa else ""
        observaciones = seguimiento.observaciones if seguimiento.observaciones else ""
        fecha_pedido = datetime.strftime(seguimiento.fecha_pedido,"%d/%m/%Y") if seguimiento.fecha_pedido else ""
        fecha_transito = datetime.strftime(seguimiento.fecha_transito,"%d/%m/%Y") if seguimiento.fecha_transito else ""
        fecha_puerto = datetime.strftime(seguimiento.fecha_puerto,"%d/%m/%Y") if seguimiento.fecha_puerto else ""
        fecha_llegada = datetime.strftime(seguimiento.fecha_llegada,"%d/%m/%Y") if seguimiento.fecha_llegada else ""
        estado = seguimiento.estado if seguimiento.estado else ""
        buque = seguimiento.buque if seguimiento.buque else ""
        naviera = seguimiento.naviera if seguimiento.naviera else ""
        flete = seguimiento.flete if seguimiento.flete else ""
        agente_aduanero = seguimiento.agente_aduanero if seguimiento.agente_aduanero else ""
        puerto_origen = seguimiento.puerto_origen if seguimiento.puerto_origen else ""
        usuario_crea = seguimiento.usuario_crea if seguimiento.usuario_crea else ""
        fecha_crea = datetime.strftime(seguimiento.fecha_crea,"%d/%m/%Y") if seguimiento.fecha_crea else ""
        usuario_modifica = seguimiento.usuario_modifica if seguimiento.usuario_modifica else ""
        fecha_modifica = datetime.strftime(seguimiento.fecha_modifica,"%d/%m/%Y") if seguimiento.fecha_modifica else ""
        serialized_seguimientos.append({
            'cod_po': cod_po,
            'empresa': empresa,
            'observaciones': observaciones,
            'fecha_pedido': fecha_pedido,
            'fecha_transito': fecha_transito,
            'fecha_puerto': fecha_puerto,
            'fecha_llegada': fecha_llegada,
            'estado': estado,
            'buque': buque,
            'naviera': naviera,
            'flete': flete,
            'agente_aduanero': agente_aduanero,
            'puerto_origen': puerto_origen,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
        })
    return jsonify(serialized_seguimientos)

#METODO CUSTOM PARA ELIMINAR TODA LA ORDEN DE COMPRA

@bpcustom.route('/eliminar_orden_compra_total/<cod_po>/<empresa>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra(cod_po, empresa):
    try:
        orden_cab = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po, empresa=empresa).first()
        if not orden_cab:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        # Eliminar registros en StOrdenCompraDet
        db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa).delete()

        # Eliminar registros en StOrdenCompraTracking
        db.session.query(StOrdenCompraTracking).filter_by(cod_po=cod_po, empresa=empresa).delete()

        # Eliminar registros en StPackinglist
        db.session.query(StPackinglist).filter_by(cod_po=cod_po, empresa=empresa).delete()

        # Eliminar registro en StOrdenCompraCab
        db.session.delete(orden_cab)

        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra eliminada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500    