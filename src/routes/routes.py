from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from src.models.users import Usuario, Empresa
from src.models.tipo_comprobante import TipoComprobante
from src.models.proveedores import Proveedor,TgModelo,TgModeloItem, ProveedorHor, TcCoaProveedor
from src.models.orden_compra import StOrdenCompraCab, StOrdenCompraDet, StTracking, StPackinglist, stProformaImpFp
from src.models.productos import Producto, st_lista_precio, st_gen_lista_precio
from src.models.formula import StFormula, StFormulaD
from src.models.despiece import StDespiece, StDespieceD
from src.models.st_proforma import st_proforma, st_proforma_movimiento, st_cab_deuna, st_det_deuna, st_cab_datafast, st_det_datafast, st_metodos_de_pago_ecommerce
from src.models.producto_despiece import StProductoDespiece
from src.models.unidad_importacion import StUnidadImportacion
from src.models.financiero import StFinCabCredito,StFinDetCredito,StFinClientes,StFinPagos
from src.models.embarque_bl import StEmbarquesBl,StTrackingBl, StPuertosEmbarque, StNaviera, StEmbarqueContenedores, StTipoContenedor, StTrackingContenedores
from src.models.tipo_aforo import StTipoAforo
from src.models.comprobante_electronico import tc_doc_elec_recibidos
from src.models.postVenta import st_prod_packing_list, st_casos_postventa, vt_casos_postventas, st_casos_postventas_obs, st_casos_tipo_problema, st_casos_url, ArCiudades, ADcantones, ADprovincias
from src.models.despiece_repuestos import st_producto_despiece, st_despiece, st_producto_rep_anio
from src.config.database import db, engine, session
from sqlalchemy import func, text, bindparam, Integer, event, desc
from sqlalchemy.orm import scoped_session
from sqlalchemy import and_, or_, func, tuple_
import logging
import datetime
from datetime import datetime, date
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from decimal import Decimal
from src import oracle
from os import getenv
from sqlalchemy.exc import SQLAlchemyError
import cx_Oracle
import json
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
                'nro_mrn': nro_mrn,
                'bl_house_manual': bl_house_manual
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


