import logging
from fastapi import HTTPException

from app.models.direccion_entrega_model import DireccionEntrega
from app.repositories.direccion_repository import DireccionEntregaRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class DireccionEntregaService:

    def __init__(self, db):
        self.db = db
        self.repo = DireccionEntregaRepository(db)
        self.uow = UnitOfWork(db)

    def crear_direccion(self, usuario_id, datos):
        try:
            direccion = DireccionEntrega(
                usuario_id=usuario_id,
                **datos.model_dump()
            )

            self.repo.create(direccion)
            self.uow.commit()
            self.db.refresh(direccion)

            return direccion

        except Exception as e:
            logger.exception(f"Error creando direccion de entrega: {e}")
            self.uow.rollback()
            raise

    def listar_direcciones(self, usuario_id):
        return self.repo.get_by_usuario(usuario_id)

    def obtener_direccion(self, direccion_id, usuario_id):
        direccion = self.repo.get_by_id(direccion_id)

        if not direccion:
            raise HTTPException(status_code=404, detail="Direccion no encontrada")

        if direccion.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta direccion")

        return direccion

    def actualizar_direccion(self, direccion_id, usuario_id, datos):
        try:
            direccion = self.repo.get_by_id(direccion_id)

            if not direccion:
                raise HTTPException(status_code=404, detail="Direccion no encontrada")

            if direccion.usuario_id != usuario_id:
                raise HTTPException(status_code=403, detail="No tienes permiso para editar esta direccion")

            update_data = datos.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(direccion, key, value)

            direccion.updated_at = None  # Se actualiza automaticamente

            self.repo.update(direccion)
            self.uow.commit()
            self.db.refresh(direccion)

            return direccion

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error actualizando direccion: {e}")
            self.uow.rollback()
            raise

    def eliminar_direccion(self, direccion_id, usuario_id):
        try:
            direccion = self.repo.get_by_id(direccion_id)

            if not direccion:
                raise HTTPException(status_code=404, detail="Direccion no encontrada")

            if direccion.usuario_id != usuario_id:
                raise HTTPException(status_code=403, detail="No tienes permiso")

            self.repo.delete(direccion)
            self.uow.commit()

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error eliminando direccion: {e}")
            self.uow.rollback()
            raise
