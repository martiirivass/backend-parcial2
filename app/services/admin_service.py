import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.schemas.common import paginated_response
from app.repositories.admin_repository import AdminRepository

logger = logging.getLogger(__name__)


class AdminService:

    def __init__(self, db: Session):
        self.repo = AdminRepository(db)

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.repo.get_usuario(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario

    def listar_usuarios(
        self,
        limit: int,
        offset: int,
        rol_codigo: Optional[str] = None,
    ):
        usuarios, total = self.repo.list_usuarios(limit, offset, rol_codigo)
        return paginated_response(usuarios, total, page=(offset // limit) + 1, size=limit)

    def actualizar_usuario(self, usuario_id: int, datos):
        usuario = self.obtener_usuario(usuario_id)

        update_data = datos.model_dump(exclude_unset=True)

        if "rol_ids" in update_data:
            new_codigos = set(update_data["rol_ids"])
            current_roles = self.repo.get_usuario_roles(usuario_id)
            current_codigos = {ur.rol_codigo for ur in current_roles}

            for ur in current_roles:
                if ur.rol_codigo not in new_codigos:
                    self.repo.delete_usuario_role(ur)

            for codigo in new_codigos:
                if codigo not in current_codigos:
                    rol = self.repo.get_rol(codigo)
                    if rol:
                        nuevo_ur = UsuarioRol(
                            usuario_id=usuario.id, rol_codigo=codigo
                        )
                        self.repo.add_usuario_role(nuevo_ur)

            del update_data["rol_ids"]

        for key, value in update_data.items():
            setattr(usuario, key, value)

        self.repo.update(usuario)
        return usuario

    def eliminar_usuario(self, usuario_id: int) -> None:
        usuario = self.obtener_usuario(usuario_id)
        usuario.deleted_at = datetime.now(timezone.utc)
        self.repo.update(usuario)

    def restaurar_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.obtener_usuario(usuario_id)
        usuario.deleted_at = None
        self.repo.update(usuario)
        return usuario
