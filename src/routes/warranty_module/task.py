from flask import current_app, copy_current_request_context
from jinja2 import Template
from src.config.database import db
from src.models.postVenta import (
    st_casos_postventa,
    st_casos_productos,
    st_types_mail_warranty,
    ar_taller_servicio_tecnico,
    ADprovincias,
    ArCiudades,
    ADcantones,
)
from src.models.productos import Producto

from flask_mail import Message
from datetime import datetime
import logging
import threading

logger = logging.getLogger(__name__)

def send_mail_postventa(cod_comprobante: str, estado_caso: str):
    @copy_current_request_context
    def _send_mail():
        try:
            # Buscar el caso de postventa mediante el código de comprobante
            caso = st_casos_postventa.query().filter_by(cod_comprobante=cod_comprobante).first()
            if not caso:
                logger.error(f"[ERROR] Caso con comprobante {cod_comprobante} no encontrado.")
                return

            empresa = caso.empresa
            type_modulo = 'WARRANTY'

            # Buscar la plantilla de correo correspondiente
            plantilla = st_types_mail_warranty.query().filter_by(
                empresa=empresa,
                type_modulo=type_modulo,
                estado_caso=estado_caso,
                activo=1
            ).first()
            if not plantilla:
                logger.error(f"[ERROR] No se encontró plantilla para empresa={empresa}, estado={estado_caso}")
                return

            # Renderizar el cuerpo del correo utilizando Jinja2
            template = Template(plantilla.cuerpo_html)
            cuerpo = template.render(
                nombre_cliente=caso.nombre_cliente,
                fecha=caso.fecha.strftime('%d/%m/%Y') if caso.fecha else '---'
            )

            # Recopilar los destinatarios válidos
            recipients = [r for r in [caso.e_mail1, caso.e_mail2] if r]
            if not recipients:
                logger.error(f"[ERROR] Caso {cod_comprobante} no tiene correos válidos.")
                return

            # Obtener la instancia de mail desde current_app
            mail_instance = current_app.extensions.get("mail")
            sender_email = "sms@massline.com.ec"  # Correo remitente

            # Crear y enviar el mensaje
            msg = Message(subject=plantilla.asunto, sender=sender_email, recipients=recipients)
            msg.html = cuerpo
            mail_instance.send(msg)

            logger.info(f"[OK] Correo enviado para caso {cod_comprobante} a {', '.join(recipients)}")
        except Exception as e:
            logger.exception(f"[EXCEPTION] Error al enviar correo para caso {cod_comprobante}: {str(e)}")

    # Ejecutar la tarea en un hilo separado
    thread = threading.Thread(target=_send_mail)
    thread.start()
    # Retornar inmediatamente sin esperar que se complete el envío
    return True

def send_mail_envio_pedido(cod_comprobante: str) -> bool:
    """
    Envío de correo para el n (ENVÍ PEDIDOS) del módulo WARRANTY.

    • Usa la plantilla de st_types_mail_warranty (empresa, 'WARRANTY', 'EP').
    • Destinatario fijo: postventa@massline.com.ec
    • Renderiza información del caso, taller, ubicación y los productos del pedido.
    """
    @copy_current_request_context
    def _job():
        correo_posteventas = "postventa@massline.com.ec"
        try:
            # ------------------------------------------------------------------
            # 1. Cargar el caso
            # ------------------------------------------------------------------
            caso = (
                st_casos_postventa.query()
                .filter_by(cod_comprobante=cod_comprobante)
                .first()
            )
            if not caso:
                logger.error(f"[EP] Caso {cod_comprobante} no encontrado")
                return

            if not caso.cod_pedido:                              # debe existir pedido
                logger.error(f"[EP] Caso {cod_comprobante} no tiene cod_pedido generado")
                return

            empresa = caso.empresa
            modulo = "WARRANTY"
            estado = "EP"

            # ------------------------------------------------------------------
            # 2. Plantilla
            # ------------------------------------------------------------------
            plantilla_db = (
                st_types_mail_warranty.query()
                .filter_by(
                    empresa=empresa,
                    type_modulo=modulo,
                    estado_caso=estado,
                    activo=1,
                )
                .first()
            )

            if not plantilla_db:
                logger.error(f"[EP] Plantilla ausente para empresa={empresa}, estado={estado}")
                return  # Sale de la función, NO continúa

            template_str = plantilla_db.cuerpo_html
            asunto = plantilla_db.asunto
            # ------------------------------------------------------------------
            # 3. Información auxiliar (taller, provincia, cantón)
            # ------------------------------------------------------------------
            taller = (
                ar_taller_servicio_tecnico.query()
                .filter_by(
                    codigo=caso.codigo_taller,
                    codigo_empresa=empresa,
                )
                .first()
            )

            provincia = (
                ADprovincias.query()
                .filter_by(codigo_provincia=caso.codigo_provincia)
                .first()
            )
            canton = (
                ADcantones.query()
                .filter_by(
                    codigo_provincia=caso.codigo_provincia,
                    codigo_canton=caso.codigo_canton,
                )
                .first()
            )

            # ------------------------------------------------------------------
            # 4. Detalle de productos
            # ------------------------------------------------------------------
            productos_q = (
                st_casos_productos.query()
                .filter_by(
                    empresa=empresa,
                    cod_comprobante=cod_comprobante,
                    tipo_comprobante=caso.tipo_comprobante,
                )
                .all()
            )

            detalle_items = []
            for p in productos_q:
                prod = (
                    Producto.query()
                    .filter_by(empresa=empresa, cod_producto=p.cod_producto)
                    .first()
                )
                detalle_items.append(
                    {
                        "cod_producto": p.cod_producto,
                        "nombre": prod.nombre if prod else "(sin nombre)",
                        "cantidad": float(p.cantidad),
                    }
                )

            # ------------------------------------------------------------------
            # 5. Renderizar HTML con Jinja2
            # ------------------------------------------------------------------
            template = Template(template_str)
            cuerpo_html = template.render(
                caso=caso,
                taller=taller,
                provincia=provincia.descripcion if provincia else "---",
                canton=canton.descripcion if canton else "---",
                detalle_items=detalle_items,
                hoy=datetime.now(),
            )

            # ------------------------------------------------------------------
            # 6. Enviar
            # ------------------------------------------------------------------
            mail = current_app.extensions.get("mail")
            msg = Message(
                subject=asunto,
                sender="sms@massline.com.ec",
                recipients=[correo_posteventas],
            )
            msg.html = cuerpo_html
            mail.send(msg)

            logger.info(f"[EP] Correo de envío‑pedido para {cod_comprobante} OK")
            print(f"[EP] Correo de envío‑pedido para {cod_comprobante} OK")
        except Exception as exc:
            logger.exception(f"[EP] Error enviando correo {cod_comprobante}: {exc}")
            print(f"[EP] Error enviando correo {cod_comprobante}: {exc}")

    # Lanzar en segundo plano
    threading.Thread(target=_job, daemon=True).start()
    return True
