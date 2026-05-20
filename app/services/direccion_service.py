import logging
from fastapi import HTTPException

from app.models.direccion_model import Direccion
from app.repositories.direccion_repository import DireccionRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class DireccionService:

    def __init__(self, db):
        self.db = db
        self.repo = DireccionRepository(db)
        self.uow = UnitOfWork(db)

    def crear_direccion(self, usuario_id, datos):
        try:
            direccion = Direccion(
                usuario_id=usuario_id,
                **datos.model_dump()
            )

            # Si es la primera direccion, la marco como principal
            direcciones_existentes = self.repo.get_by_usuario(usuario_id)
            if len(direcciones_existentes) == 0:
                direccion.principal = True

            self.repo.create(direccion)
            self.uow.commit()
            self.db.refresh(direccion)

            return direccion

        except Exception as e:
            logger.exception(f"Error creando direccion: {e}")
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

    def marcar_principal(self, direccion_id, usuario_id):
        try:
            direccion = self.repo.get_by_id(direccion_id)

            if not direccion:
                raise HTTPException(status_code=404, detail="Direccion no encontrada")

            if direccion.usuario_id != usuario_id:
                raise HTTPException(status_code=403, detail="No tienes permiso")

            # Desmarco todas las direcciones del usuario
            direcciones = self.repo.get_by_usuario(usuario_id)
            for d in direcciones:
                d.principal = False
                self.repo.update(d)

            # Marco la seleccionada como principal
            direccion.principal = True
            self.repo.update(direccion)

            self.uow.commit()
            self.db.refresh(direccion)

            return direccion

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error marcando direccion principal: {e}")
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
