from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.base import get_db
from app.deps.auth import get_current_admin_user
from app.models.user import Users
from app.constants.enums import ConversationType
from app.crud import conversations_crud
from app.schemas.conversation import (
    MessageCreate,
    MessageResponse,
    ConversationListResponse,
    MarkAsReadRequest
)

router = APIRouter()


# ========== 管理人用エンドポイント ==========

@router.get("/conversations/delusion/list", response_model=List[ConversationListResponse])
def get_all_delusion_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Users = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理人用: すべての妄想メッセージ会話一覧を取得
    - 最後のメッセージ時刻でソート
    - 未読カウントを含む
    """
    conversations = conversations_crud.get_all_delusion_conversations_for_admin(
        db, skip, limit
    )

    return [ConversationListResponse(**conv) for conv in conversations]


@router.get("/conversations/delusion/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages_admin(
    conversation_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Users = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理人用: 特定会話のメッセージ一覧を取得
    """
    conversation = conversations_crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.type != ConversationType.DELUSION:
        raise HTTPException(status_code=403, detail="Not a delusion conversation")

    messages = conversations_crud.get_messages_by_conversation(
        db, conversation_id, skip, limit
    )

    response = []
    for message, sender in messages:
        response.append(MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_user_id=message.sender_user_id,
            type=message.type,
            body_text=message.body_text,
            created_at=message.created_at,
            updated_at=message.updated_at,
            sender_username=sender.profile_name if sender else None,
            sender_avatar=sender.avatar_url if sender else None,
            sender_profile_name=sender.profile_name if sender else None
        ))

    return response


@router.post("/conversations/delusion/{conversation_id}/messages", response_model=MessageResponse)
def send_message_as_admin(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: Users = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理人用: メッセージを送信
    """
    conversation = conversations_crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.type != ConversationType.DELUSION:
        raise HTTPException(status_code=403, detail="Not a delusion conversation")

    message = conversations_crud.create_message(
        db=db,
        conversation_id=conversation_id,
        sender_user_id=current_user.id,
        body_text=message_data.body_text
    )

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_user_id=message.sender_user_id,
        type=message.type,
        body_text=message.body_text,
        created_at=message.created_at,
        updated_at=message.updated_at,
        sender_username=current_user.username,
        sender_avatar=current_user.avatar_storage_key,
        sender_profile_name=current_user.profile_name
    )


@router.post("/conversations/delusion/{conversation_id}/mark-read")
def mark_conversation_as_read(
    conversation_id: UUID,
    read_data: MarkAsReadRequest,
    current_user: Users = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理人用: メッセージを既読にする
    """
    conversation = conversations_crud.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.type != ConversationType.DELUSION:
        raise HTTPException(status_code=403, detail="Not a delusion conversation")

    conversations_crud.mark_as_read(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        message_id=read_data.message_id
    )

    return {"status": "success", "message": "Marked as read"}
