# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import relationship,deferred
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)


class Empresa(db.Model):
    __tablename__ = 'empresa'
    __table_args__ = {'schema': 'computo'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    pais = Column(VARCHAR(15), nullable=False)
    ciudad = Column(VARCHAR(20), nullable=False)
    direccion = Column(VARCHAR(40), nullable=False)
    telefono1 = Column(NUMBER(8, 0, False))
    telefono2 = Column(NUMBER(8, 0, False))
    fax = Column(NUMBER(8, 0, False))
    iva = Column(NUMBER(5, 2, True))
    ice = Column(NUMBER(5, 2, True))
    ise = Column(NUMBER(5, 2, True))
    contabilidad_consulta_inicial = Column(DateTime, nullable=False)
    contabilidad_consulta_final = Column(DateTime, nullable=False)
    contabilidad_modifica_inicial = Column(DateTime, nullable=False)
    contabilidad_modifica_final = Column(DateTime, nullable=False)
    inventario_consulta_inicial = Column(DateTime, nullable=False)
    inventario_consulta_final = Column(DateTime, nullable=False)
    inventario_modifica_inicial = Column(DateTime, nullable=False)
    inventario_modifica_final = Column(DateTime, nullable=False)
    ruc = Column(VARCHAR(13), nullable=False)
    moneda = Column(VARCHAR(20), nullable=False)
    signo_moneda = Column(VARCHAR(3), nullable=False)
    casilla = Column(VARCHAR(10))
    contador = Column(VARCHAR(40), nullable=False)
    interes = Column(NUMBER(5, 2, True))
    interes_mora = Column(NUMBER(5, 2, True))
    descuento = Column(NUMBER(5, 2, True))
    entrada = Column(NUMBER(5, 2, True))
    mensaje = Column(VARCHAR(100))
    numero_patronal = Column(VARCHAR(10))
    provincia = Column(VARCHAR(20), nullable=False)
    canton = Column(VARCHAR(20), nullable=False)
    parroquia = Column(VARCHAR(20))
    gerente_apellido1 = Column(VARCHAR(20), nullable=False)
    gerente_apellido2 = Column(VARCHAR(20))
    gerente_nombre = Column(VARCHAR(20))
    gerente_cedula = Column(VARCHAR(13))
    iess_patronal = Column(NUMBER(5, 2, True))
    iess_cesantia = Column(NUMBER(5, 2, True))
    iess_secap = Column(NUMBER(5, 2, True))
    iess_iece = Column(NUMBER(5, 2, True))
    comision_vendedores = Column(NUMBER(5, 2, True))
    comision_choferes = Column(NUMBER(5, 2, True))
    comision_supervisor = Column(NUMBER(5, 2, True))
    habitaciones = Column(NUMBER(4, 0, False))
    hotel_consulta_inicial = Column(DateTime, nullable=False)
    hotel_consulta_final = Column(DateTime, nullable=False)
    hotel_modifica_inicial = Column(DateTime, nullable=False)
    hotel_modifica_final = Column(DateTime, nullable=False)
    ecuasoft = Column(VARCHAR(120))
    forma = Column(NUMBER(2, 0, False))
    logo = Column(VARCHAR(50))
    valor_acciones = Column(NUMBER(12, 0, False))
    cod_tipo_persona = Column(VARCHAR(3))
    cod_persona = Column(VARCHAR(14))
    iess_personal = Column(NUMBER(5, 2, True))
    aa_ventas = Column(NUMBER(4, 0, False))
    factor_venta = Column(NUMBER(14, 2, True))
    color = Column(VARCHAR(3))

    def to_dict(empresa):
        return {
            'empresa': empresa.empresa,
            'nombre': empresa.nombre,
            'pais': empresa.pais,
            'ciudad': empresa.ciudad,
            'direccion': empresa.direccion,
            'telefono1': empresa.telefono1,
            'telefono2': empresa.telefono2,
            'fax': empresa.fax,
            'iva': (empresa.iva),
            'ice': (empresa.ice),
            'ise': (empresa.ise),
            'contabilidad_consulta_inicial': str(empresa.contabilidad_consulta_inicial),
            'contabilidad_consulta_final': str(empresa.contabilidad_consulta_final),
            'contabilidad_modifica_inicial': str(empresa.contabilidad_modifica_inicial),
            'contabilidad_modifica_final': str(empresa.contabilidad_modifica_final),
            'inventario_consulta_inicial': str(empresa.inventario_consulta_inicial),
            'inventario_consulta_final': str(empresa.inventario_consulta_final),
            'inventario_modifica_inicial': str(empresa.inventario_modifica_inicial),
            'inventario_modifica_final': str(empresa.inventario_modifica_final),
            'ruc': empresa.ruc,
            'moneda': empresa.moneda,
            'signo_moneda': empresa.signo_moneda,
            'casilla': empresa.casilla,
            'contador': empresa.contador,
            'interes': (empresa.interes),
            'interes_mora': (empresa.interes_mora),
            'descuento': (empresa.descuento),
            'entrada': (empresa.entrada),
            'mensaje': empresa.mensaje,
            'numero_patronal': empresa.numero_patronal,
            'provincia': empresa.provincia,
            'canton': empresa.canton,
            'parroquia': empresa.parroquia,
            'gerente_apellido1': empresa.gerente_apellido1,
            'gerente_apellido2': empresa.gerente_apellido2,
            'gerente_nombre': empresa.gerente_nombre,
            'gerente_cedula': empresa.gerente_cedula,
            'iess_patronal': (empresa.iess_patronal),
            'iess_cesantia': (empresa.iess_cesantia),
            'iess_secap': (empresa.iess_secap),
            'iess_iece': (empresa.iess_iece),
            'comision_vendedores': (empresa.comision_vendedores),
            'comision_choferes': (empresa.comision_choferes),
            'habitaciones': empresa.habitaciones,
            'hotel_consulta_inicial': str(empresa.hotel_consulta_inicial),
            'hotel_consulta_final': str(empresa.hotel_consulta_final),
            'hotel_modifica_inicial': str(empresa.hotel_modifica_inicial),
            'hotel_modifica_final': str(empresa.hotel_modifica_final),
            'ecuasoft': empresa.ecuasoft,
            'forma': empresa.forma,
            'logo': empresa.logo,
            'valor_acciones': (empresa.valor_acciones),
            'cod_tipo_persona': empresa.cod_tipo_persona,
            'cod_persona': empresa.cod_persona,
            'iess_personal' : empresa.iess_personal,
            'aa_ventas': empresa.aa_ventas,
            'factor_venta' : empresa.factor_venta,
            'color' : empresa.color 
        }


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'computo'}

    usuario_oracle = Column(VARCHAR(20), primary_key=True)
    apellido1 = Column(VARCHAR(20), nullable=False)
    apellido2 = Column(VARCHAR(20))
    nombre = Column(VARCHAR(20), nullable=False)
    empresa_actual = Column(ForeignKey('computo.empresa.empresa'), nullable=False)
    useridc = Column(VARCHAR(3), nullable=False, unique=True)
    toda_bodega = Column(VARCHAR(1))
    toda_empresa = Column(VARCHAR(1))
    agencia_actual = Column(NUMBER(4, 0, False))
    aa = Column(NUMBER(4, 0, False))
    e_mail = Column(VARCHAR(60))
    password = Column(VARCHAR(110))
    empresa = deferred(relationship(Empresa, backref = 'Usuario'))
    @classmethod
    def query(cls):
        return db.session.query(cls)

