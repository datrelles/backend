# coding: utf-8
from sqlalchemy import FetchedValue
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.models.clientes import cliente_hor

from src.config.database import db
from marshmallow import Schema, fields, validate, EXCLUDE, ValidationError, validates_schema, pre_load

Base = declarative_base(metadata = db.metadata)

class STRuta(db.Model):
    __tablename__ = "ST_RUTAS"
    cod_ruta = db.Column(
        "COD_RUTA",
        db.Integer,
        Sequence("SEQ_ST_RUTAS"),
        primary_key=True,
        autoincrement=True
    )
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)
    id = db.Column("ID", db.String(20))
    nombre = db.Column("NOMBRE", db.String(200))
    @staticmethod
    def identity_key(cod_ruta: int, empresa: int):
        return (cod_ruta, empresa)

class RutaOutSchema(Schema):
    cod_ruta = fields.Integer()
    empresa = fields.Integer()
    id = fields.String(allow_none=True)
    nombre = fields.String(allow_none=True)

class RutaCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    nombre = fields.String(required=False, allow_none=True, validate=validate.Length(max=200))

class RutaUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa = fields.Integer()
    cod_ruta = fields.Integer()

    nombre = fields.String(required=False, allow_none=True, validate=validate.Length(max=200))

class STDireccionRuta(db.Model):
    __tablename__ = "ST_DIRECCION_RUTAS"
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)
    cod_cliente = db.Column("COD_CLIENTE", db.String(14), primary_key=True)
    cod_direccion = db.Column("COD_DIRECCION", db.Integer, primary_key=True)
    cod_ruta = db.Column("COD_RUTA", db.Integer, primary_key=True)

class DirRutaOutSchema(Schema):
    empresa = fields.Integer()
    cod_cliente = fields.String()
    cod_direccion = fields.Integer()
    cod_ruta = fields.Integer()

class DirRutaCreateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_cliente = fields.String(required=True, validate=validate.Length(max=14))
    cod_direccion = fields.Integer(required=True)
    cod_ruta = fields.Integer(required=True)

class DirRutaDetailSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_cliente = fields.String(required=True, validate=validate.Length(max=14))
    cod_direccion = fields.Integer(required=True)
    cod_ruta = fields.Integer(required=True)

class DirRutaSearchSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer()
    cod_cliente = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()
    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

class DirRutaDeleteSchema(DirRutaDetailSchema):
    pass

class STTransportistaRuta(db.Model):
    __tablename__ = "ST_TRANSPORTISTA_RUTA"

    codigo = db.Column(
        "CODIGO",
        db.Integer,
        Sequence("SEQ_ST_TRANSPORTISTA_RUTA"),
        primary_key=True,
        autoincrement=True
    )
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)
    cod_transportista = db.Column("COD_TRANSPORTISTA", db.String(14))
    cod_ruta = db.Column("COD_RUTA", db.Integer)

class TRutaOutSchema(Schema):
    codigo = fields.Integer()
    empresa = fields.Integer()
    cod_transportista = fields.String(allow_none=True)
    cod_ruta = fields.Integer(allow_none=True)

class TRutaCreateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_transportista = fields.String(required=True, validate=validate.Length(max=14))
    cod_ruta = fields.Integer(required=True)

class TRutaDetailSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    codigo = fields.Integer(required=True)

class TRutaUpdateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    codigo = fields.Integer(required=True)
    cod_transportista = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()

class TRutaSearchSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer()
    cod_transportista = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()
    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

class TRutaDeleteSchema(TRutaDetailSchema):
    pass

#############VISTA DESPACHOS FINAL##############################################

ALLOWED_ORDERING_FIELDS = [
    "fecha_est_desp", "fecha_despacho", "fecha_envio", "fecha_entrega",
    "cod_pedido", "cod_orden", "cod_ruta"
]

