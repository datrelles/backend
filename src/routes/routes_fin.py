from flask import Blueprint, jsonify, request
from src.models.productos import Producto
from src.models.proveedores import Proveedor
from src.models.clientes import Cliente
from src.models.financiero import StFinCabCredito, StFinDetCredito, StFinClientes, StFinPagos, StFinNegociacion
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

bpfin = Blueprint('routes_fin', __name__)

logger = logging.getLogger(__name__)

def parse_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%d/%m/%Y').date()
    return None

def excel_date_to_datetime(excel_date):
    return datetime(*xlrd.xldate_as_tuple(excel_date, 0))

@bpfin.route('/neg')
@jwt_required()
@cross_origin()
def obtener_negociacion():
    tipo_comprobante = request.args.get('tipo_comprobante', None)
    cod_comprobante = request.args.get('cod_comprobante', None)
    empresa = request.args.get('empresa', None)

    query = StFinNegociacion.query()
    if empresa:
        query = query.filter(StFinNegociacion.empresa == empresa)
    if cod_comprobante:
        query = query.filter(StFinNegociacion.cod_comprobante == cod_comprobante)
    if tipo_comprobante:
        query = query.filter(StFinNegociacion.tipo_comprobante == tipo_comprobante)


    negociaciones = query.all()

    serialized_negociaciones = []
    for negociacion in negociaciones:
        empresa = negociacion.empresa if negociacion.empresa else ""
        cod_comprobante = negociacion.cod_comprobante if negociacion.cod_comprobante else ""
        tipo_comprobante = negociacion.tipo_comprobante if negociacion.tipo_comprobante else ""
        cod_cliente = negociacion.cod_cliente if negociacion.cod_cliente else ""
        fecha_negociacion = datetime.strftime(negociacion.fecha_negociacion, "%d/%m/%Y") if negociacion.fecha_negociacion else ""
        cod_proveedor = negociacion.cod_proveedor if negociacion.cod_proveedor else ""
        usuario_crea = negociacion.usuario_crea if negociacion.usuario_crea else ""
        fecha_crea = datetime.strftime(negociacion.fecha_crea, "%d/%m/%Y") if negociacion.fecha_crea else ""
        usuario_modifica = negociacion.usuario_modifica if negociacion.usuario_modifica else ""
        fecha_modifica = datetime.strftime(negociacion.fecha_modifica, "%d/%m/%Y") if negociacion.fecha_modifica else ""
        tipo_destino = negociacion.tipo_destino if negociacion.tipo_destino else ""

        serialized_negociaciones.append({
            'empresa': empresa,
            'cod_comprobante': cod_comprobante,
            'tipo_comprobante': tipo_comprobante,
            'cod_cliente': cod_cliente,
            'fecha_negociacion': fecha_negociacion,
            'cod_proveedor': cod_proveedor,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'tipo_destino': tipo_destino
        })
    return jsonify(serialized_negociaciones)

