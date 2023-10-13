from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from src.models.users import Usuario, Empresa
from src.models.tipo_comprobante import TipoComprobante
from src.models.proveedores import Proveedor,TgModelo,TgModeloItem, ProveedorHor, TcCoaProveedor
from src.models.orden_compra import StOrdenCompraCab, StOrdenCompraDet, StTracking, StPackinglist
from src.models.productos import Producto
from src.models.despiece import StDespiece, StDespieceD
from src.models.producto_despiece import StProductoDespiece
from src.models.unidad_importacion import StUnidadImportacion
from src.models.embarque_bl import StEmbarquesBl,StTrackingBl, StPuertosEmbarque, StNaviera, StEmbarqueContenedores, StTipoContenedor
from src.models.tipo_aforo import StTipoAforo
from src.config.database import db,engine,session
from sqlalchemy import func, text,bindparam,Integer, event
from sqlalchemy.orm import scoped_session
import logging
import datetime
from datetime import datetime,date
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from decimal import Decimal
import json
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
bp = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)

#METODOS GET

@bp.route('/usuarios')
@jwt_required()
@cross_origin()
def obtener_usuarios():
    query = Usuario.query()
    usuarios = query.all()
    serialized_usuarios = []
    for usuario in usuarios:
        serialized_usuarios.append({
            'usuario_oracle': usuario.usuario_oracle,
            'apellido1': usuario.apellido1,
            'apellido2': usuario.apellido2,
            'nombre': usuario.nombre,
            'empresa_actual': usuario.empresa_actual,
            'useridc': usuario.useridc,
            'toda_bodega': usuario.toda_bodega,
            'toda_empresa': usuario.toda_empresa,
            'agencia_actual': usuario.agencia_actual,
            'aa': usuario.aa,
            'e_mail': usuario.e_mail,
            'password': usuario.password
        })
    return jsonify(serialized_usuarios)

@bp.route('/empresas')
@jwt_required()
@cross_origin()
def obtener_empresas():
    empresas = Empresa.query.all()
    #print(type(empresas))
    resultados = []
    for empresa in empresas:
        resultados.append(empresa.to_dict())
    #empresas_dict = [e.__dict__ for e in empresas]
    return jsonify(resultados)

@bp.route('/tipo_comprobante')
@jwt_required()
@cross_origin()
def obtener_tipo_comprobante():
    query = TipoComprobante.query()
    comprobantes = query.all()
    serialized_comprobantes = []
    for comprobante in comprobantes:
        serialized_comprobantes.append({
            'empresa': comprobante.empresa,
            'tipo': comprobante.tipo,
            'nombre': comprobante.nombre,
            'cod_sistema': comprobante.cod_sistema,
        })
    return jsonify(serialized_comprobantes)

@bp.route('/proveedores_ext')
@jwt_required()
@cross_origin()
def obtener_proveedores_ext():
    query = db.session.query(Proveedor).join(ProveedorHor, Proveedor.cod_proveedor == ProveedorHor.cod_proveedorh).filter(ProveedorHor.cod_tipo_proveedorh == 'EXT')
    proveedores = query.all()
    serialized_proveedores = []
    for proveedor in proveedores:
        empresa = proveedor.empresa if proveedor.empresa else ""
        cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
        nombre = proveedor.nombre if proveedor.nombre else ""
        direccion = proveedor.direccion if proveedor.direccion else ""
        telefono = proveedor.telefono if proveedor.telefono else ""
        # Consulta adicional para obtener la ciudad del proveedor
        ciudad_query = db.session.query(TcCoaProveedor.ciudad_matriz).filter(TcCoaProveedor.ruc == proveedor.cod_proveedor)
        ciudad = ciudad_query.scalar()
        #cod_proveedores = [cod_proveedor.to_dict() for cod_proveedor in proveedor.cod_proveedores]
        serialized_proveedores.append({
            'empresa': empresa,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'ciudad': ciudad,
            'direccion': direccion,
            'telefono': telefono
        })
    return jsonify(serialized_proveedores)

@bp.route('/proveedores_nac')
@jwt_required()
@cross_origin()
def obtener_proveedores_nac():
    query = db.session.query(Proveedor).join(ProveedorHor, Proveedor.cod_proveedor == ProveedorHor.cod_proveedorh).filter(ProveedorHor.cod_tipo_proveedorh == 'NAC')
    proveedores = query.all()
    serialized_proveedores = []
    for proveedor in proveedores:
        empresa = proveedor.empresa if proveedor.empresa else ""
        cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
        nombre = proveedor.nombre if proveedor.nombre else ""
        direccion = proveedor.direccion if proveedor.direccion else ""
        telefono = proveedor.telefono if proveedor.telefono else ""
        # Consulta adicional para obtener la ciudad del proveedor
        ciudad_query = db.session.query(TcCoaProveedor.ciudad_matriz).filter(TcCoaProveedor.ruc == proveedor.cod_proveedor)
        ciudad = ciudad_query.scalar()
        #cod_proveedores = [cod_proveedor.to_dict() for cod_proveedor in proveedor.cod_proveedores]
        serialized_proveedores.append({
            'empresa': empresa,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'ciudad': ciudad,
            'direccion': direccion,
            'telefono': telefono
        })
    return jsonify(serialized_proveedores)

@bp.route('/puertos_embarque')
@jwt_required()
@cross_origin()
def obtener_puertos_embarque():
    query = StPuertosEmbarque.query()
    puertos_embarque = query.all()
    serialized_puertos = []
    for puerto in puertos_embarque:
        empresa = puerto.empresa if puerto.empresa else ""
        cod_puerto = puerto.cod_puerto if puerto.cod_puerto else ""
        descripcion = puerto.descripcion if puerto.descripcion else ""
        serialized_puertos.append({
            'empresa': empresa,
            'cod_puerto': cod_puerto,
            'descripcion': descripcion
        })
    return jsonify(serialized_puertos)

@bp.route('/naviera')
@jwt_required()
@cross_origin()
def obtener_naviera():
    query = StNaviera.query()
    navieras = query.all()
    serialized_navieras = []
    for naviera in navieras:
        empresa = naviera.empresa if naviera.empresa else ""
        codigo = naviera.codigo if naviera.codigo else ""
        nombre = naviera.nombre if naviera.nombre else ""
        estado = naviera.estado
        usuario_crea = naviera.usuario_crea if naviera.usuario_crea else ""
        fecha_crea = datetime.strftime(naviera.fecha_crea, "%d%m%Y") if naviera.fecha_crea else ""
        usuario_modifica = naviera.usuario_modifica if naviera.usuario_modifica else ""
        fecha_modifica = datetime.strftime(naviera.fecha_modifica, "%d%m%Y") if naviera.fecha_modifica else ""
        serialized_navieras.append({
            "empresa": empresa,
            "codigo": codigo,
            "nombre": nombre,
            "estado": estado,
            "usuario_crea": usuario_crea,
            "fecha_crea": fecha_crea,
            "usuario_modifica": usuario_modifica,
            "fecha_modifica": fecha_modifica
        })
    return jsonify(serialized_navieras)        

@bp.route('/orden_compra_cab')
@jwt_required()
@cross_origin()
def obtener_orden_compra_cab():
    query = StOrdenCompraCab.query()
    ordenes_compra = query.all()
    serialized_ordenes_compra = []
    for orden in ordenes_compra:
        empresa = orden.empresa if orden.empresa else ""
        cod_po = orden.cod_po if orden.cod_po else ""
        tipo_comprobante = orden.tipo_comprobante if orden.tipo_comprobante else ""
        cod_agencia = orden.cod_agencia if orden.cod_agencia else ""
        cod_proveedor = orden.cod_proveedor if orden.cod_proveedor else ""
        nombre = orden.nombre if orden.nombre else ""
        proforma = orden.proforma if orden.proforma else ""
        usuario_crea = orden.usuario_crea if orden.usuario_crea else ""
        fecha_crea = datetime.strftime(orden.fecha_crea,"%d/%m/%Y") if orden.fecha_crea else ""
        usuario_modifica = orden.usuario_modifica if orden.usuario_modifica else ""
        fecha_modifica = datetime.strftime(orden.fecha_modifica,"%d/%m/%Y") if orden.fecha_modifica else ""
        cod_modelo = orden.cod_modelo if orden.cod_modelo else ""
        cod_item = orden.cod_item if orden.cod_item else ""
        bodega = orden.bodega if orden.bodega else ""
        ciudad = orden.ciudad if orden.ciudad else ""
        fecha_estimada_produccion = datetime.strftime(orden.fecha_estimada_produccion,"%d/%m/%Y") if orden.fecha_estimada_produccion else ""
        fecha_estimada_puerto = datetime.strftime(orden.fecha_estimada_puerto,"%d/%m/%Y") if orden.fecha_estimada_puerto else ""
        fecha_estimada_llegada = datetime.strftime(orden.fecha_estimada_llegada,"%d/%m/%Y") if orden.fecha_estimada_llegada else ""
        cod_opago = orden.cod_opago if orden.cod_opago else ""
        serialized_ordenes_compra.append({
            'empresa': empresa,
            'cod_po': cod_po,
            'tipo_combrobante': tipo_comprobante,
            'cod_agencia': cod_agencia,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'proforma': proforma,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'bodega': bodega,
            'ciudad': ciudad,
            'fecha_estimada_produccion': fecha_estimada_produccion,
            'fecha_estimada_puerto': fecha_estimada_puerto,
            'fecha_estimada_llegada': fecha_estimada_llegada,
            'cod_opago': cod_opago
        })

    return jsonify(serialized_ordenes_compra)