class DespachoSearchIn(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa = fields.Integer(required=True)
    cod_ruta = fields.Integer()
    cod_despacho = fields.Integer()
    cod_tipo_pedido = fields.String(validate=validate.Length(max=4))
    cod_pedido = fields.String(validate=validate.Length(max=30))
    cod_tipo_orden = fields.String(validate=validate.Length(max=4))
    cod_orden = fields.String(validate=validate.Length(max=14))
    cod_cliente = fields.String(validate=validate.Length(max=14))
    cod_producto = fields.String(validate=validate.Length(max=30))
    cadena = fields.String(validate=validate.OneOf(["RETAIL","MAYOREO"]))
    fac_con = fields.String(validate=validate.OneOf(["CONSIGNACION","FACTURACION"]))
    transportista = fields.String()
    destino = fields.String()
    ruta = fields.String()
    bod_destino = fields.String()
    modelo = fields.String()
    numero_serie = fields.String()

    en_despacho = fields.Integer(validate=validate.OneOf([0,1]))
    despachada = fields.Integer(validate=validate.OneOf([0,1]))

    date_field = fields.String(load_default="fecha_est_desp",
                               validate=validate.OneOf(["fecha_est_desp","fecha_despacho","fecha_envio","fecha_entrega"]))
    fecha_desde = fields.Date()
    fecha_hasta = fields.Date()

    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

    ordering = fields.String()

    def validate_ordering(self, value):
        if not value:
            return
        for token in value.split(","):
            key = token.strip().lstrip("-")
            if key not in ALLOWED_ORDERING_FIELDS:
                raise ValidationError(f"Campo de ordenamiento no permitido: {key}")

class DespachoRowOut(Schema):
    empresa = fields.Integer()
    cod_despacho = fields.Integer()
    cod_tipo_pedido = fields.String()
    cod_pedido = fields.String()
    cod_tipo_orden = fields.String()
    cod_orden = fields.String()
    tipo_pretransferencia = fields.String(allow_none=True)
    cod_pretransferencia = fields.String(allow_none=True)
    cod_guia_des = fields.String(allow_none=True)
    cod_tipo_guia_des = fields.String(allow_none=True)
    fecha_agrega = fields.DateTime(allow_none=True)
    fecha_est_desp = fields.DateTime(allow_none=True)
    fecha_despacho = fields.DateTime(allow_none=True)
    fecha_envio = fields.DateTime(allow_none=True)
    fecha_entrega = fields.DateTime(allow_none=True)
    fac_con = fields.String()
    cod_ruta = fields.Integer(allow_none=True)
    ruta = fields.String(allow_none=True)
    bod_destino = fields.String(allow_none=True)
    cadena = fields.String(allow_none=True)
    cliente = fields.String(allow_none=True)
    ruc_cliente = fields.String(allow_none=True)
    destino = fields.String(allow_none=True)
    transportista = fields.String(allow_none=True)
    producto = fields.String(allow_none=True)
    cod_producto = fields.String(allow_none=True)
    cantidad_x_enviar = fields.Decimal(as_string=True, allow_none=True)
    modelo = fields.String(allow_none=True)
    cod_color = fields.String(allow_none=True)
    numero_serie = fields.String(allow_none=True)
    nombre = fields.String(allow_none=True)
    en_despacho = fields.Integer()
    despachada = fields.Integer()
    cod_ddespacho = fields.Integer(allow_none=True)
    cod_guia_envio = fields.String(allow_none=True)
    tipo_guia_envio = fields.String(allow_none=True)

class STClienteDireccionGuias(db.Model):
    __tablename__ = "ST_CLIENTE_DIRECCION_GUIAS"

    empresa         = db.Column("EMPRESA", db.Integer, nullable=False)
    cod_cliente     = db.Column("COD_CLIENTE", db.String(14), nullable=False)
    ciudad          = db.Column("CIUDAD", db.String(200), nullable=False)
    direccion       = db.Column("DIRECCION", db.String(200))
    direccion_larga = db.Column("DIRECCION_LARGA", db.String(500))
    cod_direccion   = db.Column("COD_DIRECCION", db.Integer, nullable=False)
    cod_zona_ciudad = db.Column("COD_ZONA_CIUDAD", db.String(14))
    es_activo       = db.Column("ES_ACTIVO", db.Integer, nullable=False, server_default="1")
    nombre          = db.Column("NOMBRE", db.String(100))

    __table_args__ = (
        db.PrimaryKeyConstraint("EMPRESA", "COD_CLIENTE", "COD_DIRECCION",
                                name="PK_CLIENTE_DIRECCION_GUIAS"),
        db.ForeignKeyConstraint(
            ["EMPRESA", "COD_CLIENTE"],
            ["STOCK.CLIENTE_HOR.empresah", "STOCK.CLIENTE_HOR.cod_clienteh"],
            name="FK_CLIENTE_DIRECCION_CLIENTE"
        ),
        db.Index("IND_CLIENTE_DIRECCION_GUIAS01", "EMPRESA", "COD_CLIENTE"),
    )
    cliente = relationship(
        cliente_hor,
        viewonly=True,
        lazy="select",
    )

class STClienteDireccionGuiasSearchIn(Schema):
    empresa = fields.Int(required=False)
    cod_cliente = fields.Str(required=False, validate=validate.Length(max=14))
    cod_direccion = fields.Int(required=False)
    cod_zona_ciudad = fields.Str(required=False, validate=validate.Length(max=14))
    es_activo = fields.Int(required=False, validate=validate.OneOf([0, 1]))

    ciudad = fields.Str(required=False)
    direccion = fields.Str(required=False)
    direccion_larga = fields.Str(required=False)
    nombre = fields.Str(required=False)

    q = fields.Str(required=False)

    ordering = fields.List(fields.Str(), required=False)  # p.ej. ["-ciudad", "cod_cliente"]
    page = fields.Int(load_default=1)
    page_size = fields.Int(load_default=20)

class STClienteDireccionGuiasOut(Schema):
    empresa = fields.Int()
    cod_cliente = fields.Str()
    ciudad = fields.Str(allow_none=True)
    direccion = fields.Str(allow_none=True)
    direccion_larga = fields.Str(allow_none=True)
    cod_direccion = fields.Int()
    cod_zona_ciudad = fields.Str(allow_none=True)
    es_activo = fields.Int(allow_none=True)
    nombre = fields.Str(allow_none=True)

class STCDespachoEntrega(db.Model):
    __tablename__ = "ST_CDESPACHO_ENTREGA"
    empresa           = db.Column("EMPRESA", db.Integer, nullable=False, primary_key=True)
    cde_codigo = db.Column(
        "CDE_CODIGO",
        db.Integer,
        Sequence("SEQ_STC_DESPACHO_ENTREGA"),
        primary_key=True,
        autoincrement=True
    )
    fecha             = db.Column("FECHA", db.Date)
    usuario           = db.Column("USUARIO", db.String(20))
    cod_ruta          = db.Column("COD_RUTA", db.Integer)
    observacion       = db.Column("OBSERVACION", db.String(200))
    cod_persona       = db.Column("COD_PERSONA", db.String(14))
    cod_tipo_persona  = db.Column("COD_TIPO_PERSONA", db.String(3))
    cod_transportista = db.Column("COD_TRANSPORTISTA", db.String(14))
    finalizado        = db.Column("FINALIZADO", db.Integer, server_default="0")

    __table_args__ = (
        db.PrimaryKeyConstraint("CDE_CODIGO", "EMPRESA", name="PK_CDESPACHO_ENTREGA"),
        db.ForeignKeyConstraint(
            ["COD_RUTA", "EMPRESA"],
            ["ST_RUTAS.COD_RUTA", "ST_RUTAS.EMPRESA"],
            name="FK_CDESPACHO_ENTREG_RUTA"
        ),
    )

class CDECreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa = fields.Int(required=True)
    cde_codigo = fields.Int(dump_only=True)
    fecha = fields.Date(required=False)
    usuario = fields.Str(required=False, validate=validate.Length(max=20))
    cod_ruta = fields.Int(required=False)
    observacion = fields.Str(required=False, validate=validate.Length(max=200))
    cod_persona = fields.Str(required=True, validate=validate.Length(max=14))
    cod_tipo_persona = fields.Str(required=True, validate=validate.Length(max=3))
    cod_transportista = fields.Str(required=False, validate=validate.Length(max=14))
    finalizado = fields.Int(required=False, validate=validate.OneOf([0, 1]))

    @pre_load
    def drop_cde_codigo_if_present(self, in_data, **kwargs):
        in_data.pop("cde_codigo", None)
        return in_data


class CDEUpdateSchema(Schema):
    fecha             = fields.Date(required=True)
    usuario           = fields.Str(required=False, validate=validate.Length(max=20))
    cod_ruta          = fields.Int(required=False)
    observacion       = fields.Str(required=False, validate=validate.Length(max=200))
    cod_persona       = fields.Str(required=True, validate=validate.Length(max=14))
    cod_tipo_persona  = fields.Str(required=True, validate=validate.Length(max=3))
    cod_transportista = fields.Str(required=False, validate=validate.Length(max=14))
    finalizado        = fields.Int(required=False, validate=validate.OneOf([0,1]))

class CDEQuerySchema(Schema):
    page              = fields.Int(load_default=1)
    page_size         = fields.Int(load_default=20)
    empresa           = fields.Int(required=False)
    cde_codigo        = fields.Int(required=False)
    cod_ruta          = fields.Int(required=False)
    cod_persona       = fields.Str(required=False)
    cod_tipo_persona  = fields.Str(required=False)
    cod_transportista = fields.Str(required=False)
    finalizado        = fields.Int(required=False, validate=validate.OneOf([0,1]))

class CDEOutSchema(Schema):
    empresa = fields.Int()
    cde_codigo = fields.Int()
    cod_transportista = fields.Str()
    cod_ruta = fields.Int()

class STDDespachoEntrega(db.Model):
    __tablename__ = "ST_DDESPACHO_ENTREGA"

    empresa    = db.Column("EMPRESA", db.Integer, primary_key=True, nullable=False)
    cde_codigo = db.Column("CDE_CODIGO", db.Integer, primary_key=True, nullable=False)

    secuencia  = db.Column(
        "SECUENCIA",
        db.Integer,
        primary_key=True,
        nullable=False,
        server_default=FetchedValue()
    )
    cod_ddespacho = db.Column("COD_DDESPACHO", db.Integer)
    cod_producto  = db.Column("COD_PRODUCTO", db.String(14))
    numero_serie  = db.Column("NUMERO_SERIE", db.String(40))
    fecha         = db.Column("FECHA", db.Date)
    observacion   = db.Column("OBSERVACION", db.String(200))

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["CDE_CODIGO", "EMPRESA"],
            ["ST_CDESPACHO_ENTREGA.CDE_CODIGO", "ST_CDESPACHO_ENTREGA.EMPRESA"],
            name="FK_DDESPACHO_ENT_CDESPACHOP"
        ),
        db.ForeignKeyConstraint(
            ["COD_DDESPACHO", "EMPRESA"],
            ["ST_DDESPACHO.COD_DDESPACHO", "ST_DDESPACHO.EMPRESA"],
            name="FK_DDESPACHO_ENT_DDESPACHO"
        ),
    )

    __mapper_args__ = {"eager_defaults": True}

    cabecera = relationship(
        "STCDespachoEntrega",
        primaryjoin="and_(STDDespachoEntrega.empresa==STCDespachoEntrega.empresa, "
                    "STDDespachoEntrega.cde_codigo==STCDespachoEntrega.cde_codigo)",
        backref="detalles"
    )

    ddespacho = relationship(
        "STDDespacho",
        primaryjoin="and_(STDDespachoEntrega.empresa==STDDespacho.empresa, "
                    "STDDespachoEntrega.cod_ddespacho==STDDespacho.cod_ddespacho)",
        viewonly=True
    )
class DDECreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa        = fields.Int(required=True)
    cde_codigo     = fields.Int(required=True)
    cod_ddespacho  = fields.Int(allow_none=True)
    cod_producto   = fields.Str(allow_none=True)
    numero_serie   = fields.Str(allow_none=True)
    fecha          = fields.Date(allow_none=True)
    observacion    = fields.Str(allow_none=True)

    secuencia      = fields.Int(dump_only=True)

    @pre_load
    def drop_secuencia(self, in_data, **kwargs):
        in_data.pop("secuencia", None)
        return in_data

class STCDespacho(db.Model):
    __tablename__  = "ST_CDESPACHO"

    empresa           = db.Column("EMPRESA", db.Integer, primary_key=True, nullable=False)
    cod_despacho      = db.Column("COD_DESPACHO", db.Integer, primary_key=True, nullable=False)
    cod_pedido        = db.Column("COD_PEDIDO", db.String(9))
    cod_tipo_pedido   = db.Column("COD_TIPO_PEDIDO", db.String(2))
    cod_orden         = db.Column("COD_ORDEN", db.String(9))
    cod_tipo_orden    = db.Column("COD_TIPO_ORDEN", db.String(2))
    cod_producto      = db.Column("COD_PRODUCTO", db.String(14))
    fecha_agrega      = db.Column("FECHA_AGREGA", db.Date)
    fecha_est_desp    = db.Column("FECHA_EST_DESP", db.Date)
    fecha_entrega     = db.Column("FECHA_ENTREGA", db.Date)
    usr_agrega        = db.Column("USR_AGREGA", db.String(20))
    bodega_ini        = db.Column("BODEGA_INI", db.Integer)
    bodega_destino    = db.Column("BODEGA_DESTINO", db.Integer)
    cod_cliente       = db.Column("COD_CLIENTE", db.String(14))
    cod_ruta          = db.Column("COD_RUTA", db.Integer)
    cod_transportista = db.Column("COD_TRANSPORTISTA", db.String(14))
    en_despacho       = db.Column("EN_DESPACHO", db.Integer)
    es_despachada     = db.Column("ES_DESPACHADA", db.Integer)
    secuencia         = db.Column("SECUENCIA", db.Integer)
    cod_direccion_cli = db.Column("COD_DIRECCION_CLI", db.Integer)

class CDCUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    cod_pedido        = fields.Str(allow_none=True, validate=validate.Length(max=9))
    cod_tipo_pedido   = fields.Str(allow_none=True, validate=validate.Length(max=2))
    cod_orden         = fields.Str(allow_none=True, validate=validate.Length(max=9))
    cod_tipo_orden    = fields.Str(allow_none=True, validate=validate.Length(max=2))
    cod_producto      = fields.Str(allow_none=True, validate=validate.Length(max=14))
    fecha_agrega      = fields.Date(allow_none=True)       # 'YYYY-MM-DD'
    fecha_est_desp    = fields.Date(allow_none=True)
    fecha_entrega     = fields.Date(allow_none=True)
    usr_agrega        = fields.Str(allow_none=True, validate=validate.Length(max=20))
    bodega_ini        = fields.Int(allow_none=True)
    bodega_destino    = fields.Int(allow_none=True)
    cod_cliente       = fields.Str(allow_none=True, validate=validate.Length(max=14))
    cod_ruta          = fields.Int(allow_none=True)
    cod_transportista = fields.Str(allow_none=True, validate=validate.Length(max=14))
    en_despacho       = fields.Int(allow_none=True, validate=validate.OneOf([0,1]))
    es_despachada     = fields.Int(allow_none=True, validate=validate.OneOf([0,1]))
    secuencia         = fields.Int(allow_none=True)
    cod_direccion_cli = fields.Int(allow_none=True)
    empresa      = fields.Int(load_only=True)
    cod_despacho = fields.Int(load_only=True)

    @staticmethod
    def require_any_editable(data: dict) -> bool:
        editable = {
            "cod_pedido","cod_tipo_pedido","cod_orden","cod_tipo_orden","cod_producto",
            "fecha_agrega","fecha_est_desp","fecha_entrega","usr_agrega",
            "bodega_ini","bodega_destino","cod_cliente","cod_ruta","cod_transportista",
            "en_despacho","es_despachada","secuencia","cod_direccion_cli"
        }
        return any(k in data for k in editable)


