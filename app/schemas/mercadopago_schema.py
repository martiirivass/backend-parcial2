from pydantic import BaseModel


class PreferenciaResponse(BaseModel):
    """Respuesta de la creación de preferencia en Mercado Pago (id + init_point)."""
    id: str
    init_point: str