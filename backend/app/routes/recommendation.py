"""Authenticated route for mood-based film recommendations."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services import recommendation_service


router = APIRouter(tags=["推薦"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="気分に合う映画を推薦",
    description=(
        "気分、視聴タグ、最近のジャンル傾向をローカルで点数化し、"
        "視聴済み作品を除外して返します。"
    ),
)
def create_recommendations(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Return deterministic recommendations from the local catalogue."""
    return recommendation_service.recommend(
        db=db,
        user=current_user,
        mood=payload.mood,
        limit=payload.limit,
    )
