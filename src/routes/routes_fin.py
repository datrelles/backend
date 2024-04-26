from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.financiero import StFinCabCredito, StFinDetCredito, StFinClientes, StFinPagos
from src.routes.routes import obtener_secuencia_pagos
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import datetime
from decimal import Decimal
from datetime import datetime, date
from src import oracle
from os import getenv
import cx_Oracle
from src.config.database import db, engine, session

bpfin = Blueprint('routes_fin', __name__)

logger = logging.getLogger(__name__)

def parse_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%d/%m/%Y').date()
    return None
@bpfin.route('/cab')
@jwt_required()
@cross_origin()
def obtener_cab_financiero():
    cod_comprobante = request.args.get('cod_comprobante', None)
    empresa = request.args.get('empresa', None)
    nro_operacion = request.args.get('nro_operacion', None)
    id_cliente = request.args.get('id_cliente', None)

    query = StFinCabCredito.query()
    if empresa:
        query = query.filter(StFinCabCredito.empresa == empresa)
    if cod_comprobante:
        query = query.filter(StFinCabCredito.cod_comprobante == cod_comprobante)
    if nro_operacion:
        query = query.filter(StFinCabCredito.nro_operacion == nro_operacion)
    if id_cliente:
        query = query.filter(StFinCabCredito.id_cliente == id_cliente)

    cabeceras = query.all()

    serialized_cabeceras = []
    for cabecera in cabeceras:
        empresa = cabecera.empresa if cabecera.empresa else ""
        cod_comprobante = cabecera.cod_comprobante if cabecera.cod_comprobante else ""
        tipo_comprobante = cabecera.tipo_comprobante if cabecera.tipo_comprobante else ""
        tipo_id_cliente = cabecera.tipo_id_cliente if cabecera.tipo_id_cliente else ""
        id_cliente = cabecera.id_cliente if cabecera.id_cliente else ""
        nro_operacion = cabecera.nro_operacion if cabecera.nro_operacion else ""
        capital_original = cabecera.capital_original if cabecera.capital_original else ""
        saldo_capital = cabecera.saldo_capital if cabecera.saldo_capital else ""
        fecha_emision = datetime.strftime(cabecera.fecha_emision, "%d%m%Y") if cabecera.fecha_emision else ""
        fecha_vencimiento = datetime.strftime(cabecera.fecha_vencimiento, "%d%m%Y") if cabecera.fecha_vencimiento else ""
        plazo_credito = cabecera.plazo_credito if cabecera.plazo_credito else ""
        tasa_interes = cabecera.tasa_interes if cabecera.tasa_interes else ""
        tasa_mora = cabecera.tasa_mora if cabecera.tasa_mora else ""
        nro_cuota_total = cabecera.nro_cuota_total if cabecera.nro_cuota_total else ""
        nro_cuotas_pagadas = cabecera.nro_cuotas_pagadas if cabecera.nro_cuotas_pagadas else ""
        nro_cuotas_mora = cabecera.nro_cuotas_mora if cabecera.nro_cuotas_mora else ""
        base_calculo = cabecera.base_calculo if cabecera.base_calculo else ""
        usuario_crea = cabecera.usuario_crea if cabecera.usuario_crea else ""
        fecha_crea = datetime.strftime(cabecera.fecha_crea, "%d%m%Y") if cabecera.fecha_crea else ""
        usuario_modifica = cabecera.usuario_modifica if cabecera.usuario_modifica else ""
        fecha_modifica = datetime.strftime(cabecera.fecha_modifica, "%d%m%Y") if cabecera.fecha_modifica else ""
        cod_modelo = cabecera.cod_modelo if cabecera.cod_modelo else ""
        cod_item = cabecera.cod_item if cabecera.cod_item else ""

        serialized_cabeceras.append({
            'empresa': empresa,
            'cod_comprobante': cod_comprobante,
            'tipo_comprobante': tipo_comprobante,
            'tipo_id_cliente': tipo_id_cliente,
            'id_cliente': id_cliente,
            'nro_operacion': nro_operacion,
            'capital_original': capital_original,
            'saldo_capital': saldo_capital,
            'fecha_emision': fecha_emision,
            'fecha_vencimiento': fecha_vencimiento,
            'plazo_credito': plazo_credito,
            'tasa_interes': tasa_interes,
            'tasa_mora': tasa_mora,
            'nro_cuota_total': nro_cuota_total,
            'nro_cuotas_pagadas': nro_cuotas_pagadas,
            'nro_cuotas_mora': nro_cuotas_mora,
            'base_calculo': base_calculo,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item
        })
    return jsonify(serialized_cabeceras)

