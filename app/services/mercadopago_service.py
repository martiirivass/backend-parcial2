import uuid

import mercadopago

from app.core.config import settings


class MercadoPagoService:

    def __init__(self):
        self.sdk = mercadopago.SDK(
            settings.MP_ACCESS_TOKEN
        )

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
            "external_reference": str(pedido.id),
        }

        request_options = {
            "idempotency_key": str(uuid.uuid4())
        }

        response = self.sdk.preference().create(
            preference_data,
            request_options
        )

        return response["response"]

    def obtener_pago(self, payment_id):

        response = self.sdk.payment().get(
            payment_id
        )

        return response["response"]