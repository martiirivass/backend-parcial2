import logging
from sqlmodel import Session

logger = logging.getLogger(__name__)


class UnitOfWork:

    def __init__(self, db: Session):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Si hubo una excepcion, hago rollback
            self.rollback()
        else:
            # Si todo salio bien, commit
            self.commit()

    def commit(self):
        self.db.commit()

    def rollback(self):
        logger.info("Rolling back transaction")
        self.db.rollback()
