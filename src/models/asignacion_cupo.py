# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Sequence
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError, OperationalError
from src.config.database import db
from decimal import Decimal
from datetime import datetime
from marshmallow import Schema, fields, validates_schema, ValidationError, validate, EXCLUDE


Base = declarative_base(metadata = db.metadata)

BODEGAS_STOCK = (5, 1, 25)
class StAsignacionCupo(Base):
    __tablename__ = 'st_asignacion_cupo'
    __table_args__ = (
        Index('PK_ASIGNACION_CUPO', 'empresa', 'ruc_cliente', 'cod_producto'),
        Index('UDX_ASIGNA_CUPO_CLIENTE', 'empresa', 'ruc_cliente'),
        Index('UDX_ASIGNA_CUPO_PRODUCTO', 'empresa', 'cod_producto'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    ruc_cliente = Column(VARCHAR(13), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(20), primary_key=True, nullable=False)
    porcentaje_maximo = Column(NUMBER(14,2))
    cantidad_minima = Column(NUMBER(10))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class STReservaProducto(db.Model):
    __tablename__ = "ST_RESERVA_PRODUCTO"

    # PK compuesta (orden invertido en constraint; aquí lo dejamos explícito)
    cod_reserva = db.Column(
        "COD_RESERVA",
        db.Integer,  # NUMBER(10) mapea perfecto a Integer
        Sequence("SEQ_ST_RESERVA"),  # <<< generador Python-side
        primary_key=True,
        autoincrement=True  # <<< obligatorio en PK compuesta
    )
    empresa = db.Column("EMPRESA", db.Numeric(10), primary_key=True)

    cod_producto = db.Column("COD_PRODUCTO", db.String(14))
    cod_bodega = db.Column("COD_BODEGA", db.Numeric(4))
    cod_cliente = db.Column("COD_CLIENTE", db.String(14))
    fecha_ini = db.Column("FECHA_INI", db.Date)
    fecha_fin = db.Column("FECHA_FIN", db.Date)
    observacion = db.Column("OBSERVACION", db.String(200))
    es_inactivo = db.Column("ES_INACTIVO", db.Numeric(1), default=0)
    cantidad = db.Column("CANTIDAD", db.Numeric(17, 4))
    cod_bodega_destino = db.Column("COD_BODEGA_DESTINO", db.Numeric(4))
    cantidad_utilizada = db.Column("CANTIDAD_UTILIZADA", db.Numeric(17, 4))

# ---------- Serializador (Marshmallow) ----------
class ReservaSchema(Schema):
    empresa = fields.Integer()
    cod_reserva = fields.Integer()
    cod_producto = fields.String(allow_none=True)
    cod_bodega = fields.Integer(allow_none=True)
    cod_cliente = fields.String(allow_none=True)
    fecha_ini = fields.Date(allow_none=True)
    fecha_fin = fields.Date(allow_none=True)
    observacion = fields.String(allow_none=True)
    es_inactivo = fields.Integer()
    cantidad = fields.Decimal(as_string=True, allow_none=True)
    cod_bodega_destino = fields.Integer(allow_none=True)
    cantidad_utilizada = fields.Decimal(as_string=True, allow_none=True)

reserva_schema = ReservaSchema()
reservas_schema = ReservaSchema(many=True)

# ---------- Validación de query params (estilo DRF) ----------
ALLOWED_ORDERING = {"fecha_ini": STReservaProducto.fecha_ini,
                    "fecha_fin": STReservaProducto.fecha_fin,
                    "cod_reserva": STReservaProducto.cod_reserva,
                    "cod_bodega": STReservaProducto.cod_bodega}

class QueryParamsSchema(Schema):
    # Filtros
    cod_producto = fields.String(required=False, validate=validate.Length(min=1, max=14))
    cod_cliente = fields.String(required=False, validate=validate.Length(min=1, max=14))
    cod_bodega = fields.Integer(required=False)
    empresa = fields.Integer(required=False)  # útil si manejas multi-empresa
    fecha_desde = fields.Date(required=False) # ISO-8601: YYYY-MM-DD
    fecha_hasta = fields.Date(required=False)

    # Paginación
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    page_size = fields.Integer(load_default=20, validate=validate.Range(min=1, max=200))

    # Ordenamiento estilo DRF: ?ordering=-fecha_ini,cod_reserva
    ordering = fields.String(required=False)

    @validates_schema
    def check_dates(self, data, **kwargs):
        fd = data.get("fecha_desde")
        fh = data.get("fecha_hasta")
        if fd and fh and fd > fh:
            raise ValidationError("fecha_desde no puede ser mayor que fecha_hasta.")

    @validates_schema
    def check_ordering(self, data, **kwargs):
        ord_param = data.get("ordering")
        if not ord_param:
            return
        for token in ord_param.split(","):
            key = token.strip().lstrip("-")
            if key not in ALLOWED_ORDERING:
                raise ValidationError(
                    f"Campo de ordenamiento no permitido: {key}. "
                    f"Permitidos: {', '.join(ALLOWED_ORDERING.keys())}"
                )

class CreateReservaSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # rechaza campos no definidos

    # PK: en Oracle no hay autoincremento nativo; si no usas secuencia, exige ambos
    empresa = fields.Integer(required=True)
    cod_reserva = fields.Integer(required=False, allow_none=True)
    cod_producto = fields.String(validate=validate.Length(max=14))
    cod_bodega = fields.Integer()
    cod_cliente = fields.String(validate=validate.Length(max=14))
    fecha_ini = fields.Date()   # ISO yyyy-mm-dd
    fecha_fin = fields.Date()
    observacion = fields.String(validate=validate.Length(max=200))
    es_inactivo = fields.Integer(validate=validate.OneOf([0,1]), load_default=0)
    cantidad = fields.Decimal(as_string=True, places=4)
    cod_bodega_destino = fields.Integer()
    cantidad_utilizada = fields.Decimal(as_string=True, places=4)

    @validates_schema
    def check_dates(self, data, **_):
        if data.get("fecha_ini") and data.get("fecha_fin") and data["fecha_ini"] > data["fecha_fin"]:
            raise ValidationError("fecha_ini no puede ser mayor que fecha_fin.")

class UpdateReservaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # No permitimos cambiar PK por PUT
    empresa = fields.Integer()
    cod_reserva = fields.Integer()

    cod_producto = fields.String(validate=validate.Length(max=14))
    cod_bodega = fields.Integer()
    cod_cliente = fields.String(validate=validate.Length(max=14))
    fecha_ini = fields.Date()
    fecha_fin = fields.Date()
    observacion = fields.String(validate=validate.Length(max=200))
    es_inactivo = fields.Integer(validate=validate.OneOf([0,1]))
    cantidad = fields.Decimal(as_string=True, places=4)
    cod_bodega_destino = fields.Integer()
    cantidad_utilizada = fields.Decimal(as_string=True, places=4)

    @validates_schema
    def check_dates(self, data, **_):
        if data.get("fecha_ini") and data.get("fecha_fin") and data["fecha_ini"] > data["fecha_fin"]:
            raise ValidationError("fecha_ini no puede ser mayor que fecha_fin.")

def map_integrity_error(err: IntegrityError):
    # Traducción simple de errores Oracle comunes
    msg = str(err.orig)
    if "ORA-00001" in msg:
        return 409, "Conflicto de clave única. Ya existe un registro con esa PK."
    if "ORA-02291" in msg or "ORA-02292" in msg:
        return 409, "Violación de integridad referencial. Verifique claves foráneas."
    return 400, "Violación de integridad. Revise los datos enviados."

def validate_no_active_duplicate(data):
    """
    Reglas:
    - Si viene cod_bodega_destino, valida contra ese campo.
    - Si no viene, valida contra cod_bodega.
    - Es 'activa' si NVL(es_inactivo,0)=0 y fecha_fin > SYSDATE.
    """
    empresa = data.get("empresa")
    cod_producto = data.get("cod_producto")
    bodega_dest = data.get("cod_bodega_destino")
    bodega = data.get("cod_bodega")

    # Si no tenemos producto o ninguna bodega, no aplicamos esta validación.
    if not cod_producto or (bodega_dest is None and bodega is None):
        return

    if bodega_dest is not None:
        sql = """
            SELECT 1
            FROM ST_RESERVA_PRODUCTO
            WHERE EMPRESA = :empresa
              AND COD_PRODUCTO = :p
              AND COD_BODEGA_DESTINO = :b
              AND NVL(ES_INACTIVO, 0) = 0
              AND FECHA_FIN IS NOT NULL
              AND FECHA_FIN > SYSDATE
              AND ROWNUM = 1
        """
        params = {"empresa": empresa, "p": cod_producto, "b": bodega_dest}
        field_used = "cod_bodega_destino"
    else:
        sql = """
            SELECT 1
            FROM ST_RESERVA_PRODUCTO
            WHERE EMPRESA = :empresa
              AND COD_PRODUCTO = :p
              AND COD_BODEGA = :b
              AND NVL(ES_INACTIVO, 0) = 0
              AND FECHA_FIN IS NOT NULL
              AND FECHA_FIN > SYSDATE
              AND ROWNUM = 1
        """
        params = {"empresa": empresa, "p": cod_producto, "b": bodega}
        field_used = "cod_bodega"

    exists = db.session.execute(text(sql), params).first() is not None
    if exists:
        raise ValidationError({
            field_used: [
                f"Ya existe una reserva activa para cod_producto='{cod_producto}' y {field_used}={params['b']} "
                f"(es_inactivo=0 y fecha_fin>SYSDATE). No se permite crear otra."
            ]
        })

def validate_available_stock_before_create(data):
    """
    Valida que la cantidad solicitada no supere el inventario disponible:
    disponible = stock_total(bodegas 5,1,25) - reservas_activas_remanente(mismo producto, mismas bodegas).
    Requiere: empresa, cod_producto, cantidad (en payload).
    """
    empresa = data.get("empresa")
    cod_producto = data.get("cod_producto")
    cantidad = data.get("cantidad")

    # Requisitos mínimos
    if empresa is None:
        raise ValidationError({"empresa": ["Campo requerido para validar stock."]})
    if not cod_producto:
        raise ValidationError({"cod_producto": ["Campo requerido para validar stock."]})
    if cantidad is None:
        raise ValidationError({"cantidad": ["Campo requerido para validar stock."]})

    try:
        qty_req = Decimal(str(cantidad))
    except Exception:
        raise ValidationError({"cantidad": ["Formato inválido. Debe ser numérico (hasta 4 decimales)."]})

    if qty_req <= 0:
        raise ValidationError({"cantidad": ["Debe ser mayor que 0."]})

    # Stock total en st_inventario para bodegas (5,1,25)
    stock_sql = text(f"""
        SELECT NVL(SUM(s.cantidad), 0) AS stock
          FROM st_inventario s
         WHERE s.cod_producto = :cod_producto
           AND s.empresa = :empresa
           AND s.cod_bodega IN ({",".join([f":b{i}" for i in range(len(BODEGAS_STOCK))])})
           AND s.aa = 0
           AND s.cod_tipo_inventario = 1
    """)
    stock_params = {
        "cod_producto": cod_producto,
        "empresa": empresa,
        **{f"b{i}": b for i, b in enumerate(BODEGAS_STOCK)},
    }
    row = db.session.execute(stock_sql, stock_params).first()
    stock_total = Decimal(str(row[0])) if row is not None else Decimal("0")

    # Reservas activas (es_inactivo=0 y fecha_fin>SYSDATE) para el mismo producto
    # Usamos bodegas fuente (cod_bodega). Si tu lógica usa cod_bodega_destino, cambia el campo en el WHERE (comentado abajo).
    reservas_sql = text(f"""
        SELECT NVL(SUM(GREATEST(r.cantidad - NVL(r.cantidad_utilizada,0), 0)), 0) AS reservado
          FROM ST_RESERVA_PRODUCTO r
         WHERE r.empresa = :empresa
           AND r.cod_producto = :cod_producto
           AND NVL(r.es_inactivo, 0) = 0
           AND r.fecha_fin IS NOT NULL
           AND r.fecha_fin > SYSDATE
           AND r.cod_bodega IN ({",".join([f":rb{i}" for i in range(len(BODEGAS_STOCK))])})
           -- Si debes considerar el destino, reemplaza la línea anterior por:
           -- AND r.cod_bodega_destino IN ({",".join([f":rb{i}" for i in range(len(BODEGAS_STOCK))])})
    """)
    reservas_params = {
        "cod_producto": cod_producto,
        "empresa": empresa,
        **{f"rb{i}": b for i, b in enumerate(BODEGAS_STOCK)},
    }
    row2 = db.session.execute(reservas_sql, reservas_params).first()
    reservado_activo = Decimal(str(row2[0])) if row2 is not None else Decimal("0")

    disponible = stock_total - reservado_activo

    if qty_req > disponible:
        raise ValidationError({
            "cantidad": [
                "La cantidad a reservar supera el inventario disponible.",
                f"Solicitado: {qty_req}",
                f"Disponible: {disponible}",
                f"Stock total: {stock_total}",
                f"Reservas activas (remanente): {reservado_activo}"
            ]
        })

def validate_available_stock_before_update(obj, data):
    """
    Valida que el UPDATE no deje el inventario disponible en negativo.
    disponible = stock_total - reservado_otros
    Debe cumplirse: remanente_propuesto <= disponible
    Donde:
      remanente_propuesto = GREATEST(cantidad_nueva - NVL(cantidad_utilizada,0), 0)
      reservado_otros = SUM de remanentes de otras reservas (activas y vigentes) del mismo producto.
    """

    empresa = int(obj.empresa)
    cod_reserva = int(obj.cod_reserva)

    # Tomar valores propuestos: si no vienen en payload, usar los actuales del DB
    cod_producto_new = data.get("cod_producto", obj.cod_producto)
    cantidad_new = data.get("cantidad", obj.cantidad)
    es_inactivo_new = data.get("es_inactivo", obj.es_inactivo or 0)
    fecha_fin_new = data.get("fecha_fin", obj.fecha_fin)

    # Validaciones básicas
    if not cod_producto_new:
        raise ValidationError({"cod_producto": ["Campo requerido para validar stock."]})
    if cantidad_new is None:
        raise ValidationError({"cantidad": ["Campo requerido para validar stock."]})

    try:
        qty_new = Decimal(str(cantidad_new))
    except Exception:
        raise ValidationError({"cantidad": ["Formato inválido. Debe ser numérico (hasta 4 decimales)."]})
    if qty_new <= 0:
        raise ValidationError({"cantidad": ["Debe ser mayor que 0."]})

    # coherencia frente a lo ya utilizado
    used = Decimal(str(obj.cantidad_utilizada or 0))
    if qty_new < used:
        raise ValidationError({
            "cantidad": [
                "La cantidad no puede ser menor que la cantidad ya utilizada.",
                f"cantidad_utilizada actual: {used}"
            ]
        })

    # ¿La reserva resultante será activa y vigente?
    will_be_active = int(es_inactivo_new or 0) == 0
    will_be_vigente = (fecha_fin_new is not None) and (fecha_fin_new > datetime.utcnow().date())
    # Nota: usamos fecha de aplicación. Si quieres estrictamente SYSDATE de Oracle, se puede mover esta condición al SQL,
    # pero aquí solo decide si el registro editado se considera en el cálculo.

    # Stock total en bodegas 5,1,25
    stock_sql = text(f"""
        SELECT NVL(SUM(s.cantidad), 0) AS stock
          FROM st_inventario s
         WHERE s.cod_producto = :cod_producto
           AND s.empresa = :empresa
           AND s.cod_bodega IN ({",".join([f":b{i}" for i in range(len(BODEGAS_STOCK))])})
           AND s.aa = 0
           AND s.cod_tipo_inventario = 1
    """)
    stock_params = {
        "cod_producto": cod_producto_new,
        "empresa": empresa,
        **{f"b{i}": b for i, b in enumerate(BODEGAS_STOCK)},
    }
    row = db.session.execute(stock_sql, stock_params).first()
    stock_total = Decimal(str(row[0])) if row else Decimal("0")

    # Reservas activas y vigentes de OTROS registros del mismo producto
    reservas_sql = text(f"""
        SELECT NVL(SUM(GREATEST(r.cantidad - NVL(r.cantidad_utilizada,0), 0)), 0) AS reservado
          FROM ST_RESERVA_PRODUCTO r
         WHERE r.empresa = :empresa
           AND r.cod_producto = :cod_producto
           AND NVL(r.es_inactivo, 0) = 0
           AND r.fecha_fin IS NOT NULL
           AND r.fecha_fin > SYSDATE
           AND r.cod_reserva <> :cod_reserva   -- excluirme
           AND r.cod_bodega IN ({",".join([f":rb{i}" for i in range(len(BODEGAS_STOCK))])})
           -- si tu negocio descuenta por bodega_destino, cambia la condición anterior por cod_bodega_destino
    """)
    reservas_params = {
        "empresa": empresa,
        "cod_producto": cod_producto_new,
        "cod_reserva": cod_reserva,
        **{f"rb{i}": b for i, b in enumerate(BODEGAS_STOCK)},
    }
    row2 = db.session.execute(reservas_sql, reservas_params).first()
    reservado_otros = Decimal(str(row2[0])) if row2 else Decimal("0")

    # Remanente propuesto para este registro
    remanente_propuesto = Decimal("0")
    if will_be_active and will_be_vigente:
        remanente_propuesto = max(qty_new - used, Decimal("0"))

    # Chequeo final
    disponible = stock_total - reservado_otros
    if remanente_propuesto > disponible:
        raise ValidationError({
            "cantidad": [
                "La cantidad a actualizar supera el inventario disponible.",
                f"Solicitado: {qty_new}",
                f"Utilizado: {used}",
                f"Remanente propuesto: {remanente_propuesto}",
                f"Disponible: {disponible}",
                f"Stock total: {stock_total}",
                f"Reservas activas de otros: {reservado_otros}"
            ]
        })

def ajustar_cantidad_reserva_old(empresa: int, cod_bodega: int, cod_producto: str, op: str) -> dict:
    """
    Incrementa o decrementa en 1 la 'cantidad' de la reserva activa y vigente
    que coincida con (empresa, cod_bodega, cod_producto).
    """
    out_schema = ReservaSchema()
    delta = Decimal("1") if op == "inc" else Decimal("-1")

    # 1) Selección y bloqueo de la fila objetivo
    q = (db.session.query(STReservaProducto)
         .filter(STReservaProducto.empresa == empresa)
         .filter(STReservaProducto.cod_bodega_destino == cod_bodega)           # usar cod_bodega_destino si tu negocio lo requiere
         .filter(STReservaProducto.cod_producto == cod_producto)
         .filter(text("NVL(ES_INACTIVO,0) = 0"))
         .filter(text("FECHA_FIN IS NOT NULL AND FECHA_FIN > SYSDATE")))

    try:
        obj = q.first()
    except OperationalError:
        # Fila bloqueada por otra transacción
        raise ValidationError({"detail": ["La reserva está siendo modificada. Intente nuevamente."]})

    if not obj:
        raise ValidationError({"detail": ["No existe una reserva activa y vigente para el modelo seleccionado."]})

    # 2) Calcular nueva cantidad
    qty_current = Decimal(str(obj.cantidad))
    qty_used = Decimal(str(obj.cantidad_utilizada))
    qty_new = qty_used + delta

    if qty_new > qty_current:
        raise ValidationError({
            "cantidad": [
                "La reserva de este modelo para la bodega actual ya ha sido completada.",
                f"cantidad_actual: {qty_current}",
                f"cantidad_utilizada: {qty_used}"
            ]
        })

    if qty_new < 0:
        raise ValidationError({
            "cantidad": [
                "La cantidad resultante debe ser 0 o mayor.",
                f"propuesta: {qty_new}"
            ]
        })

    # 3) Validar disponibilidad con la lógica existente de UPDATE
    # Solo pasamos los campos que cambian; el helper toma los demás del objeto
    validate_available_stock_before_update(obj, {"cantidad_utilizada": qty_new})

    # 4) Aplicar cambio y confirmar
    obj.cantidad_utilizada = qty_new
    db.session.commit()

    return out_schema.dump(obj)

def ajustar_cantidad_reserva(empresa: int, cod_bodega: int, cod_producto: str, op: str):
    """
    Incrementa o decrementa en 1 la 'cantidad_utilizada' de la reserva activa y vigente
    que coincida con (empresa, cod_bodega_destino, cod_producto).
    Si no existe una reserva que cumpla, retorna None sin alterar el flujo del llamador.
    """
    out_schema = ReservaSchema()
    delta = Decimal("1") if op == "inc" else Decimal("-1")

    # 1) Buscar una reserva activa y vigente (sin bloquear ni fallar si no hay)
    q = (db.session.query(STReservaProducto)
         .filter(STReservaProducto.empresa == empresa)
         .filter(STReservaProducto.cod_bodega_destino == cod_bodega)  # usa destino según tu comentario
         .filter(STReservaProducto.cod_producto == cod_producto)
         .filter(text("NVL(ES_INACTIVO,0) = 0"))
         .filter(text("FECHA_FIN IS NOT NULL AND FECHA_FIN > SYSDATE"))
         .order_by(STReservaProducto.fecha_ini.desc(),
                   STReservaProducto.cod_reserva.desc()))

    obj = q.first()

    # 1.a) Si no hay reserva, no-op (salida silenciosa)
    if not obj:
        return None

    # 2) Calcular nueva 'cantidad_utilizada' y validar coherencia
    qty_actual_total = Decimal(str(obj.cantidad or 0))
    qty_usada = Decimal(str(obj.cantidad_utilizada or 0))
    qty_usada_nueva = qty_usada + delta

    # No permitir superar la cantidad total
    if qty_usada_nueva > qty_actual_total:
        raise ValidationError({
            "cantidad_utilizada": [
                "La reserva ya está completamente utilizada; no se puede incrementar más.",
                f"cantidad_total: {qty_actual_total}",
                f"cantidad_utilizada_actual: {qty_usada}"
            ]
        })

    # Permitir 0, pero no negativo
    if qty_usada_nueva < 0:
        raise ValidationError({
            "cantidad_utilizada": [
                "La cantidad utilizada resultante debe ser 0 o mayor.",
                f"propuesta: {qty_usada_nueva}"
            ]
        })

    # 3) Aplicar cambio y confirmar
    obj.cantidad_utilizada = qty_usada_nueva
    db.session.commit()

    return out_schema.dump(obj)