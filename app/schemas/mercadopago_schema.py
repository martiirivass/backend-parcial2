from pydantic import BaseModel


class PreferenciaResponse(BaseModel):
    id: str
    init_point: str