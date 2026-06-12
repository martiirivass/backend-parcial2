import logging
from fastapi import HTTPException

from app.models.direccion_entrega_model import DireccionEntrega
from app.repositories.direccion_repository import DireccionEntregaRepository
<<<<<<< HEAD
from app.unit_of_work import UnitOfWork
=======
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

logger = logging.getLogger(__name__)


class DireccionEntregaService:

    def __init__(self, db):
<<<<<<< HEAD
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
=======
        self.repo = DireccionEntregaRepository(db)

    def crear_direccion(self, usuario_id, datos):

        direccion = DireccionEntrega(
            usuario_id=usuario_id,
            **datos.model_dump()
        )

        self.repo.create(direccion)

        return direccion
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

    def listar_direcciones(self, usuario_id):
        return self.repo.get_by_usuario(usuario_id)

    def obtener_direccion(self, direccion_id, usuario_id):
<<<<<<< HEAD
        direccion = self.repo.get_by_id(direccion_id)

        if not direccion:
            raise HTTPException(status_code=404, detail="Direccion no encontrada")

        if direccion.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta direccion")
=======

        direccion = self.repo.get_by_id(direccion_id)

        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Direccion no encontrada"
            )

        if direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para ver esta direccion"
            )
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

        return direccion

    def actualizar_direccion(self, direccion_id, usuario_id, datos):
<<<<<<< HEAD
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
=======

        direccion = self.repo.get_by_id(direccion_id)

        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Direccion no encontrada"
            )

        if direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para editar esta direccion"
            )

        update_data = datos.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(direccion, key, value)

        self.repo.update(direccion)

        return direccion

    def eliminar_direccion(self, direccion_id, usuario_id):

        direccion = self.repo.get_by_id(direccion_id)

        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Direccion no encontrada"
            )

        if direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso"
            )

        self.repo.delete(direccion)
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
