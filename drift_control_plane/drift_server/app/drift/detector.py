from __future__ import annotations

import json
from typing import Any

from drift_server.app.drift.runtime_registry import RuntimeMethodNotFound, get_runtime_method
from drift_server.app.repositories.event_repository import EventRepository
from drift_server.app.repositories.method_repository import MethodRepository


class DriftDetector:
    def __init__(self, conn: Any) -> None:
        self.conn = conn
        self.methods = MethodRepository(conn)
        self.events = EventRepository(conn)

    # @managed-contract contract_id=drift_detector.DriftDetector.run_for_bucket level=P0
    def run_for_bucket(self, bucket: dict[str, Any]) -> None:
        assignments = self.methods.list_enabled_assignments(
            bucket["source_id"], bucket["adapter_id"], bucket["feature_id"]
        )
        for assignment in assignments:
            self._run_assignment(bucket, assignment)

    # @managed-contract contract_id=drift_detector.DriftDetector._run_assignment level=P0
    def _run_assignment(self, bucket: dict[str, Any], assignment: Any) -> None:
        assignment_id = assignment["assignment_id"]
        method_run_id = f"{assignment_id}:{bucket['bucket_id']}"
        if self.methods.method_run_exists(method_run_id):
            return

        if int(bucket["row_count"]) == 0:
            self.methods.insert_run_once(
                method_run_id,
                assignment,
                bucket,
                "skipped",
                "unknown",
                None,
                {"metrics": {}, "diagnostics": {"reason": "empty bucket"}, "payloadHints": {}, "event": None},
                None,
            )
            return

        state_row = self.methods.get_state_row(assignment_id)
        previous_state = json.loads(state_row["state_json"]) if state_row else {}
        try:
            runtime_method = get_runtime_method(assignment["runtime_method_key"])
            output = runtime_method(assignment, bucket, previous_state)
        except RuntimeMethodNotFound:
            self.methods.insert_run_once(
                method_run_id,
                assignment,
                bucket,
                "error",
                "unknown",
                None,
                {"metrics": {}, "diagnostics": {"errorCode": "RUNTIME_METHOD_NOT_FOUND"}, "payloadHints": {}, "event": None},
                "RUNTIME_METHOD_NOT_FOUND",
            )
            return

        self.methods.insert_run_once(
            method_run_id,
            assignment,
            bucket,
            output["runStatus"],
            output["level"],
            output["score"],
            {
                "metrics": output["metrics"],
                "diagnostics": output["diagnostics"],
                "payloadHints": output["payloadHints"],
                "event": output["event"],
            },
            None,
        )
        if output["runStatus"] == "success":
            self.methods.upsert_state(assignment_id, output["nextState"], bucket["bucket_id"], bucket["window_end"])
        if output["level"] in {"warning", "drift"}:
            self.events.insert_event_once(method_run_id, assignment, bucket, output)