@bp.route('/orden_compra_det_aprob', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_det_aprob():
    try:
        data = request.get_json()
        fecha_crea = date.today()
        empresa = data['empresa']
        cod_po = data['cod_po']
        usuario_crea=data['usuario_crea'].upper()

        #####################################Eliminar los detalles previos##########################################################

        detalles_query = db.session.query(StOrdenCompraDet)
        if cod_po:
            detalles_query = detalles_query.filter_by(cod_po=cod_po)
        if empresa:
            detalles_query = detalles_query.filter_by(empresa=empresa)

        detalles_to_delete = detalles_query.all()

        # if not detalles_to_delete:
        #     return jsonify({'mensaje': 'No se encontraron registros para eliminar.'}), 404

        for detalle in detalles_to_delete:
            db.session.delete(detalle)
        db.session.commit()

        ###########################################################################################################################
        
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
                    exportar= 1 if order['agrupado'] == 'TRUE' else 0,
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
                    cantidad_pedido=order['pedido'],
                    costo_cotizado=order['costo_cotizado'],
                    saldo_producto=order['pedido'],
                    unidad_medida=unidad_medida,
                    usuario_crea=usuario_crea,
                    fecha_crea=fecha_crea,
                    usuario_modifica=usuario_crea,
                    fecha_modifica=date.today(),
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


@bp.route('/orden_compra_det', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_det():
    try:
        data = request.get_json()
        # print(data)
        fecha_crea = date.today()  # funcion para que se asigne la fecha actual al momento de crear el detalle de la oden de compra
        # fecha_modifica = date.today()

        empresa = data['empresa']
        cod_po = data['cod_po']
        usuario_crea = data['usuario_crea'].upper()

        # Verificar si el usuario existe en la base de datos
        usuario = Usuario.query().filter_by(usuario_oracle=usuario_crea).first()
        if not usuario:
            return jsonify({'mensaje': 'El usuario no existe.'}), 404

        cod_po_no_existe = []  # Lista para almacenar los codigo de productos que no existen
        unidad_medida_no_existe = []  # Lista para almacenar las unidades mal ingresadas
        cod_modelo_no_existe = []  # Lista para almacenar los cod_producto_modelo que no existen
        print(data)
        for order in data['orders']:
            print(order['cod_producto_modelo'])
            cod_producto = order['cod_producto'].strip()
            cod_producto_modelo = order['cod_producto_modelo'].strip()
            unidad_medida = order['unidad_medida'].upper()

            # Verificar si el producto existe en la tabla de Productos
            query = Producto.query().filter_by(cod_producto=cod_producto).first()
            query_umedida = StUnidadImportacion.query().filter_by(cod_unidad=unidad_medida).first()
            query_modelo = Producto.query().filter_by(cod_producto=cod_producto_modelo).first()
            if query and query_umedida and query_modelo:
                secuencia = obtener_secuencia(cod_po)
                costo_sistema = query.costo

                # Consultar la tabla StDespiece para obtener los valores correspondientes
                despiece = StProductoDespiece.query().filter_by(cod_producto=order['cod_producto'],
                                                                empresa=empresa).first()  # usar la empresa
                if despiece is not None:
                    nombre_busq = StDespieceD.query().filter_by(cod_despiece=despiece.cod_despiece,
                                                                secuencia=despiece.secuencia).first()
                    nombre = nombre_busq.nombre_e
                    nombre_i = nombre_busq.nombre_i
                    nombre_c = nombre_busq.nombre_c
                else:
                    nombre_busq = Producto.query().filter_by(cod_producto=order['cod_producto']).first()
                    nombre = nombre_busq.nombre
                    nombre_i = nombre_busq.nombre
                    nombre_c = nombre_busq.nombre

                detalle = StOrdenCompraDet(
                    exportar=order['agrupado'],
                    cod_po=cod_po,
                    tipo_comprobante='PO',
                    secuencia=secuencia,
                    empresa=empresa,
                    cod_producto=cod_producto,
                    cod_producto_modelo=cod_producto_modelo,
                    nombre=nombre if nombre else None,
                    nombre_i=nombre_i if nombre_i else order['nombre_ingles'],
                    nombre_c=nombre_c if nombre_c else None,
                    nombre_mod_prov=order['nombre_proveedor'],
                    nombre_comercial=order['nombre_comercial'],
                    costo_sistema=costo_sistema if costo_sistema else 0,
                    # fob=order['FOB'] if order['FOB'] else "",
                    cantidad_pedido=order['pedido'],
                    saldo_producto=order['pedido'],
                    unidad_medida=unidad_medida,
                    usuario_crea=usuario_crea,
                    fecha_crea=fecha_crea,
                    # usuario_modifica=order['usuario_modifica'].upper(),
                    # fecha_modifica=fecha_modifica,
                )
                # detalle.fob_total = order['FOB'] * order['CANTIDAD_PEDIDO']
                db.session.add(detalle)
                try:
                    # Intenta hacer la confirmación de la sesión
                    db.session.commit()
                except Exception as commit_error:
                    # Captura la excepción si ocurre un error al confirmar
                    db.session.rollback()  # Realiza un rollback para deshacer cambios pendientes
                    print(f"Error al confirmar: {str(commit_error)}")
                # secuencia = obtener_secuencia(order['COD_PO'])
            else:
                if query is None:
                    cod_po_no_existe.append(cod_producto + '\n')
                if query_modelo is None:
                    cod_modelo_no_existe.append(cod_producto_modelo + '\n')
                else:
                    unidad_medida_no_existe.append(unidad_medida + '\n')
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


def obtener_secuencia_formule(cod_formula):
    existe_cod_formula = db.session.query(StFormula).filter_by(cod_formula=cod_formula).first()

    if existe_cod_formula is not None:
        print('EXISTE', existe_cod_formula.cod_formula)
        existe_formula_det = db.session.query(StFormulaD).filter_by(cod_formula=cod_formula).first()

        if existe_formula_det is not None:
            print('EXISTE2', existe_formula_det.cod_formula)
            max_secuencia = db.session.query(func.max(StFormulaD.secuencia)).filter_by(
                cod_formula=cod_formula).distinct().scalar()
            print('MAXIMO', max_secuencia)
            nueva_secuencia = int(max_secuencia) + 1
            print('PROXIMO', nueva_secuencia)
            return nueva_secuencia
        else:
            nueva_secuencia = 1
            print('Secuencia de inicio', nueva_secuencia)
            return nueva_secuencia
    else:
        raise ValueError('La Formula no existe.')

def obtener_secuencia_pagos(empresa, cod_cliente, cod_proveedor, nro_operacion, nro_pago):
    existe_cuota = db.session.query(StFinDetCredito).filter_by(empresa=empresa, cod_cliente=cod_cliente,cod_proveedor=cod_proveedor, nro_operacion=nro_operacion,nro_pago=nro_pago).first()

    if existe_cuota is not None:
        print('Cuota', existe_cuota.nro_operacion , ' :', existe_cuota.nro_pago)
        existe_pago = db.session.query(StFinPagos).filter_by(empresa=empresa, cod_cliente=cod_cliente,cod_proveedor=cod_proveedor, nro_operacion=nro_operacion,nro_cuota=nro_pago).first()

        if existe_pago is not None:
            print('Pago', existe_pago.secuencia)
            max_secuencia = db.session.query(func.max(StFinPagos.secuencia)).filter_by(
                empresa=empresa, cod_cliente=cod_cliente,cod_proveedor=cod_proveedor, nro_operacion=nro_operacion,nro_cuota=nro_pago).distinct().scalar()
            print('MAXIMO', max_secuencia)
            nueva_secuencia = int(max_secuencia) + 1
            print('PROXIMO', nueva_secuencia)
            return nueva_secuencia
        else:
            nueva_secuencia = 1
            print('Secuencia de inicio', nueva_secuencia)
            return nueva_secuencia
    else:
        raise ValueError('No existe cuota.')


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

@bp.route('/generar_orden_compra', methods=['POST'])
@jwt_required()
@cross_origin()
def generar_orden_compra():
    try:
        data = request.json
        print(data)
        p_cod_empresa = float(data["p_cod_empresa"])
        p_tipo_proforma = data["p_tipo_proforma"]
        p_cod_proforma = data["p_cod_proforma"]
        p_cod_agencia = data["p_cod_agencia"]
        p_usuario = data["p_usuario"]

        #Ejecutar el procedimiento PL/SQL
        query = """
                       DECLARE
                            p_tipo_compra VARCHAR(100);
                            p_cod_compra VARCHAR (100);
                       BEGIN
                         ks_prof_importacion_rep.genera_orden_compra(
                           p_cod_empresa => :p_cod_empresa,
                           p_tipo_proforma => :p_tipo_proforma,
                           p_cod_proforma => :p_cod_proforma,
                           p_cod_agencia => :p_cod_agencia,
                           P_USUARIO => :P_USUARIO,
                           p_tipo_compra => p_tipo_compra,
                           p_cod_compra => p_cod_compra
                         );
                         -- Asigna los valores de las variables a los parámetros de salida
                         :p_tipo_compra := p_tipo_compra;
                         :p_cod_compra := p_cod_compra;
                       END;
                       """
        with engine.connect() as conn:
            result = conn.execute(text(query), {
                'p_cod_empresa': p_cod_empresa,
                'p_tipo_proforma': p_tipo_proforma,
                'p_cod_proforma': p_cod_proforma,
                'p_cod_agencia': p_cod_agencia,
                'P_USUARIO': p_usuario,
                'p_tipo_compra': None,
                'p_cod_compra': None
            })
            conn.commit()
            print(result)
        return jsonify({"data": "Orden de Compra generada correctamente"})

    except Exception as e:
        error_message = f"Error al procesar la solicitud: {str(e)}"
        print(str(e))
        return jsonify({"error": error_message}), 500

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
                query_conte = StEmbarqueContenedores.query().filter_by(nro_contenedor=nro_contenedor, empresa=empresa).first()
                if query_conte:
                    if query :
                        packinlist = StPackinglist(
                            nro_contenedor=nro_contenedor,
                            empresa=empresa,
                            cod_po=packing['cod_po'],
                            secuencia=secuencia,
                            tipo_comprobante=tipo_comprobante,
                            cod_producto=cod_producto,
                            cantidad=packing['cantidad'],
                            fob=packing['fob'],
                            unidad_medida=query_prod.cod_unidad if query_prod.cod_unidad else unidad_medida,
                            usuario_crea=usuario_crea,
                            fecha_crea=fecha_crea,
                            codigo_bl_house=query_contenedor.codigo_bl_house
                            # usuario_modifica = packing['usuario_modifica'].upper(),
                            # fecha_modifica = fecha_modifica
                        )
                        query.saldo_producto = query.saldo_producto - packing['cantidad']
                        if query.fob is None or float(query.fob) == 0:
                            query.fob = packing['fob']
                        if query.fob_total is None:
                            query.fob_total = Decimal(0)
                        query.fob_total = query.fob_total + Decimal(packing['fob']) * Decimal(packing['cantidad'])
                        query.costo_sistema = costo_sistema
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
                                    unidad_medida=query_prod.cod_unidad if query_prod.cod_unidad else unidad_medida,
                                    usuario_crea=usuario_crea,
                                    fecha_crea=fecha_crea,
                                    codigo_bl_house=query_contenedor.codigo_bl_house
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
                                    unidad_medida=query_prod.cod_unidad if query_prod.cod_unidad else unidad_medida, #setear el cod unidad del producto en vez del cod unidad ingresado por excel
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

                            unidad_medida_no_existe.append(cod_producto +" "+ unidad_medida)

                else:
                    bl_no_existe.append(nro_contenedor)
            else:
                prod_no_existe.append(cod_producto)
        query_contenedor.cod_item = 'A'
        db.session.commit()
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
        if fecha_embarque is None:
            return jsonify({'error': 'Ingrese fecha de embarque'})

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        cursor.execute("""
                            SELECT KS_EMBARQUES_BL.OBT_SECUENCIA_BL(
                                :param1,
                                :param2
                            ) AS resultado
                            FROM dual
                        """,
                       param1=data['empresa'], param2=fecha_embarque)
        db1.close
        result = cursor.fetchone()
        cursor.close()
        codigo_bl_house = result[0]
        print(codigo_bl_house)
        embarque = StEmbarquesBl(
            empresa=data['empresa'],
            codigo_bl_master=data['codigo_bl_master'],
            codigo_bl_house=codigo_bl_house,
            cod_proveedor=data['cod_proveedor'],
            fecha_embarque=fecha_embarque,
            fecha_llegada=fecha_llegada,
            fecha_bodega=fecha_bodega,
            numero_tracking=data.get('codigo_bl_master')[-4:],
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
            nro_mrn = data.get('nro_mrn'),
            bl_house_manual = data.get('bl_house_manual')
        )

        db.session.add(embarque)
        db.session.commit()

        return jsonify({'codigo_bl_house': codigo_bl_house})

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
            if embarque.cod_item != data['cod_item']:
                tracking = StTrackingBl(
                  cod_bl_house=codigo_bl_house,
                  empresa=empresa,
                  observaciones="Tracking BackEnd",
                  cod_modelo=data.get('cod_modelo'),
                  usuario_crea=data.get('modificado_por'),
                  fecha_crea=date.today(),
                  fecha=date.today(),
                  cod_item=data['cod_item'],
                  secuencial= db.session.query(StTrackingBl).filter_by(cod_bl_house=codigo_bl_house, empresa=empresa).order_by(desc(StTrackingBl.secuencial)).first().secuencial + 1
                )
                db.session.add(tracking)

            embarque.cod_item = data['cod_item']


        # Verificar si el campo 'estado' está presente en el JSON antes de asignarlo
        if 'estado' in data:
            embarque.estado = data['estado']

        embarque.cod_proveedor = data.get('cod_proveedor', embarque.cod_proveedor)
        embarque.numero_tracking = data.get('codigo_bl_master')[-4:] if data.get('codigo_bl_master') else embarque.numero_tracking
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
        embarque.bl_house_manual = data.get('bl_house_manual', embarque.bl_house_manual)
        embarque.codigo_bl_master = data.get('codigo_bl_master', embarque.codigo_bl_master)

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
#BOX FORMAS DE PAGO
@bp.route('/crear_anticipo_forma_de_pago_general', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_anticipo_forma_de_pago_general():
    try:
        data = request.json
        print(float(data['pct_valor']))
        data['valor'] = float(data['valor'])
        data['saldo'] = float(data['saldo'])
        data['pct_valor'] = float(data['pct_valor'])
        data['dias_vencimiento'] = int(data['dias_vencimiento'])
        max_secuencia = db.session.query(func.max(stProformaImpFp.secuencia)).filter_by(
            cod_proforma=data['cod_proforma']).scalar()

        if max_secuencia is None:
            data['secuencia'] = 1
        else:
            data['secuencia'] = max_secuencia + 1

        nueva_proforma = stProformaImpFp(
            empresa=data['empresa'],
            cod_proforma=data['cod_proforma'],
            secuencia=data['secuencia'],
            tipo_proforma=data['tipo_proforma'],
            fecha_vencimiento=datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d'),
            valor=data['valor'],
            saldo=data['saldo'],
            descripcion=data['descripcion'],
            cod_forma_pago=data['cod_forma_pago'],
            dias_vencimiento=data['dias_vencimiento'],
            pct_valor=data['pct_valor']
        )

        db.session.add(nueva_proforma)
        db.session.commit()

        return jsonify({"data": "Registro añadido correctamente"})

    except Exception as e:
        error_message = f"Error al procesar la solicitud: {str(e)}"
        return jsonify({"error": error_message}), 500

@bp.route('/actualizar_anticipo_forma_de_pago_general/<int:secuencia>/<string:cod_proforma>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_anticipo_forma_de_pago_general(secuencia, cod_proforma):
    data = request.json
    proforma_actualizada = db.session.query(stProformaImpFp).filter_by(secuencia=secuencia, cod_proforma=cod_proforma).first()

    if proforma_actualizada:
        proforma_actualizada.empresa = data['empresa']
        proforma_actualizada.tipo_proforma = data['tipo_proforma']
        proforma_actualizada.fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d')
        proforma_actualizada.valor = float(data['valor'])
        proforma_actualizada.saldo = data['saldo']
        proforma_actualizada.descripcion = data['descripcion']
        proforma_actualizada.cod_forma_pago = data['cod_forma_pago']
        proforma_actualizada.dias_vencimiento = data['dias_vencimiento']
        proforma_actualizada.pct_valor = float(data['pct_valor'])

        db.session.commit()
        return jsonify({"message": "Registro actualizado exitosamente."})
    else:
        return jsonify({"error": "No se encontró el registro para actualizar."}), 404

@bp.route('/proformas_por_cod_proforma/<string:cod_proforma>', methods=['GET'])
@jwt_required()
def obtener_proformas_por_cod_proforma(cod_proforma):
    proformas = db.session.query(stProformaImpFp).filter_by(cod_proforma=cod_proforma).order_by(stProformaImpFp.secuencia).all()
    if not proformas:
        return jsonify({'mensaje': 'No se encontraron proformas para el código proporcionado'}), 404

    proformas_data = []
    for proforma in proformas:
        proformas_data.append({
            'empresa': proforma.empresa,
            'cod_proforma': proforma.cod_proforma,
            'secuencia': proforma.secuencia,
            'tipo_proforma': proforma.tipo_proforma,
            'fecha_vencimiento': proforma.fecha_vencimiento.strftime('%Y-%m-%d'),
            'valor': proforma.valor,
            'saldo': proforma.saldo,
            'descripcion': proforma.descripcion,
            'cod_forma_pago': proforma.cod_forma_pago,
            'dias_vencimiento': proforma.dias_vencimiento,
            'pct_valor': proforma.pct_valor
        })
    #print(proformas_data)
    return jsonify({'proformas': proformas_data})

@bp.route('/proformas_delete_anticipo', methods=['DELETE'])
@jwt_required()
def delete_anticipo():
    data = request.json
    secuenciaToDelete=data["secuencia"]
    codProformaToDelete=data["cod_proforma"]
    print(data)
    if stProformaImpFp.eliminar_registro(secuenciaToDelete, codProformaToDelete):
        return "Registro eliminado Correctamente"
    else:
        return "No se pudo eliminar Registro"

    #proformas = db.session.query(stProformaImpFp).filter_by(cod_proforma=cod_proforma).all()
    #print(proformas)
    return jsonify({'proformas': 'proformas_data'})

@bp.route('/anticipos_por_cod_proforma/<string:cod_proforma>', methods=['GET'])
@jwt_required()
def obtener_anticipos_por_cod_proforma(cod_proforma):
    proformas = db.session.query(stProformaImpFp).filter_by(cod_proforma=cod_proforma, cod_forma_pago='ANT').order_by(stProformaImpFp.secuencia).all()
    if not proformas:
        return jsonify({'mensaje': 'No se encontraron proformas para el código proporcionado'}), 404

    proformas_data = []
    for proforma in proformas:
        proformas_data.append({
            'empresa': proforma.empresa,
            'cod_proforma': proforma.cod_proforma,
            'secuencia': proforma.secuencia,
            'tipo_proforma': proforma.tipo_proforma,
            'fecha_vencimiento': proforma.fecha_vencimiento.strftime('%Y-%m-%d'),
            'valor': proforma.valor,
            'saldo': proforma.saldo,
            'descripcion': proforma.descripcion,
            'cod_forma_pago': proforma.cod_forma_pago,
            'dias_vencimiento': proforma.dias_vencimiento,
            'pct_valor': proforma.pct_valor
        })
    #print(proformas_data)
    return jsonify({'proformas': proformas_data})

@bp.route('/pagar_anticipo_forma_de_pago_general', methods=['POST'])
@jwt_required()
@cross_origin()
def pagar_anticipo_forma_de_pago_general():
    try:
        data = request.json
        print(data)
        p_cod_empresa = float(data["p_cod_empresa"])
        p_tipo_proforma = data["p_tipo_proforma"]
        p_cod_proforma = data["p_cod_proforma"]
        p_usuario = data["p_usuario"]

        #Ejecutar el procedimiento PL/SQL
        query = """
                       DECLARE
                            tipo_pago VARCHAR(100);
                            cod_pago VARCHAR (100);
                       BEGIN
                         ks_prof_importacion_rep.genera_orden_pago(
                           p_cod_empresa => :p_cod_empresa,
                           p_tipo_proforma => :p_tipo_proforma,
                           p_cod_proforma => :p_cod_proforma,
                           p_usuario => :p_usuario,
                           p_tipo_opago => tipo_pago,
                           p_cod_opago => cod_pago
                         );
                         -- Asigna los valores de las variables a los parámetros de salida
                         :tipo_pago := tipo_pago;
                         :cod_pago := cod_pago;
                       END;
                       """
        with engine.connect() as conn:
            result = conn.execute(text(query), {
                'p_cod_empresa': p_cod_empresa,
                'p_tipo_proforma': p_tipo_proforma,
                'p_cod_proforma': p_cod_proforma,
                'p_usuario': p_usuario,
                'tipo_pago': None,
                'cod_pago': None
            })
            print(result)
        return jsonify({"data": "Pago generado correctamente"})

    except Exception as e:
        error_message = f"Error al procesar la solicitud: {str(e)}"
        print(str(e))
        return jsonify({"error": error_message}), 500

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
        fecha_bodega = datetime.strftime(contenedor.fecha_bodega,"%d/%m/%Y") if contenedor.fecha_bodega else ""
        cod_modelo = contenedor.cod_modelo if contenedor.cod_modelo else ""
        cod_item = contenedor.cod_item if contenedor.cod_item else ""
        es_repuestos = contenedor.es_repuestos if contenedor.es_repuestos else ""
        es_motos = contenedor.es_motos if contenedor.es_motos else ""
        fecha_salida = datetime.strftime(contenedor.fecha_salida,"%d/%m/%Y") if contenedor.fecha_salida else ""

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
            return jsonify(response_data)
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
            usuario_crea=data.get('usuario_crea'),
            cod_item= 1,
            cod_modelo='BL',
            fecha_bodega=parse_date(data.get('fecha_bodega')),
            es_repuestos=data.get('es_repuestos'),
            es_motos=data.get('es_motos'),
            fecha_salida=datetime.strptime(data.get('fecha_salida'), '%d/%m/%Y').date()
        )

        tracking = StTrackingContenedores(
            nro_contenedor=nro_contenedor,
            empresa=empresa,
            secuencial=1,
            observaciones="Tracking BackEnd",
            cod_modelo='BL',
            usuario_crea=data.get('modificado_por'),
            fecha_crea=date.today(),
            fecha=date.today(),
            cod_item=1,
            codigo_bl_house=data.get('codigo_bl_house')
        )
        db.session.add(tracking)

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

        if 'cod_item' in data:
            if contenedor.cod_item != data['cod_item']:
                tracking = StTrackingContenedores(
                  nro_contenedor=data.get('nro_contenedor', contenedor.nro_contenedor),
                  empresa=empresa,
                  secuencial=db.session.query(StTrackingContenedores).filter_by(nro_contenedor=nro_contenedor,empresa=empresa).order_by(desc(StTrackingContenedores.secuencial)).first().secuencial + 1 if db.session.query(StTrackingContenedores).filter_by(nro_contenedor=nro_contenedor,empresa=empresa).order_by(desc(StTrackingContenedores.secuencial)).first() else 1,
                  observaciones="Tracking BackEnd",
                  cod_modelo=data.get('cod_modelo'),
                  usuario_crea=data.get('modificado_por'),
                  fecha_crea=date.today(),
                  fecha=date.today(),
                  cod_item=data['cod_item'],
                  codigo_bl_house=data.get('codigo_bl_house', contenedor.codigo_bl_house)
                )
                db.session.add(tracking)
            contenedor.cod_item = data['cod_item']

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
        contenedor.fecha_bodega = data.get('fecha_bodega', contenedor.fecha_bodega)
        contenedor.cod_modelo = data.get('cod_modelo', contenedor.cod_modelo)
        contenedor.es_repuestos = data.get('es_repuestos', contenedor.es_repuestos)
        contenedor.es_motos = data.get('es_motos', contenedor.es_motos)
        contenedor.fecha_salida = datetime.strptime(data.get('fecha_salida'), '%d/%m/%Y').date() if data.get('fecha_salida') else contenedor.fecha_salida

        db.session.commit()

        return jsonify({'mensaje': 'Embarque o BL actualizado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al actualizar Embarque: {str(e)}")
        return jsonify({'error': str(e)}), 500

#DOC-SRI-ELECTRONICS--------------------------------------------------------------
@bp.route('/comprobante/electronico', methods=['POST'])
@jwt_required()
@cross_origin()
def insertFortLote():
    try:
        # Obtén el JSON enviado desde el front-end
        data = request.get_json()
        query = tc_doc_elec_recibidos.query()
        # Verifica si se recibió correctamente el JSON
        if data:
            # Puedes acceder a los datos del JSON usando dataSr
            for item in data:
                existing_entry = query.filter(
                    tc_doc_elec_recibidos.ruc_emisor == item['RUC_EMISOR'],
                    tc_doc_elec_recibidos.serie_comprobante == item['SERIE_COMPROBANTE']
                ).first()

                if existing_entry:
                    pass
                else:
                    fecha_emision = datetime.strptime(item['FECHA_EMISION'], '%d/%m/%Y')
                    fecha_autorizacion = datetime.strptime(item['FECHA_AUTORIZACION'], '%d/%m/%Y %H:%M:%S')
                    importe_total = float(item.get('IMPORTE_TOTAL', '0')) if item.get('IMPORTE_TOTAL', '0') != '' else 0
                    iva = float(item.get('IVA', '0')) if item.get('IVA', '0') != '' else 0
                    valor_sin_impuestos = float(item.get('VALOR_SIN_IMPUESTOS', '0')) if item.get('VALOR_SIN_IMPUESTOS', '0') != '' else 0
                    new_entry = tc_doc_elec_recibidos(
                        ruc_emisor=item.get('RUC_EMISOR'),
                        serie_comprobante=item['SERIE_COMPROBANTE'],
                        comprobante=item['COMPROBANTE'].upper(),
                        razon_social_emisor=item['RAZON_SOCIAL_EMISOR'].upper(),
                        fecha_emision=fecha_emision,
                        fecha_autorizacion=fecha_autorizacion,
                        tipo_emision=item.get('TIPO_EMISION',''),
                        numero_documento_modificado=item.get('NUMERO_DOCUMENTO_MODIFICADO', ''),
                        identificacion_receptor=item['IDENTIFICACION_RECEPTOR'],
                        clave_acceso=item['CLAVE_ACCESO'],
                        numero_autorizacion=item.get('NUMERO_AUTORIZACION', ''),
                        importe_total=importe_total,
                        iva=iva,
                        valor_sin_impuestos=valor_sin_impuestos
                    )

                    db.session.add(new_entry)
                    db.session.commit()
        else:
            return jsonify({'error': 'No se recibió el JSON esperado'}), 400
        return jsonify({'message': 'success'})
    except Exception as e:
            # En lugar de devolver un mensaje genérico, imprime el error para obtener más información
            print(str(e))
            return jsonify({'error': 'Server Error'}), 500


@bp.route('/doc_elec_recibidos', methods=['GET'])
@jwt_required()
@cross_origin()
def obtener_doc_elec_recibidos():
    try:
        #query = tc_doc_elec_recibidos.query().slice(0, 100)  # Utiliza el método query de la clase tc_doc_elec_recibidos
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')


        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

            query = tc_doc_elec_recibidos.query()
            documentos = query.filter(and_(
            tc_doc_elec_recibidos.fecha_emision >= start_date,
            tc_doc_elec_recibidos.fecha_emision <= end_date
            ))

            serialized_documentos = []

            for documento in documentos:
                serialized_documentos.append({
                    'ruc_emisor': documento.ruc_emisor,
                    'serie_comprobante': documento.serie_comprobante,
                    'comprobante': documento.comprobante,
                    'razon_social_emisor': documento.razon_social_emisor,
                    'fecha_emision': documento.fecha_emision.strftime("%d/%m/%Y") if documento.fecha_emision else "",
                    'fecha_autorizacion': documento.fecha_autorizacion.strftime(
                        "%d/%m/%Y") if documento.fecha_autorizacion else "",
                    'tipo_emision': documento.tipo_emision,
                    'numero_documento_modificado': documento.numero_documento_modificado,
                    'identificacion_receptor': documento.identificacion_receptor,
                    'clave_acceso': documento.clave_acceso,
                    'numero_autorizacion': documento.numero_autorizacion,
                    'importe_total': float(documento.importe_total) if documento.importe_total is not None else None,
                    'iva': float(documento.iva) if documento.iva is not None else None,
                    'valor_sin_impuestos':float(documento.valor_sin_impuestos) if documento.valor_sin_impuestos is not None else None,
                })

            return jsonify(serialized_documentos)
        else:
                return jsonify('without date')



    except Exception as e:
        logger.exception(f"Error al actualizar Embarque: {str(e)}")
        return jsonify({'error': str(e)}), 500

#WARRANTY MODULES------------------------------------------------------------
@bp.route('/checkInfoForCodeEngine/<code>', methods=['GET'])
@jwt_required()
@cross_origin()
def chekInfoForCodeEngine(code):
    codeEngine = st_prod_packing_list.query().filter(
        st_prod_packing_list.empresa == 20,
        st_prod_packing_list.es_anulado == 0,
        func.replace(st_prod_packing_list.cod_motor, ' ', '').like(f'%{code}%')
    ).limit(10).all()
    # Construir los datos a devolver en formato JSON
    data = [{"COD_MOTOR": registro.cod_motor, "COD_CHASIS": registro.cod_chasis} for registro in codeEngine]
    return jsonify(data)
@bp.route('/getInfoForCodeEngine/<code>', methods=['GET'])
@jwt_required()
@cross_origin()
def getInfoForCodeEngine(code):
    print(code)
    codeEngine = st_prod_packing_list.query().filter(
        st_prod_packing_list.empresa == 20,
        st_prod_packing_list.es_anulado == 0,
        func.replace(st_prod_packing_list.cod_motor, ' ', '').like(f'%{code}%')
    ).limit(10).all()
    # Construir los datos a devolver en formato JSON
    data = [{"COD_MOTOR": registro.cod_motor, "COD_CHASIS": registro.cod_chasis} for registro in codeEngine]
    print(data)
    return jsonify(data)

@bp.route('/getInfoCasosPostventas', methods=['GET'])
@jwt_required()
@cross_origin()
def getInfoCasosPostventas():
    filtros_params = request.args.to_dict()
    #Filter initial by enterprise
    query = st_casos_postventa.query().filter(
        st_casos_postventa.empresa == 20,
    )
    #data processing date prior to consultation

    start_date = datetime.strptime(filtros_params['start_date'], '%d/%m/%Y') if filtros_params['start_date'] else None
    finish_date = datetime.strptime(filtros_params['finish_date'], '%d/%m/%Y') if filtros_params['finish_date'] else None
    #Aumentar un dia
    if finish_date:
        finish_date += timedelta(days=1)
    if start_date:
        start_date -= timedelta(days=1)
    cod_provincia = filtros_params['cod_provincia'] if filtros_params['cod_provincia'] else None
    cod_canton = filtros_params['cod_canton'] if filtros_params['cod_canton'] else None
    warranty_status = filtros_params['warranty_status'] if filtros_params['warranty_status'] else None
    case_status = filtros_params['case_status'] if filtros_params['case_status'] else None

# Filter date range
    if start_date is not None and finish_date is not None:
        query = query.filter(
            st_casos_postventa.fecha.between(start_date, finish_date)
        )
#Filter by City (Cantón) and Province
    if cod_provincia is not None:
        query = query.filter(
              st_casos_postventa.codigo_provincia == cod_provincia
        )
    if cod_canton is not None:
        query = query.filter(
            st_casos_postventa.codigo_canton == cod_canton
        )
#Filter warranty status
    if warranty_status is not None:
        query = query.filter(
            st_casos_postventa.aplica_garantia == warranty_status
        )
#Filter by case status
    if case_status is not None:
        query = query.filter(
                st_casos_postventa.estado == case_status
        )
    casos_postventas = query.all()
#Construir los datos a devolver en formato JSON
    casos_json = []
    for caso in casos_postventas:
        caso_dict = {
            "cod_comprobante": caso.cod_comprobante,
            "tipo_comprobante": caso.tipo_comprobante,
            "nombre_caso": caso.nombre_caso,
            "descripcion": caso.descripcion,
            "codigo_nacion": caso.codigo_nacion,
            "codigo_provincia": caso.codigo_provincia,
            "codigo_canton": caso.codigo_canton,
            "nombre_cliente": caso.nombre_cliente,
            "cod_producto": caso.cod_producto,
            "cod_motor": caso.cod_motor,
            "kilometraje": caso.kilometraje,
            "codigo_taller": caso.codigo_taller,
            "codigo_responsable": caso.codigo_responsable,
            "cod_tipo_problema": caso.cod_tipo_problema,
            "aplica_garantia": caso.aplica_garantia,
            "adicionado_por": caso.adicionado_por,
            "cod_distribuidor": caso.cod_distribuidor,
            "manual_garantia": caso.manual_garantia,
            "estado": caso.estado,
            "usuario_cierra": caso.usuario_cierra,
            "observacion_final": caso.observacion_final,
            "identificacion_cliente": caso.identificacion_cliente,
            "telefono_contacto1": caso.telefono_contacto1,
            "telefono_contacto2": caso.telefono_contacto2,
            "telefono_contacto3": caso.telefono_contacto3,
            "e_mail1": caso.e_mail1,
            "e_mail2": caso.e_mail2,
            "cod_tipo_identificacion": caso.cod_tipo_identificacion,
            "cod_agente": caso.cod_agente,
            "cod_pedido": caso.cod_pedido,
            "cod_tipo_pedido": caso.cod_tipo_pedido,
            "numero_guia": caso.numero_guia,
            "cod_distribuidor_cli": caso.cod_distribuidor_cli,
            "es_cliente_contactado": caso.es_cliente_contactado,
            "cod_canal": caso.cod_canal,
            "referencia": caso.referencia,
            "aplica_excepcion": caso.aplica_excepcion,
            "cod_empleado": caso.cod_empleado,
            "cod_tipo_persona": caso.cod_tipo_persona
        }
        # Tratamiento para fecha_adicion
        if caso.fecha_adicion:
            caso_dict["fecha_adicion"] = caso.fecha_adicion.strftime('%Y-%m-%d %H:%M:%S')
        else:
            caso_dict["fecha_adicion"] = None

        # Tratamiento para fecha_cierre
        if caso.fecha_cierre:
            caso_dict["fecha_cierre"] = caso.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S')
        else:
            caso_dict["fecha_cierre"] = None

        # Tratamiento para fecha_venta
        if caso.fecha_venta:
            caso_dict["fecha_venta"] = caso.fecha_venta.strftime('%Y-%m-%d')
        else:
            caso_dict["fecha_venta"] = None

        # Tratamiento para fecha
        if caso.fecha:
            caso_dict["fecha"] = caso.fecha.strftime('%Y-%m-%d %H:%M:%S')
        else:
            caso_dict["fecha"] = None

        query2 = vt_casos_postventas.query().filter(
            vt_casos_postventas.empresa == 20,
            vt_casos_postventas.cod_comprobante == caso_dict["cod_comprobante"],
        )

        vt_casos = query2.first()
        if vt_casos is not None:
            if vt_casos.porcentaje_avance is None:
                caso_dict["porcentaje"] = 0
            else:
                caso_dict["porcentaje"] = vt_casos.porcentaje_avance
            caso_dict["taller"] = vt_casos.taller
        casos_json.append(caso_dict)
    #print(casos_json)
    return jsonify(casos_json)

@bp.route('/casosTipo/<cp_code>', methods=['GET'])
@jwt_required()
@cross_origin()
def casosTipoFunction(cp_code):
    try:
        cases = st_casos_tipo_problema.query().filter(
            st_casos_tipo_problema.cod_comprobante == cp_code,
            st_casos_tipo_problema.empresa == 20
        )
        cases_json = []
        for case in cases:
            case_dict = {
                "cod_comprobante": case.cod_comprobante,
                "codigo_problema": case.codigo_duracion,
                "estado": case.estado,
                "adicionado_by": case.adicionado_por,
                "descripcion": case.descripcion
            }
            cases_json.append(case_dict)

        return jsonify(cases_json)

    except Exception as e:
        print(e)
        error_msg = "An error occurred while processing the request."
        return jsonify({"error": e}), 500

@bp.route('/casosTipoImages/<code_cp>', methods=['GET'])
@jwt_required()
@cross_origin()
def url_media(code_cp):
    try:
        url = st_casos_url.query().filter(
            st_casos_url.empresa == 20,
            st_casos_url.cod_comprobante == code_cp,
            st_casos_url.tipo_comprobante == 'CP'
        ).first()
        images = url.url_photos
        videos = url.url_videos
        dic = {
            "images": images,
            "videos": videos
        }
        return jsonify(dic)

    except Exception as e:
        return jsonify(e)

@bp.route('/view_casos/<code_cp>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_info_casos_post_view_ventas(code_cp):
    try:
        filtros_params = request.args.to_dict()
        query = vt_casos_postventas.query().filter(
            vt_casos_postventas.cod_comprobante == code_cp
        )
        casos_postventas = query.all()

        # Convertir resultados a formato JSON
        casos_json = []
        for caso in casos_postventas:
            caso_dict = {
                "empresa": caso.empresa,
                "tipo_comprobante": caso.tipo_comprobante,
                "cod_comprobante": caso.cod_comprobante,
                "fecha": caso.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                "nombre_caso": caso.nombre_caso,
                "descripcion": caso.descripcion,
                "codigo_responsable": caso.codigo_responsable,
                "responsable": caso.responsable,
                "nombre_cliente": caso.nombre_cliente,
                "cod_producto": caso.cod_producto,
                "cod_motor": caso.cod_motor,
                "kilometraje": caso.kilometraje,
                "codigo_taller": caso.codigo_taller,
                "taller": caso.taller,
                "cod_tipo_problema": caso.cod_tipo_problema,
                "aplica_garantia": caso.aplica_garantia,
                "cod_distribuidor": caso.cod_distribuidor,
                "distribuidor": caso.distribuidor,
                "manual_garantia": caso.manual_garantia,
                "estado": caso.estado,
                "nombre_estado": caso.nombre_estado,
                "fecha_cierre": caso.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S') if caso.fecha_cierre else None,
                "usuario_cierra": caso.usuario_cierra,
                "observacion_final": caso.observacion_final,
                "identificacion_cliente": caso.identificacion_cliente,
                "telefono_contacto1": caso.telefono_contacto1,
                "telefono_contacto2": caso.telefono_contacto2,
                "telefono_contacto3": caso.telefono_contacto3,
                "e_mail1": caso.e_mail1,
                "e_mail2": caso.e_mail2,
                "producto": caso.producto,
                "provincia": caso.provincia,
                "canton": caso.canton,
                "dias_transcurridos": caso.dias_transcurridos,
                "porcentaje_avance": caso.porcentaje_avance,
                "tipo_problema": caso.tipo_problema,
                "numero_guia": caso.numero_guia,
                "codigo_provincia": caso.codigo_provincia,
                "codigo_canton": caso.codigo_canton,
                "fecha_cierre_previo": caso.fecha_cierre_previo.strftime(
                    '%Y-%m-%d %H:%M:%S') if caso.fecha_cierre_previo else None,
                "fecha_venta": caso.fecha_venta.strftime('%Y-%m-%d') if caso.fecha_venta else None,
                "es_cliente_contactado": caso.es_cliente_contactado,
            }
            casos_json.append(caso_dict)

        return jsonify(casos_json)

    except SQLAlchemyError as e:
        error_msg = "Error en la base de datos: {}".format(str(e))
        return jsonify({"error": error_msg}), 500

    except Exception as e:
        error_msg = "Error inesperado: {}".format(str(e))
        return jsonify({"error": error_msg}), 500

@bp.route('/update_status_tipo_problema', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_estado_casos():
    try:
        params = request.args.to_dict()
            #Get the one record of the subcases by their cod_problema, in this case, cod_probelma refers to cod_duracion.
        update_status = st_casos_tipo_problema.query().filter(
            st_casos_tipo_problema.empresa == 20,
            st_casos_tipo_problema.cod_comprobante == params["cod_comprobante"],
            st_casos_tipo_problema.codigo_duracion == params["cod_duracion"],
        ).first()
            #Get the records of the cases by their cod_comprobante
        update_status_st_casos_postventa = st_casos_postventa.query().filter(
            st_casos_postventa.empresa == 20,
            st_casos_postventa.cod_comprobante == params["cod_comprobante"]
        ).first()
            #Get all record of the subcases by their cod_comprobante except the case that contains the cod_duration, in this case, cod_probelma refers to cod_duracion.
        all_subcases_status = st_casos_tipo_problema.query().filter(
            st_casos_tipo_problema.empresa == 20,
            st_casos_tipo_problema.cod_comprobante == params["cod_comprobante"],
            st_casos_tipo_problema.codigo_duracion != params["cod_duracion"]
        ).all()

        all_states_are_2 = True

        if len(all_subcases_status) == 0 and params["status"] == '1':
            all_states_are_2 = False

        for status in all_subcases_status:
            if status.estado != 0 or status.estado is None or params["status"] != '0':
                all_states_are_2 = False
                break

        if update_status:
            update_status.estado = params["status"]
            number_help = update_status_st_casos_postventa.aplica_garantia
            if number_help != 1 and params["status"] == '1' and all_states_are_2 == False:
                update_status_st_casos_postventa.aplica_garantia = params["status"]
                update_status_st_casos_postventa.estado = 'P'

            elif all_states_are_2 == True and params["status"] != '2':
                 update_status_st_casos_postventa.aplica_garantia = params["status"]
                 update_status_st_casos_postventa.estado = 'C'
            db.session.commit()
            return jsonify({"message": "Estado actualizado correctamente"}), 200
        else:
            return jsonify({"error": "No se encontro los resultados"}), 500

    except SQLAlchemyError as e:
        error_msg = "Error en la base de datos: {}".format(str(e))
        return jsonify({"error": error_msg}), 500

    except Exception as e:
        error_msg = "Error inesperado: {}".format(str(e))
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@bp.route('/get_info_provinces', methods=['GET'])
@jwt_required()
@cross_origin()
def get_info_provinces():
    try:
        query_provinces = ADprovincias.query().filter(
            ADprovincias.codigo_nacion == 1
        ).all()
        data_provinces = []
        for province in query_provinces:
            province_dict = {
                "codigo_provincia": province.codigo_provincia,
                "descripcion": province.descripcion
            }
            data_provinces.append(province_dict)
        return jsonify(data_provinces)
    except SQLAlchemyError as e:
        # En caso de un error de base de datos, se puede devolver un mensaje de error apropiado
        return jsonify({"error": f"Error de base de datos al obtener información de provincias ${e} "}), 500
    except Exception as e:
        # Otros errores que no sean de base de datos pueden ser manejados aquí
        return jsonify({"error": f"Se ha producido un error al procesar la solicitud ${e}"}), 500


@bp.route('/get_info_city_by_province/<codigo_provincia>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_info_cities(codigo_provincia):
    try:
        query_cities_by_provinces = ADcantones.query().filter(
            ADcantones.codigo_provincia == codigo_provincia
        ).all()
        data_cities = []
        for city in query_cities_by_provinces:
            city_dict = {
                "codigo_ciudad": city.codigo_canton,
                "codigo_provincia": city.codigo_provincia,
                "descripcion": city.descripcion
            }
            data_cities.append(city_dict)
        return jsonify(data_cities)
    except SQLAlchemyError as e:
        # En caso de un error de base de datos, se puede devolver un mensaje de error apropiado
        return jsonify({"error": "Error de base de datos al obtener información de ciudades por provincia"}), 500
    except Exception as e:
        # Otros errores que no sean de base de datos pueden ser manejados aquí
        return jsonify({"error": "Se ha producido un error al procesar la solicitud"+e}), 500

#UPDATE_YEAR_PARTS----------------------------------------------------------------------------
@bp.route('/get_info_despiece/motos', methods=['GET'])
@jwt_required()
@cross_origin()
def get_info_despice():# Retrieve a tree view of motorcycle brands, models and subsystem
    empresa= request.args.get("empresa")
    try:
        marcas = st_despiece.query().filter(
        st_despiece.nivel == 1,
        st_despiece.cod_despiece != 'A',
        st_despiece.cod_despiece != 'U',
        st_despiece.cod_despiece != 'Q',
        st_despiece.cod_despiece != 'L',
        st_despiece.empresa      == empresa,
        ).all()
        dict_despiece = {}

        for marca in marcas:
            categorias = st_despiece.query().filter(
                st_despiece.empresa == empresa,
                st_despiece.nivel == 2,
                st_despiece.cod_despiece != 'SGN',
                st_despiece.cod_despiece != 'BGN',
                st_despiece.cod_despiece != 'SLF',
                st_despiece.cod_despiece_padre == marca.cod_despiece
            ).all()
            dict_categorias = {}

            for category in categorias:
                modelos = st_despiece.query().filter(
                st_despiece.empresa == empresa,
                st_despiece.nivel == 3,
                st_despiece.cod_despiece_padre == category.cod_despiece
                ).all()
                dict_modelos = {}

                for modelo in modelos:
                    subsistemas = st_despiece.query().filter(
                        st_despiece.empresa == empresa,
                        st_despiece.nivel == 4,
                        st_despiece.cod_despiece_padre == modelo.cod_despiece
                    ).all()
                    list_subsistemas = []
                    dict_subsistema = {}

                    for subsistema in subsistemas:
                        dict_subsistema_new = {}
                        dict_subsistema_new[subsistema.nombre_e] = subsistema.cod_despiece
                        dict_subsistema_new["id"]                = subsistema.cod_despiece
                        dict_subsistema_new["name"]              = subsistema.nombre_e

                        dict_subsistema[subsistema.nombre_e] = subsistema.cod_despiece
                        list_subsistemas.append(dict_subsistema_new)

                    dict_modelos[modelo.nombre_e] = list_subsistemas
                dict_categorias[category.nombre_e] = dict_modelos
            dict_despiece[marca.nombre_e] = dict_categorias
    except Exception as e:
        print(e)
        return jsonify({"error": "Se ha producido un error al procesar la solicitud: " + str(e)}), 500

    return jsonify(dict_despiece)

@bp.route('/get_info_despiece/parts', methods=['GET'])
@jwt_required()
@cross_origin()
def get_info_despiece_parts(): # Retrieve a tree view of motorcycle parts
    empresa = request.args.get("empresa")
    subsistema = request.args.get("subsistema")
    try:
        parts = st_producto_despiece.query().filter(
            st_producto_despiece.empresa == empresa,
            st_producto_despiece.cod_despiece==subsistema
        ).all()

        list_parts = []
        dict_parts = {}

        for part in parts:
            list_parts.append(part.cod_producto)
            names_parts = Producto.query().filter(
                Producto.cod_producto == part.cod_producto,
                Producto.empresa == empresa
            ).all()
            for name in names_parts:
                dict_parts[part.cod_producto] = name.nombre
        return jsonify(dict_parts), 200

    except Exception as e:
        return jsonify({"error": "Se ha producido un error al procesar la solicitud: " +str(e)}), 500

@bp.route('/update_year_parts', methods=['PUT'])
@jwt_required()
@cross_origin()
def udpateYearParts():#Function to update the year data fora model, a subsystem, and a single motorcycle part
    try:
        from_year = request.args.get('from_year')
        to_year = request.args.get('to_year')
        flag_id_level = request.args.get('flag_id_level')
        empresa = request.args.get("empresa")
        empresa = int(empresa)
        flag_id_level = int(flag_id_level)
        data_subsystem = request.json
        user_shineray = request.args.get('user_shineray')

        # Imprimir las variables
        #print(f"from_year: {from_year}")
        #print(f"to_year: {to_year}")
        #print(f"flag_id_level: {flag_id_level}")
        #print(f"data_subsystem: {data_subsystem}")
        if flag_id_level == 1:
            code_subsystem = data_subsystem['cod_subsystem']
            for code in code_subsystem:
                parts = st_producto_despiece.query().filter(
                    st_producto_despiece.empresa == empresa,
                    st_producto_despiece.cod_despiece == code
                ).all()
                for part in parts:
                    existing_register = st_producto_rep_anio.query().filter(
                        st_producto_rep_anio.empresa == empresa,
                        st_producto_rep_anio.cod_producto == part.cod_producto
                    ).first()
                    if existing_register:
                        existing_register.anio_desde = from_year
                        existing_register.anio_hasta = to_year
                        existing_register.usuario_modifica = user_shineray
                        existing_register.fecha_modificacion = datetime.now()
                    else:
                        new_register_anio= st_producto_rep_anio(
                            empresa         =   empresa,
                            anio_desde      =   from_year,
                            anio_hasta      =   to_year,
                             cod_producto   =   part.cod_producto,
                            usuario_crea    =   user_shineray,
                            fecha_crea      =   datetime.now()
                        )
                        db.session.add(new_register_anio)
            db.session.commit()
            return jsonify({"succes": "Años actualizados correctamente"}), 200
        if flag_id_level == 2:
            code_products = data_subsystem['cod_producto']
            for part in code_products:
                existing_register = st_producto_rep_anio.query().filter(
                    st_producto_rep_anio.empresa == empresa,
                    st_producto_rep_anio.cod_producto == part
                ).first()
                if existing_register:
                    existing_register.anio_desde = from_year
                    existing_register.anio_hasta = to_year
                    existing_register.usuario_modifica = user_shineray
                    existing_register.fecha_modificacion = datetime.now()
                else:
                    new_register_anio = st_producto_rep_anio(
                        empresa=empresa,
                        anio_desde=from_year,
                        anio_hasta=to_year,
                        cod_producto=part,
                        usuario_crea=user_shineray,
                        fecha_crea=datetime.now()
                    )
                    db.session.add(new_register_anio)
            db.session.commit()
            return jsonify({"succes": "Años actualizados correctamente"}), 200

    except Exception as e:
        return jsonify({"error":"Error en el proceso: "+str(e)}), 500

@bp.route('/get_info_parts_year_by_cod_producto', methods = ['GET'])
@jwt_required()
@cross_origin()
def get_info_year(): #function to get year about a specific  motorcycle part
    try:
        empresa = request.args.get("empresa")
        empresa = int(empresa)
        cod_producto = request.args.get("cod_producto")
        year_parts = st_producto_rep_anio.query().filter(
            st_producto_rep_anio.empresa == empresa,
            st_producto_rep_anio.cod_producto == cod_producto
        ).first()
        dict = {}
        if year_parts is not None:
            if hasattr(year_parts, 'anio_desde'):
                dict["from"] = year_parts.anio_desde

            if hasattr(year_parts, 'anio_hasta'):
                dict["to"] = year_parts.anio_hasta
        return jsonify(dict), 200

    except Exception as e:
        return jsonify({"error": "Se ha producido un error al procesar la solicitud: " +str(e)}), 500

#ECOMMERCE INVOICE---------------------------------------------------------------------------------------

#-----------------EN DESARROLLO--------------------------->
@bp.route('/post_invoice_ecommerce', methods=['POST'])
@jwt_required()
@cross_origin()
def post_invoice_ecommerce():
    try:
        #--------------------Parametros Iniciales----------------------
        p_cod_empresa = 20
        p_cod_agencia = 18
        p_cod_tipo_comprobante_pr = 'PR'
        p_fecha = datetime.today()

        #-------------------Conexion base de Datos-------------------
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        #-----------------COMPROBACION DE LIQUIDACION--------------------
        cod_liquidacion = get_cod_liquidacion(p_cod_empresa, p_cod_agencia, p_fecha, db)
        if cod_liquidacion["success"] == False:
             raise ValueError('Error en la liquidacion')

        #-------------COMPROBACION DE COMPRAS ECOMMERCE-----------------------
        query = """
                    SELECT * FROM ST_CAB_DATAFAST WHERE COD_COMPROBANTE IS NULL
                """
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        cases = []

        #---------------------INGRESO DE CASOS QUE NO ESTEN FACTURADOS--------------------------------
        for row in records:
            cases.append(dict(zip(columns, row)))
        cursor.close()
        db.close()
        resultados = []

        #---------------------FACTURAR Y DESPACHAR------------------------------------------------------
        for i, case in enumerate(cases, start=1):
            resultado = post_invoice_ecommerce_one(case, cod_liquidacion)
            resultados.append({f"case{i}": resultado})

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": "Se ha producido un error al procesar la solicitud: " +str(e)}), 500
def post_invoice_ecommerce_one(datafast_case, cod_liquidacion):
    try:
#-----------------------------Parametros Iniciales------------------------------------------
        p_cod_empresa = 20
        p_cod_agencia = 18
        p_cod_politica = 4
        p_fecha = datetime.today()
        p_cod_tipo_comprobante_pr = 'PR'
        cod_persona_age = '001076'
        #p_cod_producto = 'R200-181610GRI'
        monto_total = round(float(datafast_case["TOTAL"]), 2)

#----------------------------Conexion Base de datos-------------------------------------------
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        id_transaction = datafast_case["ID_TRANSACTION"]
#-----------------------------------------------------------------------------------------
        cod_productos_data_fast = get_details_by_id_transaction(id_transaction,db)


#----------------------------Comprobacion de stock y lotes----------------------------------------------
        dict_lotes = {}
        for cod_producto_data_fast in cod_productos_data_fast:
            result_lote = get_lote_list(p_cod_empresa, p_cod_agencia, cod_producto_data_fast["code"], db)
            if isinstance(result_lote, list) and len(result_lote) > 0 and cod_producto_data_fast["quantity"]<=result_lote[0]['cantidad'] :
                dict_lotes[cod_producto_data_fast["code"]] = result_lote[0]['lote']
            else:
                raise ValueError(f' No hay suficiente existencia Lote: {str(cod_producto_data_fast["code"])}')

        cod_comprobante = get_cod_comprobante(p_cod_empresa, p_cod_agencia, p_cod_tipo_comprobante_pr, db)

#--------------------------------COMPROBACION DE LOS PRECIOS-------------------------------------------------------
        politica = get_politica_credito_ecommerce(db, p_cod_politica)
        prices_dict = {}
        for p_cod_producto in dict_lotes.keys():
            price = get_price_of_parts_ecommerce(p_cod_producto, db, p_cod_agencia)
            prices_dict[p_cod_producto] = round(price*politica, 2)
        iva = get_iva_porcent(db)
        base_imponible = round(float(datafast_case["SUB_TOTAL"]), 2)

        #print(cod_productos_data_fast)
        #print(prices_dict)
        #print(dict_lotes)
#----------------------------------------INGRESO DE 1 CASO ST_PROFORMA---------------------------------------
        insert_st_proforma_ecommerce(p_cod_empresa, cod_comprobante, datafast_case, db, p_cod_politica, base_imponible, iva, monto_total, p_cod_agencia, cod_liquidacion,p_fecha, p_cod_tipo_comprobante_pr, cod_persona_age, politica)

#----------------------------------------INGRESO_CASOS_PRODUCTOS---------------------------------------------
        secuencia = 1
        for cod_producto in cod_productos_data_fast:
            insert_st_proforma_movimiento(db, cod_comprobante, p_cod_tipo_comprobante_pr, p_cod_empresa, cod_producto, secuencia, iva, dict_lotes, p_fecha, politica  )
            secuencia += 1

        #print(insert_st_proforma_succes )
        #raise ValueError("Se ha forzado una excepción debido a una condición específica")
        db.commit()
        db.close()
        print(cod_comprobante)
        return id_transaction

    except Exception as e:
        if db:
            db.rollback()
            error_message = f"error: se ha producido un error, details: {str(e)}"
        return error_message
def get_cod_comprobante(p_cod_empresa, p_cod_agencia, p_cod_tipo_comprobante_pr,db):
    try:
        cursor = db.cursor()
        result = cursor.var(cx_Oracle.STRING)
        cursor.execute("""
                    BEGIN
                      :result := contabilidad.kc_orden.asigna_cod_comprobante(p_cod_empresa => :p_cod_empresa,
                                                                              p_cod_tipo_comprobante => :p_cod_tipo_comprobante,
                                                                              p_cod_agencia => :p_cod_agencia);
                    END;
                """, result=result, p_cod_empresa=p_cod_empresa, p_cod_tipo_comprobante=p_cod_tipo_comprobante_pr,
                       p_cod_agencia=p_cod_agencia)
        cod_comprobante = result.getvalue()
        cursor.close()
        return {"success":True, "value":cod_comprobante}
    except Exception as e:
        return f"Unexpected error: {str(e)}"
def get_lote_list(p_cod_empresa, p_cod_agencia, p_cod_producto, db):
    try:
        cursor = db.cursor()
        query = """
            SELECT a.cod_comprobante lote, a.fecha, a.descripcion, a.tipo_comprobante tipo, x.cantidad
            FROM st_lote a,
                 st_inventario_lote x
            WHERE a.empresa = :p_cod_empresa
              AND x.empresa = a.empresa
              AND x.tipo_comprobante_lote = a.tipo_comprobante
              AND x.cod_comprobante_lote = a.cod_comprobante
              AND x.cod_bodega = :p_cod_agencia
              AND x.cod_producto = :p_cod_producto
              AND x.cod_aamm = 0
              AND x.cantidad > 0
              AND x.cod_tipo_inventario = 1
            ORDER BY a.fecha
        """
        cursor.execute(query, p_cod_empresa=p_cod_empresa, p_cod_agencia=p_cod_agencia, p_cod_producto=p_cod_producto)
        rows = cursor.fetchall()
        lote_list = []
        for row in rows:
            lote_list.append({
                'lote': row[0],
                'fecha': row[1],
                'descripcion': row[2],
                'tipo': row[3],
                'cantidad': row[4]
            })
        cursor.close()
        return lote_list
    except Exception as e:
        return None
def get_cod_liquidacion(p_cod_empresa, p_cod_agencia, p_fecha, db):
    try:
        # Conexión a la base de datos
        cursor = db.cursor()

        # Variable para almacenar el resultado
        result = cursor.var(cx_Oracle.STRING)

        # Ejecución del procedimiento PL/SQL
        cursor.execute("""
                        begin
                        :result := ks_liquidacion.consulta_cod_liquidacion(p_cod_empresa => :p_cod_empresa,
                                                     p_cod_agencia => :p_cod_agencia,
                                                     p_fecha => :p_fecha);
                        end;

                """, result=result, p_cod_empresa=p_cod_empresa, p_cod_agencia=p_cod_agencia, p_fecha=p_fecha)

        # Obtener el valor del resultado
        cod_liquidacion = result.getvalue()
        # Cerrar el cursor y la conexión
        cursor.close()
        return {"success": True, "value": cod_liquidacion}
    except Exception as e:
        return {"success": False, "error": str(e)}
def get_details_by_id_transaction(id_transaction, db):
    try:
        cursor = db.cursor()
        sql = """
        SELECT cod_producto, quantity, price
        FROM ST_DET_DATAFAST
        WHERE id_transaction = :id_transaction
        """
        cursor.execute(sql, {'id_transaction': id_transaction})
        rows = cursor.fetchall()
        cursor.close()
        # Convertir los resultados a una lista de diccionarios
        results = [{'code': row[0], 'quantity': row[1], 'price': row[2]} for row in rows]

        return results
    except Exception as e:
        return  str(e)
def get_price_of_parts_ecommerce(p_cod_producto,db, p_cod_agencia):
    try:
        cursor = db.cursor()
        sql = """
        SELECT 
            L.PRECIO
        FROM 
            PRODUCTO P
        JOIN 
            ST_LISTA_PRECIO L 
        ON 
                L.COD_PRODUCTO = :p_cod_producto
                AND P.COD_PRODUCTO=  :p_cod_producto
                AND L.COD_AGENCIA = :p_cod_agencia
                AND L.COD_UNIDAD = P.COD_UNIDAD
                AND L.COD_FORMA_PAGO = 'EFE'
                AND L.COD_DIVISA = 'DOLARES'
                AND L.COD_MODELO_CLI = 'CLI1'
                AND L.COD_ITEM_CLI = 'CF'
                AND L.ESTADO_GENERACION = 'R'
                AND (L.FECHA_FINAL IS NULL OR L.FECHA_FINAL >= TRUNC(SYSDATE))
                JOIN 
                PRODUCTO D
                ON 
                P.EMPRESA = D.EMPRESA
                AND D.COD_PRODUCTO = P.COD_PRODUCTO
            """
        cursor.execute(sql, {'p_cod_producto': p_cod_producto, 'p_cod_agencia': p_cod_agencia})
        rows = cursor.fetchone()
        cursor.close()
        precio = rows[0]
        return precio
    except Exception as e:
        return str(e)
def get_iva_porcent(db):
    try:
        cursor = db.cursor()
        sql = """ 
                select iva from empresa a
                where a.empresa=20
            """
        cursor.execute(sql)
        rows = cursor.fetchone()
        cursor.close()
        iva = rows[0]
        return iva
    except Exception as e:
        return str(e)
def insert_st_proforma_ecommerce(p_cod_empresa, cod_comprobante, datafast_case, db, p_cod_politica, base_imponible, iva, monto_total, p_cod_agencia, cod_liquidacion,p_fecha, p_cod_tipo_comprobante_pr, cod_persona_age, politica):
    try:
        # Definiendo las variables necesarias
        cod_politica = p_cod_politica
        cod_forma_pago = 'TCR'
        cod_persona_age = cod_persona_age
        comprobante_manual = '0'
        cod_persona = datafast_case['CLIENT_ID'][:-1] + '-' + datafast_case['CLIENT_ID'][-1]
        cod_comprobante = cod_comprobante['value']
        cod_estado_producto = 'A'
        es_facturado = 0
        tipo_comprobante = p_cod_tipo_comprobante_pr
        cod_divisa = 'DOLARES'
        cod_tipo_identificacion = 1
        cod_tipo_persona = 'CLI'
        cod_tipo_persona_age = 'VEN'
        cod_tipo_persona_gar = 'CLI'
        num_cuotas = 0
        num_cuotas_gratis = 0
        dias_validez = 8
        entrada = 0
        otros = 0
        descuento = 0
        iva_pedido = round((monto_total)*(iva/(100+iva)), 2)
        financiamiento = 0
        valor = monto_total
        es_anulado = 0
        es_invalido = 0
        es_aprobado = 1
        useridc = 'DTP'
        descuento_usuario = 0
        useridc_autoriza_descuento = 'DTP'
        cod_bodega_egreso = p_cod_agencia
        cantidad_mov_completo = 0
        por_intereses = 0.0
        rebate = 0.0
        base_excenta = 0.0
        cod_tipo_comprobante_ref = 'A0'
        fecha_sol_ver_telefonica = p_fecha
        es_banco = 0
        ice = 0
        tipo_comprobante_factura = 'A0'
        cursor = db.cursor()

        sql = """
        INSERT INTO ST_PROFORMA (
            EMPRESA, COD_COMPROBANTE, TIPO_COMPROBANTE, COD_FORMA_PAGO, COD_AGENCIA, COMPROBANTE_MANUAL, 
            COD_DIVISA, COD_TIPO_IDENTIFICACION, COD_TIPO_PERSONA, COD_PERSONA, 
            COD_TIPO_PERSONA_AGE, COD_PERSONA_AGE, COD_TIPO_PERSONA_GAR, 
            NUM_CUOTAS, NUM_CUOTAS_GRATIS, DIAS_VALIDEZ, ENTRADA, OTROS, DESCUENTO, 
            IVA, FINANCIAMIENTO, VALOR, ES_ANULADO, ES_INVALIDO, ES_FACTURADO, ES_APROBADO, 
            USERIDC, DESCUENTO_USUARIO, USERIDC_AUTORIZA_DESCUENTO, COD_BODEGA_EGRESO, 
            CANTIDAD_MOV_COMPLETO, POR_INTERES, BASE_IMPONIBLE, BASE_EXCENTA, 
            COD_TIPO_COMPROBANTE_REF, FECHA_SOL_VER_TELEFONICA, ES_BANCO, ICE, COD_LIQUIDACION, COD_POLITICA, REBATE, TIPO_COMPROBANTE_FACTURA
        ) VALUES (
            :EMPRESA, :COD_COMPROBANTE, :TIPO_COMPROBANTE, :COD_FORMA_PAGO,:COD_AGENCIA, :COMPROBANTE_MANUAL, 
            :COD_DIVISA, :COD_TIPO_IDENTIFICACION, :COD_TIPO_PERSONA, :COD_PERSONA, 
            :COD_TIPO_PERSONA_AGE, :COD_PERSONA_AGE, :COD_TIPO_PERSONA_GAR, 
            :NUM_CUOTAS, :NUM_CUOTAS_GRATIS, :DIAS_VALIDEZ, :ENTRADA, :OTROS, :DESCUENTO, 
            :IVA, :FINANCIAMIENTO, :VALOR, :ES_ANULADO, :ES_INVALIDO, :ES_FACTURADO, :ES_APROBADO, 
            :USERIDC, :DESCUENTO_USUARIO, :USERIDC_AUTORIZA_DESCUENTO, :COD_BODEGA_EGRESO, 
            :CANTIDAD_MOV_COMPLETO, :POR_INTERES, :BASE_IMPONIBLE, :BASE_EXCENTA, 
            :COD_TIPO_COMPROBANTE_REF, :FECHA_SOL_VER_TELEFONICA, :ES_BANCO, :ICE, :COD_LIQUIDACION, :COD_POLITICA, :REBATE, :TIPO_COMPROBANTE_FACTURA
        )
        """

        cursor.execute(sql, {
            'EMPRESA': p_cod_empresa, 'COD_COMPROBANTE': cod_comprobante, 'TIPO_COMPROBANTE': tipo_comprobante,
             'COD_AGENCIA':p_cod_agencia, 'COD_FORMA_PAGO': cod_forma_pago, 'COMPROBANTE_MANUAL': comprobante_manual,
            'COD_DIVISA': cod_divisa, 'COD_TIPO_IDENTIFICACION': cod_tipo_identificacion,
            'COD_TIPO_PERSONA': cod_tipo_persona, 'COD_PERSONA': cod_persona,
            'COD_TIPO_PERSONA_AGE': cod_tipo_persona_age, 'COD_PERSONA_AGE': cod_persona_age,
            'COD_TIPO_PERSONA_GAR': cod_tipo_persona_gar, 'NUM_CUOTAS': num_cuotas,
            'NUM_CUOTAS_GRATIS': num_cuotas_gratis, 'DIAS_VALIDEZ': dias_validez,
            'ENTRADA': entrada, 'OTROS': otros, 'DESCUENTO': descuento, 'IVA': iva_pedido,
            'FINANCIAMIENTO': financiamiento, 'VALOR': valor, 'ES_ANULADO': es_anulado,
            'ES_INVALIDO': es_invalido, 'ES_FACTURADO': es_facturado, 'ES_APROBADO': es_aprobado,
            'USERIDC': useridc, 'DESCUENTO_USUARIO': descuento_usuario,
            'USERIDC_AUTORIZA_DESCUENTO': useridc_autoriza_descuento, 'COD_BODEGA_EGRESO': cod_bodega_egreso,
            'CANTIDAD_MOV_COMPLETO': cantidad_mov_completo, 'POR_INTERES': por_intereses,
            'BASE_IMPONIBLE': base_imponible, 'BASE_EXCENTA': base_excenta,
            'COD_TIPO_COMPROBANTE_REF': cod_tipo_comprobante_ref, 'FECHA_SOL_VER_TELEFONICA': fecha_sol_ver_telefonica,
            'ES_BANCO': es_banco, 'ICE': ice, 'COD_LIQUIDACION': cod_liquidacion['value'], 'COD_POLITICA': cod_politica,'REBATE': rebate, 'TIPO_COMPROBANTE_FACTURA': tipo_comprobante_factura
        })

        db.commit()
        cursor.close()
        success = 'true'
        print(cod_comprobante)
        print(success)

        return True
    except Exception as e:
        print(str(e))
        if db:
            db.rollback()
        success = 'false'
        return False
def insert_st_proforma_movimiento(db, cod_comprobante, p_cod_tipo_comprobante_pr, p_cod_empresa, cod_producto, secuencia, iva, dict_lotes, p_fecha,  politica ):
    cod_unidad = 'U'
    es_serie = 0
    cod_estado_producto = 'A'
    cantidad = 1.00
    cantidad_serie = 0
    costo = 0.0
    precio_lista = round(cod_producto['price']/politica, 2)    #PRECIO SIN RECARGO DE TARJETA
    descuento = 0.0
    financiamiento = 0.0
    valor = cod_producto['price']     #precio*1.0224 #PRECIO FINAL CON REGARGO TARJETA
    iva = round(cod_producto['price']*(iva/(100+iva)), 2)
    rebate = 0.0
    por_descuento = 0.0
    es_iva = 1
    aplica_promocion = 0
    ice = 0.0
    tipo_comprobante_lote ='LT'
    cod_porcentaje_iva = 4
    cod_comprobante_lote = dict_lotes[cod_producto['code']]
    cod_comprobante = cod_comprobante['value']
    cod_producto    = cod_producto['code']

    try:
        cursor = db.cursor()

        sql = """
        INSERT INTO ST_PROFORMA_MOVIMIENTO (
            cod_comprobante, tipo_comprobante, empresa, secuencia, 
            cod_producto, cod_unidad, es_serie, cod_estado_producto, 
            cantidad, cantidad_serie, precio_lista, costo, precio, 
            descuento, iva, financiamiento, valor, rebate, por_descuento, 
            es_iva, aplica_promocion, ice, tipo_comprobante_lote, 
            cod_comprobante_lote, cod_porcentaje_iva
        ) VALUES (
            :cod_comprobante, :tipo_comprobante, :empresa, :secuencia, 
            :cod_producto, :cod_unidad, :es_serie, :cod_estado_producto, 
            :cantidad, :cantidad_serie, :precio_lista, :costo, :precio, 
            :descuento, :iva, :financiamiento, :valor, :rebate, :por_descuento, 
            :es_iva, :aplica_promocion, :ice, :tipo_comprobante_lote, 
            :cod_comprobante_lote, :cod_porcentaje_iva
        )
        """

        cursor.execute(sql, {
            'cod_comprobante': cod_comprobante,
            'tipo_comprobante': p_cod_tipo_comprobante_pr,
            'empresa': p_cod_empresa,
            'secuencia': secuencia,
            'cod_producto': cod_producto,
            'cod_unidad': cod_unidad,
            'es_serie': es_serie,
            'cod_estado_producto': cod_estado_producto,
            'cantidad': cantidad,
            'cantidad_serie': cantidad_serie,
            'precio_lista': precio_lista,
            'costo': costo,
            'precio': precio_lista,
            'descuento': descuento,
            'iva': iva,
            'financiamiento': financiamiento,
            'valor': valor,
            'rebate': rebate,
            'por_descuento': por_descuento,
            'es_iva': es_iva,
            'aplica_promocion': aplica_promocion,
            'ice': ice,
            'tipo_comprobante_lote': tipo_comprobante_lote,
            'cod_comprobante_lote': cod_comprobante_lote,
            'cod_porcentaje_iva': cod_porcentaje_iva
        })

        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(str(e))
        if db:
            db.rollback()
        return False
def get_politica_credito_ecommerce(db, p_cod_politica):
    try:
        # Establece la conexión
        cursor = db.cursor()
        # Define y ejecuta la consulta SQL
        sql = """
                select factor_credito from st_politica_credito_d a
                where a.num_cuotas=0
                and   a.cod_politica=:p_cod_politica
        """
        cursor.execute(sql, {'p_cod_politica': p_cod_politica})
        rules_politica = cursor.fetchone()
        if rules_politica:
            result = rules_politica[0]
        else:
            # Si no hay resultado, asigna un valor por defecto o maneja el caso adecuadamente
            result = None
        return result
    except cx_Oracle.DatabaseError as e:
        print(f"Error de base de datos: {e}")
    finally:
        # Asegúrate de cerrar el cursor y la conexión
        if cursor:
            cursor.close()
#--------------------------------
@bp.route('/get_invoice_ecommerce', methods = ['GET'])
@jwt_required()
@cross_origin()
def get_sell_ecommerce():
    try:
        filtros_params = request.args.to_dict()
        option = filtros_params.get('pay_method').upper()  # Opción para elegir la tabla
        invoiced = int(filtros_params.get('invoiced'))

        start_date = datetime.strptime(filtros_params['start_date'],
                                       '%d/%m/%Y') if 'start_date' in filtros_params else None

        finish_date = datetime.strptime(filtros_params['finish_date'],
                                        '%d/%m/%Y') if 'finish_date' in filtros_params else None
        # Aumentar un día
        if finish_date:
            finish_date += timedelta(days=1)
        if start_date:
            start_date -= timedelta(days=1)

        if option == 'DATAFAST' and invoiced == 1:
            results = st_cab_datafast.query().filter(st_cab_datafast.empresa == 20,
            st_cab_datafast.cod_comprobante.isnot(None))
            model_class = st_cab_datafast

        elif option == 'DEUNA' and invoiced == 1:
            results = st_cab_deuna.query().filter(st_cab_deuna.empresa == 20,
            st_cab_deuna.cod_comprobante.isnot(None))
            model_class = st_cab_deuna

        elif option == 'DATAFAST' and invoiced == 0:
            results = st_cab_datafast.query().filter(st_cab_datafast.empresa == 20,
            st_cab_datafast.cod_comprobante == None)
            model_class = st_cab_datafast

        elif option == 'DEUNA' and invoiced == 0:
            results = st_cab_deuna.query().filter(st_cab_deuna.empresa == 20,
            st_cab_deuna.cod_comprobante == None)
            model_class = st_cab_deuna

        else:
            return jsonify({"error": "Invalid option"}), 400

        # Filtrar por rango de fechas
        if start_date is not None and finish_date is not None:
            results = results.filter(model_class.fecha.between(start_date, finish_date))

        # Obtener todos los resultados
        results = results.all()

        results_list = []
        if not results:
            return jsonify(results_list), 200

        for result in results:
            result_data = {
                "empresa": result.empresa,
                "id_transaction": result.id_transaction,
                "total": result.total,
                "sub_total": result.sub_total,
                "discount_percentage": result.discount_percentage,
                "discount_amount": result.discount_amount,
                "currency": result.currency,
                "id_guia_servientrega": result.id_guia_servientrega,
                "client_type_id": result.client_type_id,
                "client_name": result.client_name,
                "client_last_name": result.client_last_name,
                "client_id": result.client_id,
                "client_address": result.client_address,
                "cod_orden_ecommerce": result.cod_orden_ecommerce,
                "cod_comprobante": result.cod_comprobante,
                "fecha": result.fecha.strftime('%d/%m/%Y'),
                "shiping_discount": result.shiping_discount
            }
            if option == 'DATAFAST':
                result_data.update({
                    "payment_type": result.payment_type,
                    "payment_brand": result.payment_brand,
                    "batch_no": result.batch_no,
                    "card_type": result.card_type,
                    "bin_card": result.bin_card,
                    "last_4_digits": result.last_4_digits,
                    "holder": result.holder,
                    "expiry_month": result.expiry_month,
                    "expiry_year": result.expiry_year,
                    "acquirer_code": result.acquirer_code,
                    "cost_shiping": result.cost_shiping_calculate,
                    "shiping_discount": result.shiping_discount,
                })
            if option == 'DEUNA':
                result_data.update({
                        "cost_shiping": result.cost_shiping,
                    })

            results_list.append(result_data)

        return jsonify(results_list), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@bp.route('/buy_parts_ecommerce/<id_code>', methods=['GET'])
@jwt_required()
@cross_origin()
def buy_parts_ecommerce(id_code):
    try:
        option = request.args.get('pay_method').upper()
        if option == 'DATAFAST':
            cases = st_det_datafast.query().filter(
                st_det_datafast.id_transaction == id_code,
                st_det_datafast.empresa == 20
            ).all()
        elif option == 'DEUNA':
            cases = st_det_deuna.query().filter(
                st_det_deuna.id_transaction == id_code,
                st_det_deuna.empresa == 20
            ).all()
        else:
            return jsonify({"error": "Invalid option"}), 400

        cases_json = []
        for case in cases:
            case_dict = {
                "codigo": case.cod_producto,
                "precio": case.price,
                "cantidad": case.quantity
            }
            cases_json.append(case_dict)

        return jsonify(cases_json), 200

    except Exception as e:
        print(e)
        error_msg = "An error occurred while processing the request."
        return jsonify({"error": error_msg, "details": str(e)}), 500

@bp.route('/get_methods_payment_ecommerce', methods=['GET'])
@jwt_required()
@cross_origin()
def get_ecommerce_payment_method():
    try:
        methods_payment = st_metodos_de_pago_ecommerce.query().filter(
            st_metodos_de_pago_ecommerce.empresa == 20
        ).all()
        methods = []
        print(methods_payment)
        for method in methods_payment:
            dict = {
                "metodo de pago": method.nombre,
                "metodo_info_fac": method.tipo_facturacion
            }
            methods.append(dict)

        return jsonify(methods), 200

    except Exception as e:
        error_msg = "An error occurred while processing the request."
        return jsonify({"error": error_msg, "details": str(e)}), 500

@bp.route('/post_cod_comprobante_ecommerce', methods=['POST'])
@jwt_required()
@cross_origin()
def post_cod_comprobante_ecommerce():
    try:
        pay_method = request.args.get("pay_method")
        pay_id = request.args.get("pay_id")
        cod_comprobante = request.args.get("cod_comprobante")

        if not pay_method or not pay_id or not cod_comprobante:
            return jsonify({"error": "Missing parameters"}), 400
        if pay_method == 'datafast':
            model = st_cab_datafast
        elif pay_method == 'deuna':
            model = st_cab_deuna
        else:
            return jsonify({"error": "Invalid pay_method"}), 400
            # Busca el registro por id_transaction
        try:
            record = model.query().filter_by(id_transaction=pay_id).one()
        except Exception as e:
            return jsonify({"error": "Transaction not found"}), 404
        record.cod_comprobante = cod_comprobante
        db.session.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        db.session.rollback()  # Revierte los cambios en caso de error
        error_msg = "An error occurred while processing the request."
        return jsonify({"error": error_msg, "details": str(e)}), 500

@bp.route('/post_change_price_ecommerce', methods=['POST'])
@jwt_required()
@cross_origin()
def post_change_price_ecommerce():
    try:
        p_cod_empresa = 20
        p_cod_agencia = 50
        p_user = 'stock'
        p_tipo_generacion = 'VF'
        p_useridc = 'st'

        # Obtén los parámetros de la solicitud
        cod_producto = "YSLZCT1001"
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        price = request.args.get("price")
        p_cod_politica = 48
        politica = get_politica_credito_ecommerce(db1, p_cod_politica)
        price = round(float(price) / politica, 2)
        if not cod_producto or not price:
            return jsonify({"error": "Missing cod_producto or price"}), 400
        # search producto code
        producto = Producto.query().filter_by(cod_producto=cod_producto).first()

        if producto:
            # Actualiza el precio del producto
            producto.precio = price
            result = generar_listas_de_precio(p_cod_empresa, p_user, p_tipo_generacion, p_useridc, db1)

            db.session.commit()  # Guarda los cambios en la base de datos
            secuencia = result["p_secuencia"]
            print(secuencia)
            status_inset = insert_precios_ecommerce(p_cod_empresa, p_cod_agencia, price, secuencia)
            print(status_inset)
            return jsonify({"status": "ok", "message": "Price updated successfully"})

        else:
            return jsonify({"error": "Product not found"}), 404

    except SQLAlchemyError as e:
        db.session.rollback()  # Revierte los cambios en caso de error
        error_msg = "An error occurred while processing the request."
        return jsonify({"error": error_msg, "details": str(e)}), 500
def generar_listas_de_precio(p_cod_empresa, p_user, p_tipo_generacion, p_useridc, db1):
    try:
        # Conexión a la base de datos
        cursor = db1.cursor()
        # Variable para almacenar el resultado de salida
        p_secuencia = cursor.var(cx_Oracle.NUMBER)
        # Ejecución del procedimiento PL/SQL
        cursor.execute("""
                        begin
                        ks_lista_precio.generar_listas_de_precio(p_cod_empresa => :p_cod_empresa,
                                                                p_user => :p_user,
                                                                p_tipo_generacion => :p_tipo_generacion,
                                                                p_useridc => :p_useridc,
                                                                p_fecha_inicio => '',
                                                                p_fecha_final => '',
                                                                p_precio => '',
                                                                p_observaciones => '',
                                                                p_secuencia => :p_secuencia);
                        end;
                """, p_cod_empresa=p_cod_empresa, p_user=p_user, p_tipo_generacion=p_tipo_generacion, p_useridc=p_useridc, p_secuencia=p_secuencia)

        #Obtener el valor del parámetro de salida
        secuencia = p_secuencia.getvalue()

        #Cerrar el cursor y la conexión
        cursor.close()
        return {"success": True, "p_secuencia": secuencia}
    except Exception as e:
        return {"success": False, "error": str(e)}

def insert_precios_ecommerce(p_cod_empresa, p_cod_agencia, price, secuencia):
    try:
        # Define the records with the current date and time
        current_datetime = datetime.now()
        print(current_datetime)

        current_datetime_without_hours = current_datetime.date()
        print(current_datetime_without_hours)

        records = [
            (p_cod_empresa, 'YSLZCT1001', 'CLI1', 'CF', 'REG1', 'COS', p_cod_agencia, 'U', 'EFE', 'DOLARES', 'R', current_datetime_without_hours, None, price, None, 0, price, 0, 'JPJ', secuencia, 'N', None, None, current_datetime, 'JPALAGUACHI', 'TS1PROD'),
            (p_cod_empresa, 'YSLZCT1001', 'CLI1', 'CF', 'REG1', 'COS', p_cod_agencia, 'U', 'TCR', 'DOLARES', 'R', current_datetime_without_hours, None, price, None, 0, price, 0, 'JPJ', secuencia, 'N', None, None, current_datetime, 'JPALAGUACHI', 'TS1PROD'),
            (p_cod_empresa, 'YSLZCT1001', 'CLI1', 'TA', 'REG1', 'COS', p_cod_agencia, 'U', 'EFE', 'DOLARES', 'R', current_datetime_without_hours, None, price, None, 0, price, 0, 'JPJ', secuencia, 'N', None, None, current_datetime, 'JPALAGUACHI', 'TS1PROD'),
            (p_cod_empresa, 'YSLZCT1001', 'CLI1', 'TA', 'REG1', 'COS', p_cod_agencia, 'U', 'TCR', 'DOLARES', 'R', current_datetime_without_hours, None, price, None, 0, price, 0, 'JPJ', secuencia, 'N', None, None, current_datetime, 'JPALAGUACHI', 'TS1PROD')
        ]

        # Insert the records
        for record in records:
            new_entry = st_lista_precio(
                empresa=record[0], cod_producto=record[1], cod_modelo_cli=record[2], cod_item_cli=record[3],
                cod_modelo_zona=record[4], cod_item_zona=record[5], cod_agencia=record[6], cod_unidad=record[7],
                cod_forma_pago=record[8], cod_divisa=record[9], estado_generacion=record[10], fecha_inicio=record[11],
                fecha_final=record[12], valor=record[13], iva=record[14], ice=record[15], precio=record[16],
                cargos=record[17], useridc=record[18], secuencia_generacion=record[19], estado_vida=record[20],
                valor_alterno=record[21], rebate=record[22], aud_fecha=record[23], aud_usuario=record[24],
                aud_terminal=record[25]
            )
            session.add(new_entry)

        # Commit the session
        session.commit()
        return {"success": True}
    except Exception as e:
        # Handle the exception and rollback the session
        session.rollback()
        return {"success": False, "error": str(e)}