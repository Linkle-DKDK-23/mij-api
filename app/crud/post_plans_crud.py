from sqlalchemy.orm import Session
from app.models.plans import PostPlans

def create_post_plan(db: Session, post_plan_data) -> PostPlans:
    """
    投稿に紐づくプランを作成
    """
    db_post_plan = PostPlans(**post_plan_data)
    db.add(db_post_plan)
    db.flush()
    return db_post_plan