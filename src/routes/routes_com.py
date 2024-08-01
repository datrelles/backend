from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.proveedores import Proveedor
from src.models.clientes import Cliente
from src.models.asignacion_cupo import StAsignacionCupo
from src.models.productos import Producto
from sqlalchemy import and_, or_, func, tuple_
from src.routes.routes import obtener_secuencia_pagos
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import datetime
import re
from decimal import Decimal
from datetime import datetime, date
import xlrd
from src import oracle
from os import getenv
import cx_Oracle
from src.config.database import db, engine, session

bpcom = Blueprint('routes_com', __name__)

logger = logging.getLogger(__name__)

@bpcom.route('/asig', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_asignacion():
    data = request.get_json()
    empresa = data['empresa']
    ruc_cliente = data.get('ruc_cliente')
    cod_producto = data.get('cod_producto')

    query = db.session.query(
        StAsignacionCupo.empresa,
        StAsignacionCupo.ruc_cliente,
        StAsignacionCupo.cod_producto,
        StAsignacionCupo.porcentaje_maximo,
        StAsignacionCupo.cantidad_minima,
        Producto.nombre.label("producto"),
        Cliente.apellido1.label("cliente")
    ).filter(
        StAsignacionCupo.empresa == empresa
    )

    if ruc_cliente:
        query = query.filter(StAsignacionCupo.ruc_cliente == ruc_cliente)

    if cod_producto:
        query = query.filter(StAsignacionCupo.cod_producto == cod_producto)

    query = query.outerjoin(
        Producto,
        and_(Producto.cod_producto == StAsignacionCupo.cod_producto, Producto.empresa == StAsignacionCupo.empresa)
    ).outerjoin(
        Cliente,
        and_(Cliente.cod_cliente == StAsignacionCupo.ruc_cliente, Cliente.empresa == StAsignacionCupo.empresa)
    )

    asignaciones = query.all()
    serialized_asignaciones = [
        {
            "empresa": result.empresa,
            "ruc_cliente": result.ruc_cliente,
            "cod_producto": result.cod_producto,
            "cantidad_minima": result.cantidad_minima,
            "porcentaje_maximo": result.porcentaje_maximo,
            "producto": result.producto,
            "cliente": result.cliente,
        }
        for result in asignaciones
    ]


    return jsonify(serialized_asignaciones)

@bpcom.route('/asig_new', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_asignacion():
    data = request.get_json()
    empresa = data.get('empresa')
    ruc_cliente = data.get('ruc_cliente')
    cod_producto = data.get('cod_producto')
    porcentaje_maximo = data.get('porcentaje_maximo')
    cantidad_minima = data.get('cantidad_minima')

    if not (empresa and ruc_cliente and cod_producto and porcentaje_maximo is not None and cantidad_minima is not None):
        return jsonify({'error': 'Faltan datos necesarios para crear la asignación'}), 400

    query = db.session.query().filter(
        StAsignacionCupo.empresa == empresa, StAsignacionCupo.ruc_cliente == ruc_cliente, StAsignacionCupo.cod_producto == cod_producto
    )

    if query:
        return jsonify({'error': 'Asignación de Modelo ' + cod_producto + ' ya existe para el cliente: ' + ruc_cliente}), 500

    nueva_asignacion = StAsignacionCupo(
        empresa=empresa,
        ruc_cliente=ruc_cliente,
        cod_producto=cod_producto,
        porcentaje_maximo=float(porcentaje_maximo),
        cantidad_minima=int(cantidad_minima)
    )

    db.session.add(nueva_asignacion)
    db.session.commit()

    return jsonify({'message': 'Asignación creada exitosamente'}), 201

@bpcom.route('/asig_edit', methods=['POST'])
@jwt_required()
@cross_origin()
def editar_asignacion():
    data = request.get_json()
    empresa = data.get('empresa')
    ruc_cliente = data.get('ruc_cliente')
    cod_producto = data.get('cod_producto')
    porcentaje_maximo = float(data.get('porcentaje_maximo'))
    cantidad_minima = int(data.get('cantidad_minima'))

    if porcentaje_maximo is None or cantidad_minima is None:
        return jsonify({'error': 'Faltan datos necesarios para actualizar la asignación'}), 400

    asignacion = db.session.query(StAsignacionCupo).filter_by(empresa=empresa, cod_producto=cod_producto, ruc_cliente=ruc_cliente).first()
    print(asignacion)
    if not asignacion:
        return jsonify({'error': 'Asignación no encontrada'}), 404

    asignacion.porcentaje_maximo = porcentaje_maximo
    asignacion.cantidad_minima = cantidad_minima

    db.session.commit()

    return jsonify({'message': 'Asignación actualizada exitosamente'}), 200

@bpcom.route('/modelos_by_cod', methods=['POST'])
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
        query = query.filter(Producto.cod_item_cat.in_(['T', 'E']))

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

