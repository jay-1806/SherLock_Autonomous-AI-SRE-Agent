"""Investigation latency benchmarks."""

import asyncio
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

import os
os.environ.setdefault("ROOT_CAUSE_POSTERIOR_THRESHOLD", "0.35")

DATASET_PATH = Path(__file__).parent.parent / "dataset" / "labeled_incidents.json"


async def run_latency_benchmark(subset: str = "all", sample_size: int = 5) -> dict:
    """Measure P50/P75/P95 investigation latency in seconds."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from evals.dataset.schema import LabeledIncident
    from agent.graph.investigation_graph import INVESTIGATION_GRAPH
    from agent.models.alert import AlertPayload

    if not DATASET_PATH.exists():
        return {"total_runs": 0, "p50_s": 0, "p75_s": 0, "p95_s": 0}

    with open(DATASET_PATH) as f:
        all_incidents = [LabeledIncident(**i) for i in json.load(f)]

    if subset != "all":
        incidents = [i for i in all_incidents if i.difficulty == subset or i.incident_category == subset]
    else:
        incidents = all_incidents

    incidents = incidents[:sample_size]  # Cap for fast benchmarks
    durations = []

    for incident in incidents:
        alert = AlertPayload(**incident.alert_payload)
        inv_id = f"latency-{incident.incident_id}"
        t0 = time.perf_counter()
        try:
            await INVESTIGATION_GRAPH.ainvoke({
                "alert": alert,
                "investigation_id": inv_id,
                "step_timings": {},
                "hypotheses": [],
                "requires_human_review": False,
            })
        except Exception:
            pass
        dur = time.perf_counter() - t0
        durations.append(dur)

    if not durations:
        return {"total_runs": 0, "p50_s": 0, "p75_s": 0, "p95_s": 0}

    durations.sort()
    n = len(durations)
    p50 = durations[int(n * 0.5) - 1] if n else 0
    p75 = durations[int(n * 0.75) - 1] if n else 0
    p95 = durations[int(n * 0.95) - 1] if n else durations[-1]

    return {
        "total_runs": n,
        "p50_s": round(p50, 2),
        "p75_s": round(p75, 2),
        "p95_s": round(p95, 2),
        "target_p75_s": 360,
    }


if __name__ == "__main__":
    subset = sys.argv[-1] if len(sys.argv) > 1 else "all"
    if subset.startswith("--"):
        subset = "all"
    r = asyncio.run(run_latency_benchmark(subset))
    print(json.dumps(r, indent=2))
