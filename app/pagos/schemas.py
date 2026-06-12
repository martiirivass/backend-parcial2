from typing import Optional
from pydantic import BaseModel


class CrearPreferenciaRequest(BaseModel):
    pedido_id: int


class CrearPreferenciaResponse(BaseModel):
    preference_id: str
    init_point: str
    pedido_id: int


class WebhookResponse(BaseModel):
    recibido: bool


class PagoStatusResponse(BaseModel):
    pedido_id: int
    payment_id: Optional[int] = None
    status: Optional[str] = None
    transaction_amount: Optional[float] = None