@bpfin.route('/cabeceras', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_cab_financiero():
    data = request.get_json()
    cod_comprobante = data.get('cod_comprobante', None)
    empresa = data.get('empresa', None)
    nro_operacion = data.get('nro_operacion', None)
    id_cliente = data.get('id_cliente', None)
    print(cod_comprobante)
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
        fecha_emision = datetime.strftime(cabecera.fecha_emision, "%d/%m/%Y") if cabecera.fecha_emision else ""
        fecha_vencimiento = datetime.strftime(cabecera.fecha_vencimiento, "%d/%m/%Y") if cabecera.fecha_vencimiento else ""
        plazo_credito = cabecera.plazo_credito if cabecera.plazo_credito else ""
        tasa_interes = cabecera.tasa_interes if cabecera.tasa_interes else ""
        tasa_mora = cabecera.tasa_mora if cabecera.tasa_mora else ""
        nro_cuota_total = cabecera.nro_cuota_total if cabecera.nro_cuota_total else ""
        nro_cuotas_pagadas = cabecera.nro_cuotas_pagadas if cabecera.nro_cuotas_pagadas else ""
        nro_cuotas_mora = cabecera.nro_cuotas_mora if cabecera.nro_cuotas_mora else ""
        base_calculo = cabecera.base_calculo if cabecera.base_calculo else ""
        usuario_crea = cabecera.usuario_crea if cabecera.usuario_crea else ""
        fecha_crea = datetime.strftime(cabecera.fecha_crea, "%d/%m/%Y") if cabecera.fecha_crea else ""
        usuario_modifica = cabecera.usuario_modifica if cabecera.usuario_modifica else ""
        fecha_modifica = datetime.strftime(cabecera.fecha_modifica, "%d/%m/%Y") if cabecera.fecha_modifica else ""
        cod_modelo = cabecera.cod_modelo if cabecera.cod_modelo else ""
        cod_item = cabecera.cod_item if cabecera.cod_item else ""
        tipo_destino = cabecera.tipo_destino if cabecera.tipo_destino else ""
        cod_cliente = cabecera.cod_cliente if cabecera.cod_cliente else ""
        cod_proveedor = cabecera.cod_proveedor if cabecera.cod_proveedor else ""
        secuencia_negociacion = cabecera.secuencia_negociacion if cabecera.secuencia_negociacion else ""
        liquidacion = cabecera.liquidacion if cabecera.liquidacion else ""
        es_parcial = cabecera.es_parcial if cabecera.es_parcial else ""
        cuota_inicial = cabecera.cuota_inicial if cabecera.cuota_inicial else ""

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
            'cod_item': cod_item,
            'tipo_destino': tipo_destino,
            'cod_proveedor': cod_proveedor,
            'cod_cliente': cod_cliente,
            'secuencia_negociacion': secuencia_negociacion,
            'liquidacion': liquidacion,
            'es_parcial': es_parcial,
            'cuota_inicial': cuota_inicial
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
        fecha_inicio_cuota = datetime.strftime(detalle.fecha_inicio_cuota, "%d/%m/%Y") if detalle.fecha_inicio_cuota else ""
        fecha_vencimiento_cuota = datetime.strftime(detalle.fecha_vencimiento_cuota, "%d/%m/%Y") if detalle.fecha_vencimiento_cuota else ""
        plazo_cuota = detalle.plazo_cuota if detalle.plazo_cuota else ""
        valor_capital = detalle.valor_capital if detalle.valor_capital else ""
        valor_interes = detalle.valor_interes if detalle.valor_interes else ""
        valor_mora = detalle.valor_mora if detalle.valor_mora else ""
        valor_cuota = detalle.valor_cuota if detalle.valor_cuota else ""
        estado_cuota = detalle.estado_cuota if detalle.estado_cuota else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = datetime.strftime(detalle.fecha_crea, "%d/%m/%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = datetime.strftime(detalle.fecha_modifica, "%d/%m/%Y") if detalle.fecha_modifica else ""
        cod_cliente = detalle.cod_cliente if detalle.cod_cliente else ""
        cod_proveedor = detalle.cod_proveedor if detalle.cod_proveedor else ""

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
            'fecha_modifica': fecha_modifica,
            'cod_proveedor': cod_proveedor,
            'cod_cliente': cod_cliente
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
        fecha_crea = datetime.strftime(cliente.fecha_crea, "%d/%m/%Y") if cliente.fecha_crea else ""
        usuario_modifica = cliente.usuario_modifica if cliente.usuario_modifica else ""
        fecha_modifica = datetime.strftime(cliente.fecha_modifica, "%d/%m/%Y") if cliente.fecha_modifica else ""

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
@jwt_required()
@cross_origin()
def obtener_pagos_financiero():
    data = request.get_json()
    cod_cliente = data.get('cod_cliente', None)
    empresa = data.get('empresa', None)
    nro_operacion = data.get('nro_operacion', None)
    id_cliente = data.get('id_cliente', None)
    nro_pago = data.get('nro_pago', None)
    secuencia = data.get('secuencia', None)

    query = StFinPagos.query()
    if empresa:
        query = query.filter(StFinPagos.empresa == empresa)
    if cod_cliente:
        query = query.filter(StFinPagos.cod_cliente == cod_cliente)
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
        cod_cliente = pago.cod_cliente if pago.cod_cliente else ""
        cod_proveedor = pago.cod_proveedor if pago.cod_proveedor else ""
        id_cliente = pago.id_cliente if pago.id_cliente else ""
        nro_operacion = pago.nro_operacion if pago.nro_operacion else ""
        nro_cuota = pago.nro_cuota if pago.nro_cuota else ""
        secuencia = pago.secuencia if pago.secuencia else ""
        valor_total_cuota = pago.valor_total_cuota if pago.valor_total_cuota else ""
        valor_pagado_capital = pago.valor_pagado_capital if pago.valor_pagado_capital else ""
        valor_pagado_interes = pago.valor_pagado_interes if pago.valor_pagado_interes else ""
        valor_pagado_mora = pago.valor_pagado_mora if pago.valor_pagado_mora else ""
        fecha_registro = datetime.strftime(pago.fecha_registro,"%d/%m/%Y") if pago.fecha_registro else ""
        usuario_crea = pago.usuario_crea if pago.usuario_crea else ""
        fecha_crea = datetime.strftime(pago.fecha_crea, "%d/%m/%Y") if pago.fecha_crea else ""
        usuario_modifica = pago.usuario_modifica if pago.usuario_modifica else ""
        fecha_modifica = datetime.strftime(pago.fecha_modifica, "%d/%m/%Y") if pago.fecha_modifica else ""

        serialized_pagos.append({
            'empresa': empresa,
            'cod_cliente': cod_cliente,
            'cod_proveedor': cod_proveedor,
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

@bpfin.route('/negociacion', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_negociacion():
    try:
        data = request.get_json()
        empresa = str(data.get('empresa'))
        cod_agencia = str(data.get('cod_agencia'))
        tipo_comprobante = str(data.get('tipo_comprobante'))
        usuario_crea = str(data.get('usuario_crea'))
        fecha_negociacion = parse_date(data.get('fecha_negociacion'))
        cod_cliente = str(data.get('cod_cliente'))
        cod_proveedor = str(data.get('cod_proveedor'))
        tipo_destino = data.get('tipo_destino') if data.get('tipo_destino') else 0
        fecha_crea = date.today()

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
        cur.execute(query, (empresa, tipo_comprobante, cod_agencia, result_var))
        cod_comprobante = result_var.getvalue()
        cur.close()

        negociacion = StFinNegociacion(
            empresa=int(empresa),
            cod_comprobante=cod_comprobante,
            tipo_comprobante= tipo_comprobante,
            cod_cliente=cod_cliente,
            fecha_negociacion=fecha_negociacion,
            cod_proveedor=cod_proveedor,
            tipo_destino=tipo_destino,
            fecha_crea=fecha_crea,
            usuario_crea=usuario_crea.upper()
        )
        db.session.add(negociacion)
        db1.commit()
        db1.close()
        db.session.commit()

        return jsonify({'mensaje': 'Creación de negociacion','cod_comprobante': cod_comprobante})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500
@bpfin.route('/cab', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_cabecera():
    try:
        data = request.get_json()
        cabeceras = data.get('cabeceras')
        cod_comprobante = data.get('cod_comprobante')
        cod_cliente = data.get('cod_cliente')
        cod_proveedor = data.get('cod_proveedor')
        print(cod_comprobante , ' / ', cod_proveedor)
        for cabecera_data in cabeceras:
            empresa = str(cabecera_data['empresa'])
            id_cliente = str(cabecera_data['id_cliente'])
            nro_operacion = str(cabecera_data['nro_operacion'])
            verificacion = StFinCabCredito.query().filter(StFinCabCredito.empresa == int(empresa),StFinCabCredito.id_cliente == id_cliente, StFinCabCredito.nro_operacion == nro_operacion).all()
            invalid_cabs = []
            tipo_comprobante = 'FM' if cabecera_data['tipo_destino'] == 1 else 'FC'
            if verificacion == []:


                fecha_crea = date.today()
                fecha_emision = excel_date_to_datetime(cabecera_data.get('fecha_emision')).date()
                fecha_vencimiento = excel_date_to_datetime(cabecera_data.get('fecha_vencimiento')).date()

                if fecha_emision is None:
                    return jsonify({'error': 'Ingrese fecha de emision'})
                if fecha_vencimiento is None:
                    return jsonify({'error': 'Ingrese fecha de vencimiento'})

                cabecera = StFinCabCredito(
                    empresa=int(empresa),
                    cod_comprobante=cod_comprobante,
                    cod_cliente=cod_cliente,
                    cod_proveedor=cod_proveedor,
                    tipo_comprobante= tipo_comprobante,
                    tipo_id_cliente=cabecera_data['tipo_id_cliente'],
                    id_cliente=re.sub(r"^'", "", str(cabecera_data['id_cliente'])),
                    nro_operacion=cabecera_data['nro_operacion'],
                    capital_original=float(cabecera_data['capital_original']),
                    saldo_capital=float(cabecera_data['saldo_capital']),
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                    plazo_credito=int(cabecera_data['plazo_credito']),
                    tasa_interes=float(cabecera_data['tasa_interes']),
                    tasa_mora=float(cabecera_data['tasa_mora']),
                    nro_cuota_total=int(cabecera_data['nro_cuota_total']),
                    nro_cuotas_pagadas=int(cabecera_data['nro_cuotas_pagadas']),
                    nro_cuotas_mora=int(cabecera_data['nro_cuotas_mora']),
                    base_calculo=cabecera_data['base_calculo'],
                    tipo_destino=cabecera_data['tipo_destino'] if cabecera_data['tipo_destino'] else 0,
                    cod_modelo='FIN',
                    cod_item=cabecera_data['cod_item'],
                    fecha_crea=fecha_crea,
                    usuario_crea=cabecera_data['usuario_crea'].upper(),
                    secuencia_negociacion=cabecera_data['secuencia_negociacion'] if cabecera_data['secuencia_negociacion'] else 0,
                    liquidacion=cabecera_data['liquidacion'] if cabecera_data['liquidacion'] else "",
                    es_parcial=cabecera_data['es_parcial'] if cabecera_data['es_parcial'] else 0,
                    cuota_inicial=cabecera_data['cuota_inicial'] if cabecera_data['cuota_inicial'] else 1
                )
                db.session.add(cabecera)
            else:
                for item in verificacion:
                    invalid_cabs.append(item.nro_operacion + ' ')

        db.session.commit()

        return jsonify({'mensaje': 'Creación de cabeceras exitosa','invalids': invalid_cabs})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500


@bpfin.route('/cli', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_cliente_fin():
    try:
        data = request.get_json()
        costumers = data.get('costumers')
        invalid_users = []
        for customer_data in costumers:
            empresa = str(customer_data['empresa'])
            fecha_crea = date.today()
            id_cliente = str(customer_data['id_cliente'])
            verificacion = StFinClientes.query().filter(StFinClientes.empresa == empresa, StFinClientes.id_cliente == id_cliente).all()
            if verificacion == []:
                cliente = StFinClientes(
                    empresa=empresa,
                    id_cliente=re.sub(r"^'", "", str(id_cliente)),
                    pais_origen=str(customer_data['pais_origen']),
                    primer_apellido=str(customer_data['primer_apellido']),
                    segundo_apellido=str(customer_data['segundo_apellido']),
                    primer_nombre=str(customer_data['primer_nombre']),
                    segundo_nombre=str(customer_data['segundo_nombre']),
                    calle_principal=str(customer_data['calle_principal']),
                    calle_secundaria=str(customer_data['calle_secundaria']),
                    numero_casa=str(customer_data['numero_casa']),
                    ciudad=str(customer_data['ciudad']),
                    numero_celular=str(customer_data['numero_celular']),
                    numero_convencional=str(customer_data['numero_convencional']),
                    direccion_electronica=str(customer_data['direccion_electronica']),
                    usuario_crea=str(customer_data['usuario_crea'].upper()),
                    fecha_crea=fecha_crea
                )
                db.session.add(cliente)
            else:
                for item in verificacion:
                    invalid_users.append(item.id_cliente + ' ')
        db.session.commit()

        return jsonify({'mensaje': 'Creación de usuario exitoso','invalids': invalid_users})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/pay', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_pago_fin():
    try:
        data = request.get_json()
        pagos = data.get('pagos')

        for pago in pagos:
            empresa = str(pago['empresa'])
            fecha_crea = date.today()
            id_cliente = pago['id_cliente']
            cod_comprobante = pago['cod_comprobante']
            tipo_comprobante = pago['tipo_comprobante']
            nro_operacion = pago['nro_operacion']
            nro_cuota = pago['nro_cuota']
            secuencia = obtener_secuencia_pagos(empresa, cod_comprobante, tipo_comprobante, nro_operacion, nro_cuota)
            fecha_pago = excel_date_to_datetime(pago['fecha_pago']).date()
            fecha_registro = excel_date_to_datetime(pago['fecha_registro']).date()

            pago = StFinPagos(
                empresa=empresa,
                cod_comprobante=cod_comprobante,
                tipo_comprobante=tipo_comprobante,
                nro_operacion=nro_operacion,
                id_cliente=id_cliente,
                fecha_pago=fecha_pago,
                nro_cuota=nro_cuota,
                valor_total_cuota=pago['valor_total_cuota'],
                valor_pagado_capital=pago['valor_pagado_capital'],
                valor_pagado_interes=pago['valor_pagado_interes'],
                valor_pagado_mora=pago['valor_pagado_mora'],
                fecha_registro=fecha_registro,
                usuario_crea=pago['usuario_crea'].upper(),
                fecha_crea=fecha_crea,
                secuencia=secuencia
            )

            db.session.add(pago)

        db.session.commit()

        return jsonify({'mensaje': 'Creación de pagos correcta'})

    except Exception as e:
        logger.exception(f"Error al crear el pago: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bpfin.route('/det', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_det_fin():
    try:
        data = request.get_json()
        detalles = data.get('detalles')
        cod_cliente = data.get('cod_cliente')
        cod_proveedor = data.get('cod_proveedor')
        for detalle in detalles:
            empresa = str(detalle['empresa'])
            fecha_crea = date.today()
            id_cliente = detalle['id_cliente']
            cod_comprobante = detalle['cod_comprobante']
            tipo_comprobante = detalle['tipo_comprobante']
            nro_operacion = detalle['nro_operacion']
            nro_pago = detalle['nro_pago']
            verificacion = StFinDetCredito.query().filter(StFinDetCredito.empresa == empresa,
                                                          StFinDetCredito.id_cliente == id_cliente,
                                                          StFinDetCredito.nro_operacion == str(nro_operacion),
                                                          StFinDetCredito.nro_pago == nro_pago).all()
            invalid_dets = []
            if verificacion == []:
                fecha_inicio_cuota = excel_date_to_datetime(detalle['fecha_inicio_cuota']).date()
                fecha_vencimiento_cuota = excel_date_to_datetime(detalle['fecha_vencimiento_cuota']).date()

                detalle_credito = StFinDetCredito(
                    empresa=empresa,
                    cod_comprobante=cod_comprobante,
                    tipo_comprobante=tipo_comprobante,
                    cod_cliente=cod_cliente,
                    cod_proveedor=cod_proveedor,
                    nro_operacion=nro_operacion,
                    id_cliente=id_cliente,
                    nro_pago=nro_pago,
                    fecha_inicio_cuota=fecha_inicio_cuota,
                    fecha_vencimiento_cuota=fecha_vencimiento_cuota,
                    plazo_cuota=detalle['plazo_cuota'],
                    valor_capital=detalle['valor_capital'],
                    valor_interes=detalle['valor_interes'],
                    valor_mora=detalle['valor_mora'],
                    valor_cuota=detalle['valor_cuota'],
                    estado_cuota=detalle['estado_cuota'],
                    usuario_crea=detalle['usuario_crea'].upper(),
                    fecha_crea=fecha_crea,
                )

                db.session.add(detalle_credito)
            else:
                for item in verificacion:
                    invalid_dets.append(item.nro_operacion + ', ' + str(item.nro_pago))
        db.session.commit()

        return jsonify({'mensaje': 'Creación de detalles correcta','invalid_dets': invalid_dets})

    except Exception as e:
        logger.exception(f"Error al crear : {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/pay_general', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_pago_fin_general():
    try:
        data = request.get_json()
        pagos = data.get('pagos')

        for pago in pagos:
            empresa = str(pago['empresa'])
            fecha_crea = date.today()
            id_cliente = pago['id_cliente']
            nro_operacion = pago['nro_operacion']
            nro_cuota = pago['nro_cuota']
            query = StFinDetCredito.query()
            if empresa:
                query = query.filter(StFinDetCredito.empresa == empresa)
            if nro_operacion:
                query = query.filter(StFinDetCredito.nro_operacion == nro_operacion)
            if nro_cuota:
                query = query.filter(StFinDetCredito.nro_pago == nro_cuota)

            detalle = query.first()
            cod_cliente = detalle.cod_cliente
            cod_proveedor = detalle.cod_proveedor

            secuencia = obtener_secuencia_pagos(empresa, cod_cliente, cod_proveedor, nro_operacion, nro_cuota)
            fecha_pago = excel_date_to_datetime(pago['fecha_pago']).date()
            fecha_registro = excel_date_to_datetime(pago['fecha_registro']).date()

            pago = StFinPagos(
                empresa=empresa,
                cod_cliente=cod_cliente,
                cod_proveedor=cod_proveedor,
                nro_operacion=nro_operacion,
                id_cliente=id_cliente,
                fecha_pago=fecha_pago,
                nro_cuota=nro_cuota,
                valor_total_cuota=pago['valor_total_cuota'],
                valor_pagado_capital=pago['valor_pagado_capital'],
                valor_pagado_interes=pago['valor_pagado_interes'],
                valor_pagado_mora=pago['valor_pagado_mora'],
                fecha_registro=fecha_registro,
                usuario_crea=pago['usuario_crea'].upper(),
                fecha_crea=fecha_crea,
                secuencia=secuencia
            )

            db.session.add(pago)

        db.session.commit()

        return jsonify({'mensaje': 'Creación de pagos correcta'})

    except Exception as e:
        logger.exception(f"Error al crear el pago: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/cabecera_edit_status', methods=['POST'])
@jwt_required()
@cross_origin()
def edit_cab_financiero():
    try:
        data = request.get_json()
        cod_comprobante = data.get('cod_comprobante', None)
        empresa = data.get('empresa', None)
        nro_operacion = data.get('nro_operacion', None)
        cod_cliente = data.get('cod_cliente', None)
        cod_proveedor = data.get('cod_proveedor', None)
        cod_item = data.get('cod_item', None)
        query = StFinCabCredito.query()
        if empresa:
            query = query.filter(StFinCabCredito.empresa == empresa)
        if cod_comprobante:
            query = query.filter(StFinCabCredito.cod_comprobante == cod_comprobante)
        else:
            return jsonify({'error': 'Cod Negociación Inválido'}), 500
        if nro_operacion:
            query = query.filter(StFinCabCredito.nro_operacion == nro_operacion)
        else:
            return jsonify({'error': 'Nro Operación Inválido'}), 500
        if cod_cliente:
            query = query.filter(StFinCabCredito.cod_cliente == cod_cliente)
        else:
            return jsonify({'error': 'Cod Cliente Inválido'}), 500
        if cod_proveedor:
            query = query.filter(StFinCabCredito.cod_proveedor == cod_proveedor)
        else:
            return jsonify({'error': 'Cod Proveedor Inválido'}), 500


        cabecera = query.first()
        cabecera.cod_item = cod_item if cod_item else 0
        db.session.commit()

        return jsonify({'mensaje': 'Guardado exitosamente'})

    except Exception as e:
        logger.exception(f"Error al guardar operación: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/providers_by_cod', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_proveedores_por_codigo():
    try:
        data = request.get_json()
        empresa = data.get('empresa', None)
        cod_proveedor = data.get('cod_proveedor', None)
        print(cod_proveedor)
        if not cod_proveedor:
            return jsonify({'error': 'Falta ingresar el codigo de proveedor.'}), 404

        query = Proveedor.query()

        if empresa:
            query = query.filter(Proveedor.empresa == empresa)

        query = query.filter(Proveedor.nombre.like(f'%{cod_proveedor}%'))

        proveedores = query.all()
        serialized_proveedores = []

        for proveedor in proveedores:
            empresa = proveedor.empresa if proveedor.empresa else ""
            cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
            nombre = proveedor.nombre if proveedor.nombre else ""
            direccion = proveedor.direccion if proveedor.direccion else ""
            useridc = proveedor.useridc if proveedor.useridc else ""
            telefono = proveedor.telefono if proveedor.telefono else ""
            ruc = proveedor.ruc if proveedor.ruc else ""
            serialized_proveedores.append({
                'empresa': empresa,
                'cod_proveedor': cod_proveedor,
                'nombre': nombre,
                'direccion': direccion,
                'useridc': useridc,
                'telefono': telefono,
                'ruc': ruc
            })
        return jsonify(serialized_proveedores)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bpfin.route('/costumers_by_cod', methods=['POST'])
@jwt_required()
@cross_origin()
def obtener_clientes_por_codigo():
    try:
        data = request.get_json()
        empresa = data.get('empresa', None)
        cod_cliente = data.get('cod_cliente', None)
        print(cod_cliente)
        if not cod_cliente:
            return jsonify({'error': 'Falta ingresar el codigo de cliente.'}), 404

        query = Cliente.query()

        if empresa:
            query = query.filter(Cliente.empresa == empresa)

        query = query.filter(Cliente.apellido1.like(f'%{cod_cliente}%'))
        query = query.filter(Cliente.cod_tipo_identificacion == 2)

        clientes = query.all()
        serialized_clientes = []

        for cliente in clientes:
            empresa = cliente.empresa if cliente.empresa else ""
            cod_cliente = cliente.cod_cliente if cliente.cod_cliente else ""
            nombre = cliente.nombre if cliente.nombre else ""
            apellido1 = cliente.apellido1 if cliente.apellido1 else ""
            ruc = cliente.ruc if cliente.ruc else ""
            serialized_clientes.append({
                'empresa': empresa,
                'cod_cliente': cod_cliente,
                'nombre': nombre,
                'apellido1': apellido1,
                'ruc': ruc
            })
        return jsonify(serialized_clientes)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        return jsonify({'error': str(e)}), 500
