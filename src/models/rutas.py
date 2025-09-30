# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy import Sequence, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.models.clientes import cliente_hor

from src.config.database import db
from marshmallow import Schema, fields, validate, EXCLUDE, ValidationError


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

    # Obligatorio
    empresa = fields.Integer(required=True)

    # Filtros exactos/opcionales
    cod_ruta = fields.Integer()
    cod_tipo_pedido = fields.String(validate=validate.Length(max=4)) # p.ej. 'PC'
    cod_pedido = fields.Integer()
    cod_tipo_orden = fields.String(validate=validate.Length(max=4))
    cod_orden = fields.Integer()
    cod_cliente = fields.String(validate=validate.Length(max=14))
    cod_producto = fields.String(validate=validate.Length(max=30))
    cadena = fields.String(validate=validate.OneOf(["RETAIL","MAYOREO"]))
    fac_con = fields.String(validate=validate.OneOf(["CONSIGNACION","FACTURACION"]))  # FAC_CON en la vista
    transportista = fields.String()  # texto LIKE
    destino = fields.String()        # ciudad LIKE
    ruta = fields.String()           # nombre de la ruta LIKE
    bod_destino = fields.String()    # nombre bodega LIKE
    modelo = fields.String()
    numero_serie = fields.String()

    # Estados (opcionales)
    en_despacho = fields.Integer(validate=validate.OneOf([0,1]))
    despachada = fields.Integer(validate=validate.OneOf([0,1]))

    # Rango de fechas (elige el campo sobre el que se filtra)
    date_field = fields.String(load_default="fecha_est_desp",
                               validate=validate.OneOf(["fecha_est_desp","fecha_despacho","fecha_envio","fecha_entrega"]))
    fecha_desde = fields.Date()
    fecha_hasta = fields.Date()

    # Paginación
    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

    # Ordenamiento estilo DRF: "-fecha_est_desp,cod_orden"
    ordering = fields.String()

    def validate_ordering(self, value):
        if not value:
            return
        for token in value.split(","):
            key = token.strip().lstrip("-")
            if key not in ALLOWED_ORDERING_FIELDS:
                raise ValidationError(f"Campo de ordenamiento no permitido: {key}")

class DespachoRowOut(Schema):
    # Campos clave (ajusta tipos si necesitas exactitud decimal)
    empresa = fields.Integer()
    cod_tipo_pedido = fields.String()
    cod_pedido = fields.String()
    cod_tipo_orden = fields.String()
    cod_orden = fields.String()
    tipo_pretransferencia = fields.String(allow_none=True)
    cod_pretransferencia = fields.String(allow_none=True)
    cod_guia_des = fields.String(allow_none=True)
    cod_tipo_guia_des = fields.String(allow_none=True)
    fecha_agrega = fields.Date(allow_none=True)
    fecha_est_desp = fields.Date(allow_none=True)
    fecha_despacho = fields.Date(allow_none=True)
    fecha_envio = fields.Date(allow_none=True)
    fecha_entrega = fields.Date(allow_none=True)
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
        # ⬇⬇⬇ AQUI LA CORRECCIÓN: referencias a TABLA y COLUMNAS reales con ESQUEMA
        db.ForeignKeyConstraint(
            ["EMPRESA", "COD_CLIENTE"],
            ["STOCK.CLIENTE_HOR.empresah", "STOCK.CLIENTE_HOR.cod_clienteh"],
            name="FK_CLIENTE_DIRECCION_CLIENTE"
        ),
        db.Index("IND_CLIENTE_DIRECCION_GUIAS01", "EMPRESA", "COD_CLIENTE"),
    )

    # Relación SIN primaryjoin: ahora sí puede inferirse por la FK compuesta
    cliente = relationship(
        cliente_hor,     # usa la CLASE (o el string "ClienteHor" si prefieres)
        viewonly=True,  # quítalo si quieres permitir escritura a través de la relación
        lazy="select",
    )

class STCDespachoEntrega(db.Model):
    __tablename__ = "ST_CDESPACHO_ENTREGA"
    empresa           = db.Column("EMPRESA", db.Integer, nullable=False, primary_key=True)
    cde_codigo = db.Column(
        "CDE_CODIGO",
        db.Integer,
        Sequence("SEQ_STC_DESPACHO_ENTREGA"),  # crea/usa la secuencia
        primary_key=True,  # parte de la PK
        autoincrement=True  # delega en la secuencia
    )
    fecha             = db.Column("FECHA", db.Date)  # enviar ISO 'YYYY-MM-DD'
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
    empresa           = fields.Int(required=True)
    cde_codigo        = fields.Int(required=True)
    fecha             = fields.Date(required=False)  # ISO 'YYYY-MM-DD'
    usuario           = fields.Str(required=False, validate=validate.Length(max=20))
    cod_ruta          = fields.Int(required=False)
    observacion       = fields.Str(required=False, validate=validate.Length(max=200))
    cod_persona       = fields.Str(required=False, validate=validate.Length(max=14))
    cod_tipo_persona  = fields.Str(required=False, validate=validate.Length(max=3))
    cod_transportista = fields.Str(required=False, validate=validate.Length(max=14))
    finalizado        = fields.Int(required=False, validate=validate.OneOf([0,1]))

class CDEUpdateSchema(Schema):
    # Todos opcionales en update
    fecha             = fields.Date(required=False)
    usuario           = fields.Str(required=False, validate=validate.Length(max=20))
    cod_ruta          = fields.Int(required=False)
    observacion       = fields.Str(required=False, validate=validate.Length(max=200))
    cod_persona       = fields.Str(required=False, validate=validate.Length(max=14))
    cod_tipo_persona  = fields.Str(required=False, validate=validate.Length(max=3))
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
    empresa           = fields.Int()
    cde_codigo        = fields.Int()
    fecha             = fields.Date(allow_none=True)
    usuario           = fields.Str(allow_none=True)
    cod_ruta          = fields.Int(allow_none=True)
    observacion       = fields.Str(allow_none=True)
    cod_persona       = fields.Str(allow_none=True)
    cod_tipo_persona  = fields.Str(allow_none=True)
    cod_transportista = fields.Str(allow_none=True)
    finalizado        = fields.Int()