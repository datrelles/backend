from sqlalchemy import Column, text, VARCHAR, DateTime, FetchedValue, ForeignKeyConstraint, and_
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import declarative_base, validates, relationship, foreign
from src.config.database import db
from src.enums import tipo_estado
from src.enums.validation import tipo_estado_activacion, cod_canal_activacion
from src.exceptions import validation_error
from src.models.clientes import Cliente, cliente_hor
from src.models.custom_base import custom_base
from src.models.proveedores import Proveedor
from src.validations import validar_number, validar_varchar, validar_fecha
from src.validations.alfanumericas import validar_hora, validar_celular, validar_correo

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido, valores_permitidos=tipo_estado.values())


def validar_cod_canal_activacion(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido,
                          valores_permitidos=cod_canal_activacion.values())

def validar_estado_activacion(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido,
                          valores_permitidos=tipo_estado_activacion.values())


def validar_escala(clave, valor, es_requerido=True, inicio=1, fin=5):
    return validar_number(clave, valor, 1, es_requerido=es_requerido, valores_permitidos=range(inicio, fin + 1))


def validar_observacion(clave, valor, es_requerido=False, longitud=500):
    return validar_varchar(clave, valor, longitud, es_requerido)


class ad_usuarios(custom_base):
    __tablename__ = 'ad_usuarios'
    __table_args__ = {'schema': 'jaher'}

    codigo_usuario = Column(VARCHAR(30), primary_key=True)
    identificacion = Column(VARCHAR(10), nullable=False)
    codigo_usuario_externo = Column(VARCHAR(10))


