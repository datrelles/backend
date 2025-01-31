from sqlalchemy import (Column, DateTime,
                        Index, VARCHAR,
                        NVARCHAR, text, CHAR,
                        Float, Unicode, ForeignKeyConstraint,
                        PrimaryKeyConstraint, CheckConstraint,  and_)
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
Base = declarative_base(metadata=db.metadata)
class st_prod_packing_list(Base):
    __tablename__ = 'ST_PROD_PACKING_LIST'
    __table_args__ = (
        Index("IND$_PROD_PACKI_LIST_MOTOR", "cod_motor"),
        Index("IND$_PROD_PACKI_LIST_MOTOR2", "cod_motor", "cod_producto", "empresa"),
        Index("IND$_PROD_PACKI_LIST_PRODUCTO", "cod_producto", "empresa"),
        Index("PK_PROD_PACKING_LIST", "cod_chasis", "cod_producto", "empresa"),
        Index("UK_PROD_PACKING_LIST_CHASIS", "cod_chasis"),
        Index("UK_PROD_PACKING_LIST_IMPRONT", "secuencia_impronta"),
        {'schema': 'stock'}
    )
    cod_chasis = Column(VARCHAR(30), primary_key=True)
    cod_motor = Column(VARCHAR(30), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    empresa = Column(NUMBER(precision=2, scale=0), nullable=False)
    fecha = Column(DateTime, nullable=False)
    es_disponible = Column(NUMBER(1, scale=0))
    es_anulado = Column(NUMBER(1, scale=0))
    adicionado_por = Column(VARCHAR(30), nullable=False)
    fecha_adicion = Column(DateTime, nullable=False)
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    eliminado_por = Column(VARCHAR(30))
    fecha_elimiacion = Column(DateTime)
    camvcpn = Column(VARCHAR(20))
    anio = Column(NUMBER(4, scale=0))
    cod_color = Column(VARCHAR(3))
    marca = Column(VARCHAR(30))
    cilindraje = Column(NUMBER(8, scale=2))
    tonelaje = Column(NUMBER(14, scale=2), default=0.25)
    ocupantes = Column(NUMBER(3, scale=0), default=2)
    modelo = Column(VARCHAR(100))
    clase = Column(VARCHAR(100), default='MOTOCICLETA')
    subclase = Column(VARCHAR(100))
    pais_origen = Column(VARCHAR(50), default='CHINA')
    secuencia_impronta = Column(NUMBER(14, scale=0))
    potencia = Column(VARCHAR(10))
    @classmethod
    def query(cls):
        return db.session.query(cls)
class st_casos_postventa(Base):
    __tablename__ = 'ST_CASOS_POSTVENTA'
    __table_args__ = (
        Index("IDX_CASOS_CANAL_VENTAS", "cod_canal", "empresa"),
        Index("IDX_CASOS_PERSONA", "cod_empleado", "cod_tipo_persona", "empresa"),
        Index("IDX_CASOS_PV_CIUDADES", "codigo_canton", "codigo_provincia"),
        Index("IDX_CASOS_PV_DURACION_PROB", "cod_tipo_problema", "empresa"),
        Index("IDX_CASOS_PV_EMPRESA_DIST", "cod_distribuidor"),
        Index("IDX_CASOS_PV_PACKI_MO", "cod_motor"),
        Index("IDX_CASOS_PV_PEDIDOS_CAB", "cod_pedido", "cod_tipo_pedido", "empresa"),
        Index("IDX_CASOS_PV_PRODUCTO", "empresa", "cod_producto"),
        Index("PK_CASOS_POSTVENTA", "cod_comprobante", "tipo_comprobante", "empresa"),
        {'schema': 'stock'}
    )
    empresa = Column(NUMBER(precision=4), nullable=False)
    tipo_comprobante = Column(VARCHAR(2), nullable=False)
    cod_comprobante = Column(VARCHAR(9), nullable=False, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    nombre_caso = Column(VARCHAR(60), nullable=False)
    descripcion = Column(VARCHAR(300), nullable=False)
    codigo_nacion = Column(NUMBER(3), nullable=False)
    codigo_provincia = Column(VARCHAR(6), nullable=False)
    codigo_canton = Column(VARCHAR(4), nullable=False)
    nombre_cliente = Column(VARCHAR(100), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    cod_motor = Column(VARCHAR(30), nullable=False)
    kilometraje = Column(NUMBER(14, 2), nullable=False)
    codigo_taller = Column(VARCHAR(30), nullable=False)
    codigo_responsable = Column(VARCHAR(30))
    cod_tipo_problema = Column(NUMBER(6), nullable=False)
    aplica_garantia = Column(NUMBER(1))
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    cod_distribuidor = Column(NUMBER(4))
    manual_garantia = Column(NUMBER(10))
    estado = Column(VARCHAR(2), nullable=False, server_default=text("'A'"))
    fecha_cierre = Column(DateTime)
    usuario_cierra = Column(VARCHAR(30))
    observacion_final = Column(VARCHAR(300))
    identificacion_cliente = Column(VARCHAR(14))
    telefono_contacto1 = Column(VARCHAR(20))
    telefono_contacto2 = Column(VARCHAR(20))
    telefono_contacto3 = Column(VARCHAR(20))
    e_mail1 = Column(VARCHAR(100))
    e_mail2 = Column(VARCHAR(100))
    cod_tipo_identificacion = Column(NUMBER(1))
    cod_agente = Column(VARCHAR(14))
    cod_pedido = Column(VARCHAR(9))
    cod_tipo_pedido = Column(VARCHAR(2))
    numero_guia = Column(VARCHAR(30))
    cod_distribuidor_cli = Column(VARCHAR(14))
    fecha_venta = Column(DateTime)
    es_cliente_contactado = Column(NUMBER(1), server_default=text("0"))
    cod_canal = Column(NUMBER(2))
    referencia = Column(NUMBER(2))
    aplica_excepcion = Column(NUMBER(1), server_default=text("0"))
    cod_empleado = Column(VARCHAR(14))
    cod_tipo_persona = Column(VARCHAR(3))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_casos_postventas_obs(Base):
    __tablename__ = 'ST_CASOS_POSTVENTAS_OBS'
    __table_args__ = (
        Index("IND_CASOS_POSTVENTAS01", "cod_comprobante", "tipo_comprobante", "empresa"),
        Index("PK_CASOS_POSTVENTAS_OBS", "cod_comprobante", "secuencia", "tipo_comprobante", "empresa"),
        {'schema': 'stock'}
    )
    empresa = Column(NUMBER(precision=4), nullable=False, primary_key=True)
    tipo_comprobante = Column(VARCHAR(2), nullable=False, primary_key=True)
    cod_comprobante = Column(VARCHAR(9), nullable=False, primary_key=True)
    secuencia = Column(NUMBER(3), nullable=False, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    usuario = Column(VARCHAR(30), nullable=False)
    observacion = Column(VARCHAR(1000), nullable=False)
    tipo = Column(VARCHAR(3), nullable=False)
    @classmethod
    def query(cls):
        return db.session.query(cls)

class vt_casos_postventas(Base):
    __tablename__ = 'vt_casos_postventas'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(precision=4), nullable=False)
    tipo_comprobante = Column(VARCHAR(2), nullable=False)
    cod_comprobante = Column(VARCHAR(9), nullable=False, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    nombre_caso = Column(VARCHAR(60), nullable=False)
    descripcion = Column(VARCHAR(300), nullable=False)
    codigo_responsable = Column(VARCHAR(30))
    responsable = Column(VARCHAR(100))  # Concatenated from apellido1 and nombre
    nombre_cliente = Column(VARCHAR(100), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    cod_motor = Column(VARCHAR(30), nullable=False)
    kilometraje = Column(NUMBER(14, 2), nullable=False)
    codigo_taller = Column(VARCHAR(30), nullable=False)
    taller = Column(VARCHAR(100))
    cod_tipo_problema = Column(NUMBER(6), nullable=False)
    aplica_garantia = Column(VARCHAR(2))  # Decoded value from 1 or 0 to 'SI' or 'NO'
    cod_distribuidor = Column(VARCHAR(14))
    distribuidor = Column(VARCHAR(100))  # Concatenated from apellido1 and nombre
    manual_garantia = Column(NUMBER(10))
    estado = Column(VARCHAR(2), nullable=False)
    nombre_estado = Column(VARCHAR(100))
    fecha_cierre = Column(DateTime)
    usuario_cierra = Column(VARCHAR(30))
    observacion_final = Column(VARCHAR(300))
    identificacion_cliente = Column(VARCHAR(14))
    telefono_contacto1 = Column(VARCHAR(20))
    telefono_contacto2 = Column(VARCHAR(20))
    telefono_contacto3 = Column(VARCHAR(20))
    e_mail1 = Column(VARCHAR(100))
    e_mail2 = Column(VARCHAR(100))
    producto = Column(VARCHAR(100))
    provincia = Column(VARCHAR(100))
    canton = Column(VARCHAR(100))
    dias_transcurridos = Column(NUMBER)  # Calculated value
    porcentaje_avance = Column(Float)  # Fetched using a function
    tipo_problema = Column(VARCHAR(100))
    numero_guia = Column(VARCHAR(30))
    codigo_provincia = Column(VARCHAR(6))
    codigo_canton = Column(VARCHAR(4))
    fecha_cierre_previo = Column(DateTime)
    fecha_venta = Column(DateTime)
    es_cliente_contactado = Column(VARCHAR(2))  # Decoded value from 1 or 0 to 'SI' or 'NO'
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_casos_tipo_problema(Base):
    __tablename__ = 'ST_CASOS_TIPO_PROBLEMA'
    __table_args__ = (
        Index("PK_ST_CASOS_TIPO_PROBLEMA", "cod_comprobante", "tipo_comprobante", "codigo_duracion"),
    )
    empresa = Column(NUMBER(precision=4), nullable=False)
    tipo_comprobante = Column(VARCHAR(2), nullable=False, primary_key=True)
    cod_comprobante = Column(VARCHAR(9), nullable=False, primary_key=True)
    codigo_duracion = Column(NUMBER(6), nullable=False, primary_key=True)
    estado = Column(NUMBER(1))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    descripcion = Column(VARCHAR(300), nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_casos_url(Base):
    __tablename__ = 'ST_CASOS_URL'
    __table_args__ = (
        Index("PK_ST_CASOS_URL", "empresa", "cod_comprobante", "tipo_comprobante", "secuencial"),
    )
    empresa = Column(NUMBER(precision=4), nullable=False, primary_key=True)
    cod_comprobante = Column(VARCHAR(9), nullable=False, primary_key=True)
    tipo_comprobante = Column(VARCHAR(2), nullable=False, primary_key=True)
    secuencial = Column(VARCHAR(6), nullable=False, primary_key=True)
    url_photos = Column(VARCHAR(300), nullable=False)
    url_videos = Column(VARCHAR(300), nullable=False)
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ArCiudades(Base):
    __tablename__ = 'AR_CIUDADES'
    __table_args__ = {'schema': 'JAHER'}

    codigo_ciudad = Column(NUMBER(precision=4), primary_key=True, nullable=False)
    codigo_provincia = Column(NUMBER(precision=4), primary_key=True, nullable=False)
    descripcion = Column(VARCHAR(50), nullable=False)
    anulado = Column(VARCHAR(1), nullable=False)
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)

    # Define relationship to AR_PROVINCIAS table if needed
    # provincia = relationship("ArProvincias", back_populates="ciudades")

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ADprovincias(Base):
    __tablename__ = 'AD_PROVINCIAS'
    __table_args__ = (
        Index("AD_PROVINCIAS_01_IDX", "codigo_nacion"),
        Index("AD_PROVINCIAS_02_IDX", "codigo_region"),
        {'schema': 'JAHER'}

    )
    codigo_provincia = Column(VARCHAR(6), primary_key=True)
    codigo_nacion = Column(NUMBER(3), nullable=False, primary_key=True)
    descripcion = Column(VARCHAR(100))
    codigo_region = Column(NUMBER(3), nullable=False)
    sigla = Column(VARCHAR(3))
    adicionado_por = Column(VARCHAR(30), nullable=False)
    fecha_adicion = Column(DateTime, nullable=False)
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ADcantones(Base):
    __tablename__ = 'AD_CANTONES'
    __table_args__ = (
        Index("AD_CANTONES_01_IDX", "codigo_provincia", "codigo_nacion"),
    )

    codigo_canton = Column(VARCHAR(4), primary_key=True)
    codigo_provincia = Column(VARCHAR(6), primary_key=True)
    codigo_nacion = Column(NUMBER(3), primary_key=True)
    descripcion = Column(VARCHAR(50), nullable=False)
    sigla = Column(VARCHAR(3))
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ar_taller_servicio_tecnico(Base):
    __tablename__ = 'AR_TALLER_SERVICIO_TECNICO'
    __table_args__ = (
        # Primary Key
        PrimaryKeyConstraint('codigo', 'codigo_empresa', name='PK_AR_TALLER_SERVICIO_TECNICO'),
        # Foreign Keys
        ForeignKeyConstraint(
            ['codigo_ciudad', 'codigo_provincia'],
            ['JAHER.AR_CIUDADES.CODIGO_CIUDAD', 'JAHER.AR_CIUDADES.CODIGO_PROVINCIA'],
            name='FK_AR_TAL_SER_TEC_COD_CIU'
        ),
        ForeignKeyConstraint(
            ['codigo_empresa', 'codigo_marca'],
            ['MARCA.EMPRESA', 'MARCA.COD_MARCA'],
            name='FK_AR_TAL_SER_TEC_COD_MARCA'
        ),
        ForeignKeyConstraint(
            ['codigo_empresa'],
            ['JAHER.AD_EMPRESAS.CODIGO_EMPRESA'],
            name='FK_AR_TAL_SER_TEC_EMPRESA'
        ),
        ForeignKeyConstraint(
            ['codigo_tipo_taller', 'codigo_empresa'],
            ['JAHER.AR_TIPOS_TECNICO.CODIGO_TIPO_TECNICO', 'JAHER.AR_TIPOS_TECNICO.CODIGO_EMPRESA'],
            name='FK_AR_TAL_SER_TEC_TIP_TAL'
        ),
        # Check Constraint
        CheckConstraint("anulado IN ('S','N')", name='CK_AR_TAL_SER_TEC_ANULADO'),
        # Esquema de la tabla
        {'schema': 'JAHER'}
    )

    # Columns
    codigo = Column(VARCHAR(30), nullable=False)
    codigo_empresa = Column(NUMBER(2), nullable=False)
    codigo_tipo_taller = Column(VARCHAR(1), nullable=False)
    descripcion = Column(VARCHAR(200), nullable=False)
    codigo_provincia = Column(NUMBER(4))
    codigo_ciudad = Column(NUMBER(4))
    codigo_marca = Column(NUMBER(3), nullable=False)
    nombre_contacto = Column(VARCHAR(200))
    telefono1 = Column(VARCHAR(12))
    extencion1 = Column(VARCHAR(5))
    telefono2 = Column(VARCHAR(12))
    extencion2 = Column(VARCHAR(5))
    telefono3 = Column(VARCHAR(12))
    extencion3 = Column(VARCHAR(5))
    email = Column(VARCHAR(60))
    email2 = Column(VARCHAR(60))
    email3 = Column(VARCHAR(60))
    anulado = Column(VARCHAR(1), nullable=False)
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    direccion = Column(VARCHAR(300))
    ruc = Column(VARCHAR(14), nullable=False)
    tipo_identificacion = Column(VARCHAR(1), nullable=False, server_default=text("'R'"))
    cod_canton = Column(VARCHAR(4))
    cod_provincia = Column(VARCHAR(6), nullable=False)
    cod_nacion = Column(NUMBER(3), nullable=False)
    es_taller_autorizado = Column(NUMBER(1), nullable=False, server_default=text("0"))
    tipo_taller = Column(NUMBER(1), nullable=False, server_default=text("0"))
    fecha_nacimiento = Column(DateTime)
    cupo_x_hora = Column(NUMBER(4), nullable=False, server_default=text("1"))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class ar_duracion_reparacion(Base):
    __tablename__ = 'AR_DURACION_REPARACION'
    __table_args__ = (
        PrimaryKeyConstraint('codigo_duracion', 'codigo_empresa', name='PK_AR_DUR_REP_COD_DUR_COD_EMP'),
        ForeignKeyConstraint(
            ['codigo_empresa'],
            ['JAHER.AD_EMPRESAS.CODIGO_EMPRESA'],
            name='FK_AR_DUR_REP_COD_EMP'
        ),
        CheckConstraint("anulado IN ('S','N')", name='CK_AR_DUR_REP_ANULADO'),
        CheckConstraint("tipo_duracion IN ('D','H','N')", name='CK_AR_DUR_REP_TIP_DUR'),
        {'schema': 'JAHER'}
    )

    codigo_duracion = Column(NUMBER(6), nullable=False)
    codigo_empresa = Column(NUMBER(2), nullable=False)
    descripcion = Column(VARCHAR(200), nullable=False)
    duracion = Column(NUMBER(3), nullable=False)
    anulado = Column(VARCHAR(1), nullable=False)
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER"))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    tipo_duracion = Column(VARCHAR(1), nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)
