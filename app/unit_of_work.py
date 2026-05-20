import logging
from sqlmodel import Session

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        self.db.commit()

    def rollback(self):
        logger.info("Rolling back transaction")
        self.db.rollback()