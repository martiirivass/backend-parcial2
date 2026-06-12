from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlmodel import Session

from app.db.database import get_session

from app.repositories.pedido_repository import (
    PedidoRepository
)

from app.services.mercadopago_service import (
    MercadoPagoService
)

router = APIRouter(
    prefix="/mercadopago",
    tags=["Mercado Pago"]
)

@router.post("/pedido/{pedido_id}")
def crear_preferencia(self, pedido):

    preference_data = {
        "items": [
            {
                "title": f"Pedido #{pedido.id}",
                "quantity": 1,
                "unit_price": float(pedido.total),
                "currency_id": "ARS"
            }
        ],
        "external_reference": str(pedido.id)
    }

    response = self.sdk.preference().create(
        preference_data
    )

    return response["response"]