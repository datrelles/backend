from sqlalchemy import Column, VARCHAR,  DateTime
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db


Base = declarative_base(metadata = db.metadata)

class VtDetallesOrdenGeneral(Base):
    __tablename__ = 'vt_detalles_orden_general'
    __table_args__ = {'schema': 'stock'}
    id = Column(VARCHAR(10), primary_key=True, nullable=False, index=True)
    cod_po = Column(VARCHAR(10))
    cod_producto = Column(VARCHAR(14))
    nombre = Column(VARCHAR(200))
    modelo = Column(VARCHAR(200))
    costo_sistema = Column(NUMBER(16,6))
    costo_cotizado = Column(NUMBER(16,6))
    cantidad_pedido = Column(NUMBER(9))
    saldo_producto = Column(NUMBER(16,6))
    fob_detalle = Column(NUMBER(16,6))
    fob_total = Column(NUMBER(16,6))
    proforma = Column(VARCHAR(30))
    proveedor = Column(VARCHAR(100))
    fecha_estimada_produccion = Column(DateTime)
    fecha_estimada_puerto = Column(DateTime)
    fecha_estimada_llegada = Column(DateTime)
    nro_contenedor = Column(VARCHAR(15))
    codigo_bl_house = Column(VARCHAR(30))
    fecha_embarque = Column(DateTime)
    fecha_llegada = Column(DateTime)
    fecha_bodega = Column(DateTime)
    total_precio_container = Column(NUMBER(14,2))
    cantidad_container = Column(NUMBER(14,2))
    estado_embarque = Column(VARCHAR(2))
    estado_orden = Column(VARCHAR(2))
    @classmethod
    def query(cls):
        return db.session.query(cls)