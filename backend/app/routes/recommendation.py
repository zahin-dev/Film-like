"""Authenticated route for mood-based film recommendations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services import recommendation_service


router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
)
async def create_recommendations(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Recommend TMDB-verified films for the user's selected mood."""
    try:
        return await recommendation_service.recommend(
            db=db,
            user=current_user,
            mood=payload.mood,
            limit=payload.limit,
        )
    except recommendation_service.RecommendationServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc
