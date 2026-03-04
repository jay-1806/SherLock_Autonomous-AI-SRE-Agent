"""RCA accuracy evaluation runner."""

import asyncio
import json
import sys
from pathlib import Path

# Load .env before any agent imports (Neo4j, OpenAI, etc.)
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Lower root-cause threshold during eval so partial predictions get scored
import os
os.environ.setdefault("ROOT_CAUSE_POSTERIOR_THRESHOLD", "0.35")

DATASET_PATH = Path(__file__).parent.parent / "dataset" / "labeled_incidents.json"


async def run_accuracy_eval(subset: str = "all") -> dict:
    """Run accuracy eval against labeled incidents."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from evals.dataset.schema import LabeledIncident
    from evals.metrics.compute import compute_rca_accuracy, compute_hypothesis_recall
    from agent.graph.investigation_graph import INVESTIGATION_GRAPH
    from agent.models.alert import AlertPayload

    if not DATASET_PATH.exists():
        return {"total_incidents": 0, "valid_results": 0, "rca_accuracy_mean": 0.0}

    with open(DATASET_PATH) as f:
        all_incidents = [LabeledIncident(**i) for i in json.load(f)]

    if subset != "all":
        incidents = [
            i for i in all_incidents
            if i.difficulty == subset or i.incident_category == subset
        ]
    else:
        incidents = all_incidents

    results = []
    for incident in incidents:
        alert = AlertPayload(**incident.alert_payload)
        try:
            inv = await INVESTIGATION_GRAPH.ainvoke({
                "alert": alert,
                "investigation_id": f"eval-{incident.incident_id}",
                "step_timings": {},
                "hypotheses": [],
                "requires_human_review": False,
            })
            result = inv.get("investigation_result")
        except Exception as e:
            results.append({"incident_id": incident.incident_id, "error": str(e)})
            continue

        if not result:
            results.append({"incident_id": incident.incident_id, "error": "No result"})
            continue

        pred_rca = result.root_cause.description if result.root_cause else ""
        accuracy = compute_rca_accuracy(pred_rca, incident.ground_truth_root_cause)
        recall = compute_hypothesis_recall(
            [h.description for h in result.hypotheses],
            incident.ground_truth_root_cause,
        )
        results.append({
            "incident_id": incident.incident_id,
            "rca_accuracy": accuracy,
            "hypothesis_recall": recall,
            "confidence_score": result.confidence_score,
        })

    valid = [r for r in results if "error" not in r]
    n = len(valid)
    return {
        "total_incidents": len(results),
        "valid_results": n,
        "rca_accuracy_mean": sum(r["rca_accuracy"] for r in valid) / n if n else 0.0,
        "per_incident_results": results,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("subset", nargs="?", default="all", help="easy|medium|hard|all")
    p.add_argument("--fail-threshold", type=float, default=None, help="Exit 1 if rca_accuracy_mean < threshold")
    args = p.parse_args()
    subset = (args.subset or "all").replace("--", "").strip() or "all"
    r = asyncio.run(run_accuracy_eval(subset))
    print(json.dumps(r, indent=2))
    if args.fail_threshold is not None and r.get("rca_accuracy_mean", 0) < args.fail_threshold:
        sys.exit(1)
