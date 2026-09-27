"""Safe starter agents: explicit planning, bounded tool invocation, and verification."""
from uuid import uuid4

def make_plan(goal: str, has_file: bool = False) -> list[dict]:
    tasks = [{"id": str(uuid4()), "name": "Understand the goal", "agent": "planner", "status": "COMPLETED"}]
    if has_file:
        tasks.append({"id": str(uuid4()), "name": "Inspect the uploaded file", "agent": "document_agent", "status": "PENDING"})
    if any(word in goal.lower() for word in ("csv", "excel", "dataset", "spreadsheet", "analyz")) and has_file:
        tasks.append({"id": str(uuid4()), "name": "Analyze tabular data", "agent": "data_agent", "status": "PENDING"})
    if any(word in goal.lower() for word in ("research", "current", "latest", "sources")):
        tasks.append({"id": str(uuid4()), "name": "Gather verified external sources", "agent": "research_agent", "status": "WAITING", "note": "Search provider is not configured; no search has been performed."})
    tasks.append({"id": str(uuid4()), "name": "Prepare and verify response", "agent": "verifier", "status": "PENDING"})
    return tasks

def verify_result(goal: str, result: str) -> dict:
    return {"passed": bool(result.strip()), "checks": {"non_empty_result": bool(result.strip()), "goal_recorded": bool(goal.strip())},
            "note": "Basic structural checks only; this does not establish factual correctness."}
