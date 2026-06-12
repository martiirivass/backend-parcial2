import logging

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

logger = logging.getLogger(__name__)

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.db.database import get_session
from app.models.usuario import Usuario
from app.pagos.schemas import (
    CrearPreferenciaRequest,
    CrearPreferenciaResponse,
    PagoStatusResponse,
    WebhookResponse,
)
from app.pagos.service import PagoService

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos MP"]
)


@router.get("/health")
def health_check():
    mp_configured = bool(settings.MP_ACCESS_TOKEN)

    if not mp_configured:
        return {
            "status": "error",
            "mercadopago": False,
            "detail": "MP_ACCESS_TOKEN no configurado en el .env del backend"
        }

    return {
        "status": "ok",
        "mercadopago": True
    }


@router.post(
    "/crear-preferencia",
    response_model=CrearPreferenciaResponse
)
def crear_preferencia(
    request: CrearPreferenciaRequest,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    service = PagoService(db)
    return service.crear_preferencia(
        request,
        current_user.id
    )


@router.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_session),
):
    data_id = request.query_params.get("data.id") or request.query_params.get("id")
    topic = request.query_params.get("topic") or request.query_params.get("type")

    try:
        body = await request.json()
        data_id = data_id or body.get("data", {}).get("id")
        topic = topic or body.get("type") or body.get("topic")
        logger.info(f"Webhook body — action: {body.get('action')}, data.id: {body.get('data', {}).get('id')}")
    except Exception:
        pass

    if not data_id:
        logger.warning("Webhook recibido sin payment_id")
        return WebhookResponse(recibido=True)

    logger.info(f"Webhook procesando — payment_id: {data_id}, topic: {topic}")

    service = PagoService(db)
    service.process_webhook(str(data_id))

    return WebhookResponse(recibido=True)


@router.get(
    "/{pedido_id}",
    response_model=PagoStatusResponse
)
def get_pago_status(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    service = PagoService(db)
    return service.get_pago_status(pedido_id, current_user.id)
