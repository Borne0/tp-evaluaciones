from sqlalchemy.orm import Session


class BaseGestor:
    def __init__(self, db: Session):
        self.db = db
