from sqlmodel import Session, select

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol_model import UsuarioRol


class AuthRepository:

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    def get_user_by_email(
        self,
        email: str
    ) -> Usuario | None:

        statement = select(Usuario).where(
            Usuario.email == email
        )

        return self.session.exec(
            statement
        ).first()

    def get_client_role(
        self
    ) -> Rol | None:

        statement = select(Rol).where(
            Rol.codigo == "CLIENT"
        )

        return self.session.exec(
            statement
        ).first()

    def add(
        self,
        entity
    ) -> None:

        self.session.add(entity)

    def add_user_role(
        self,
        usuario_rol: UsuarioRol
    ) -> None:

        self.session.add(usuario_rol)
        