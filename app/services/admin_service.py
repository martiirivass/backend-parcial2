import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.models.rol import Rol

logger = logging.getLogger(__name__)


class AdminService:

    def __init__(self, db: Session):
        self.db = db

    # Obtener usuario por ID
    def obtener_usuario(
        self,
        usuario_id: int
    ):

        usuario = self.db.get(
            Usuario,
            usuario_id
        )

        if not usuario:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        return usuario

    # Listar usuarios con paginacion y filtro opcional por rol
    def listar_usuarios(
        self,
        limit: int,
        offset: int,
        rol_codigo: Optional[str] = None
    ):

        base = select(Usuario)
        count_base = select(func.count()).select_from(Usuario)

        if rol_codigo:
            base = base.join(
                UsuarioRol
            ).where(
                UsuarioRol.rol_codigo == rol_codigo
            )
            count_base = count_base.join(
                UsuarioRol
            ).where(
                UsuarioRol.rol_codigo == rol_codigo
            )

        usuarios = self.db.exec(
            base.offset(offset).limit(limit)
        ).all()

        total = self.db.exec(count_base).one()

        return {
            "data": usuarios,
            "total": total
        }

    # Actualizar datos y roles de un usuario
    def actualizar_usuario(
        self,
        usuario_id: int,
        datos
    ):

        usuario = self.obtener_usuario(
            usuario_id
        )

        update_data = datos.model_dump(
            exclude_unset=True
        )

        if "rol_ids" in update_data:

            new_codigos = set(
                update_data["rol_ids"]
            )

            current_codigos = {
                ur.rol_codigo
                for ur in (
                    usuario.usuario_roles or []
                )
            }

            # Quitar roles que ya no estan
            for ur in list(
                usuario.usuario_roles or []
            ):

                if (
                    ur.rol_codigo
                    not in new_codigos
                ):

                    self.db.delete(ur)

            # Agregar roles nuevos
            for codigo in new_codigos:

                if codigo not in current_codigos:

                    # Validar que el rol existe
                    rol = self.db.exec(
                        select(Rol).where(
                            Rol.codigo == codigo
                        )
                    ).first()

                    if rol:

                        nuevo_ur = UsuarioRol(
                            usuario_id=usuario.id,
                            rol_codigo=codigo
                        )

                        self.db.add(nuevo_ur)

            del update_data["rol_ids"]

        # Actualizar campos del usuario
        for key, value in update_data.items():

            setattr(
                usuario,
                key,
                value
            )

        self.db.add(usuario)

        return usuario

    # Soft delete — marca deleted_at
    def eliminar_usuario(
        self,
        usuario_id: int
    ):

        usuario = self.obtener_usuario(
            usuario_id
        )

        usuario.deleted_at = datetime.now(
            timezone.utc
        )

        self.db.add(usuario)

    # Restaurar usuario soft-deleteado
    def restaurar_usuario(
        self,
        usuario_id: int
    ):

        usuario = self.obtener_usuario(
            usuario_id
        )

        usuario.deleted_at = None

        self.db.add(usuario)

        return usuario
