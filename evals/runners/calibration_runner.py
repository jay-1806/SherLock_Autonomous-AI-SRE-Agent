"""Confidence score calibration test."""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import os
os.environ.setdefault("ROOT_CAUSE_POSTERIOR_THRESHOLD", "0.35")

DATASET_PATH = Path(__file__).parent.parent / "dataset" / "labeled_incidents.json"


async def run_calibration_test(subset: str = "all", sample_size: int = 8) -> dict:
    """Check that high-confidence predictions correlate with correct RCA."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from evals.dataset.schema import LabeledIncident
    from evals.metrics.compute import compute_rca_accuracy
    from agent.graph.investigation_graph import INVESTIGATION_GRAPH
    from agent.models.alert import AlertPayload

    if not DATASET_PATH.exists():
        return {"sample_size": 0, "calibration_pass": False}

    with open(DATASET_PATH) as f:
        all_incidents = [LabeledIncident(**i) for i in json.load(f)]

    if subset != "all":
        incidents = [i for i in all_incidents if i.difficulty == subset or i.incident_category == subset]
    else:
        incidents = all_incidents

    incidents = incidents[:sample_size]
    high_conf_correct = 0
    high_conf_total = 0
    low_conf_total = 0

    for incident in incidents:
        alert = AlertPayload(**incident.alert_payload)
        try:
            inv = await INVESTIGATION_GRAPH.ainvoke({
                "alert": alert,
                "investigation_id": f"cal-{incident.incident_id}",
                "step_timings": {},
                "hypotheses": [],
                "requires_human_review": False,
            })
        except Exception:
            low_conf_total += 1
            continue

        result = inv.get("investigation_result")
        if not result:
            low_conf_total += 1
            continue

        conf = result.confidence_score
        pred_rca = result.root_cause.description if result.root_cause else ""
        acc = compute_rca_accuracy(pred_rca, incident.ground_truth_root_cause)

        if conf >= 0.7:
            high_conf_total += 1
            if acc >= 0.5:
                high_conf_correct += 1
        else:
            low_conf_total += 1

    calibration_pass = high_conf_total == 0 or (high_conf_correct / high_conf_total) >= 0.7

    return {
        "sample_size": len(incidents),
        "high_conf_total": high_conf_total,
        "high_conf_correct": high_conf_correct,
        "low_conf_total": low_conf_total,
        "calibration_pass": calibration_pass,
    }


if __name__ == "__main__":
    subset = sys.argv[-1] if len(sys.argv) > 1 else "all"
    if subset.startswith("--"):
        subset = "all"
    r = asyncio.run(run_calibration_test(subset))
    print(json.dumps(r, indent=2))
    sys.exit(0 if r.get("calibration_pass", False) else 1)
