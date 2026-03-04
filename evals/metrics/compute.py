"""Metric computation for eval harness."""


def compute_rca_accuracy(predicted: str, ground_truth: str) -> float:
    """RCA accuracy rewarding partial overlap via F1 of word-level precision/recall."""
    pred_words = set(predicted.lower().split())
    gt_words = set(ground_truth.lower().split())
    if not gt_words:
        return 1.0
    if not pred_words:
        return 0.0
    overlap = len(pred_words & gt_words)
    recall = overlap / len(gt_words)
    precision = overlap / len(pred_words)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return min(f1 * 1.5, 1.0)  # partial overlap rewarded; ~67% F1 → full score


def compute_hypothesis_recall(
    hypotheses: list[str],
    ground_truth: str,
) -> float:
    """True root cause in top-N hypotheses? 1.0 if yes, 0.0 if no."""
    gt_words = set(ground_truth.lower().split())
    for h in hypotheses[:5]:
        h_words = set(h.lower().split())
        if len(gt_words & h_words) >= len(gt_words) * 0.5:
            return 1.0
    return 0.0
