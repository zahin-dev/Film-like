"""Authenticated HTTP route for deterministic diary reaction insights."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.insight import DiaryInsightsResponse
from app.services import insight_service


router = APIRouter(tags=["分析"])


@router.get(
    "/insights",
    response_model=DiaryInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="視聴傾向を分析",
    description="ユーザー自身が選んだ日本語タグだけを決定的に集計します。",
)
def get_diary_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiaryInsightsResponse:
    """Return explainable signals from the user's selected diary tags."""
    return insight_service.get_diary_insights(db, current_user)
