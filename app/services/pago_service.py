import logging
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.pago_model import Pago
from app.models.pedido_model import Pedido
from app.repositories.pago_repository import PagoRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class PagoService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = PagoRepository(db)
        self.uow = UnitOfWork(db)

    def registrar_pago(self, datos):
        try:
            # Verifico que el pedido exista
            pedido = self.db.get(Pedido, datos.pedido_id)
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")

            # El monto del pago no puede exceder el total del pedido
            pagos_actuales = self.repo.get_by_pedido(datos.pedido_id)
            total_pagado = sum(p.monto for p in pagos_actuales)
            if total_pagado + datos.monto > pedido.total:
                raise HTTPException(
                    status_code=400,
                    detail=f"El pago excede el saldo pendiente ({pedido.total - total_pagado:.2f})"
                )

            pago = Pago(
                pedido_id=datos.pedido_id,
                monto=datos.monto,
                forma_pago_codigo=datos.forma_pago_codigo,
                referencia=datos.referencia
            )
            self.repo.create(pago)
            self.uow.commit()
            self.db.refresh(pago)
            return pago

        except HTTPException:
            self.uow.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error registrando pago: {e}")
            self.uow.rollback()
            raise

    def listar_por_pedido(self, pedido_id: int):
        return self.repo.get_by_pedido(pedido_id)

    def listar_todos(self):
        return self.repo.get_all()
