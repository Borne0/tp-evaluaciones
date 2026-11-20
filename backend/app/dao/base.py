from sqlalchemy.orm import Session


class BaseDAO:
    """Los DAO reciben la sesión; el commit lo hace el Gestor (límite de la transacción)."""

    def __init__(self, db: Session):
        self.db = db
