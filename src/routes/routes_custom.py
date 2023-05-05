from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.proveedores import Proveedor, TgModeloItem
from src.models.tipo_comprobante import TipoComprobante
from src.models.producto_despiece import StProductoDespiece
from src.models.despiece import StDespiece

bpcustom = Blueprint('routes_custom', __name__)

#CONSULTAS GET CON PARAMETROS

@bpcustom.route('/productos_param') #sw para mostrar los productos por parametros
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

