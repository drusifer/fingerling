"""stdlib HTTP webhook telemetry ingestion server (STORY-FING-08).

Exposes a single POST /telemetry endpoint accepting batch or single JSONL
telemetry records and feeds them in-process through the tokenizer, warehouse,
ringbuffer sliding-window matcher, and policy compiler.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from fingerling.policy import compile_policy
from fingerling.tokenizer import MaskEntry, parse_jsonl, tokenize
from fingerling.warehouse import Warehouse
from fingerling.ringbuffer import SlidingWindowMatcher


def create_handler(
    warehouse: Warehouse,
    matcher: SlidingWindowMatcher,
    mask_profile: list[MaskEntry],
    workload_name: str,
    match_labels: dict[str, str],
    gitops_repo_path: str | None = None,
    gpg_sign: bool = False,
    gpg_key_id: str | None = None,
    log_writer: Any = None,
) -> type[BaseHTTPRequestHandler]:
    """Factory to create a TelemetryHandler bound to in-memory pipeline state."""

    class TelemetryHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            if log_writer:
                log_writer.write(f"[Server webhook.log] 127.0.0.1 - - [{self.log_date_time_string()}] {format % args}\n")

        def do_POST(self) -> None:
            if self.path != "/telemetry":
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "Not Found"}')
                return

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                records = parse_jsonl(body)
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                err_data = {"error": f"Invalid JSONL: {e}"}
                self.wfile.write(json.dumps(err_data).encode("utf-8"))
                return

            scores = []
            policies = []
            gitops_status = None

            for r in records:
                try:
                    tokens = tokenize(r, mask_profile)
                    duration = float(r.get("duration_ms", 0.0))
                    fid = warehouse.upsert(tokens, duration_ms=duration, raw_record=r)
                    score = matcher.push(fid)
                    scores.append(score)
                    if matcher.warm and score > 0.05:
                        policy_yaml = compile_policy(
                            workload_name=workload_name,
                            match_labels=match_labels,
                            anomalous_trajectory=tuple(matcher._window),
                        )
                        policies.append(policy_yaml)

                        if gitops_repo_path:
                            try:
                                import uuid
                                from fingerling.gitops import commit_policy, auto_merge_policy
                                branch_name = f"fingerling-policy-{workload_name}-{uuid.uuid4().hex[:8]}"
                                commit_policy(
                                    repo_path=gitops_repo_path,
                                    policy_yaml=policy_yaml,
                                    workload_name=workload_name,
                                    branch_name=branch_name,
                                    gpg_sign=gpg_sign,
                                    gpg_key_id=gpg_key_id,
                                )
                                auto_merge_policy(
                                    repo_path=gitops_repo_path,
                                    branch_name=branch_name,
                                    target_branch="main",
                                )
                                gitops_status = "success"
                            except Exception as gitops_err:
                                gitops_status = f"failed: {gitops_err}"
                except Exception:
                    # Skip malformed individual records without crashing the loop
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_data = {
                "status": "success",
                "processed_records": len(records),
                "scores": scores,
                "policies": policies,
            }
            if gitops_status is not None:
                response_data["gitops_status"] = gitops_status

            self.wfile.write(json.dumps(response_data).encode("utf-8"))

    return TelemetryHandler


def run_server(
    port: int,
    warehouse: Warehouse,
    matcher: SlidingWindowMatcher,
    mask_profile: list[MaskEntry],
    workload_name: str,
    match_labels: dict[str, str],
    gitops_repo_path: str | None = None,
    gpg_sign: bool = False,
    gpg_key_id: str | None = None,
    log_writer: Any = None,
) -> HTTPServer:
    """Initialize and return a running HTTP server instance."""
    handler_class = create_handler(
        warehouse,
        matcher,
        mask_profile,
        workload_name,
        match_labels,
        gitops_repo_path,
        gpg_sign,
        gpg_key_id,
        log_writer,
    )
    server = HTTPServer(("127.0.0.1", port), handler_class)
    return server