class CDCOutSchema(Schema):
    empresa           = fields.Int()
    cod_despacho      = fields.Int()
    cod_pedido        = fields.Str()
    cod_tipo_pedido   = fields.Str()
    cod_orden         = fields.Str()
    cod_tipo_orden    = fields.Str()
    cod_producto      = fields.Str()
    fecha_agrega      = fields.Date(allow_none=True)
    fecha_est_desp    = fields.Date(allow_none=True)
    fecha_entrega     = fields.Date(allow_none=True)
    usr_agrega        = fields.Str()
    bodega_ini        = fields.Int()
    bodega_destino    = fields.Int()
    cod_cliente       = fields.Str()
    cod_ruta          = fields.Int()
    cod_transportista = fields.Str()
    en_despacho       = fields.Int()
    es_despachada     = fields.Int()
    secuencia         = fields.Int()
    cod_direccion_cli = fields.Int()
class STDDespacho(db.Model):
    __tablename__ = "ST_DDESPACHO"

    empresa       = db.Column("EMPRESA", db.Integer, primary_key=True, nullable=False)
    cod_ddespacho = db.Column("COD_DDESPACHO", db.Integer, primary_key=True, nullable=False)
    cod_despacho         = db.Column("COD_DESPACHO", db.Integer)
    cod_producto         = db.Column("COD_PRODUCTO", db.String(14))
    numero_serie         = db.Column("NUMERO_SERIE", db.String(30))
    fecha_despacho       = db.Column("FECHA_DESPACHO", db.Date)
    usuario_despacha     = db.Column("USUARIO_DESPACHA", db.String(50))
    cod_comprobante      = db.Column("COD_COMPROBANTE", db.String(20))
    tipo_comprobante     = db.Column("TIPO_COMPROBANTE", db.String(2))
    en_despacho          = db.Column("EN_DESPACHO", db.Integer, server_default="0")
    despachada           = db.Column("DESPACHADA", db.Integer, server_default="0")
    cod_comprobante_gui  = db.Column("COD_COMPROBANTE_GUI", db.String(20))
    tipo_comprobante_gui = db.Column("TIPO_COMPROBANTE_GUI", db.String(2))
    cod_guia_des         = db.Column("COD_GUIA_DES", db.String(20))
    cod_tipo_guia_des    = db.Column("COD_TIPO_GUIA_DES", db.String(2))
    fecha_entrega = db.Column("FECHA_ENTREGA", db.Date)
    observacion_entrega = db.Column("OBSERVACION_ENTREGA", db.String(500))

    __table_args__ = (
        db.PrimaryKeyConstraint("COD_DDESPACHO", "EMPRESA", name="PK_ST_DDESPACHO"),
        db.ForeignKeyConstraint(
            ["COD_DESPACHO", "EMPRESA"],
            ["ST_CDESPACHO.COD_DESPACHO", "ST_CDESPACHO.EMPRESA"],
            name="FK_DDESPACHO_ST_DESPACHO"
        ),
    )
class DDEUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    cod_ddespacho  = fields.Int(allow_none=True)
    cod_producto   = fields.Str(allow_none=True)
    numero_serie   = fields.Str(allow_none=True)
    fecha          = fields.Date(allow_none=True)
    observacion    = fields.Str(allow_none=True)
    empresa        = fields.Int(load_only=True)
    cde_codigo     = fields.Int(load_only=True)
    secuencia      = fields.Int(load_only=True)

    @validates_schema
    def forbid_keys(self, data, **kwargs):
        forbidden = [k for k in ("empresa", "cde_codigo", "secuencia") if k in data]
        if forbidden:
            raise ValidationError({f: ["Campo no editable."] for f in forbidden})

class DDEListBodySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa    = fields.Int(required=True)
    cde_codigo = fields.Int(required=True)
    page     = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=200))
class DDEOutSchema(Schema):
    empresa        = fields.Int()
    cde_codigo     = fields.Int()
    secuencia      = fields.Int()
    cod_ddespacho  = fields.Int(allow_none=True)
    cod_producto   = fields.Str(allow_none=True)
    numero_serie   = fields.Str(allow_none=True)
    fecha          = fields.Date(allow_none=True)
    observacion    = fields.Str(allow_none=True)

###################################GENERACION DE GUIAS FINAL################################################
class GenGuiasSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa  = fields.Int(required=True)
    despacho = fields.Int(required=True)


