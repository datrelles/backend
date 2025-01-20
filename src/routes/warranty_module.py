from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from src import oracle
from src.models.postVenta import ar_taller_servicio_tecnico, ADprovincias, ADcantones
from sqlalchemy import (and_)
#here modules

import logging

rmwa = Blueprint('routes_module_warranty', __name__)

@rmwa.route('/manual_entry_of_warranty_cases', methods=['POST'])
@jwt_required()
def manual_entry_of_warranty_cases():
    print('PRINT')
    return jsonify("test" , "test")

#check information by engine code
@rmwa.route('/check_info_bye_engine_code', methods=['GET'])
@jwt_required()
def check_info_bye_engine_code():
    engine_code = request.args.get('engine_code')
    if not engine_code:
        return jsonify({'error': 'El parámetro engine_code es requerido.'}), 400

    info_moto = oracle.infoMotor(engine_code)

    dict_info_motor = {
                            "RUC_DISTRIBUIDOR": info_moto[0],
                            "COD_PRODUCTO": info_moto[1],
                            "COD_CHASIS":info_moto[2],
                            "IMPORTACION":info_moto[3],
                            "NOMBRE_DISTRIBUIDOR": info_moto[4],
                            "COD_MOTOR": engine_code
                      }
    return jsonify(dict_info_motor)

@rmwa.route('/get_info_active_talleres', methods=['GET'])
@jwt_required()
def get_talleres_authorized_warranty():
    status = int(request.args.get('active'))
    enterprise = request.args.get('enterprise')

    if status == 1:
        status = 'N'
    elif status == 0:
        status = 'S'
    else:
        return jsonify({'error': 'The active parameter can only be 1 or 0.'}), 400

    # Using ar_taller_servicio_tecnico.query without explicit db.session
    query = (
        ar_taller_servicio_tecnico.query()
        .join(
            ADprovincias,
            and_(
                ar_taller_servicio_tecnico.cod_provincia == ADprovincias.codigo_provincia,
                ar_taller_servicio_tecnico.cod_nacion == ADprovincias.codigo_nacion
            )
        )
        .join(
            ADcantones,
            and_(
                ar_taller_servicio_tecnico.cod_provincia == ADcantones.codigo_provincia,
                ar_taller_servicio_tecnico.cod_nacion == ADcantones.codigo_nacion,
                ar_taller_servicio_tecnico.cod_canton == ADcantones.codigo_canton
            )
        )
        .filter(ar_taller_servicio_tecnico.anulado == status)
        .filter(ar_taller_servicio_tecnico.codigo_empresa == enterprise)
        .with_entities(
            ar_taller_servicio_tecnico.codigo.label('codigo'),
            ar_taller_servicio_tecnico.descripcion.label('taller'),
            ADprovincias.descripcion.label('provincia'),
            ADcantones.descripcion.label('canton'),
            ADcantones.codigo_canton.label('codigo_canton'),
            ADcantones.codigo_provincia.label('codigo_provincia')
        )
    )

    results = query.all()

    data = []
    for row in results:
        data.append({
            'codigo': row.codigo,
            'taller': row.taller,
            'provincia': row.provincia,
            'canton': row.canton,
            'codigo_canton': row.codigo_canton,
            'codigo_provincia': row.codigo_provincia
        })

    return jsonify(data), 200