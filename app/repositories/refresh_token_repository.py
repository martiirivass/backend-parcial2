from datetime import datetime, timezone
<<<<<<< HEAD
from sqlmodel import Session, select
=======

from sqlmodel import Session, select

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from app.models.refresh_token_model import RefreshToken
from app.repositories.base import BaseRepository


<<<<<<< HEAD
class RefreshTokenRepository(BaseRepository[RefreshToken]):
=======
class RefreshTokenRepository(
    BaseRepository[RefreshToken]
):
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

    def __init__(self, db: Session):
        super().__init__(db, RefreshToken)

<<<<<<< HEAD
    def get_valid_token(self, token_hash: str):
        return self.db.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at == None,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        ).first()

    def revoke_user_tokens(self, usuario_id: int):
        tokens = self.db.exec(
            select(RefreshToken).where(
                RefreshToken.usuario_id == usuario_id,
                RefreshToken.revoked_at == None
            )
        ).all()
        now = datetime.now(timezone.utc)
        for t in tokens:
            t.revoked_at = now
            self.db.add(t)
        return tokens
=======
    def get_valid_token(
        self,
        token_hash: str
    ):

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash
                == token_hash,

                RefreshToken.revoked_at.is_(None),

                RefreshToken.expires_at
                > datetime.now(timezone.utc)
            )
        )

        return self.db.exec(statement).first()

    def revoke_user_tokens(
        self,
        usuario_id: int
    ):

        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.usuario_id
                == usuario_id,

                RefreshToken.revoked_at.is_(None)
            )
        )

        tokens = self.db.exec(statement).all()

        now = datetime.now(timezone.utc)

        for token in tokens:

            token.revoked_at = now

            self.db.add(token)

        return tokens
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