@bpfin.route('/detail', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_det_financiero():
    data = request.get_json()
    cod_comprobante = data.get('cod_comprobante', None)
    empresa = data.get('empresa', None)
    nro_operacion = data.get('nro_operacion', None)
    id_cliente = data.get('id_cliente', None)
    nro_pago = data.get('nro_pago', None)

    query = StFinDetCredito.query()
    if empresa:
        query = query.filter(StFinDetCredito.empresa == empresa)
    if cod_comprobante:
        query = query.filter(StFinDetCredito.cod_comprobante == cod_comprobante)
    if nro_operacion:
        query = query.filter(StFinDetCredito.nro_operacion == nro_operacion)
    if id_cliente:
        query = query.filter(StFinDetCredito.id_cliente == id_cliente)
    if nro_pago:
        query = query.filter(StFinDetCredito.nro_pago == nro_pago)

    detalles = query.all()

    serialized_detalles = []
    for detalle in detalles:
        empresa = detalle.empresa if detalle.empresa else ""
        cod_comprobante = detalle.cod_comprobante if detalle.cod_comprobante else ""
        tipo_comprobante = detalle.tipo_comprobante if detalle.tipo_comprobante else ""
        id_cliente = detalle.id_cliente if detalle.id_cliente else ""
        nro_operacion = detalle.nro_operacion if detalle.nro_operacion else ""
        nro_pago = detalle.nro_pago if detalle.nro_pago else ""
        fecha_inicio_cuota = datetime.strftime(detalle.fecha_inicio_cuota, "%d%m%Y") if detalle.fecha_inicio_cuota else ""
        fecha_vencimiento_cuota = datetime.strftime(detalle.fecha_vencimiento_cuota, "%d%m%Y") if detalle.fecha_vencimiento_cuota else ""
        plazo_cuota = detalle.plazo_cuota if detalle.plazo_cuota else ""
        valor_capital = detalle.valor_capital if detalle.valor_capital else ""
        valor_interes = detalle.valor_interes if detalle.valor_interes else ""
        valor_mora = detalle.valor_mora if detalle.valor_mora else ""
        valor_cuota = detalle.valor_cuota if detalle.valor_cuota else ""
        estado_cuota = detalle.estado_cuota if detalle.estado_cuota else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = datetime.strftime(detalle.fecha_crea, "%d%m%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = datetime.strftime(detalle.fecha_modifica, "%d%m%Y") if detalle.fecha_modifica else ""

        serialized_detalles.append({
            'empresa': empresa,
            'cod_comprobante': cod_comprobante,
            'tipo_comprobante': tipo_comprobante,
            'id_cliente': id_cliente,
            'nro_operacion': nro_operacion,
            'nro_pago': nro_pago,
            'fecha_inicio_cuota': fecha_inicio_cuota,
            'fecha_vencimiento_cuota': fecha_vencimiento_cuota,
            'plazo_cuota': plazo_cuota,
            'valor_capital': valor_capital,
            'valor_interes': valor_interes,
            'valor_mora': valor_mora,
            'valor_cuota': valor_cuota,
            'estado_cuota': estado_cuota,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica
        })
    return jsonify(serialized_detalles)

@bpfin.route('/cliente', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_cli_financiero():
    empresa = request.args.get('empresa', None)
    id_cliente = request.args.get('id_cliente', None)

    query = StFinClientes.query()
    if empresa:
        query = query.filter(StFinClientes.empresa == empresa)
    if id_cliente:
        query = query.filter(StFinClientes.id_cliente == id_cliente)

    clientes = query.all()

    serialized_clientes = []
    for cliente in clientes:
        empresa = cliente.empresa if cliente.empresa else ""
        id_cliente = cliente.id_cliente if cliente.id_cliente else ""
        pais_origen = cliente.pais_origen if cliente.pais_origen else ""
        primer_apellido = cliente.primer_apellido if cliente.primer_apellido else ""
        segundo_apellido = cliente.segundo_apellido if cliente.segundo_apellido else ""
        primer_nombre = cliente.primer_nombre if cliente.primer_nombre else ""
        segundo_nombre = cliente.segundo_nombre if cliente.segundo_nombre else ""
        calle_principal = cliente.calle_principal if cliente.calle_principal else ""
        calle_secundaria = cliente.calle_secundaria if cliente.calle_secundaria else ""
        numero_casa = cliente.numero_casa if cliente.numero_casa else ""
        ciudad = cliente.ciudad if cliente.ciudad else ""
        numero_celular = cliente.numero_celular if cliente.numero_celular else ""
        numero_convencional = cliente.numero_convencional if cliente.numero_convencional else ""
        direccion_electronica = cliente.direccion_electronica if cliente.direccion_electronica else ""
        usuario_crea = cliente.usuario_crea if cliente.usuario_crea else ""
        fecha_crea = datetime.strftime(cliente.fecha_crea, "%d%m%Y") if cliente.fecha_crea else ""
        usuario_modifica = cliente.usuario_modifica if cliente.usuario_modifica else ""
        fecha_modifica = datetime.strftime(cliente.fecha_modifica, "%d%m%Y") if cliente.fecha_modifica else ""

        serialized_clientes.append({
            'empresa': empresa,
            'id_cliente': id_cliente,
            'pais_origen': pais_origen,
            'primer_apellido': primer_apellido,
            'segundo_apellido': segundo_apellido,
            'primer_nombre': primer_nombre,
            'segundo_nombre': segundo_nombre,
            'calle_principal': calle_principal,
            'calle_secundaria': calle_secundaria,
            'numero_casa': numero_casa,
            'ciudad': ciudad,
            'numero_celular': numero_celular,
            'numero_convencional': numero_convencional,
            'direccion_electronica': direccion_electronica,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica
        })
    return jsonify(serialized_clientes)

@bpfin.route('/fee', methods=['POST'])
#@jwt_required()
@cross_origin()
def obtener_pagos_financiero():
    data = request.get_json()
    cod_comprobante = data.get('cod_comprobante', None)
    empresa = data.get('empresa', None)
    nro_operacion = data.get('nro_operacion', None)
    id_cliente = data.get('id_cliente', None)
    nro_pago = data.get('nro_pago', None)
    secuencia = data.get('secuencia', None)

    query = StFinPagos.query()
    if empresa:
        query = query.filter(StFinPagos.empresa == empresa)
    if cod_comprobante:
        query = query.filter(StFinPagos.cod_comprobante == cod_comprobante)
    if nro_operacion:
        query = query.filter(StFinPagos.nro_operacion == nro_operacion)
    if id_cliente:
        query = query.filter(StFinPagos.id_cliente == id_cliente)
    if nro_pago:
        query = query.filter(StFinPagos.nro_cuota == nro_pago)
    if secuencia:
        query = query.filter(StFinPagos.secuencia == secuencia)

    pagos = query.all()

    serialized_pagos = []
    for pago in pagos:
        empresa = pago.empresa if pago.empresa else ""
        cod_comprobante = pago.cod_comprobante if pago.cod_comprobante else ""
        tipo_comprobante = pago.tipo_comprobante if pago.tipo_comprobante else ""
        id_cliente = pago.id_cliente if pago.id_cliente else ""
        nro_operacion = pago.nro_operacion if pago.nro_operacion else ""
        nro_cuota = pago.nro_cuota if pago.nro_cuota else ""
        secuencia = pago.secuencia if pago.secuencia else ""
        valor_total_cuota = pago.valor_total_cuota if pago.valor_total_cuota else ""
        valor_pagado_capital = pago.valor_pagado_capital if pago.valor_pagado_capital else ""
        valor_pagado_interes = pago.valor_pagado_interes if pago.valor_pagado_interes else ""
        valor_pagado_mora = pago.valor_pagado_mora if pago.valor_pagado_mora else ""
        fecha_registro = datetime.strftime(pago.fecha_registro,"%d%m%Y") if pago.fecha_registro else ""
        usuario_crea = pago.usuario_crea if pago.usuario_crea else ""
        fecha_crea = datetime.strftime(pago.fecha_crea, "%d%m%Y") if pago.fecha_crea else ""
        usuario_modifica = pago.usuario_modifica if pago.usuario_modifica else ""
        fecha_modifica = datetime.strftime(pago.fecha_modifica, "%d%m%Y") if pago.fecha_modifica else ""

        serialized_pagos.append({
            'empresa': empresa,
            'cod_comprobante': cod_comprobante,
            'tipo_comprobante': tipo_comprobante,
            'id_cliente': id_cliente,
            'nro_operacion': nro_operacion,
            'nro_cuota': nro_cuota,
            'secuencia': secuencia,
            'valor_total_cuota': valor_total_cuota,
            'valor_pagado_capital': valor_pagado_capital,
            'valor_pagado_interes': valor_pagado_interes,
            'valor_pagado_mora': valor_pagado_mora,
            'fecha_registro': fecha_registro,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica
        })
    return jsonify(serialized_pagos)

@bpfin.route('/cab', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_cabecera():
    try:
        data = request.get_json()
        empresa = data.get('empresa')
        cod_agencia = data.get('cod_agencia')
        fecha_crea = date.today()
        fecha_emision = parse_date(data.get('fecha_emision'))
        fecha_vencimiento = parse_date(data.get('fecha_vencimiento'))

        if fecha_emision is None:
            return jsonify({'error': 'Ingrese fecha de emision'})
        if fecha_vencimiento is None:
            return jsonify({'error': 'Ingrese fecha de vencimiento'})

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
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
        cur.execute(query, (empresa, 'FC', cod_agencia, result_var))
        cod_comprobante = result_var.getvalue()
        cur.close()

        cabecera = StFinCabCredito(
            empresa=empresa,
            cod_comprobante=cod_comprobante,
            tipo_comprobante='FC',
            tipo_id_cliente=data['tipo_id_cliente'],
            id_cliente=data['id_cliente'],
            nro_operacion=data['nro_operacion'],
            capital_original=data['capital_original'],
            saldo_capital=data['saldo_capital'],
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            plazo_credito=data['plazo_credito'],
            tasa_interes=data['tasa_interes'],
            tasa_mora=data['tasa_mora'],
            nro_cuota_total=data['nro_cuota_total'],
            nro_cuotas_pagadas=data['nro_cuotas_pagadas'],
            nro_cuotas_mora=data['nro_cuotas_mora'],
            base_calculo=data['base_calculo'],
            cod_modelo='FIN',
            cod_item=data['cod_item'],
            fecha_crea=fecha_crea,
            usuario_crea=data['usuario_crea'].upper()
        )
        db1.commit()
        db1.close()
        db.session.add(cabecera)
        db.session.commit()

        return jsonify({'cod_comprobante': cod_comprobante})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/cli', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_cliente_fin():
    try:
        data = request.get_json()
        empresa = data.get('empresa')
        fecha_crea = date.today()
        id_cliente = data['id_cliente']

        cliente = StFinClientes(
            empresa=empresa,
            id_cliente=id_cliente,
            pais_origen=data['pais_origen'],
            primer_apellido=data['primer_apellido'],
            segundo_apellido=data['segundo_apellido'],
            primer_nombre=data['primer_nombre'],
            segundo_nombre=data['segundo_nombre'],
            calle_principal=data['calle_principal'],
            calle_secundaria=data['calle_secundaria'],
            numero_casa=data['numero_casa'],
            ciudad=data['ciudad'],
            numero_celular=data['numero_celular'],
            numero_convencional=data['numero_convencional'],
            direccion_electronica=data['direccion_electronica'],
            usuario_crea=data['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data.get('usuario_modifica', None),  # Puedes ajustar según tu lógica de datos
            fecha_modifica=data.get('fecha_modifica', None)  # Puedes ajustar según tu lógica de datos
        )
        db.session.add(cliente)
        db.session.commit()

        return jsonify({'id_cliente': id_cliente})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/pay', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_pago_fin():
    try:
        data = request.get_json()
        empresa = data.get('empresa')
        fecha_crea = date.today()
        id_cliente = data['id_cliente']
        cod_comprobante = data['cod_comprobante']
        tipo_comprobante = data['tipo_comprobante']
        nro_operacion = data['nro_operacion']
        nro_pago = data['nro_pago']
        secuencia = obtener_secuencia_pagos(empresa, cod_comprobante, tipo_comprobante, nro_operacion, nro_pago)
        pago = StFinPagos(
            empresa=empresa,
            cod_comprobante=cod_comprobante,
            tipo_comprobante=tipo_comprobante,
            nro_operacion=nro_operacion,
            id_cliente=id_cliente,
            fecha_pago=parse_date(data['fecha_pago']),
            nro_cuota=nro_pago,
            valor_total_cuota=data['valor_total_cuota'],
            valor_pagado_capital=data['valor_pagado_capital'],
            valor_pagado_interes=data['valor_pagado_interes'],
            valor_pagado_mora=data['valor_pagado_mora'],
            fecha_registro=parse_date(data['fecha_registro']),
            usuario_crea=data['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data.get('usuario_modifica', None),
            fecha_modifica=data.get('fecha_modifica', None),
            secuencia=secuencia
        )

        db.session.add(pago)
        db.session.commit()

        return jsonify({'nro_pago_cuota': secuencia})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/det', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_det_fin():
    try:
        data = request.get_json()
        empresa = data.get('empresa')
        fecha_crea = date.today()
        id_cliente = data['id_cliente']
        cod_comprobante = data['cod_comprobante']
        tipo_comprobante = data['tipo_comprobante']
        nro_operacion = data['nro_operacion']
        nro_pago = data['nro_pago']
        detalle_credito = StFinDetCredito(
            empresa=empresa,
            cod_comprobante=cod_comprobante,
            tipo_comprobante=tipo_comprobante,
            nro_operacion=nro_operacion,
            id_cliente=id_cliente,
            nro_pago=nro_pago,
            fecha_inicio_cuota=parse_date(data['fecha_inicio_cuota']),
            fecha_vencimiento_cuota=parse_date(data['fecha_vencimiento_cuota']),
            plazo_cuota=data['plazo_cuota'],
            valor_capital=data['valor_capital'],
            valor_interes=data['valor_interes'],
            valor_mora=data['valor_mora'],
            valor_cuota=data['valor_cuota'],
            estado_cuota=data['estado_cuota'],  # Inserta aquí el valor correspondiente según la lógica de tu aplicación
            usuario_crea=data['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data.get('usuario_modifica', None),
            fecha_modifica=data.get('fecha_modifica', None)
        )

        db.session.add(detalle_credito)
        db.session.commit()

        return jsonify({'nro_pago': nro_pago})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500