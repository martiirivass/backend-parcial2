import logging
import uuid
from datetime import datetime, timezone

import mercadopago
import requests

from fastapi import HTTPException

from app.core.config import settings
from app.pagos.repository import PagoRepository
from app.pagos.schemas import (
    CrearPreferenciaRequest,
    CrearPreferenciaResponse,
    PagoStatusResponse,
)

logger = logging.getLogger(__name__)


MP_API_BASE = "https://api.mercadopago.com"


class PagoService:

    def __init__(self, db):
        self.db = db
        self.repo = PagoRepository(db)

        if not settings.MP_ACCESS_TOKEN:
            raise RuntimeError(
                "MP_ACCESS_TOKEN no configurado. "
                "Agregalo en el .env del backend."
            )

        self.sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    def crear_preferencia(
        self,
        request: CrearPreferenciaRequest,
        usuario_id: int
    ) -> CrearPreferenciaResponse:

        from app.models.pedido_model import Pedido

        pedido = self.db.get(Pedido, request.pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        logger.info(f"Pedido encontrado: {pedido.id}")

        if pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="El pedido no pertenece al usuario autenticado"
            )

        external_reference = str(pedido.id)
        pagos_existentes = self.repo.get_by_pedido_id(pedido.id)

        pago = None

        for p in pagos_existentes:
            if p.mp_status in ("pending", "rejected", None):
                pago = p
                logger.info(f"Pago existente reutilizado: {pago.id}")
                break
            elif p.mp_status == "approved":
                raise HTTPException(
                    status_code=400,
                    detail="El pedido ya está pagado"
                )

        preference_data = {
            "items": [
                {
                    "title": f"Pedido #{pedido.id}",
                    "quantity": 1,
                    "unit_price": float(pedido.total),
                    "currency_id": "ARS"
                }
            ],
            "external_reference": external_reference,
            "back_urls": {
                "success": f"http://localhost:5174/pago-exitoso?pedido_id={pedido.id}",
                "failure": f"http://localhost:5174/pago-fallido?pedido_id={pedido.id}",
                "pending": f"http://localhost:5174/pago-pendiente?pedido_id={pedido.id}"
            },
        }

        if settings.MP_NOTIFICATION_URL:
            preference_data["notification_url"] = settings.MP_NOTIFICATION_URL

        idempotency_key = str(uuid.uuid4())

        response = self.sdk.preference().create(
            preference_data
        )

        logger.info("Preferencia creada en Mercado Pago")

        mp_response = response["response"]
        preference_id = mp_response["id"]
        init_point = mp_response["init_point"]

        logger.info(f"Preference ID generado: {preference_id}")

        if pago is None:
            from app.models.pago_model import Pago as PagoModel

            pago = PagoModel(
                pedido_id=pedido.id,
                external_reference=external_reference,
                idempotency_key=idempotency_key,
                mp_status="pending",
            )
            self.repo.create(pago)
            logger.info(f"Pago creado: {pago.id}")
        else:
            pago.idempotency_key = idempotency_key
            self.repo.update(pago)
            logger.info(f"Pago actualizado: {pago.id}")

        self.db.commit()
        self.db.refresh(pago)

        return CrearPreferenciaResponse(
            preference_id=preference_id,
            init_point=init_point,
            pedido_id=pedido.id
        )

    def process_webhook(self, payment_id: str) -> None:
        logger.info(f"Webhook recibido — payment_id: {payment_id}")

        headers = {
            "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"
        }

        url = f"{MP_API_BASE}/v1/payments/{payment_id}"

        resp = requests.get(url, headers=headers, timeout=15)

        if resp.status_code != 200:
            logger.warning(
                f"Error consultando MP API: {resp.status_code} — {resp.text}"
            )
            return

        payment_data = resp.json()
        logger.info("Payment consultado en MP API")

        mp_id = payment_data.get("id")
        mp_status = payment_data.get("status")
        transaction_amount = payment_data.get("transaction_amount")
        date_approved = payment_data.get("date_approved")
        external_reference = payment_data.get("external_reference")

        logger.info(
            f"Datos obtenidos — mp_id: {mp_id}, status: {mp_status}, "
            f"external_ref: {external_reference}"
        )

        if not external_reference:
            logger.warning("external_reference vacío en response de MP")
            return

        pago = self.repo.get_by_external_reference(external_reference)

        if not pago:
            logger.warning(
                f"No se encontró pago local para external_reference: "
                f"{external_reference}"
            )
            return

        pago.mp_payment_id = mp_id
        pago.mp_status = mp_status
        pago.transaction_amount = transaction_amount

        if date_approved:
            try:
                pago.date_approved = datetime.fromisoformat(
                    date_approved.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        pago.actualizado_en = datetime.now(timezone.utc)

        self.repo.update(pago)
        logger.info(
            f"Pago actualizado — mp_status: {mp_status}, "
            f"mp_payment_id: {mp_id}"
        )

        if mp_status == "approved":
            self._marcar_pedido_pagado(pago.pedido_id)

        self.db.commit()

    def _marcar_pedido_pagado(self, pedido_id: int) -> None:
        from app.models.pedido_model import Pedido

        pedido = self.db.get(Pedido, pedido_id)

        if not pedido:
            logger.warning(f"Pedido {pedido_id} no encontrado al marcar pagado")
            return

        if pedido.estado_codigo in ("CONFIRMADO", "EN_PREP", "ENTREGADO"):
            logger.info(
                f"Pedido {pedido_id} ya estaba en estado "
                f"'{pedido.estado_codigo}' — no se modifica"
            )
            return

        pedido.estado_codigo = "CONFIRMADO"
        pedido.updated_at = datetime.now(timezone.utc)
        self.db.add(pedido)

        logger.info(f"Pedido {pedido_id} marcado como CONFIRMADO (pagado vía MP)")

    def get_pago_status(self, pedido_id: int, usuario_id: int) -> PagoStatusResponse:
        from app.models.pedido_model import Pedido

        pedido = self.db.get(Pedido, pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        if pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="El pedido no pertenece al usuario autenticado"
            )

        pagos = self.repo.get_by_pedido_id(pedido_id)

        if not pagos:
            return PagoStatusResponse(
                pedido_id=pedido_id,
                status=None
            )

        pago = pagos[-1]

        if pago.mp_status in ("pending", None):
            self._sincronizar_con_mp(pago)

        return PagoStatusResponse(
            pedido_id=pedido_id,
            payment_id=pago.mp_payment_id,
            status=pago.mp_status,
            transaction_amount=pago.transaction_amount,
        )

    def _sincronizar_con_mp(self, pago):
        logger.info(f"Sincronizando pago {pago.id} con MP API")
        try:
            headers = {"Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"}

            if pago.mp_payment_id:
                resp = requests.get(
                    f"{MP_API_BASE}/v1/payments/{pago.mp_payment_id}",
                    headers=headers, timeout=15
                )
                if resp.status_code != 200:
                    logger.warning(f"Error consultando payment: {resp.status_code}")
                    return
                data = resp.json()
            else:
                resp = requests.get(
                    f"{MP_API_BASE}/v1/payments/search",
                    headers=headers,
                    params={"external_reference": pago.external_reference},
                    timeout=15
                )
                if resp.status_code != 200:
                    logger.warning(f"Error buscando pago en MP: {resp.status_code}")
                    return
                results = resp.json().get("results", [])
                if not results:
                    logger.info("No se encontraron pagos en MP para esta referencia")
                    return
                data = results[0]
                pago.mp_payment_id = data.get("id")
            mp_status = data.get("status")
            transaction_amount = data.get("transaction_amount")
            date_approved = data.get("date_approved")

            if mp_status:
                pago.mp_status = mp_status
            if transaction_amount is not None:
                pago.transaction_amount = transaction_amount
            if date_approved:
                try:
                    pago.date_approved = datetime.fromisoformat(date_approved.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
            pago.actualizado_en = datetime.now(timezone.utc)
            self.repo.update(pago)
            self.db.commit()

            if mp_status == "approved":
                self._marcar_pedido_pagado(pago.pedido_id)

            logger.info(f"Pago sincronizado — mp_status: {mp_status}")
        except requests.RequestException as e:
            logger.error(f"Error de conexión con MP API: {e}")
