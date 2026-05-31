from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.refresh_token_model import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(
    BaseRepository[RefreshToken]
):

    def __init__(self, db: Session):
        super().__init__(db, RefreshToken)

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