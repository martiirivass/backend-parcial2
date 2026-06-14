import logging
from fastapi import HTTPException

from app.models.direccion_entrega_model import DireccionEntrega
from app.repositories.direccion_repository import DireccionEntregaRepository

logger = logging.getLogger(__name__)


class DireccionEntregaService:

    def __init__(self, db):
        self.repo = DireccionEntregaRepository(db)

    def crear_direccion(self, usuario_id, datos):

        direccion = DireccionEntrega(
            usuario_id=usuario_id,
            **datos.model_dump()
        )

        self.repo.create(direccion)

        return direccion

    def listar_direcciones(self, usuario_id):
        return self.repo.get_by_usuario(usuario_id)

    def obtener_direccion(self, direccion_id, usuario_id):

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

        return direccion

    def actualizar_direccion(self, direccion_id, usuario_id, datos):

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

    def marcar_principal(self, direccion_id, usuario_id):

        direccion = self.obtener_direccion(direccion_id, usuario_id)

        if direccion.es_principal:
            return direccion

        direcciones = self.repo.get_by_usuario(usuario_id)

        for d in direcciones:
            if d.es_principal:
                d.es_principal = False
                self.repo.update(d)

        direccion.es_principal = True
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