class st_cliente_direccion_guias(custom_base):
    __tablename__ = 'st_cliente_direccion_guias'
    __table_args__ = (
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_direccion'],
                             ['{}.st_bodega_consignacion.empresa'.format(schema_name),
                              '{}.st_bodega_consignacion.ruc_cliente'.format(schema_name),
                              '{}.st_bodega_consignacion.cod_direccion'.format(schema_name)]),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cliente = relationship(
        Cliente,
        primaryjoin=and_(
            empresa == foreign(Cliente.empresa),
            cod_cliente == foreign(Cliente.cod_cliente)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cliente_hor = relationship(
        cliente_hor,
        primaryjoin=and_(
            empresa == foreign(cliente_hor.empresah),
            cod_cliente == foreign(cliente_hor.cod_clienteh)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cod_direccion = Column(NUMBER(precision=3), primary_key=True)
    bodega = relationship(
        "st_bodega_consignacion",
        foreign_keys=[empresa, cod_cliente, cod_direccion],
        uselist=False,
        viewonly=True
    )
    ciudad = Column(VARCHAR(200), nullable=False)
    direccion = Column(VARCHAR(200))
    direccion_larga = Column(VARCHAR(500))
    cod_zona_ciudad = Column(VARCHAR(14))
    es_activo = Column(NUMBER(precision=1), nullable=False)
    nombre = Column(VARCHAR(100))

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_direccion')
    def validar_cod_direccion(self, key, value):
        return validar_number(key, value, 3)

    @validates('ciudad')
    def validar_ciudad(self, key, value):
        return validar_varchar(key, value, 200)

    @validates('direccion')
    def validar_direccion(self, key, value):
        return validar_varchar(key, value, 200, False)

    @validates('direccion_larga')
    def validar_direccion_larga(self, key, value):
        return validar_varchar(key, value, 200, False)

    @validates('cod_zona_ciudad')
    def validar_cod_zona_ciudad(self, key, value):
        return validar_varchar(key, value, 14, False)

    @validates('es_activo')
    def validar_es_activo(self, key, value):
        return validar_number(key, value, 1, valores_permitidos=[0, 1])

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 100, False)


class rh_empleados(custom_base):
    __tablename__ = 'rh_empleados'
    __table_args__ = {'schema': 'jaher'}

    identificacion = Column(VARCHAR(20), primary_key=True)
    apellido_paterno = Column(VARCHAR(25), nullable=False)
    apellido_materno = Column(VARCHAR(25), nullable=False)
    nombres = Column(VARCHAR(50), nullable=False)
    activo = Column(VARCHAR(1), nullable=False)


class st_bodega_consignacion(custom_base):
    __tablename__ = 'st_bodega_consignacion'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_bodega = Column(NUMBER(precision=4), primary_key=True)
    ruc_cliente = Column(VARCHAR(14), nullable=False)
    cod_direccion = Column(NUMBER(precision=3), nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
    responsable = Column(VARCHAR(60), nullable=False)
    correo_electronico = Column(VARCHAR(300))
    telefono1 = Column(VARCHAR(20), nullable=False)


class st_promotor_tienda(custom_base):
    __tablename__ = 'st_promotor_tienda'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_promotor = Column(VARCHAR(20), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cod_direccion_guia = Column(NUMBER(precision=3), primary_key=True)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)


class st_activacion(custom_base):
    __tablename__ = 'st_activacion'
    __table_args__ = (
        ForeignKeyConstraint(['cod_promotor'],
                             ['jaher.rh_empleados.identificacion']),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_cliente_direccion_guias.empresa'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_cliente'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_direccion'.format(schema_name)]),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_bodega_consignacion.empresa'.format(schema_name),
                              '{}.st_bodega_consignacion.ruc_cliente'.format(schema_name),
                              '{}.st_bodega_consignacion.cod_direccion'.format(schema_name)]),
        ForeignKeyConstraint(['empresa', 'cod_proveedor'],
                             ['proveedor.empresa', 'proveedor.cod_proveedor']),
        {'schema': schema_name}
    )

    cod_activacion = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    empresa = Column(NUMBER(precision=2))
    cod_promotor = Column(VARCHAR(20))
    promotor = relationship(
        "rh_empleados",
        foreign_keys=[cod_promotor]
    )
    cod_cliente = Column(VARCHAR(14))
    cliente = relationship(
        Cliente,
        primaryjoin=and_(
            empresa == foreign(Cliente.empresa),
            cod_cliente == foreign(Cliente.cod_cliente)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cliente_hor = relationship(
        cliente_hor,
        primaryjoin=and_(
            empresa == foreign(cliente_hor.empresah),
            cod_cliente == foreign(cliente_hor.cod_clienteh)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cod_tienda = Column(NUMBER(precision=3))
    tienda = relationship(
        st_cliente_direccion_guias,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
    )
    bodega = relationship(
        st_bodega_consignacion,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
        uselist=False
    )
    cod_proveedor = Column(VARCHAR(14))
    proveedor = relationship(
        Proveedor,
        foreign_keys=[empresa, cod_proveedor],
        viewonly=True,
        uselist=False
    )
    cod_modelo_act = Column(VARCHAR(8))
    cod_item_act = Column(VARCHAR(3))
    cod_canal = Column(NUMBER(precision=1))
    estado = Column(NUMBER(precision=1), server_default=text("0"))
    estados = relationship("st_estado_activacion", order_by="st_estado_activacion.cod_estado_act")
    hora_inicio = Column(VARCHAR(5), nullable=False)
    hora_fin = Column(VARCHAR(5), nullable=False)
    fecha_act = Column(DateTime, nullable=False)
    total_minutos = Column(NUMBER(precision=4))
    num_exhi_motos = Column(NUMBER(precision=3))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_activacion')
    def validar_cod_activacion(self, key, value):
        return validar_number(key, value, 22)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_promotor')
    def validar_cod_promotor(self, key, value):
        return validar_varchar(key, value, 20)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_tienda')
    def validar_cod_tienda(self, key, value):
        return validar_number(key, value, 3)

    @validates('cod_proveedor')
    def validar_cod_proveedor(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_modelo_act')
    def validar_cod_modelo_act(self, key, value):
        return validar_varchar(key, value, 8)

    @validates('cod_item_act')
    def validar_cod_item_act(self, key, value):
        return validar_varchar(key, value, 3)

    @validates('cod_canal')
    def validar_cod_canal(self, key, value):
        return validar_cod_canal_activacion(key, value)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado_activacion(key, value)

    @validates('hora_inicio')
    def validar_hora_inicio(self, key, value):
        return validar_hora(key, value)

    @validates('hora_fin')
    def validar_hora_fin(self, key, value):
        return validar_hora(key, value)

    @validates('fecha_act')
    def validar_fecha_act(self, key, value):
        return validar_fecha(key, value)

    @validates('num_exhi_motos')
    def validar_num_exhi_motos(self, key, value):
        return validar_number(key, value, 3, 0)


class st_estado_activacion(custom_base):
    __tablename__ = 'st_estado_activacion'
    __table_args__ = (
        ForeignKeyConstraint(['cod_activacion'],
                             ['{}.st_activacion.cod_activacion'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_estado_act = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    cod_activacion = Column(NUMBER(precision=22), nullable=False)
    estado = Column(NUMBER(precision=1), nullable=False)
    observacion = Column(VARCHAR(200))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))

    @validates('cod_activacion')
    def validar_cod_activacion(self, key, value):
        return validar_number(key, value, 22)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado_activacion(key, value)

    @validates('observacion')
    def validar_observacion(self, key, value):
        return validar_observacion(key, value, longitud=200)


class st_encuesta(custom_base):
    __tablename__ = 'st_encuesta'
    __table_args__ = (
        ForeignKeyConstraint(['cod_promotor'],
                             ['jaher.rh_empleados.identificacion']),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_cliente_direccion_guias.empresa'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_cliente'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_direccion'.format(schema_name)]),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_bodega_consignacion.empresa'.format(schema_name),
                              '{}.st_bodega_consignacion.ruc_cliente'.format(schema_name),
                              '{}.st_bodega_consignacion.cod_direccion'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_encuesta = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    empresa = Column(NUMBER(precision=2))
    cod_promotor = Column(VARCHAR(20))
    promotor = relationship(
        "rh_empleados",
        foreign_keys=[cod_promotor]
    )
    cod_cliente = Column(VARCHAR(14))
    cliente = relationship(
        Cliente,
        primaryjoin=and_(
            empresa == foreign(Cliente.empresa),
            cod_cliente == foreign(Cliente.cod_cliente)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cliente_hor = relationship(
        cliente_hor,
        primaryjoin=and_(
            empresa == foreign(cliente_hor.empresah),
            cod_cliente == foreign(cliente_hor.cod_clienteh)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cod_tienda = Column(NUMBER(precision=3))
    tienda = relationship(
        st_cliente_direccion_guias,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
        uselist=False
    )
    bodega = relationship(
        st_bodega_consignacion,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
        uselist=False
    )
    respuestas_multiples = relationship(
        "st_respuesta_multiple", order_by="st_respuesta_multiple.cod_pregunta"
    )
    limp_orden = Column(NUMBER(1), nullable=False)
    pop_actual = Column(NUMBER(1), nullable=False)
    pop_sufic = Column(NUMBER(3), nullable=False)
    prec_vis_corr = Column(NUMBER(1))
    motos_desper = Column(NUMBER(1), nullable=False)
    motos_falt = Column(NUMBER(1), nullable=False)
    motos_bat = Column(NUMBER(1), nullable=False)
    estado_publi = Column(NUMBER(1))
    conoc_portaf = Column(NUMBER(1), nullable=False)
    conoc_prod = Column(NUMBER(1), nullable=False)
    conoc_garan = Column(NUMBER(1), nullable=False)
    existe_promo = Column(NUMBER(1))
    conoc_promo = Column(NUMBER(1))
    confor_shine_j = Column(NUMBER(1))
    confor_shine_v = Column(NUMBER(1))
    confor_compe_j = Column(NUMBER(1))
    confor_compe_v = Column(NUMBER(1))
    conoc_shibot = Column(NUMBER(1), nullable=False)
    ubi_talleres = Column(NUMBER(1), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_encuesta')
    def validar_cod_encuesta(self, key, value):
        return validar_number(key, value, 22)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_promotor')
    def validar_cod_promotor(self, key, value):
        return validar_varchar(key, value, 20)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_tienda')
    def validar_cod_tienda(self, key, value):
        return validar_number(key, value, 3)

    @validates('limp_orden')
    def validar_limp_orden(self, key, value):
        return validar_escala(key, value)

    @validates('pop_actual')
    def validar_pop_actual(self, key, value):
        return validar_estado(key, value)

    @validates('pop_sufic')
    def validar_pop_sufic(self, key, value):
        return validar_number(key, value, 3, valores_permitidos=range(101))

    @validates('prec_vis_corr')
    def validar_prec_vis_corr(self, key, value):
        return validar_estado(key, value, es_requerido=False)

    @validates('motos_desper')
    def validar_motos_desper(self, key, value):
        return validar_estado(key, value)

    @validates('motos_falt')
    def validar_motos_falt(self, key, value):
        return validar_estado(key, value)

    @validates('motos_bat')
    def validar_motos_bat(self, key, value):
        return validar_estado(key, value)

    @validates('estado_publi')
    def validar_estado_publi(self, key, value):
        return validar_estado(key, value, es_requerido=False)

    @validates('conoc_portaf')
    def validar_conoc_portaf(self, key, value):
        return validar_escala(key, value)

    @validates('conoc_prod')
    def validar_conoc_prod(self, key, value):
        return validar_escala(key, value)

    @validates('conoc_garan')
    def validar_conoc_garan(self, key, value):
        return validar_escala(key, value)

    @validates('existe_promo')
    def validar_existe_promo(self, key, value):
        return validar_estado(key, value, es_requerido=False)

    @validates('conoc_promo')
    def validar_conoc_promo(self, key, value):
        return validar_estado(key, value, es_requerido=False)

    @validates('confor_shine_j')
    def validar_confor_shine_j(self, key, value):
        return validar_escala(key, value, es_requerido=False)

    @validates('confor_shine_v')
    def validar_confor_shine_v(self, key, value):
        return validar_escala(key, value, es_requerido=False)

    @validates('confor_compe_j')
    def validar_confor_compe_j(self, key, value):
        return validar_escala(key, value, es_requerido=False)

    @validates('confor_compe_v')
    def validar_confor_compe_v(self, key, value):
        return validar_escala(key, value, es_requerido=False)

    @validates('conoc_shibot')
    def validar_conoc_shibot(self, key, value):
        return validar_escala(key, value)

    @validates('ubi_talleres')
    def validar_ubi_talleres(self, key, value):
        return validar_estado(key, value)


class st_opcion_pregunta(custom_base):
    __tablename__ = 'st_opcion_pregunta'
    __table_args__ = ({'schema': schema_name})

    cod_pregunta = Column(NUMBER(precision=3), primary_key=True)
    orden = Column(NUMBER(precision=3), primary_key=True)
    opcion = Column(VARCHAR(100), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_pregunta')
    def validar_cod_pregunta(self, key, value):
        return validar_number(key, value, 3)

    @validates('orden')
    def validar_orden(self, key, value):
        return validar_number(key, value, 3)

    @validates('opcion')
    def validar_opcion(self, key, value):
        return validar_varchar(key, value, 100)


class st_respuesta_multiple(custom_base):
    __tablename__ = 'st_respuesta_multiple'
    __table_args__ = (
        ForeignKeyConstraint(['cod_encuesta'],
                             ['{}.st_encuesta.cod_encuesta'.format(schema_name)]),
        ForeignKeyConstraint(['cod_pregunta', 'opcion'],
                             ['{}.st_opcion_pregunta.cod_pregunta'.format(schema_name),
                              '{}.st_opcion_pregunta.orden'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_encuesta = Column(NUMBER(precision=22), primary_key=True)
    cod_pregunta = Column(NUMBER(precision=3), primary_key=True)
    opcion = Column(NUMBER(precision=3), primary_key=True)
    texto = Column(VARCHAR(100))
    numero = Column(NUMBER(8, 2))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))

    @validates('cod_encuesta')
    def validar_cod_encuesta(self, key, value):
        return validar_number(key, value, 22)

    @validates('cod_pregunta')
    def validar_cod_pregunta(self, key, value):
        return validar_number(key, value, 3)

    @validates('opcion')
    def validar_opcion(self, key, value):
        return validar_number(key, value, 3)

    @validates('texto')
    def validar_texto(self, key, value):
        return validar_varchar(key, value, 100, False)

    @validates('numero')
    def validar_numero(self, key, value):
        return validar_number(key, value, 8, 2, False)


class st_form_promotoria(custom_base):
    __tablename__ = 'st_form_promotoria'
    __table_args__ = (
        ForeignKeyConstraint(['cod_promotor'],
                             ['jaher.rh_empleados.identificacion']),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_cliente_direccion_guias.empresa'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_cliente'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_direccion'.format(schema_name)]),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_bodega_consignacion.empresa'.format(schema_name),
                              '{}.st_bodega_consignacion.ruc_cliente'.format(schema_name),
                              '{}.st_bodega_consignacion.cod_direccion'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_form = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    empresa = Column(NUMBER(precision=2))
    cod_promotor = Column(VARCHAR(20))
    promotor = relationship(
        "rh_empleados",
        foreign_keys=[cod_promotor]
    )
    cod_cliente = Column(VARCHAR(14))
    cliente = relationship(
        Cliente,
        primaryjoin=and_(
            empresa == foreign(Cliente.empresa),
            cod_cliente == foreign(Cliente.cod_cliente)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cliente_hor = relationship(
        cliente_hor,
        primaryjoin=and_(
            empresa == foreign(cliente_hor.empresah),
            cod_cliente == foreign(cliente_hor.cod_clienteh)
        ),
        foreign_keys=[empresa, cod_cliente],
        viewonly=True,
        uselist=False
    )
    cod_tienda = Column(NUMBER(precision=3))
    tienda = relationship(
        st_cliente_direccion_guias,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
        uselist=False
    )
    bodega = relationship(
        st_bodega_consignacion,
        foreign_keys=[empresa, cod_cliente, cod_tienda],
        viewonly=True,
        uselist=False
    )
    modelos_segmento = relationship(
        "st_mod_seg_frm_prom",
        back_populates="form_promotoria"
    )
    marcas_segmento = relationship(
        "st_mar_seg_frm_prom",
        back_populates="form_promotoria"
    )
    total_motos_piso = Column(NUMBER(3), nullable=False)
    total_motos_shi = Column(NUMBER(3), nullable=False)
    participacion = Column(NUMBER(5, 2))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_promotor')
    def validar_cod_promotor(self, key, value):
        return validar_varchar(key, value, 20)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_tienda')
    def validar_cod_tienda(self, key, value):
        return validar_number(key, value, 3)

    @validates('total_motos_piso')
    def validar_total_motos_piso(self, key, value):
        return validar_number(key, value, 3)

    @validates('total_motos_shi')
    def validar_total_motos_shi(self, key, value):
        return validar_number(key, value, 3)

    @validates('participacion')
    def validar_participacion(self, key, value):
        valor = validar_number(key, value, 3, 2, es_requerido=False, es_positivo=True)
        return round(valor, 2)


class st_mod_seg_frm_prom(custom_base):
    __tablename__ = 'st_mod_seg_frm_prom'
    __table_args__ = (
        ForeignKeyConstraint(['cod_form'],
                             ['{}.st_form_promotoria.cod_form'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_form = Column(NUMBER(precision=22), primary_key=True)
    form_promotoria = relationship("st_form_promotoria", back_populates="modelos_segmento")
    cod_segmento = Column(NUMBER(14), primary_key=True)
    cod_linea = Column(NUMBER(14), primary_key=True)
    cod_modelo_comercial = Column(NUMBER(14), primary_key=True)
    cod_marca = Column(NUMBER(14), primary_key=True)
    cantidad = Column(NUMBER(3, 0), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_form')
    def validar_cod_form(self, key, value):
        return validar_number(key, value, 22)

    @validates('cod_segmento')
    def validar_cod_segmento(self, key, value):
        return validar_number(key, value, 14)

    @validates('cod_linea')
    def validar_cod_linea(self, key, value):
        return validar_number(key, value, 14)

    @validates('cod_modelo_comercial')
    def validar_cod_modelo_comercial(self, key, value):
        return validar_number(key, value, 14)

    @validates('cod_marca')
    def validar_cod_marca(self, key, value):
        return validar_number(key, value, 14)

    @validates('cantidad')
    def validar_cantidad(self, key, value):
        return validar_number(key, value, 3)


class st_mar_seg_frm_prom(custom_base):
    __tablename__ = 'st_mar_seg_frm_prom'
    __table_args__ = (
        ForeignKeyConstraint(['cod_form'],
                             ['{}.st_form_promotoria.cod_form'.format(schema_name)]),
        {'schema': schema_name}
    )

    cod_form = Column(NUMBER(precision=22), primary_key=True)
    form_promotoria = relationship("st_form_promotoria", back_populates="marcas_segmento")
    cod_marca = Column(NUMBER(14), primary_key=True)
    nombre_segmento = Column(VARCHAR(70), primary_key=True)
    cantidad = Column(NUMBER(3, 0), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_form')
    def validar_cod_form(self, key, value):
        return validar_number(key, value, 22)

    @validates('cod_marca')
    def validar_cod_marca(self, key, value):
        return validar_number(key, value, 14)

    @validates('nombre_segmento')
    def validar_nombre_segmento(self, key, value):
        return validar_varchar(key, value, 70)

    @validates('cantidad')
    def validar_cantidad(self, key, value):
        return validar_number(key, value, 3)