@bp.route('/orden_compra_det')
@jwt_required()
@cross_origin()
def obtener_orden_compra_det():
    query = StOrdenCompraDet.query()
    detalles = query.all()
    serialized_detalles = []
    for detalle in detalles:
        exportar = detalle.exportar if detalle.exportar else ""
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
        fob_total = detalle.fob_total if detalle.fob_total else ""
        saldo_producto = detalle.saldo_producto if detalle.saldo_producto else ""
        unidad_medida = detalle.unidad_medida if detalle.unidad_medida else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = datetime.strftime(detalle.fecha_crea,"%d/%m/%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = datetime.strftime(detalle.fecha_modifica,"%d/%m/%Y") if detalle.fecha_modifica else ""
        serialized_detalles.append({
            'exportar': exportar,
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
            'nombre_comercial':nombre_comercial,
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

@bp.route('/productos')
@jwt_required()
@cross_origin()
def obtener_productos():
    query = Producto.query()
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

@bp.route('/estados')
@jwt_required()
@cross_origin()
def obtener_estados():
    try:
        query = TgModeloItem.query()
        estados = query.all()
        #print(estados)
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
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_track')
@jwt_required()
@cross_origin()
def obtener_orden_compra_track():
    try:
        query = StTracking.query()
        seguimientos = query.all()
        serialized_seguimientos = []
        for seguimiento in seguimientos:
            cod_po = seguimiento.cod_po if seguimiento.cod_po else ""
            tipo_comprobante = seguimiento.tipo_comprobante if seguimiento.tipo_comprobante else ""
            empresa = seguimiento.empresa if seguimiento.empresa else ""
            secuencia = seguimiento.secuencia if seguimiento.secuencia else ""
            observaciones = seguimiento.observaciones if seguimiento.observaciones else ""
            fecha = datetime.strftime(seguimiento.fecha,"%d/%m/%Y") if seguimiento.fecha else ""
            cod_modelo = seguimiento.cod_modelo if seguimiento.cod_modelo else ""
            cod_item = seguimiento.cod_item if seguimiento.cod_item else ""
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
                'fecha': fecha,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modifica': fecha_modifica
            })
        return jsonify(serialized_seguimientos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/tracking_bl')
@jwt_required()
@cross_origin()
def obtener_tracking_bl():
    try:
        query = StTrackingBl.query()
        track_bls = query.all()
        serialized_bls = []
        for bl in track_bls:
            cod_bl_house = bl.cod_bl_house if bl.cod_bl_house else ""
            empresa = bl.empresa if bl.empresa else ""
            secuencial = bl.secuencial if bl.secuencial else ""
            observaciones = bl.observaciones if bl.observaciones else ""
            cod_modelo = bl.cod_modelo if bl.cod_modelo else ""
            usuario_crea = bl.usuario_crea if bl.usuario_crea else ""
            fecha_crea = datetime.strftime(bl.fecha_crea,"%d/%m/%Y") if bl.fecha_crea else ""
            usuario_modifica = bl.usuario_modifica if bl.usuario_modifica else ""
            fecha_modifica = datetime.strftime(bl.fecha_modifica,"%d/%m/%Y") if bl.fecha_modifica else ""
            fecha = datetime.strftime(bl.fecha,"%d/%m/%Y") if bl.fecha else ""
            cod_item = bl.cod_item if bl.cod_item else ""
            serialized_bls.append({
                'cod_bl_house': cod_bl_house,
                'empresa': empresa,
                'secuencial': secuencial,
                'observaciones': observaciones,
                'cod_modelo': cod_modelo,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modifica': fecha_modifica,
                'fecha': fecha,
                'cod_item': cod_item,
            })
        return jsonify(serialized_bls)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/packinglist')
@jwt_required()
@cross_origin()
def obtener_packinlist():
    try:
        query = StPackinglist.query()
        packings = query.all()
        serialized_packing = []
        for packing in packings:
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
            nro_contenedor = packing.nro_contenedor if packing.nro_contenedor else ""
            usuario_crea = packing.usuario_crea if packing.usuario_crea else ""
            fecha_crea = datetime.strftime(packing.fecha_crea,"%d/%m/%Y") if packing.fecha_crea else ""
            usuario_modifica = packing.usuario_modifica if packing.usuario_modifica else ""
            fecha_modifica = datetime.strftime(packing.fecha_modifica,"%d/%m/%Y") if packing.fecha_modifica else ""
            serialized_packing.append({
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
                'nro_contenedor': nro_contenedor,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modifica': fecha_modifica,
            })
        return jsonify(serialized_packing)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/nombre_productos')
@jwt_required()
@cross_origin()
def obtener_nombre_productos():
    try:
        query = StDespiece.query()
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

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/prod_despiece')
@jwt_required()
@cross_origin()
def obtener_producto_despiece():
    try:
        query = StProductoDespiece.query()
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
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/tgmodelo')
@jwt_required()
@cross_origin()
def obtener_tgmodelo():
    try:
        query = TgModelo.query()
        tgmodels = query.all()
        #print(estados)
        serialized_tgmodelo = []
        for tgmodelo in tgmodels:
            serialized_tgmodelo.append({
                'empresa': tgmodelo.empresa,
                'cod_modelo': tgmodelo.cod_modelo,
                'nombre': tgmodelo.nombre
            })
        return jsonify(serialized_tgmodelo)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/embarque')
@jwt_required()
@cross_origin()
def obtener_embarques():
    try:
        query = StEmbarquesBl.query()
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
            agente = embarque.agente if embarque.agente else ""
            buque = embarque.buque if embarque.buque else ""
            cod_puerto_embarque = embarque.cod_puerto_embarque if embarque.cod_puerto_embarque else ""
            cod_puerto_desembarque = embarque.cod_puerto_desembarque if embarque.cod_puerto_desembarque else ""
            costo_contenedor = embarque.costo_contenedor if embarque.costo_contenedor else 0
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
                'estado': estado,
                'agente': agente,
                'buque': buque,
                'cod_puerto_embarque': cod_puerto_embarque,
                'cod_puerto_desembarque': cod_puerto_desembarque,
                'costo_contenedor': float(costo_contenedor),
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
    
@bp.route('/tipo_aforo')
@jwt_required()
@cross_origin()
def obtener_tipo_aforo():
    try:
        query = StTipoAforo.query()
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
                'fecha_modifica': fecha_modifica
            })
        return jsonify(serialized_aforos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500

    
#METODOS POST

@bp.route('/orden_compra_cab', methods = ['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_cab():
    try:
        data = request.get_json()
        fecha_crea = date.today()#funcion para que se asigne la fecha actual al momento de crear la oden de compra
        fecha_modifica = datetime.strptime(data['fecha_modifica'], '%d/%m/%Y').date()
        fecha_estimada_produccion = datetime.strptime(data['fecha_estimada_produccion'], '%d/%m/%Y').date() if 'fecha_estimada_produccion' in data else None
        fecha_estimada_puerto = datetime.strftime(data['fecha_estimada_puerto'], '%d%m%Y').date() if 'fecha_estimada_puerto' in data else None
        fecha_estimada_llegada = datetime.strftime(data['fecha_estimada_llegada'], '%d%m%Y').date() if 'fecha_estimada_llegada' in data else None

        #busqueda para que se asigne de forma automatica la ciudad al buscarla por el cod_proveedor
        busq_ciudad = TcCoaProveedor.query().filter_by(ruc=data['cod_proveedor']).first()
        ciudad = busq_ciudad.ciudad_matriz

        #busqueda para obtener el nombre del estado para la orden de compra
        #estado = TgModeloItem.query().filter_by(cod_modelo=data['cod_modelo'], cod_item=data['cod_item']).first()
        #estado_nombre = estado.nombre if estado else ''
       
        # Generate the cod_po using the asigna_cod_comprobante function
        cod_po = asigna_cod_comprobante(data['empresa'], data['tipo_comprobante'], data['cod_agencia'])

        orden = StOrdenCompraCab(
            empresa=data['empresa'],
            cod_po=cod_po,
            bodega=data['bodega'],
            cod_agencia=data['cod_agencia'],
            tipo_comprobante=data['tipo_comprobante'],
            cod_proveedor=data['cod_proveedor'],
            nombre=data['nombre'],
            usuario_crea=data['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data['usuario_modifica'].upper(),
            fecha_modifica=fecha_modifica,
            cod_modelo='IMPR',
            cod_item=data['cod_item'],
            proforma = data.get('proforma'),
            cod_opago = data.get('cod_opago'),
            ciudad = ciudad if ciudad else "",
            fecha_estimada_produccion = fecha_estimada_produccion,
            fecha_estimada_puerto = fecha_estimada_puerto,
            fecha_estimada_llegada = fecha_estimada_llegada
        )
        db.session.add(orden)
        db.session.commit()
        return jsonify({'Cabecera de Orden de compra creada exitosamente': cod_po})

    except ValueError as ve:
        # Capturar y manejar el error específico de ValueError
        error_message = str(ve)
        return jsonify({'error': error_message}), 500

    except Exception as e:
        # Manejar otros errores y proporcionar un mensaje personalizado
        error_message = f"Se produjo un error: {str(e)}"
        return jsonify({'error': error_message}), 500
    
def asigna_cod_comprobante(p_cod_empresa, p_cod_tipo_comprobante, p_cod_agencia):
    # Realizar las operaciones de base de datos necesarias para generar el código comprobante
    # Ejecutar consultas SQL sin formato usando la función `texto` de SQLAlchemy

    # Encuentra el registro en la tabla 'orden'
    sql = text("SELECT * FROM contabilidad.orden WHERE empresa=:empresa AND bodega=:bodega AND tipo_comprobante=:tipo_comprobante")
    result = db.session.execute(sql, {'empresa': p_cod_empresa, 'bodega': p_cod_agencia, 'tipo_comprobante': p_cod_tipo_comprobante})
    print(result)
    orden = result.fetchone()
    print(orden)

    if orden is None:
        # Generar una excepción si no se encuentra el registro
        raise ValueError('Secuencia de comprobante no existe')

    # Actualizar la secuencia comprobante
    sql = text("UPDATE contabilidad.orden SET numero_comprobante=numero_comprobante+1 WHERE empresa=:empresa AND bodega=:bodega AND tipo_comprobante=:tipo_comprobante")
    db.session.execute(sql, {'empresa': p_cod_empresa, 'bodega': p_cod_agencia, 'tipo_comprobante': p_cod_tipo_comprobante})

    print(sql)
    # Acceder a los valores de las columnas por su índice en la tupla
    sigla_comprobante = orden[3]
    numero_comprobante = orden[4]

    # Convertir el número de comprobante a cadena de texto y generar el código comprobante
    comprobante_code = sigla_comprobante + str(numero_comprobante + 1).zfill(6)
    print(comprobante_code)

    return comprobante_code


@bp.route('/orden_compra_det', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_det():
    try:
        data = request.get_json()
        #print(data)
        fecha_crea = date.today()#funcion para que se asigne la fecha actual al momento de crear el detalle de la oden de compra
        #fecha_modifica = date.today()

        empresa = data['empresa']
        cod_po = data['cod_po']
        usuario_crea=data['usuario_crea'].upper()
        
        # Verificar si el usuario existe en la base de datos
        usuario = Usuario.query().filter_by(usuario_oracle=usuario_crea).first()
        if not usuario:
            return jsonify({'mensaje': 'El usuario no existe.'}), 404

        cod_po_no_existe = [] #Lista para almacenar los codigo de productos que no existen
        unidad_medida_no_existe = [] #Lista para almacenar las unidades mal ingresadas
        cod_modelo_no_existe = [] #Lista para almacenar los cod_producto_modelo que no existen
        print(data)
        for order in data['orders']:
            print(order['cod_producto_modelo'])
            cod_producto = order['cod_producto'].strip()
            cod_producto_modelo = order['cod_producto_modelo'].strip()
            unidad_medida = order['unidad_medida'].upper()

            #Verificar si el producto existe en la tabla de Productos
            query = Producto.query().filter_by(cod_producto = cod_producto).first()
            query_umedida = StUnidadImportacion.query().filter_by(cod_unidad = unidad_medida).first()
            query_modelo = Producto.query().filter_by(cod_producto = cod_producto_modelo).first()
            if query and query_umedida and query_modelo:
                secuencia = obtener_secuencia(cod_po)
                costo_sistema = query.costo

                # Consultar la tabla StDespiece para obtener los valores correspondientes
                despiece = StProductoDespiece.query().filter_by(cod_producto=order['cod_producto'], empresa = empresa).first() #usar la empresa
                if despiece is not None:
                    nombre_busq = StDespieceD.query().filter_by(cod_despiece =despiece.cod_despiece, secuencia = despiece.secuencia).first()
                    nombre = nombre_busq.nombre_e
                    nombre_i = nombre_busq.nombre_i
                    nombre_c = nombre_busq.nombre_c
                else:
                    nombre_busq = Producto.query().filter_by(cod_producto = order['cod_producto']).first()
                    nombre = nombre_busq.nombre
                    nombre_i = nombre_busq.nombre
                    nombre_c = nombre_busq.nombre

                detalle = StOrdenCompraDet(
                    exportar=order['agrupado'],
                    cod_po=cod_po,
                    tipo_comprobante ='PO',
                    secuencia=secuencia,
                    empresa=empresa,
                    cod_producto=cod_producto,
                    cod_producto_modelo=cod_producto_modelo,
                    nombre=nombre if nombre else None,
                    nombre_i=nombre_i if nombre_i else order['nombre_ingles'],
                    nombre_c=nombre_c if nombre_c else None,
                    nombre_mod_prov = order['nombre_proveedor'],
                    nombre_comercial = order['nombre_comercial'],
                    costo_sistema=costo_sistema if costo_sistema else 0,
                    #fob=order['FOB'] if order['FOB'] else "",
                    cantidad_pedido=order['pedido'],
                    saldo_producto=order['pedido'],
                    unidad_medida=unidad_medida,
                    usuario_crea=usuario_crea,
                    fecha_crea=fecha_crea,
                    #usuario_modifica=order['usuario_modifica'].upper(),
                    #fecha_modifica=fecha_modifica,
                )
                #detalle.fob_total = order['FOB'] * order['CANTIDAD_PEDIDO']
                db.session.add(detalle)
                try:
                    # Intenta hacer la confirmación de la sesión
                    db.session.commit()
                except Exception as commit_error:
                    # Captura la excepción si ocurre un error al confirmar
                    db.session.rollback()  # Realiza un rollback para deshacer cambios pendientes
                    print(f"Error al confirmar: {str(commit_error)}")
                #secuencia = obtener_secuencia(order['COD_PO'])
            else:
                if query is None:
                    cod_po_no_existe.append(cod_producto +'\n')
                if query_modelo is None:
                    cod_modelo_no_existe.append(cod_producto_modelo+'\n')
                else:
                    unidad_medida_no_existe.append(unidad_medida+'\n')
        return jsonify({'mensaje': 'Orden de compra creada exitosamente', 'cod_po': cod_po,
                        'cod_producto_no_existe': list(set(cod_po_no_existe)),
                        'unidad_medida_no_existe': list(set(unidad_medida_no_existe)),
                        'cod_producto_modelo_no_existe': list(set(cod_modelo_no_existe))})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
def obtener_secuencia(cod_po):
    # Verificar si el cod_po existe en la tabla StOrdenCompraCab
    existe_cod_po_cab = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po).first()

    if existe_cod_po_cab is not None:
        print('EXISTE',existe_cod_po_cab.cod_po)
        # Si el cod_po existe en la tabla StOrdenCompraCab, verificar si existe en la tabla StOrdenCompraDet
        existe_cod_po_det = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po).first()

        if existe_cod_po_det is not None:
            print('EXISTE2',existe_cod_po_det.cod_po)
            # Si el cod_po existe en la tabla StOrdenCompraDet, obtener el último número de secuencia
            max_secuencia = db.session.query(func.max(StOrdenCompraDet.secuencia)).filter_by(cod_po=cod_po).distinct().scalar()
            print('MAXIMO',max_secuencia)
            nueva_secuencia = int(max_secuencia) + 1
            print('PROXIMO',nueva_secuencia)
            return nueva_secuencia
        else:
            # Si el cod_po no existe en la tabla StOrdenCompraDet, generar secuencia desde 1
            nueva_secuencia = 1
            print('Secuencia de inicio', nueva_secuencia)
            return nueva_secuencia
    else:
        # Si el cod_po no existe en la tabla StOrdenCompraCab, mostrar mensaje de error
        raise ValueError('La Orden de Compra no existe.')
    
#Funcion para obtener el cod_producto_modelo segun el cod_producto
def obtener_cod_producto_modelo(empresa, cod_producto):
    try:
        query = text("""
            select substr(substr(ks_reporte.tipo_modelo_cat(a.empresa, a.cod_producto),INSTR(ks_reporte.tipo_modelo_cat(a.empresa, a.cod_producto),CHR(9))+1),1,instr(substr(ks_reporte.tipo_modelo_cat(a.empresa, a.cod_producto),INSTR(ks_reporte.tipo_modelo_cat(a.empresa, a.cod_producto),CHR(9))+1),CHR(9))-1) modelo
            from producto a
            where empresa = :empresa and a.cod_producto = :cod_producto
        """)
        result = db.session.execute(query, {"empresa": empresa, "cod_producto": cod_producto})
        row = result.fetchone()
        print(row)
        if row:
            return row[0]
        return None

    except Exception as e:
        # Manejar errores
        print('Error:', e)
        raise

@bp.route('/packinglist_contenedor', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_packinglist_contenedor():
    try:
        data = request.get_json()
        fecha_crea = date.today()
        empresa = data['empresa']
        nro_contenedor = data['nro_contenedor']
        query_contenedor = StEmbarqueContenedores.query().filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()
        tipo_comprobante = data['tipo_comprobante']
        usuario_crea = data['usuario_crea'].upper()
        cod_prod_no_existe = []
        unidad_medida_no_existe = []
        prod_no_existe = []
        bl_no_existe = []
        for packing in data['packings']:
            print(packing['unidad_medida'])
            unidad_medida = packing['unidad_medida']
            cod_producto = packing['cod_producto']
            secuencia = obtener_secuencia_packing(nro_contenedor, empresa)
            # Verificar si el producto existe en la tabla de StOrdenCompraDet
            query_prod = Producto.query().filter_by(cod_producto=cod_producto, empresa=empresa).first()
            if query_prod:
                costo_sistema = query_prod.costo
                query = StOrdenCompraDet.query().filter_by(cod_producto=cod_producto, cod_po=packing['cod_po'], empresa=empresa).first()
                print(query)
                query_umedida = StUnidadImportacion.query().filter_by(cod_unidad=unidad_medida, empresa=empresa).first()
                query_conte = StEmbarqueContenedores.query().filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()
                if query_conte:
                    if query and query_umedida:
                        packinlist = StPackinglist(
                            nro_contenedor=nro_contenedor,
                            empresa=empresa,
                            cod_po=packing['cod_po'],
                            secuencia=secuencia,
                            tipo_comprobante=tipo_comprobante,
                            cod_producto=cod_producto,
                            cantidad=packing['cantidad'],
                            fob=packing['fob'],
                            unidad_medida=unidad_medida,
                            usuario_crea=usuario_crea,
                            fecha_crea=fecha_crea,
                            # usuario_modifica = packing['usuario_modifica'].upper(),
                            # fecha_modifica = fecha_modifica
                        )
                        query.saldo_producto = query.saldo_producto - packing['cantidad']
                        if query.fob is None or query.fob >= packing['fob']:
                            query.fob = packing['fob']
                        if query.fob_total is None:
                            query.fob_total = Decimal(0)
                        query.fob_total = query.fob_total + Decimal(packing['fob']) * Decimal(packing['cantidad'])
                        db.session.add(packinlist)
                        db.session.commit()
                    else:
                        if query is None:

                            despiece = StProductoDespiece.query().filter_by(cod_producto=cod_producto,
                                                                            empresa=empresa).first()  # usar la empresa
                            if despiece:
                                packinlist = StPackinglist(
                                    nro_contenedor=nro_contenedor,
                                    empresa=empresa,
                                    cod_po=packing['cod_po'],
                                    secuencia=secuencia,
                                    tipo_comprobante=tipo_comprobante,
                                    cod_producto=cod_producto,
                                    cantidad=packing['cantidad'],
                                    fob=packing['fob'],
                                    unidad_medida=unidad_medida,
                                    usuario_crea=usuario_crea,
                                    fecha_crea=fecha_crea,
                                    # usuario_modifica = packing['usuario_modifica'].upper(),
                                    # fecha_modifica = fecha_modifica
                                )

                                if despiece is not None:
                                    nombre_busq = StDespiece.query().filter_by(cod_despiece=despiece.cod_despiece).first()
                                    nombre = nombre_busq.nombre_e
                                    nombre_i = nombre_busq.nombre_i
                                    nombre_c = nombre_busq.nombre_c
                                else:
                                    nombre_busq = Producto.query().filter_by(cod_producto=cod_producto).first()
                                    nombre = nombre_busq.nombre
                                    nombre_i = nombre_busq.nombre
                                    nombre_c = nombre_busq.nombre
                                # Crear un nuevo registro en StOrdenCompraDet con cantidad en negativo
                                detalle = StOrdenCompraDet(
                                    exportar=False,
                                    cod_po=packing['cod_po'],
                                    tipo_comprobante='PO',
                                    secuencia=obtener_secuencia(packing['cod_po']),
                                    empresa=empresa,
                                    cod_producto=cod_producto,
                                    nombre=nombre if nombre else None,
                                    nombre_i=nombre_i if nombre_i else None,
                                    nombre_c=nombre_c if nombre_c else None,
                                    costo_sistema=costo_sistema if costo_sistema else 0,
                                    cantidad_pedido=0,  # Cantidad en negativo
                                    saldo_producto=-packing['cantidad'],
                                    unidad_medida=unidad_medida,
                                    usuario_crea=usuario_crea,
                                    fecha_crea=fecha_crea,
                                    fob=packing['fob'],
                                    fob_total=packing['fob'] * packing['cantidad']
                                )
                                db.session.add(packinlist)
                                db.session.add(detalle)
                                db.session.commit()
                                cod_prod_no_existe.append(cod_producto)
                            else:
                                prod_no_existe.append(cod_producto)
                        else:
                            unidad_medida_no_existe.append(unidad_medida)

                else:
                    bl_no_existe.append(nro_contenedor)
            else:
                prod_no_existe.append(cod_producto)
        return jsonify({'mensaje': 'Packinglist cargado exitosamente.',
                        'unidad_medida_no_existe': unidad_medida_no_existe,
                        'cod_producto_no_existe': cod_prod_no_existe,
                        'prod_no_existe': prod_no_existe,
                        'bl_no_existe': bl_no_existe})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        # logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
def obtener_secuencia_packing(nro_contenedor, empresa):
    # Verificar si el codigo_bl_house existe en la tabla StEmbarquesBl
    existe_contenedor = db.session.query(StEmbarqueContenedores).filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()

    if existe_contenedor is not None:
        print('EXISTE', existe_contenedor.nro_contenedor)
        # Si el codigo_bl_house existe en la tabla StEmbarquesBl, verificar si existe en la tabla StPackinglist
        existe_nro_cont_pack = db.session.query(StPackinglist).filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()

        if existe_nro_cont_pack is not None:
            print('EXISTE2', existe_nro_cont_pack.nro_contenedor)
            # Si el codigo_bl_house existe en la tabla StPackinglist, obtener el último número de secuencia
            max_secuencia = db.session.query(func.max(StPackinglist.secuencia)).filter_by(nro_contenedor=nro_contenedor, empresa=empresa).distinct().scalar()
            print('MAXIMO', max_secuencia)
            nueva_secuencia = int(max_secuencia) + 1
            print('PROXIMO', nueva_secuencia)
            return nueva_secuencia
        else:
            # Si el codigo_bl_house no existe en la tabla StPackinglist, generar secuencia desde 1
            nueva_secuencia = 1
            print('Secuencia de inicio', nueva_secuencia)
            return nueva_secuencia
    else:
        # Si el codigo_bl_house no existe en la tabla StEmbarquesBl, mostrar mensaje de error
        raise ValueError('El nro_contenedor no existe.')
    
@bp.route('/orden_compra_track', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_track():
    try:
        data = request.get_json()
        fecha = datetime.strptime(data['fecha'], '%d/%m/%Y').date()         #datetime.datetime.strptime(data['fecha_pedido'], '%d%m%Y') if data['fecha_pedido'] else None
        fecha_crea = date.today() #funcion para que se asigne la fecha actual al momento de crear el detalle de la oden de compra
        fecha_modifica = datetime.strptime(data['fecha_modifica'], '%d/%m/%Y').date()
        tracking = StTracking(
            cod_po = data['cod_po'],
            empresa = data['empresa'],
            tipo_comprobante = data['tipo_comprobante'],
            observaciones = data['observaciones'],
            fecha = fecha,
            cod_modelo = data['cod_modelo'],
            cod_item = data['cod_item'],
            usuario_crea = data['usuario_crea'].upper(),
            fecha_crea = fecha_crea,
            usuario_modifica = data['usuario_modifica'].upper(),
            fecha_modifica = fecha_modifica
        )
        db.session.add(tracking)
        db.session.commit()
        return jsonify({'mensaje': 'Tracking de orden de compra creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/embarque', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_embarque():
    try:
        data = request.get_json()
        fecha_adicion = date.today()

        fecha_embarque = parse_date(data.get('fecha_embarque'))
        fecha_llegada = parse_date(data.get('fecha_llegada'))
        fecha_bodega = parse_date(data.get('fecha_bodega'))

        embarque = StEmbarquesBl(
            empresa=data['empresa'],
            codigo_bl_master=data['codigo_bl_master'],
            codigo_bl_house=data['codigo_bl_house'],
            cod_proveedor=data['cod_proveedor'],
            fecha_embarque=fecha_embarque,
            fecha_llegada=fecha_llegada,
            fecha_bodega=fecha_bodega,
            numero_tracking=data.get('numero_tracking'),
            naviera=data.get('naviera'),
            estado=data['estado'],
            agente=data.get('agente'),
            buque=data.get('buque'),
            cod_puerto_embarque=data.get('cod_puerto_embarque'),
            cod_puerto_desembarque=data.get('cod_puerto_desembarque'),
            costo_contenedor=data.get('costo_contenedor'),
            descripcion=data.get('descripcion'),
            tipo_flete=data.get('tipo_flete'),
            adicionado_por=data['adicionado_por'].upper(),
            fecha_adicion=fecha_adicion,
            cod_modelo='BL',
            cod_item=data['cod_item'],
            cod_aforo=data.get('cod_aforo'),
            cod_regimen = data.get('cod_regimen'),
            nro_mrn = data.get('nro_mrn')
        )

        db.session.add(embarque)
        db.session.commit()

        return jsonify({'mensaje': "Embarque o BL creado exitosamente"})

    except ValueError as ve:
        error_message = str(ve)
        return jsonify({'error': error_message}), 500

    except Exception as e:
        error_message = f"Se produjo un error: {str(e)}"
        return jsonify({'error': error_message}), 500

def parse_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%d/%m/%Y').date()
    return None
    
def secuencia_trackingbl(cod_bl_house):
    # Verificar si el embarque existe en la tabla StEmbarquesBl
    #existe_embarque = db.session.query(StEmbarquesBl).filter_by(codigo_bl_house=cod_bl_house).first()

    #if existe_embarque is not None:
        #print('EXISTE',existe_embarque.cod_bl_house)
        # Si el cod_po existe en la tabla StTrackingBl, verificar si existe en la tabla StTrackingBl
    existe_cod_bl_house = db.session.query(StTrackingBl).filter_by(cod_bl_house=cod_bl_house).first()

    if existe_cod_bl_house is not None:
        print('EXISTE2',existe_cod_bl_house.cod_bl_house)
        # Si el cod_po existe en la tabla StTrackingBl, obtener el último número de secuencia
        max_secuencia = db.session.query(func.max(StTrackingBl.secuencial)).filter_by(cod_bl_house=cod_bl_house).distinct().scalar()
        print('MAXIMO',max_secuencia)
        nueva_secuencia = int(max_secuencia) + 1
        print('PROXIMO',nueva_secuencia)
        return nueva_secuencia
    else:
        # Si el cod_bl_house no existe en la tabla StTrackingBl, generar secuencia desde 1
        nueva_secuencia = 1
        print('Secuencia de inicio', nueva_secuencia)
        return nueva_secuencia
    #else:
    # Si el embarque no existe en la tabla StEmbarquesBl, mostrar mensaje de error
    #    raise ValueError('El embarque no existe.')

# Crear un diccionario para llevar un registro de la última combinación (codigo_bl_house, empresa, cod_item)
ultimas_combinaciones_track_embarque = {}

# Función para crear o actualizar el registro en StTrackingBl
def crear_o_actualizar_registro_tracking_embarque(session):
    for target in session.new.union(session.dirty):
        if isinstance(target, StEmbarquesBl) and target.cod_item:
            # Verificar si el objeto tiene los atributos esperados
            if hasattr(target, 'codigo_bl_house') and hasattr(target, 'empresa') and hasattr(target, 'adicionado_por') and hasattr(target, 'cod_modelo'):
                codigo_bl_house = target.codigo_bl_house
                empresa = target.empresa
                cod_item = target.cod_item

                # Obtener la última combinación (codigo_bl_house, empresa, cod_item)
                ultima_combinacion = ultimas_combinaciones_track_embarque.get((codigo_bl_house, empresa), None)

                # Verificar si es una nueva combinación o si el cod_item cambió
                if not ultima_combinacion or cod_item != ultima_combinacion['cod_item']:
                    nueva_secuencia = secuencia_trackingbl(codigo_bl_house)
                    new_record = StTrackingBl(
                        cod_bl_house=codigo_bl_house,
                        empresa=empresa,
                        secuencial=nueva_secuencia,
                        cod_modelo=target.cod_modelo,
                        usuario_crea=target.adicionado_por,
                        fecha_crea=datetime.now(),
                        fecha=datetime.now(),
                        cod_item=cod_item
                    )
                    session.add(new_record)

                    # Actualizar la última combinación registrada
                    ultimas_combinaciones_track_embarque[(codigo_bl_house, empresa)] = {'cod_item': cod_item}

# Registrar el evento before_commit en la sesión de SQLAlchemy para crear o actualizar registros en StTrackingBl
event.listen(scoped_session, 'before_commit', crear_o_actualizar_registro_tracking_embarque)

@bp.route('/tipo_aforo' , methods = ['POST'])
@jwt_required()
@cross_origin()
def crear_tipo_aforo():
    try:
        data = request.get_json()
        fecha_crea = date.today()
        tipo_aforo = StTipoAforo(
            cod_aforo = data['cod_aforo'],
            empresa = data['empresa'],
            nombre = data['nombre'].upper(),
            valor = data['valor'],
            observacion = data['observacion'],
            usuario_crea = data['usuario_crea'].upper(),
            fecha_crea = fecha_crea,
        )
        db.session.add(tipo_aforo)
        db.session.commit()
        return jsonify({'mensaje': 'Tipo de Aforo creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500

# METODOS UPDATE DE TABLAS DE ORDEN DE COMPRA

@bp.route('/orden_compra_cab/<cod_po>/<empresa>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_cab(cod_po, empresa, tipo_comprobante):
    try:
        orden = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante=tipo_comprobante).first()
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        data = request.get_json()
        #busqueda para que se asigne de forma automatica la ciudad al buscarla por el cod_proveedor
        cod_proveedor = data.get('cod_proveedor')
        if cod_proveedor:
            busq_ciudad = TcCoaProveedor.query().filter_by(ruc=cod_proveedor).first()
            ciudad = busq_ciudad.ciudad_matriz
        else:
            ciudad = ""

        if 'fecha_estimada_produccion' in data and data['fecha_estimada_produccion']:
            orden.fecha_estimada_produccion = datetime.strptime(data['fecha_estimada_produccion'], '%d/%m/%Y').date()

        if 'fecha_estimada_puerto' in data and data['fecha_estimada_puerto']:
            orden.fecha_estimada_puerto = datetime.strptime(data['fecha_estimada_puerto'], '%d/%m/%Y').date()

        if 'fecha_estimada_llegada' in data and data['fecha_estimada_llegada']:
            orden.fecha_estimada_llegada = datetime.strptime(data['fecha_estimada_llegada'], '%d/%m/%Y').date()

        orden.cod_proveedor = data.get('cod_proveedor', orden.cod_proveedor)
        orden.nombre = data.get('nombre', orden.nombre)
        orden.proforma = data.get('proforma', orden.proforma)
        orden.usuario_crea = data.get('usuario_crea', orden.usuario_crea).upper()
        orden.usuario_modifica = data.get('usuario_modifica', orden.usuario_modifica).upper()
        orden.fecha_modifica = date.today()
        orden.cod_modelo = data.get('cod_modelo', orden.cod_modelo)
        orden.cod_item = data.get('cod_item', orden.cod_item)
        orden.bodega = data.get('bodega', orden.bodega)
        orden.ciudad = ciudad
        orden.cod_opago = data.get('cod_opago', orden.cod_opago)

        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra actualizada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al actualizar la orden de compra: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_det/<cod_po>/<empresa>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_det(cod_po, empresa, tipo_comprobante):
    try:
        print(cod_po, empresa, tipo_comprobante)
        orden = db.session.query(StOrdenCompraDet).filter(StOrdenCompraDet.cod_po == cod_po, StOrdenCompraDet.empresa == empresa, StOrdenCompraDet.tipo_comprobante == tipo_comprobante).all()
        print(orden)
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        data = request.get_json()
        cod_producto_no_existe = []
        usuario_modifica = data['usuario_modifica'].upper()
        fecha_modifica = date.today()

        for order in data['orders']:
            query = StOrdenCompraDet.query().filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante=tipo_comprobante, cod_producto=order['cod_producto']).first()
            if query:
                query.cod_producto = order.get('cod_producto', query.cod_producto).strip()
                query.cod_producto_modelo = order.get('cod_producto_modelo', query.cod_producto_modelo).strip()
                query.nombre_mod_prov = order.get('nombre_mod_prov', query.nombre_mod_prov)
                query.nombre_comercial = order.get('nombre_comercial', query.nombre_comercial)
                query.costo_sistema = order.get('costo_sistema', query.costo_sistema)
                query.fob = order.get('fob', query.fob)
                query.fob_total = order.get('fob_total', query.fob_total)
                query.cantidad_pedido = order.get('cantidad_pedido', query.cantidad_pedido)
                query.exportar = order.get('exportar', query.exportar)
                query.unidad_medida = order.get('unidad_medida', query.unidad_medida).upper()
                query.saldo_producto = order.get('saldo_producto', query.saldo_producto)
                query.usuario_modifica = usuario_modifica
                query.fecha_modifica = fecha_modifica

                # Calcula el valor de fob_total
                query.fob_total = (query.fob or 0) * (query.cantidad_pedido or 0)

                if 'costo_cotizado' in order:
                    query.costo_cotizado = order['costo_cotizado']
                    if query.costo_cotizado is not None:
                        query.fecha_costo = date.today()
                
            else:
                cod_producto_no_existe.append(order['cod_producto'])
        
        if cod_producto_no_existe:
            return jsonify({'mensaje': 'Productos no Actualizados.', 'cod_producto_no_existe': cod_producto_no_existe})
        else:
            db.session.commit()
            return jsonify({'mensaje': 'Detalle(s) de orden de compra actualizados exitosamente', 'cod_po': cod_po})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        return jsonify({'error': str(e)}), 500

    
@bp.route('/orden_compra_tracking/<cod_po>/<empresa>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_trancking(cod_po,empresa,tipo_comprobante):
    try:
        tracking = db.session.query(StTracking).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).first()
        if not tracking:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        fecha_modifica = date.today()
        
        data = request.get_json()
        #tracking.cod_po = data.get('cod_po', tracking.cod_po)
        #tracking.tipo_comprobante = data.get('tipo_comprobante', tracking.tipo_comprobante)
        #tracking.empresa = data.get('empresa', tracking.empresa)
        tracking.observaciones = data.get('observaciones', tracking.observaciones)
        tracking.fecha = datetime.strptime(data.get('fecha', str(tracking.fecha)), '%d/%m/%Y').date()
        tracking.cod_modelo = data.get('cod_modelo', tracking.cod_modelo)
        tracking.cod_item = data.get('cod_item', tracking.cod_item)
        tracking.fecha_crea = datetime.strptime(data.get('fecha_crea', str(tracking.fecha_crea)), '%d/%m/%Y').date()
        tracking.usuario_modifica = data.get('usuario_modifica', tracking.usuario_modifica).upper()
        tracking.fecha_modifica = fecha_modifica

        db.session.commit()

        return jsonify({'mensaje': 'Tracking de Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_packinglist/<cod_po>/<empresa>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_packinglist(cod_po, empresa):
    try:
        packinglist = db.session.query(StPackinglist).filter_by(cod_po=cod_po, empresa=empresa).first()
        if not packinglist:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        data = request.get_json()
        fecha_modifica = date.today()
        cod_producto_no_existe = []
        usuario_modifica = data['usuario_modifica'].upper()
        for order in data['orders']:
            nro_contenedor = order['nro_contenedor']
            query = StPackinglist.query().filter_by(cod_po=cod_po, empresa=empresa, nro_contenedor=nro_contenedor, cod_producto=order['cod_producto']).first()
            if query:
                query.nro_contenedor = nro_contenedor
                query.tipo_comprobante = order.get('tipo_comprobante', query.tipo_comprobante)
                query.cod_producto = order.get('cod_producto', query.cod_producto)
                query.cantidad = order.get('cantidad', query.cantidad)
                query.fob = order.get('fob', query.fob)
                query.unidad_medida = order.get('unidad_medida', query.unidad_medida).upper()
                query.cod_liquidacion = order.get('cod_liquidacion', query.cod_liquidacion)
                query.cod_tipo_liquidacion = order.get('cod_tipo_liquidacion', query.cod_tipo_liquidacion)
                query.usuario_modifica = usuario_modifica
                query.fecha_modifica = fecha_modifica
                
                # Actualizar campo saldo_pedido en StOrdenCompraDet
                orden_det = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa, cod_producto=order['cod_producto']).first()
                if orden_det:
                    saldo_producto = orden_det.cantidad_pedido - query.cantidad
                    orden_det.saldo_producto = saldo_producto
                    orden_det.fecha_modifica = fecha_modifica
                    orden_det.usuario_modifica = usuario_modifica
                else:
                    cod_producto_no_existe.append(order['cod_producto'])
            else:
                cod_producto_no_existe.append(order['cod_producto'])
        
        db.session.commit()

        if cod_producto_no_existe:
            return jsonify({'mensaje': 'Productos no Actualizados. No existe el producto o codigo_bl_house erroneo.', 'cod_producto_no_existe': cod_producto_no_existe})
        else:
            return jsonify({'mensaje': 'Packinglist de Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/embarque/<codigo_bl_house>/<empresa>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_embarque(codigo_bl_house, empresa):
    try:
        embarque = db.session.query(StEmbarquesBl).filter_by(codigo_bl_house=codigo_bl_house, empresa=empresa).first()
        if not embarque:
            return jsonify({'mensaje': 'El embarque no existe.'}), 404

        data = request.get_json()

        if 'fecha_embarque' in data and data['fecha_embarque']:
            embarque.fecha_embarque = datetime.strptime(data['fecha_embarque'], '%d/%m/%Y').date()
        
        if 'fecha_llegada' in data and data['fecha_llegada']:
            embarque.fecha_llegada = datetime.strptime(data['fecha_llegada'], '%d/%m/%Y').date()

        if 'fecha_bodega' in data and data['fecha_bodega']:
            embarque.fecha_bodega = datetime.strptime(data['fecha_bodega'], '%d/%m/%Y').date()

        # Verificar si el campo 'cod_item' está presente en el JSON antes de asignarlo
        if 'cod_item' in data:
            embarque.cod_item = data['cod_item']

        # Verificar si el campo 'estado' está presente en el JSON antes de asignarlo
        if 'estado' in data:
            embarque.estado = data['estado']

        embarque.cod_proveedor = data.get('cod_proveedor', embarque.cod_proveedor)
        embarque.numero_tracking = data.get('numero_tracking', embarque.numero_tracking)
        embarque.naviera = data.get('naviera', embarque.naviera)
        embarque.agente = data.get('agente', embarque.agente)
        embarque.fecha_modificacion = date.today()
        embarque.buque = data.get('buque', embarque.buque)
        embarque.cod_puerto_embarque = data.get('cod_puerto_embarque', embarque.cod_puerto_embarque)
        embarque.cod_puerto_desembarque = data.get('cod_puerto_desembarque', embarque.cod_puerto_desembarque)
        costo_contenedor = data.get('costo_contenedor', embarque.costo_contenedor)
        if costo_contenedor == "":
            embarque.costo_contenedor = None
        else:
            embarque.costo_contenedor = float(costo_contenedor)
        embarque.descripcion = data.get('descripcion', embarque.descripcion)
        embarque.tipo_flete = data.get('tipo_flete', embarque.tipo_flete)
        embarque.modificado_por = data.get('modificado_por', embarque.modificado_por)
        embarque.cod_modelo = data.get('cod_modelo', embarque.cod_modelo)
        embarque.cod_aforo = data.get('cod_aforo', embarque.cod_aforo)
        embarque.cod_regimen = data.get('cod_regimen', embarque.cod_regimen)
        embarque.nro_mrn = data.get('nro_mrn', embarque.nro_mrn)

        # Obtener el valor del campo valor en la tabla StTipoAforo
        tipo_aforo = db.session.query(StTipoAforo).filter_by(cod_aforo=embarque.cod_aforo).first()
        if tipo_aforo:
            valor_aforo = tipo_aforo.valor
        else:
            valor_aforo = None

        # Sumar el valor_aforo (en días) a la fecha_bodega, solo si valor_aforo no es None
        if valor_aforo is not None:
            # Sumar el valor_aforo (en días) a la fecha_bodega, solo si valor_aforo no es None
            if embarque.fecha_bodega:
                embarque.fecha_bodega += timedelta(days=valor_aforo)

        db.session.commit()

        return jsonify({'mensaje': 'Embarque o BL actualizado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al actualizar Embarque: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/tipo_aforo/<empresa>/<cod_aforo>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_tipo_aforo(empresa,cod_aforo):
    try:
        aforo = db.session.query(StTipoAforo).filter_by( empresa=empresa, cod_aforo = cod_aforo).first()
        if not aforo:
            return jsonify({'mensaje': 'El tipo de aforo no existe.'}), 404
        
        fecha_modifica = date.today()
        
        data = request.get_json()
        aforo.nombre = data.get('nombre', aforo.nombre).upper()
        aforo.valor = data.get('valor', aforo.valor)
        aforo.observacion = data.get('observacion', aforo.observacion)
        aforo.usuario_modifica = data.get('usuario_modifica', aforo.usuario_modifica).upper()
        aforo.fecha_modifica = fecha_modifica

        db.session.commit()

        return jsonify({'mensaje': 'Tipo de Aforo actualizado exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar el Tipo de Aforo: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
#METODOS DELETE PARA ORDENES DE COMPRA

@bp.route('/orden_compra_cab/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_cab(cod_po, empresa,tipo_comprobante):
    try:
        orden = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po, empresa=empresa,tipo_comprobante=tipo_comprobante).first()
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        db.session.delete(orden)
        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_det/<cod_po>/<empresa>/<secuencia>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_det(cod_po, empresa, secuencia,tipo_comprobante):
    try:
        detalle = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa, secuencia = secuencia, tipo_comprobante = tipo_comprobante).first()
        if not detalle:
            return jsonify({'mensaje': 'Detalle de orden de compra no existe.'}), 404

        db.session.delete(detalle)
        db.session.commit()

        return jsonify({'mensaje': 'Detalle de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_tracking/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_tracking(cod_po, empresa, tipo_comprobante):
    try:
        tracking = db.session.query(StTracking).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante=tipo_comprobante).first()
        if not tracking:
            return jsonify({'mensaje': 'Tracking de orden de compra no existe.'}), 404

        db.session.delete(tracking)
        db.session.commit()

        return jsonify({'mensaje': 'Tracking de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_packinglist', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_packinglist():
    try:
        cod_po = request.args.get('cod_po')
        codigo_bl_house = request.args.get('codigo_bl_house')
        secuencia = request.args.get('secuencia')
        empresa = request.args.get('empresa')

        if not cod_po and not codigo_bl_house:
            return jsonify({'error': 'Debes proporcionar al menos cod_po o codigo_bl_house para eliminar.'}), 400

        packing_query = db.session.query(StPackinglist)

        if cod_po:
            packing_query = packing_query.filter_by(cod_po=cod_po)
        if codigo_bl_house:
            packing_query = packing_query.filter_by(codigo_bl_house=codigo_bl_house)
        if secuencia:
            packing_query = packing_query.filter_by(secuencia=secuencia)
        if empresa:
            packing_query = packing_query.filter_by(empresa=empresa)

        packing_entry = packing_query.first()
        query = StOrdenCompraDet.query().filter_by(cod_producto=packing_entry.cod_producto, cod_po=cod_po,empresa=empresa).first()

        packings_to_delete = packing_query.all()

        if not packings_to_delete:
            return jsonify({'mensaje': 'No se encontraron registros para eliminar.'}), 404
        
        if query:
            query.saldo_producto = query.saldo_producto + Decimal(str(packing_entry.cantidad))
            query.fob = 0
            query.fob_total = 0
            if query.cantidad_pedido == 0:
                db.session.delete(query)

        db.session.delete(packing_entry)

        db.session.commit()

        return jsonify({'mensaje': 'Registro de Packinglists de orden de compra eliminado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/embarque/<codigo_bl_house>/<empresa>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_embarque(codigo_bl_house, empresa):
    try:
        # Verificar si existen registros en StPackinglist que dependen del código_bl_house
        existe_packing = db.session.query(StPackinglist).filter_by(codigo_bl_house=codigo_bl_house).first()
        if existe_packing:
            return jsonify({'error': 'Existen registros en StPackinglist que dependen de este embarque. No se puede eliminar.'}), 400

        embarque = db.session.query(StEmbarquesBl).filter_by(codigo_bl_house=codigo_bl_house, empresa=empresa).first()
        if not embarque:
            return jsonify({'mensaje': 'Embarque de orden de compra no existe.'}), 404

        db.session.delete(embarque)
        db.session.commit()

        return jsonify({'mensaje': 'Embarque de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/tipo_aforo/<empresa>/<cod_aforo>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_tipo_aforo(empresa, cod_aforo):
    try:
        aforo = db.session.query(StTipoAforo).filter_by(empresa=empresa, cod_aforo = cod_aforo).first()
        if not aforo:
            return jsonify({'mensaje': 'Tipo de aforo no existe.'}), 404

        db.session.delete(aforo)
        db.session.commit()

        return jsonify({'mensaje': 'Tipo de Aforo eliminado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
#METODO PARA INGRESAR CABECERA Y DETALLES DE UNA ORDEN DE IMPORTACION
    
@bp.route('/orden_compra_total', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_total():
    try:
        data = request.get_json()
        fecha_crea = date.today()

        # Obtener la ciudad del proveedor
        busq_ciudad = TcCoaProveedor.query().filter_by(ruc=data['cabecera']['cod_proveedor']).first()
        ciudad = busq_ciudad.ciudad_matriz if busq_ciudad else ''

        # Obtener el nombre del estado
        #estado = TgModeloItem.query().filter_by(cod_modelo=data['cabecera']['cod_modelo'], cod_item=data['cabecera']['cod_item']).first()
        #estado_nombre = estado.nombre if estado else ''

        # Generar el código de la cabecera
        cod_po = asigna_cod_comprobante(data['cabecera']['empresa'], data['cabecera']['tipo_comprobante'], data['cabecera']['cod_agencia'])
        
        #fecha_estimada_produccion=datetime.strptime(data['cabecera']['fecha_estimada_produccion'], '%d/%m/%Y').date(),
        #fecha_estimada_puerto=datetime.strptime(data['cabecera']['fecha_estimada_puerto'], '%d/%m/%Y').date(),
        #fecha_estimada_llegada=datetime.strptime(data['cabecera']['fecha_estimada_llegada'], '%d/%m/%Y').date(),
        # Crear la cabecera de la orden de compra
        cabecera = StOrdenCompraCab(
            empresa=data['cabecera']['empresa'],
            cod_po=cod_po,
            bodega=data['cabecera']['bodega'],
            cod_agencia=data['cabecera']['cod_agencia'],
            tipo_comprobante=data['cabecera']['tipo_comprobante'],
            cod_proveedor=data['cabecera']['cod_proveedor'],
            nombre=data['cabecera']['nombre'],
            usuario_crea=data['cabecera']['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data['cabecera']['usuario_modifica'].upper(),
            fecha_modifica=datetime.strptime(data['cabecera']['fecha_modifica'], '%d/%m/%Y').date(),
            cod_modelo='IMPR',
            cod_item=data['cabecera']['cod_item'],
            ciudad=ciudad,
        )

        try:
            cabecera.proforma = data['cabecera']['proforma']
        except KeyError:
            cabecera.proforma = None

        try:
            cabecera.cod_opago = data['cabecera']['cod_opago']
        except KeyError:
            cabecera.cod_opago = None

        try:
            cabecera.fecha_estimada_produccion = datetime.strptime(data['cabecera']['fecha_estimada_produccion'], '%d/%m/%Y').date()
        except KeyError:
            cabecera.fecha_estimada_produccion = None

        try:
            cabecera.fecha_estimada_puerto = datetime.strptime(data['cabecera']['fecha_estimada_puerto'], '%d/%m/%Y').date()
        except KeyError:
            cabecera.fecha_estimada_puerto = None

        try:
            cabecera.fecha_estimada_llegada = datetime.strptime(data['cabecera']['fecha_estimada_llegada'], '%d/%m/%Y').date()
        except KeyError:
            cabecera.fecha_estimada_llegada = None
        db.session.add(cabecera)
        db.session.commit()

        # Agregar el código de la cabecera a cada detalle
        for detalle in data['detalles']:
            detalle['cod_po'] = cod_po

        # Crear los detalles de la orden de compra
        cod_po_no_existe = []
        cod_modelo_no_existe = []
        unidad_medida_no_existe = []

        for detalle in data['detalles']:
            print(detalle['agrupado'])
            cod_producto = detalle['cod_producto'].strip()
            unidad_medida = detalle['unidad_medida']
            cod_producto_modelo = detalle['cod_producto_modelo']

            # Verificar si el producto y la unidad de medida existen
            query_producto = Producto.query().filter_by(cod_producto=cod_producto).first()
            query_unidad_medida = StUnidadImportacion.query().filter_by(cod_unidad=unidad_medida).first()
            query_modelo = Producto.query().filter_by(cod_producto = cod_producto_modelo).first()

            if query_producto and query_unidad_medida and query_modelo:
                secuencia = obtener_secuencia(cod_po)
                costo_sistema = query_producto.costo

                # Obtener los nombres correspondientes del despiece o el producto
                despiece = StProductoDespiece.query().filter_by(cod_producto=cod_producto, empresa=data['cabecera']['empresa']).first()
                if despiece:
                    nombre_busq = StDespieceD.query().filter_by(cod_despiece=despiece.cod_despiece, secuencia = despiece.secuencia).first()
                    nombre = nombre_busq.nombre_e
                    nombre_i = nombre_busq.nombre_i
                    nombre_c = nombre_busq.nombre_c
                else:
                    nombre_busq = Producto.query().filter_by(cod_producto=cod_producto).first()
                    nombre = nombre_busq.nombre
                    nombre_i = nombre_busq.nombre
                    nombre_c = nombre_busq.nombre

                detalle_orden = StOrdenCompraDet(
                    exportar = 1 if detalle['agrupado'] else 0,
                    cod_po=cod_po,
                    tipo_comprobante='PO',
                    secuencia=secuencia,
                    empresa=data['cabecera']['empresa'],
                    cod_producto=cod_producto,
                    cod_producto_modelo=cod_producto_modelo,
                    nombre=nombre if nombre else None,
                    nombre_i=nombre_i if nombre_i else None,
                    nombre_c=nombre_c if nombre_c else None,
                    nombre_mod_prov=detalle['nombre_proveedor'],
                    nombre_comercial=detalle['nombre_comercial'],
                    costo_sistema=costo_sistema if costo_sistema else 0,
                    cantidad_pedido=detalle['pedido'],
                    saldo_producto=detalle['pedido'],
                    unidad_medida=unidad_medida,
                    usuario_crea=data['cabecera']['usuario_crea'].upper(),
                    fecha_crea=fecha_crea,
                )
                db.session.add(detalle_orden)
                db.session.commit()
            else:
                if not query_producto:
                    cod_po_no_existe.append(cod_producto+'\n')
                if not query_modelo:
                    cod_modelo_no_existe.append(cod_producto_modelo+'\n')
                else:
                    unidad_medida_no_existe.append(cod_producto+': '+unidad_medida+'\n')
        return jsonify({'mensaje': 'Orden de compra creada exitosamente', 'cod_po': cod_po,
                        'cod_producto_no_existe': list(set(cod_po_no_existe)),
                        'unidad_medida_no_existe': list(set(unidad_medida_no_existe)),
                        'cod_producto_modelo_no_existe': list(set(cod_modelo_no_existe))})

    except ValueError as ve:
        error_message = str(ve)
        return jsonify({'error': error_message}), 500

    except Exception as e:
        error_message = f"Se produjo un error: {str(e)}"
        return jsonify({'error': error_message}), 500
    
# Crear un diccionario para llevar un registro de la última combinación (cod_po, empresa, cod_item)
ultimas_combinaciones_track_oc = {}

# Función para crear o actualizar el registro en StTracking
def crear_o_actualizar_registro_tracking_oc(session):
    for target in session.new.union(session.dirty):
        if isinstance(target, StOrdenCompraCab) and 'cod_item' in target.__dict__:
            # Verificar si el objeto tiene los atributos esperados
            if hasattr(target, 'cod_po') and hasattr(target, 'empresa') and hasattr(target, 'usuario_crea') and hasattr(target, 'cod_modelo'):
                cod_po = target.cod_po
                empresa = target.empresa
                cod_item = target.cod_item

                # Obtener la última combinación (cod_po, empresa, cod_item)
                ultima_combinacion = ultimas_combinaciones_track_oc.get((cod_po, empresa), None)

                # Verificar si es una nueva combinación o si el cod_item cambió
                if not ultima_combinacion or cod_item != ultima_combinacion['cod_item']:
                    nueva_secuencia = secuencia_track_oc(cod_po)
                    new_record = StTracking(
                        cod_po=cod_po,
                        tipo_comprobante='PO',
                        secuencia=nueva_secuencia,
                        empresa=empresa,
                        cod_modelo=target.cod_modelo,
                        cod_item=cod_item,
                        fecha=datetime.now(),
                        usuario_crea=target.usuario_crea,
                        fecha_crea=datetime.now()
                    )
                    session.add(new_record)

                    # Actualizar la última combinación registrada
                    ultimas_combinaciones_track_oc[(cod_po, empresa)] = {'cod_item': cod_item}

# Registrar el evento before_commit en la sesión de SQLAlchemy para crear o actualizar registros en StTracking
event.listen(scoped_session, 'before_commit', crear_o_actualizar_registro_tracking_oc)


def secuencia_track_oc(cod_po):
    existe_cod_po = db.session.query(StTracking).filter_by(cod_po=cod_po).first()

    if existe_cod_po is not None:
        print('EXISTE2',existe_cod_po.cod_po)
        # Si el cod_po existe en la tabla StTracking, obtener el último número de secuencia
        max_secuencia = db.session.query(func.max(StTracking.secuencia)).filter_by(cod_po=cod_po).distinct().scalar()
        print('MAXIMO',max_secuencia)
        nueva_secuencia = int(max_secuencia) + 1
        print('PROXIMO',nueva_secuencia)
        return nueva_secuencia
    else:
        # Si el cod_po no existe en la tabla StTracking, generar secuencia desde 1
        nueva_secuencia = 1
        print('Secuencia de inicio', nueva_secuencia)
        return nueva_secuencia

@bp.route('/packinglist_total')
@jwt_required()
@cross_origin()
def obtener_packinglist_total():
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
        Producto.nombre.label("producto"),
    ).filter(
        StPackinglist.empresa == empresa
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
            "nro_contenedor": result.nro_contenedor,
            "proforma": result.proforma,
            "producto": result.producto,
            "cod_po": result.cod_po,
            "tipo_comprobante": result.tipo_comprobante,
            "empresa": result.empresa,
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

@bp.route('/containers')
@jwt_required()
@cross_origin()
def obtener_containers():
    query = StEmbarqueContenedores.query()
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
        es_carga_suelta = contenedor.es_carga_suelta if contenedor.es_carga_suelta else ""
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
@bp.route('/packings_by_container')
@jwt_required()
@cross_origin()
def obtener_packings_por_contenedor():
    empresa = request.args.get('empresa', None)
    nro_contenedor = request.args.get('nro_contenedor', None)
    try:
        query = text("""
            select count(*)
            from st_packinglist p
            where p.empresa = :empresa and p.nro_contenedor = :nro_contenedor
        """)
        result = db.session.execute(query, {"empresa": empresa, "nro_contenedor": nro_contenedor})
        row = result.fetchone()
        print(row)
        if row:
            response_data = {"packings": row[0]}
            # Serializar el diccionario como JSON y devolverlo como respuesta
            return json.dumps(response_data)
        return None

    except Exception as e:
        # Manejar errores
        print('Error:', e)
        raise

@bp.route('/tipo_contenedor')
@jwt_required()
@cross_origin()
def obtener_containers_tipo():
    query = StTipoContenedor.query()
    tipos = query.all()
    serialized_tipos = []
    for tipo in tipos:
        empresa = tipo.empresa if tipo.empresa else ""
        cod_tipo_contenedor = tipo.cod_tipo_contenedor if tipo.cod_tipo_contenedor else ""
        nombre = tipo.nombre if tipo.nombre else ""
        es_activo = tipo.es_activo if tipo.es_activo else ""
        serialized_tipos.append({
            "empresa": empresa,
            "cod_tipo_contenedor": cod_tipo_contenedor,
            "nombre": nombre,
            "es_activo": es_activo
        })
    return jsonify(serialized_tipos)

@bp.route('/contenedor/<nro_contenedor>/<empresa>', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_contenedor(nro_contenedor, empresa):
    try:
        if not nro_contenedor:
            return jsonify({'mensaje': 'No existe numero de contenedor.'}), 404

        data = request.get_json()


        contenedor = StEmbarqueContenedores(
            empresa=empresa,
            nro_contenedor=nro_contenedor,
            codigo_bl_house=data.get('codigo_bl_house'),
            cod_tipo_contenedor = data.get('cod_tipo_contenedor'),
            peso=data.get('peso'),
            volumen=data.get('volumen'),
            line_seal=data.get('line_seal'),
            shipper_seal=data.get('shipper_seal'),
            es_carga_suelta=data.get('es_carga_suelta'),
            observaciones=data.get('observaciones'),
            fecha_crea=date.today(),
            usuario_crea=data.get('usuario_crea')
        )

        db.session.add(contenedor)
        db.session.commit()

        return jsonify({'mensaje': 'Contenedor Creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al crear Contenedor: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/contenedor/<nro_contenedor>/<empresa>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_contenedor(nro_contenedor, empresa):
    try:
        contenedor = db.session.query(StEmbarqueContenedores).filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()
        if not contenedor:
            return jsonify({'mensaje': 'El contenedor no existe.'}), 404

        data = request.get_json()

        contenedor.codigo_bl_house = data.get('codigo_bl_house', contenedor.codigo_bl_house)
        contenedor.nro_contenedor = data.get('nro_contenedor', contenedor.nro_contenedor)
        contenedor.cod_tipo_contenedor = data.get('cod_tipo_contenedor', contenedor.cod_tipo_contenedor)
        contenedor.peso = data.get('peso', contenedor.peso)
        contenedor.volumen = data.get('volumen', contenedor.volumen) #date.today()
        contenedor.line_seal = data.get('line_seal', contenedor.line_seal)
        contenedor.shipper_seal = data.get('shipper_seal', contenedor.shipper_seal)
        contenedor.es_carga_suelta = data.get('es_carga_suelta', contenedor.es_carga_suelta)
        contenedor.observaciones = data.get('observaciones', contenedor.observaciones)
        contenedor.fecha_modifica = date.today()
        contenedor.usuario_modifica = data.get('usuario_modifica', contenedor.usuario_modifica)

        db.session.commit()

        return jsonify({'mensaje': 'Embarque o BL actualizado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al actualizar Embarque: {str(e)}")
        return jsonify({'error': str(e)}), 500

