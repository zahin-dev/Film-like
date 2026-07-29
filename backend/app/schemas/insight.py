"""映画日記の決定的な視聴傾向を返すスキーマ。"""

from pydantic import BaseModel, ConfigDict, Field


class ReactionSignalSummary(BaseModel):
    """ユーザーが選んだ一つのタグの件数と割合。"""

    model_config = ConfigDict(extra="forbid", strict=True)

    tag: str = Field(min_length=1, max_length=30)
    count: int = Field(ge=1)
    percentage: float = Field(ge=0.0, le=100.0)


class DiaryInsightsResponse(BaseModel):
    """ログイン中ユーザーの映画日記から集計した視聴傾向。"""

    model_config = ConfigDict(extra="forbid", strict=True)

    total_films: int = Field(ge=0)
    tagged_films: int = Field(ge=0)
    unique_reaction_signals: int = Field(ge=0)
    top_reaction_signals: list[ReactionSignalSummary]
    recent_reaction_signals: list[ReactionSignalSummary]
