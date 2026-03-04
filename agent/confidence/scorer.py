"""Confidence score computation."""


def compute_confidence(
    evidence_count: int,
    hypothesis_count: int,
    posterior_scores: list[float],
) -> float:
    """Compute 0–1 confidence from evidence and posteriors."""
    if not posterior_scores:
        return 0.0
    top = max(posterior_scores)
    evidence_bonus = min(evidence_count * 0.05, 0.2)
    return min(top + evidence_bonus, 1.0)
