from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.refresh_token_model import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self, db: Session):
        super().__init__(db, RefreshToken)

    def get_valid_token(self, token: str):
        return self.db.exec(
            select(RefreshToken).where(
                RefreshToken.token == token,
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
