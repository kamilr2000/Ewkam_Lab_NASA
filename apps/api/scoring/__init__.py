"""Deterministic pixel scoring and ranking primitives."""

from .engine import (
    AreaRank,
    FeatureCriterion,
    FeatureResult,
    RankingResult,
    ScoredBatch,
    ScoredPixel,
    ScoringBatch,
    normalize_criteria,
    rank_pixel_batches,
    score_batch,
    select_distinct_areas,
)

__all__ = [
    "AreaRank",
    "FeatureCriterion",
    "FeatureResult",
    "RankingResult",
    "ScoredBatch",
    "ScoredPixel",
    "ScoringBatch",
    "normalize_criteria",
    "rank_pixel_batches",
    "score_batch",
    "select_distinct_areas",
]
