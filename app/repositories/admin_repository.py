from typing import List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Usuario]):

    def __init__(self, db: Session):
        super().__init__(db, Usuario)

    def get_usuario(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.get(Usuario, usuario_id)

    def list_usuarios(
        self,
        limit: int,
        offset: int,
        rol_codigo: Optional[str] = None,
    ) -> Tuple[List[Usuario], int]:
        base = select(Usuario)
        count_base = select(func.count()).select_from(Usuario)

        if rol_codigo:
            base = base.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id).where(
                UsuarioRol.rol_codigo == rol_codigo
            )
            count_base = count_base.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id).where(
                UsuarioRol.rol_codigo == rol_codigo
            )

        usuarios = self.db.exec(base.offset(offset).limit(limit)).all()
        total = self.db.exec(count_base).one()
        return usuarios, total

    def get_usuario_roles(self, usuario_id: int) -> List[UsuarioRol]:
        stmt = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        return self.db.exec(stmt).all()

    def delete_usuario_role(self, usuario_rol: UsuarioRol) -> None:
        self.db.delete(usuario_rol)

    def add_usuario_role(self, usuario_rol: UsuarioRol) -> None:
        self.db.add(usuario_rol)

    def get_rol(self, codigo: str) -> Optional[Rol]:
        stmt = select(Rol).where(Rol.codigo == codigo)
        return self.db.exec(stmt).first()