class TGAgenciaPersona(db.Model):
    __tablename__  = "TG_AGENCIA_PERSONA"
    __table_args__ = (
        db.PrimaryKeyConstraint(
            "COD_PERSONA", "COD_TIPO_PERSONA", "COD_AGENCIA", "EMPRESA",
            name="PK_TG_AGENCIA_PERSONA"
        ),
        {"schema": "COMPUTO"},
    )
    cod_persona      = db.Column("COD_PERSONA", db.String(14), primary_key=True)
    cod_tipo_persona = db.Column("COD_TIPO_PERSONA", db.String(3),  primary_key=True)
    cod_agencia      = db.Column("COD_AGENCIA", db.Integer,        primary_key=True)
    empresa          = db.Column("EMPRESA", db.Integer,            primary_key=True)

class Usuario(db.Model):
    __tablename__  = "USUARIO"
    __table_args__ = {"schema": "COMPUTO"}
    usuario_oracle = db.Column("USUARIO_ORACLE", db.String(20), primary_key=True)

class TGUsuarioVend(db.Model):
    __tablename__  = "TG_USUARIO_VEND"
    __table_args__ = (
        db.PrimaryKeyConstraint(
            "COD_PERSONA","COD_TIPO_PERSONA","COD_AGENCIA","EMPRESA","USUARIO_ORACLE",
            name="PK_USU_VEND"
        ),
        db.ForeignKeyConstraint(
            ["COD_PERSONA","COD_TIPO_PERSONA","COD_AGENCIA","EMPRESA"],
            ["COMPUTO.TG_AGENCIA_PERSONA.COD_PERSONA",
             "COMPUTO.TG_AGENCIA_PERSONA.COD_TIPO_PERSONA",
             "COMPUTO.TG_AGENCIA_PERSONA.COD_AGENCIA",
             "COMPUTO.TG_AGENCIA_PERSONA.EMPRESA"],
            name="FK_VEND_PERSONA"
        ),
        db.ForeignKeyConstraint(
            ["USUARIO_ORACLE"],
            ["COMPUTO.USUARIO.USUARIO_ORACLE"],
            name="FK_VEND_USUARIO"
        ),
        {"schema": "COMPUTO"},
    )

    cod_persona      = db.Column("COD_PERSONA", db.String(14), nullable=False, primary_key=True)
    cod_tipo_persona = db.Column("COD_TIPO_PERSONA", db.String(3),  nullable=False, primary_key=True)
    cod_agencia      = db.Column("COD_AGENCIA", db.Integer,        nullable=False, primary_key=True)
    empresa          = db.Column("EMPRESA", db.Integer,            nullable=False, primary_key=True)
    usuario_oracle   = db.Column("USUARIO_ORACLE", db.String(20),  nullable=False, primary_key=True)

class TGUVCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    cod_persona      = fields.Str(required=True, validate=validate.Length(max=14))
    cod_tipo_persona = fields.Str(required=True, validate=validate.Length(max=3))
    cod_agencia      = fields.Int(required=True)
    empresa          = fields.Int(required=True)
    usuario_oracle   = fields.Str(required=True, validate=validate.Length(max=20))

