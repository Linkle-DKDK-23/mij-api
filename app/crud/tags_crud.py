from sqlalchemy.orm import Session
from app.models.tags import Tags


def exit_tag(db: Session, tag_data) -> bool:
    """
    タグが存在するか確認
    """
    # tag_dataが文字列の場合は直接使用、辞書の場合はnameキーから取得
    tag_name = tag_data if isinstance(tag_data, str) else tag_data["name"]
    result = db.query(Tags).filter(Tags.name == tag_name).first() is not None
    return result

def create_tag(db: Session, tag_data) -> Tags:
    """
    タグを作成
    """
    db_tag = Tags(**tag_data)
    db.add(db_tag)
    db.flush()
    return db_tag