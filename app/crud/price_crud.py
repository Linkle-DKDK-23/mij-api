from sqlalchemy.orm import Session
from app.models.prices import Prices

def create_price(db: Session, price_data) -> Prices:
    """
    価格を作成
    """
    db_price = Prices(**price_data)
    db.add(db_price)
    db.flush()
    return db_price