class TGUVOutSchema(Schema):
    cod_persona      = fields.Str()
    cod_tipo_persona = fields.Str()
    cod_agencia      = fields.Int()
    empresa          = fields.Int()
    usuario_oracle   = fields.Str()

class TGUVSearchSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    # filtros
    cod_persona      = fields.Str(validate=validate.Length(max=14))
    cod_tipo_persona = fields.Str(validate=validate.Length(max=3))
    cod_agencia      = fields.Int()
    empresa          = fields.Int()
    usuario_oracle   = fields.Str(validate=validate.Length(max=20))
    q                = fields.Str()

    page             = fields.Int(load_default=1, validate=validate.Range(min=1))
    page_size        = fields.Int(load_default=20, validate=validate.Range(min=1, max=200))
    ordering         = fields.List(fields.Str(), load_default=[])

class TGUVUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    new_cod_persona      = fields.Str(validate=validate.Length(max=14))
    new_cod_tipo_persona = fields.Str(validate=validate.Length(max=3))
    new_cod_agencia      = fields.Int()
    new_empresa          = fields.Int()
    new_usuario_oracle   = fields.Str(validate=validate.Length(max=20))

    def validate_has_changes(self, data):
        if not any(k in data for k in (
            "new_cod_persona", "new_cod_tipo_persona", "new_cod_agencia", "new_empresa", "new_usuario_oracle"
        )):
            raise ValidationError("Debe enviar al menos un campo 'new_*' para actualizar.")

def build_ordering_in(allowed_map, ordering_list):
    order_by = []
    if not ordering_list:
        return [allowed_map["usuario_oracle"].asc()]
    for raw in ordering_list:
        if not raw:
            continue
        parts = raw.split(":")
        colname = parts[0].strip().lower()
        direction = parts[1].strip().lower() if len(parts) > 1 else "asc"
        col = allowed_map.get(colname)
        if not col:
            continue
        order_by.append(col.asc() if direction != "desc" else col.desc())
    return order_by or [allowed_map["usuario_oracle"].asc()]


class DDespachoUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    cod_despacho         = fields.Int(allow_none=True)
    cod_producto         = fields.Str(allow_none=True, validate=validate.Length(max=14))
    numero_serie         = fields.Str(allow_none=True, validate=validate.Length(max=30))
    fecha_despacho       = fields.Date(allow_none=True)          # ISO 'YYYY-MM-DD'
    usuario_despacha     = fields.Str(allow_none=True, validate=validate.Length(max=50))
    cod_comprobante      = fields.Str(allow_none=True, validate=validate.Length(max=20))
    tipo_comprobante     = fields.Str(allow_none=True, validate=validate.Length(max=2))
    en_despacho          = fields.Int(allow_none=True, validate=validate.OneOf([0,1]))
    despachada           = fields.Int(allow_none=True, validate=validate.OneOf([0,1]))
    cod_comprobante_gui  = fields.Str(allow_none=True, validate=validate.Length(max=20))
    tipo_comprobante_gui = fields.Str(allow_none=True, validate=validate.Length(max=2))
    cod_guia_des         = fields.Str(allow_none=True, validate=validate.Length(max=20))
    cod_tipo_guia_des    = fields.Str(allow_none=True, validate=validate.Length(max=2))
    empresa        = fields.Int(load_only=True)
    cod_ddespacho  = fields.Int(load_only=True)
    fecha_entrega = fields.Date(allow_none=True)
    observacion_entrega = fields.Str(allow_none=True, validate=validate.Length(max=500))

    @staticmethod
    def require_any_editable(data: dict):
        editable = {
            "cod_despacho","cod_producto","numero_serie","fecha_despacho","usuario_despacha",
            "cod_comprobante","tipo_comprobante","en_despacho","despachada",
            "cod_comprobante_gui","tipo_comprobante_gui","cod_guia_des","cod_tipo_guia_des",
            "fecha_entrega", "observacion_entrega"
        }
        return any(k in data for k in editable)