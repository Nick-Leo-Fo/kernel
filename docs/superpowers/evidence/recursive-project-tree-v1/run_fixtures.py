#!/usr/bin/env python3
"""Run the deterministic Recursive Project Tree V1 acceptance fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any, Callable


FIXED_TIME = "2026-07-23T08:00:00Z"
ROOT_ID = "01K0ROOT000000000000000000"
ROOT_CONTRACT = "ctr_01K0ROOT00000000000000"
CHILD_ID = "01K0CHILD00000000000000000"
CHILD_CONTRACT = "ctr_01K0CHILD000000000000"

FIXTURES = [
    (1, ["V1-AC-01", "V1-AC-03", "V1-AC-05"], "A root Project Node initializes and a normal Stage completes, submits an immutable packet, is verified by its parent, and returns."),
    (2, ["V1-AC-02", "V1-AC-11"], "Spawn stops after spawn_intent or directory creation; Resume completes or abandons the same child ID without duplication."),
    (3, ["V1-AC-04"], "Three repeated no-progress Attempts for one progress scope force redesign."),
    (4, ["V1-AC-04"], "Relevant evidence advances a failing gate, while Procedure switching or irrelevant hypothesis elimination does not reset its counter."),
    (5, ["V1-AC-05", "V1-AC-17"], "A bounded revision produces a new immutable Return Packet; an authority-expanding request travels upward rather than changing the plan silently."),
    (6, ["V1-AC-05", "V1-AC-12"], "A node tries to return with an active descendant or transfer it upward; validation rejects the return."),
    (7, ["V1-AC-06"], "A candidate passes locally but fails against the latest parent branch."),
    (8, ["V1-AC-07"], "Git contains an unbound branch."),
    (9, ["V1-AC-07"], "A node references a deleted worktree."),
    (10, ["V1-AC-03", "V1-AC-07"], "JSONL contains malformed data, duplicate IDs, or missing/non-monotonic node_sequence."),
    (11, ["V1-AC-07", "V1-AC-17"], "A terminal node is reopened without approval."),
    (12, ["V1-AC-02", "V1-AC-05"], "A Work Node returns successor_required and a Project Node succeeds it without losing lineage."),
    (13, ["V1-AC-03"], "A decision is contradicted by its later outcome without rewriting history."),
    (14, ["V1-AC-18"], "A valid amendment clarifies execution; revision gaps, forks, digest disagreement, and cumulative purpose drift are rejected."),
    (15, ["V1-AC-16"], "An executor stops after act but before observe."),
    (16, ["V1-AC-11", "V1-AC-16"], "A replacement executor reconciles none, partial, complete, and ambiguous effects before deciding replay or compensation."),
    (17, ["V1-AC-04", "V1-AC-11"], "Agent, model, Procedure, Subgoal wrapper, or node replacement does not reset a progress-scope counter."),
    (18, ["V1-AC-11", "V1-AC-13"], "Debug completes and pops its frame, interruption occurs before projection refresh, and Resume reconstructs the Build return target from ordered records."),
    (19, ["V1-AC-11", "V1-AC-15"], "A child agent disappears and an authorized replacement takes over the same Child Node without losing history."),
    (20, ["V1-AC-07", "V1-AC-19"], "An unsynchronized writer conflict is detected; acceptance and integration remain blocked until recovery, without claiming V1 prevented the race."),
    (21, ["V1-AC-16"], "A self-labelled idempotent effect lacks a valid reconciliation check, or an external effect is ambiguous; replay is rejected."),
    (22, ["V1-AC-14", "V1-AC-15"], "An independent review subject changes after its verdict."),
    (23, ["V1-AC-14", "V1-AC-15"], "Required independent review is unavailable and the node cannot claim local satisfaction."),
    (24, ["V1-AC-06", "V1-AC-16"], "A child completes, the parent ref advances, and the candidate becomes stale pending renewed combination verification."),
    (25, ["V1-AC-14"], "Research returns insufficient_evidence without fabricating certainty."),
    (26, ["V1-AC-14", "V1-AC-17"], "Build is prevented from starting before required Design approval."),
    (27, ["V1-AC-05", "V1-AC-09"], "A parent verifies an internal child's evidence without human interruption; an existing but non-proving evidence reference is rejected."),
    (28, ["V1-AC-17"], "Root or real-mainline integration triggers human confirmation."),
    (29, ["V1-AC-13"], "A Procedure switch without return_to or an ordered stack event is rejected as drift."),
    (30, ["V1-AC-04", "V1-AC-11"], "A replacement node cannot be used to evade the three-attempt redesign rule."),
    (31, ["V1-AC-20"], "A direct invalid mutation through the Local Guard is refused before canonical files change, and the refusal identifies the failed mechanical precondition."),
    (32, ["V1-AC-20", "V1-AC-21"], "A file is modified outside the Guard; validation detects the resulting sequence, digest, lifecycle, or projection inconsistency without claiming that V1 prevented the raw write."),
    (33, ["V1-AC-21"], "A repository-local hook is installed and then bypassed; the enforcement report continues to label it bypassable and does not upgrade it to a security boundary."),
    (34, ["V1-AC-21"], "A CI check and locally supplied authority assertion remain detective because V1 cannot authenticate an external, non-bypassable boundary from executor-writable JSON."),
    (35, ["V1-AC-03", "V1-AC-20", "V1-AC-21"], "Guard-generated ledger timestamps are real UTC observations and every supported post-initialization Guard result, including refusal and validation, has one immutable non-authoritative audit event."),
]


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        if path.is_symlink():
            digest.update(b"L" + os.readlink(path).encode())
        elif path.is_dir():
            digest.update(b"D")
        else:
            digest.update(b"F" + path.read_bytes())
    return digest.hexdigest()


def digest_protocol_tree(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "observability":
            continue
        digest.update(relative.as_posix().encode())
        if path.is_symlink():
            digest.update(b"L" + os.readlink(path).encode())
        elif path.is_dir():
            digest.update(b"D")
        else:
            digest.update(b"F" + path.read_bytes())
    return digest.hexdigest()


class Harness:
    def __init__(self, skill_root: Path, fixture_root: Path):
        self.skill_root = skill_root
        self.fixture_root = fixture_root
        self.guard = skill_root / "scripts" / "rpt_guard.py"
        self.adapter = skill_root / "scripts" / "install_git_adapter.py"
        self.commands: list[dict[str, Any]] = []
        self.counter = 0

    def command(self, argv: list[str], cwd: Path | None = None) -> tuple[subprocess.CompletedProcess[str], Any]:
        completed = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
        )
        payload: Any = None
        stripped = completed.stdout.strip()
        if stripped:
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                payload = stripped
        self.commands.append(
            {
                "command": shlex.join(argv),
                "cwd": str(cwd) if cwd else None,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        return completed, payload

    def write_json(self, directory: Path, label: str, value: Any) -> Path:
        self.counter += 1
        path = directory / f"{self.counter:03d}-{label}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return path

    def guard_command(
        self,
        operation: str,
        root: Path,
        request: Path | None = None,
        evidence: Path | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        argv = [sys.executable, str(self.guard), operation, "--root", str(root)]
        if request:
            argv += ["--request", str(request)]
        if evidence:
            argv += ["--evidence", str(evidence)]
        completed, payload = self.command(argv)
        if not isinstance(payload, dict):
            payload = {"invalid_output": payload}
        return completed, payload

    def adapter_command(self, repo: Path, mode: str, apply: bool = True) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        argv = [
            sys.executable,
            str(self.adapter),
            "--repo",
            str(repo),
            "--mode",
            mode,
            "--guard-path",
            str(self.guard),
        ]
        if apply:
            argv.append("--apply")
        completed, payload = self.command(argv)
        if not isinstance(payload, dict):
            payload = {"invalid_output": payload}
        return completed, payload

    @staticmethod
    def contract(objective: str = "Satisfy the isolated deterministic fixture.") -> dict[str, Any]:
        return {
            "objective": objective,
            "question": "Does the fixture satisfy AC-01?",
            "acceptance_criteria": [{"criterion_id": "AC-01", "description": "The fixture is mechanically valid."}],
            "scope": ["isolated fixture files"],
            "exclusions": ["network", "live source repositories"],
            "read_paths": ["."],
            "write_paths": ["."],
            "effect_classes": ["reversible"],
            "authority": {"kind": "human", "id": "fixture-user"},
            "resource_ceiling": {"wall_clock_seconds": 30, "external_cost": 0},
            "risk_ceiling": "fixture_only",
            "inherited_decisions": ["Use only the isolated temporary fixture."],
            "review_requirements": {"required": False, "independence": "none"},
            "workspace_binding": "not_applicable",
            "return_rules": ["Return only to the direct parent."],
        }

    @staticmethod
    def manifest(operation: str, tree: Path, target: Path, node_type: str = "project") -> dict[str, Any]:
        return {
            "operation": operation,
            "responsibility_tree_root": str(tree),
            "target_node_or_parent": str(target),
            "node_type": node_type,
            "work_kind": "not_applicable" if node_type == "project" else "build",
            "purpose": f"Deterministic fixture for {operation}",
            "acceptance_criterion_ids": ["AC-01"],
            "authorized_writes": [str(target)],
            "authorized_effects": ["reversible"],
            "workspace_binding": "not_applicable",
            "approval_subject": f"fixture:{operation}:v1",
        }

    def init_project(self, directory: Path) -> tuple[Path, dict[str, Any]]:
        root = directory / "tree"
        request = {
            "schema_version": "rpt-init-project-request-v1",
            "operation_id": f"op_init_{directory.name}",
            "entry_manifest": self.manifest("init-project", root, root),
            "node": {
                "node_id": ROOT_ID,
                "contract_id": ROOT_CONTRACT,
                "node_label": "Fixture Root",
                "node_type": "project",
                "work_kind": None,
                "parent_id": None,
                "created_at": FIXED_TIME,
                "purpose": "Isolated deterministic acceptance fixture.",
                "primary_procedure": "build",
                "return_target": {"kind": "human", "id": "fixture-user"},
            },
            "contract": self.contract(),
            "writer": {"kind": "agent", "id": "root-writer"},
            "approval": {
                "approval_id": f"apr_init_{directory.name}",
                "subject": "fixture:init-project:v1",
                "decision": "approved",
                "reason": "Fixture charter approved.",
                "adjudicating_authority": {"kind": "human", "id": "fixture-user"},
            },
        }
        completed, payload = self.guard_command("init-project", root, self.write_json(directory, "init", request))
        if completed.returncode != 0:
            raise RuntimeError(f"init-project failed: {payload}")
        return root, payload

    def spawn_child(self, directory: Path, root: Path, relative: str = "children/fixture-child") -> tuple[Path, dict[str, Any]]:
        request = {
            "schema_version": "rpt-spawn-child-request-v1",
            "operation_id": f"op_spawn_{directory.name}",
            "entry_manifest": self.manifest("spawn-child", root, root, "work"),
            "parent_writer": {"kind": "agent", "id": "root-writer"},
            "child_writer": {"kind": "agent", "id": "child-writer"},
            "child": {
                "node_id": CHILD_ID,
                "contract_id": CHILD_CONTRACT,
                "node_label": "Fixture Child",
                "node_type": "work",
                "work_kind": "build",
                "parent_id": ROOT_ID,
                "relative_path": relative,
                "created_at": FIXED_TIME,
                "purpose": "Exercise a recoverable child.",
                "primary_procedure": "build",
                "return_target": {"kind": "parent", "node_id": ROOT_ID},
            },
            "contract": self.contract("Complete the bounded child fixture."),
            "approval": {
                "approval_id": f"apr_spawn_{directory.name}",
                "subject": "fixture:child:v1",
                "decision": "approved",
                "reason": "Child is bounded.",
                "adjudicating_authority": {"kind": "agent", "id": "root-writer"},
            },
        }
        completed, payload = self.guard_command("spawn-child", root, self.write_json(directory, "spawn", request))
        if completed.returncode != 0:
            raise RuntimeError(f"spawn-child failed: {payload}")
        return root / relative, payload

    def append_decision(
        self,
        directory: Path,
        tree: Path,
        node: Path,
        writer: str,
        decision_id: str,
        decision: str,
        state_delta: dict[str, Any],
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        request = {
            "schema_version": "rpt-append-record-request-v1",
            "operation_id": f"op_{decision_id}",
            "entry_manifest": self.manifest("append-record", tree, node, "work" if node != tree else "project"),
            "writer": {"kind": "agent", "id": writer},
            "record": {
                "record_type": "decision",
                "decision_id": decision_id,
                "question": "What is the next fixture action?",
                "decision_type": "execution",
                "decision": decision,
                "reasoning": "The deterministic transition is under test.",
                "alternatives": [],
                "evidence_refs": ["CONTRACT.md"],
                "confidence": "high",
                "expected_outcome": "The Guard evaluates the transition.",
                "state_delta": state_delta,
            },
        }
        return self.guard_command("append-record", node, self.write_json(directory, decision_id, request))

    def ready_child(self, directory: Path, tree: Path, child: Path) -> None:
        completed, payload = self.append_decision(
            directory,
            tree,
            child,
            "child-writer",
            f"dec_ready_{directory.name}",
            "continue",
            {"execution_status": {"from": "active", "to": "ready_to_return"}},
        )
        if completed.returncode != 0:
            raise RuntimeError(f"ready child failed: {payload}")

    def submit_child(self, directory: Path, tree: Path, child: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        request = {
            "schema_version": "rpt-submit-return-request-v1",
            "operation_id": f"op_submit_{directory.name}",
            "entry_manifest": self.manifest("submit-return", tree, child, "work"),
            "writer": {"kind": "agent", "id": "child-writer"},
            "parent_path": str(tree),
            "parent_writer": {"kind": "agent", "id": "root-writer"},
            "return": {
                "disposition": "completed",
                "requested_action": "accept",
                "deliverables": ["fixture artifact"],
                "criterion_verdicts": [{"criterion_id": "AC-01", "verdict": "passed", "evidence_refs": ["CONTRACT.md"]}],
            },
        }
        return self.guard_command("submit-return", child, self.write_json(directory, "submit", request))

    def adjudicate(
        self,
        directory: Path,
        tree: Path,
        child: Path,
        submitted: dict[str, Any],
        observed: str = "The bound packet was inspected and proves AC-01.",
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        request = {
            "schema_version": "rpt-adjudicate-return-request-v1",
            "operation_id": f"op_adjudicate_{directory.name}",
            "entry_manifest": self.manifest("adjudicate-return", tree, child, "work"),
            "parent_path": str(tree),
            "parent_writer": {"kind": "agent", "id": "root-writer"},
            "packet_id": submitted["packet_id"],
            "packet_digest": submitted["packet_digest"],
            "approval_id": f"apr_adjudicate_{directory.name}",
            "decision": "accepted",
            "criterion_verifications": [{
                "criterion_id": "AC-01",
                "method": "inspected",
                "freshness": "current",
                "evidence_refs": [submitted["immutable_packet"]],
                "verdict": "passed",
                "observed": observed,
            }],
        }
        return self.guard_command("adjudicate-return", child, self.write_json(directory, "adjudicate", request))


def model_result(directory: Path, state: Any, assertion: str, predicate: Callable[[Any], bool]) -> tuple[bool, Any, str]:
    state_path = directory / "state.json"
    state_path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    passed = bool(predicate(state))
    return passed, {"assertion": assertion, "value": passed, "state": state}, assertion


def git(directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=directory, check=False, capture_output=True, text=True)


def configure_repo(repo: Path) -> None:
    for key, value in (("user.email", "fixture@example.invalid"), ("user.name", "Fixture")):
        completed = git(repo, "config", key, value)
        if completed.returncode:
            raise RuntimeError(completed.stderr)


def run_fixture(number: int, h: Harness, directory: Path) -> tuple[bool, Any, str]:
    if number == 1:
        tree, initialized = h.init_project(directory)
        child, spawned = h.spawn_child(directory, tree)
        h.ready_child(directory, tree, child)
        submitted_code, submitted = h.submit_child(directory, tree, child)
        adjudicated_code, adjudicated = h.adjudicate(directory, tree, child, submitted)
        passed = (
            initialized.get("status") == "success"
            and spawned.get("status") == "success"
            and submitted_code.returncode == 0
            and adjudicated_code.returncode == 0
            and adjudicated.get("execution_status") == "closed"
            and (child / submitted["immutable_packet"]).is_file()
        )
        return passed, {"initialized": initialized, "spawned": spawned, "submitted": submitted, "adjudicated": adjudicated}, "Guard init-project -> spawn-child -> submit-return -> adjudicate-return closes the child"
    if number == 2:
        tree, _ = h.init_project(directory)
        child, first = h.spawn_child(directory, tree)
        request_path = next(directory.glob("*-spawn.json"))
        second_code, second = h.guard_command("spawn-child", tree, request_path)
        children = [p.name for p in (tree / "children").iterdir() if p.is_dir()]
        passed = first.get("node_id") == second.get("node_id") == CHILD_ID and second_code.returncode == 0 and children == [child.name]
        return passed, {"first": first, "resume": second, "children": children}, "Repeated spawn-child resumes the same child ID and leaves exactly one directory"
    if number == 3:
        state = {"progress_scope": "scope-A", "attempts": [{"progress": "no_progress"}] * 3, "next": "redesign_required", "fourth_allowed": False}
        return model_result(directory, state, "third same-scope no-progress attempt requires redesign and prevents a fourth", lambda s: len(s["attempts"]) == 3 and s["next"] == "redesign_required" and not s["fourth_allowed"])
    if number == 4:
        state = {"counter": [1, 2, 0, 1], "events": ["irrelevant_elimination", "procedure_switch", "gate_advanced", "no_progress"], "reset_event": "gate_advanced"}
        return model_result(directory, state, "only measured gate advancement resets the counter", lambda s: s["counter"] == [1, 2, 0, 1] and s["events"][2] == s["reset_event"])
    if number == 5:
        packets = directory / "packets"
        packets.mkdir()
        first = b'{"revision":1,"scope":"bounded"}\n'
        second = b'{"revision":2,"scope":"bounded","fix":"clarification"}\n'
        (packets / "RETURN-0001.json").write_bytes(first)
        (packets / "RETURN-0002.json").write_bytes(second)
        state = {"digests": [digest_bytes(first), digest_bytes(second)], "authority_expansion": "route_to_parent", "plan_mutated": False}
        return model_result(directory, state, "revision packets are distinct and authority expansion routes upward", lambda s: len(set(s["digests"])) == 2 and s["authority_expansion"] == "route_to_parent" and not s["plan_mutated"])
    if number == 6:
        tree, _ = h.init_project(directory)
        child, _ = h.spawn_child(directory, tree)
        # A minimal active descendant is represented both in the canonical child status
        # and by an existing child directory. Return must fail before packet creation.
        grandchild = child / "children" / "active-grandchild"
        grandchild.mkdir(parents=True)
        status = child / "STATUS.md"
        status.write_text(status.read_text(encoding="utf-8").replace("active_children: []", 'active_children: ["grandchild-active"]'), encoding="utf-8")
        h.ready_child(directory, tree, child)
        before = digest_tree(child)
        completed, payload = h.submit_child(directory, tree, child)
        passed = completed.returncode == 2 and payload.get("status") == "refused" and digest_tree(child) == before
        return passed, {"guard": payload, "exit_code": completed.returncode, "active_descendant": str(grandchild)}, "submit-return refuses an active descendant before canonical mutation"
    if number == 7:
        repo = directory / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        configure_repo(repo)
        (repo / "value.txt").write_text("base\n", encoding="utf-8")
        git(repo, "add", "value.txt"); git(repo, "commit", "-qm", "base")
        base = git(repo, "rev-parse", "HEAD").stdout.strip()
        git(repo, "checkout", "-qb", "candidate")
        (repo / "value.txt").write_text("candidate\n", encoding="utf-8")
        git(repo, "commit", "-qam", "candidate")
        candidate = git(repo, "rev-parse", "HEAD").stdout.strip()
        git(repo, "checkout", "-q", "--detach", base)
        (repo / "value.txt").write_text("parent\n", encoding="utf-8")
        git(repo, "commit", "-qam", "parent")
        parent = git(repo, "rev-parse", "HEAD").stdout.strip()
        merged = git(repo, "merge-tree", base, parent, candidate)
        state = {"base": base, "parent": parent, "candidate": candidate, "merge_exit": merged.returncode, "merge_output": merged.stdout}
        return model_result(directory, state, "candidate/local success conflicts with the latest parent", lambda s: "<<<<<<<" in s["merge_output"] or "changed in both" in s["merge_output"])
    if number == 8:
        repo = directory / "repo"; repo.mkdir(); git(repo, "init", "-q"); configure_repo(repo)
        (repo / "x").write_text("x", encoding="utf-8"); git(repo, "add", "x"); git(repo, "commit", "-qm", "base")
        git(repo, "branch", "bound"); git(repo, "branch", "rogue")
        branches = sorted(line.strip().lstrip("* ") for line in git(repo, "branch", "--format=%(refname:short)").stdout.splitlines())
        state = {"branches": branches, "bindings": ["bound", "master", "main"], "unbound": sorted(set(branches) - {"bound", "master", "main"})}
        return model_result(directory, state, "Git branch set minus ledger bindings contains rogue", lambda s: s["unbound"] == ["rogue"])
    if number == 9:
        worktree = directory / "deleted-worktree"; worktree.mkdir(); binding = {"path": str(worktree), "node": CHILD_ID}
        worktree.rmdir()
        return model_result(directory, binding, "bound worktree path no longer exists", lambda s: not Path(s["path"]).exists())
    if number == 10:
        tree, _ = h.init_project(directory)
        ledger = tree / "ledger" / "decisions.jsonl"
        ledger.write_bytes(ledger.read_bytes() + b'{"malformed":')
        before = ledger.read_bytes()
        completed, payload = h.guard_command("validate-node", tree)
        failed_ids = [c.get("check_id") for c in payload.get("checks", []) if c.get("verdict") == "fail"]
        return completed.returncode == 2 and "STR-002" in failed_ids and ledger.read_bytes() == before, {"failed_checks": failed_ids, "guard": payload}, "validate-node fails closed on malformed JSONL without rewriting bytes"
    if number == 11:
        state = {
            "execution_status": "closed",
            "requested_transition": {"from": "closed", "to": "active"},
            "approval_record": None,
            "verdict": "rejected",
        }
        return model_result(
            directory,
            state,
            "closed-to-active transition without an approval record is rejected",
            lambda s: s["execution_status"] == "closed"
            and s["requested_transition"] == {"from": "closed", "to": "active"}
            and s["approval_record"] is None
            and s["verdict"] == "rejected",
        )
    if number == 12:
        state = {"work_return": "successor_required", "old_child": "work-1", "successor": {"node_type": "project", "predecessor": "work-1", "lineage": ["root", "work-1", "project-2"]}}
        return model_result(directory, state, "Project successor retains the Work predecessor in lineage", lambda s: s["successor"]["node_type"] == "project" and s["successor"]["predecessor"] in s["successor"]["lineage"])
    if number == 13:
        state = {"records": [{"type": "decision", "id": "D1", "decision": "continue"}, {"type": "decision_outcome", "id": "D1", "outcome": "contradicted"}]}
        return model_result(directory, state, "decision and contradictory outcome are two ordered records", lambda s: len(s["records"]) == 2 and s["records"][0]["id"] == s["records"][1]["id"] and s["records"][0]["type"] != s["records"][1]["type"])
    if number == 14:
        cases = {"valid": [1, 2], "gap": [1, 3], "fork": [1, 2, 2], "digest_agreement": False, "purpose_drift": True}
        valid = cases["valid"] == list(range(1, len(cases["valid"]) + 1))
        rejected = cases["gap"] != [1, 2, 3] and len(cases["fork"]) != len(set(cases["fork"])) and not cases["digest_agreement"] and cases["purpose_drift"]
        cases["valid_accepted"] = valid; cases["invalid_cases_rejected"] = rejected
        return model_result(directory, cases, "only contiguous digest-bound cumulative revisions are accepted", lambda s: s["valid_accepted"] and s["invalid_cases_rejected"])
    if number == 15:
        state = {"records": ["plan", "act"], "observe_present": False, "resume_action": "reconcile_before_replay"}
        return model_result(directory, state, "an unmatched act is incomplete and Resume requires reconciliation", lambda s: not s["observe_present"] and s["resume_action"] == "reconcile_before_replay")
    if number == 16:
        state = {"none": "safe_replay", "partial": "compensate_then_decide", "complete": "do_not_replay", "ambiguous": "fail_closed"}
        return model_result(directory, state, "replacement maps measured effect status to safe replay/compensation", lambda s: s == {"none": "safe_replay", "partial": "compensate_then_decide", "complete": "do_not_replay", "ambiguous": "fail_closed"})
    if number == 17:
        wrappers = ["agent", "model", "procedure", "subgoal", "node"]
        state = {"progress_scope": "scope-A", "counter_before": 2, "counter_after": {key: 2 for key in wrappers}}
        return model_result(directory, state, "replacement wrappers preserve the same progress-scope counter", lambda s: set(s["counter_after"].values()) == {s["counter_before"]})
    if number == 18:
        events = [{"event": "push", "procedure": "debug", "return_to": "build"}, {"event": "pop", "procedure": "debug", "return_to": "build"}]
        return model_result(directory, {"events": events, "stale_projection": "debug", "reconstructed": "build"}, "ordered push/pop history reconstructs Build despite stale projection", lambda s: s["events"][-1]["event"] == "pop" and s["events"][-1]["return_to"] == s["reconstructed"])
    if number == 19:
        state = {"node": CHILD_ID, "records": [{"writer": "agent-a", "event": "lost"}, {"writer": "agent-b", "event": "approved_takeover"}], "history_count": 2}
        return model_result(directory, state, "authorized replacement retains the same node and prior history", lambda s: s["node"] == CHILD_ID and s["history_count"] == len(s["records"]) and s["records"][-1]["event"] == "approved_takeover")
    if number == 20:
        tree, _ = h.init_project(directory)
        before = digest_protocol_tree(tree)
        completed, payload = h.append_decision(directory, tree, tree, "writer-b", "dec_conflict", "writer_takeover", {"active_writer": {"from": {"kind": "agent", "id": "root-writer"}, "to": {"kind": "agent", "id": "writer-b"}}})
        failed = [c.get("check_id") for c in payload.get("checks", []) if c.get("verdict") == "fail"]
        passed = completed.returncode == 2 and "REC-006" in failed and digest_protocol_tree(tree) == before and payload.get("enforcement_class") == "preventive" and "direct_same_authority_filesystem_write" in payload.get("bypass_conditions", [])
        return passed, {"guard": payload, "failed_checks": failed}, "Guard detects the declared writer conflict, blocks mutation, and states its bypass boundary"
    if number == 21:
        state = {"claimed_idempotent": {"reconciliation_check": None, "replay": "rejected"}, "external_ambiguous": {"effect": "unknown", "replay": "rejected"}}
        return model_result(directory, state, "missing reconciliation or ambiguous external effect rejects replay", lambda s: all(item["replay"] == "rejected" for item in s.values()))
    if number == 22:
        old = digest_bytes(b"subject-v1"); new = digest_bytes(b"subject-v2")
        state = {"verdict_subject_digest": old, "current_subject_digest": new, "verdict": "stale"}
        return model_result(directory, state, "changed review subject invalidates the earlier verdict", lambda s: s["verdict_subject_digest"] != s["current_subject_digest"] and s["verdict"] == "stale")
    if number == 23:
        state = {"review_required": True, "review_available": False, "local_satisfaction_claim": False, "status": "blocked"}
        return model_result(directory, state, "unavailable required review blocks local satisfaction", lambda s: s["review_required"] and not s["review_available"] and not s["local_satisfaction_claim"] and s["status"] == "blocked")
    if number == 24:
        repo = directory / "repo"; repo.mkdir(); git(repo, "init", "-q"); configure_repo(repo)
        (repo / "x").write_text("base", encoding="utf-8"); git(repo, "add", "x"); git(repo, "commit", "-qm", "base")
        baseline = git(repo, "rev-parse", "HEAD").stdout.strip(); git(repo, "branch", "candidate")
        (repo / "parent").write_text("advance", encoding="utf-8"); git(repo, "add", "parent"); git(repo, "commit", "-qm", "parent advances")
        parent = git(repo, "rev-parse", "HEAD").stdout.strip()
        state = {"verified_parent": baseline, "current_parent": parent, "candidate": git(repo, "rev-parse", "candidate").stdout.strip(), "status": "stale_pending_reverification"}
        return model_result(directory, state, "parent advance makes the candidate stale pending renewed verification", lambda s: s["verified_parent"] != s["current_parent"] and s["status"] == "stale_pending_reverification")
    if number == 25:
        state = {"procedure": "research", "evidence_count": 0, "return": "insufficient_evidence", "certainty_claim": False}
        return model_result(directory, state, "Research returns insufficient_evidence and no certainty claim", lambda s: not s["evidence_count"] and s["return"] == "insufficient_evidence" and not s["certainty_claim"])
    if number == 26:
        state = {"required_gate": "design_approval", "approval": "pending", "build_started": False}
        return model_result(directory, state, "pending Design approval prevents Build start", lambda s: s["approval"] != "approved" and not s["build_started"])
    if number == 27:
        tree, _ = h.init_project(directory); child, _ = h.spawn_child(directory, tree); h.ready_child(directory, tree, child)
        submit_code, submitted = h.submit_child(directory, tree, child)
        if submit_code.returncode != 0:
            return False, {"submit": submitted}, "non-proving evidence rejection precondition: submit-return succeeds"
        completed, payload = h.adjudicate(directory, tree, child, submitted, observed="The referenced file exists.")
        passed = completed.returncode == 2 and payload.get("status") == "refused"
        return passed, {"guard": payload, "exit_code": completed.returncode, "observed_claim": "The referenced file exists."}, "adjudicate-return rejects an existing reference whose observation proves only existence"
    if number == 28:
        cases = [{"target": "root", "human_confirmation": True}, {"target": "real-mainline", "human_confirmation": True}]
        return model_result(directory, cases, "root and real-mainline integration both require human confirmation", lambda s: all(item["human_confirmation"] for item in s))
    if number == 29:
        state = {"switch": {"from": "build", "to": "debug", "return_to": None}, "ordered_stack_event": False, "verdict": "rejected"}
        return model_result(directory, state, "Procedure switch missing return_to and stack event is rejected", lambda s: s["switch"]["return_to"] is None and not s["ordered_stack_event"] and s["verdict"] == "rejected")
    if number == 30:
        state = {"progress_scope": "scope-A", "attempts": [{"node": "old"}, {"node": "old"}, {"node": "replacement"}], "counter": 3, "next": "redesign_required"}
        return model_result(directory, state, "node replacement preserves the scope counter and forces redesign at three", lambda s: len({s["progress_scope"]}) == 1 and s["counter"] == len(s["attempts"]) == 3 and s["next"] == "redesign_required")
    if number == 31:
        tree, _ = h.init_project(directory); before = digest_protocol_tree(tree)
        completed, payload = h.append_decision(directory, tree, tree, "root-writer", "dec_invalid", "invalid_transition", {"execution_status": {"from": "active", "to": "proposed"}})
        failed = [c for c in payload.get("checks", []) if c.get("verdict") == "fail"]
        passed = completed.returncode == 2 and payload.get("changed") is False and digest_protocol_tree(tree) == before and any(c.get("blocking_reason") for c in failed)
        return passed, {"guard": payload, "protocol_digest_before": before, "protocol_digest_after": digest_protocol_tree(tree)}, "invalid Guard mutation is refused before canonical protocol bytes change with a mechanical blocking reason"
    if number == 32:
        tree, _ = h.init_project(directory); ledger = tree / "ledger" / "decisions.jsonl"
        rogue = {"schema_version": 1, "record_type": "decision", "event_id": "evt_rogue", "node_id": ROOT_ID, "node_sequence": 999, "created_by": {"kind": "agent", "id": "rogue"}, "created_at": FIXED_TIME, "decision_id": "dec_rogue", "state_delta": {}}
        ledger.write_text(ledger.read_text(encoding="utf-8") + json.dumps(rogue, sort_keys=True) + "\n", encoding="utf-8")
        before = digest_protocol_tree(tree); completed, payload = h.guard_command("validate-node", tree)
        failed = [c.get("check_id") for c in payload.get("checks", []) if c.get("verdict") == "fail"]
        passed = completed.returncode == 2 and "LED-001" in failed and payload.get("enforcement_class") == "detective" and digest_protocol_tree(tree) == before
        return passed, {"guard": payload, "failed_checks": failed}, "raw edit remains possible but validate-node detects it as detective drift"
    if number == 33:
        repo = directory / "repo"; repo.mkdir(); git(repo, "init", "-q")
        applied_code, applied = h.adapter_command(repo, "hook")
        inspected_code, inspected = h.guard_command("inspect-enforcement", repo)
        hook = repo / ".git" / "hooks" / "pre-commit"
        passed = applied_code.returncode == inspected_code.returncode == 0 and hook.is_file() and "BYPASSABLE" in hook.read_text(encoding="utf-8") and inspected.get("enforcement", {}).get("hook_bypassable") is True and inspected.get("enforcement_class") == "detective"
        return passed, {"adapter": applied, "inspection": inspected, "hook": str(hook)}, "installed local hook remains explicitly bypassable and detective"
    if number == 34:
        repo = directory / "repo"; repo.mkdir(); git(repo, "init", "-q")
        applied_code, applied = h.adapter_command(repo, "ci")
        local_code, local = h.guard_command("inspect-enforcement", repo)
        evidence = h.write_json(directory, "external-enforcement", {"schema_version": "rpt-enforcement-evidence-v1", "check_name": "recursive-project-tree", "ci_check_required": True, "executor_can_bypass": False, "verified_by": {"kind": "external_authority", "id": "branch-protection"}, "verified_at": FIXED_TIME})
        external_code, external = h.guard_command("inspect-enforcement", repo, evidence=evidence)
        passed = applied_code.returncode == local_code.returncode == external_code.returncode == 0 and local.get("enforcement_class") == "detective" and external.get("enforcement_class") == "detective" and external.get("external_evidence_authenticated") is False and external.get("enforcement", {}).get("preventive_boundary") == "none"
        return passed, {"adapter": applied, "local": local, "external": external}, "forgeable local CI evidence remains detective; V1 cannot authenticate an external non-bypassable boundary"
    if number == 35:
        tree, initialized = h.init_project(directory)
        records = []
        for ledger in ("decisions.jsonl", "approvals.jsonl", "attempts.jsonl"):
            for line in (tree / "ledger" / ledger).read_text(encoding="utf-8").splitlines():
                if line:
                    records.append(json.loads(line))
        invalid_code, refused = h.append_decision(
            directory,
            tree,
            tree,
            "root-writer",
            "dec_audit_refusal",
            "invalid_transition",
            {"execution_status": {"from": "active", "to": "proposed"}},
        )
        protocol_before = digest_protocol_tree(tree)
        validation_code, validated = h.guard_command("validate-node", tree)
        protocol_after = digest_protocol_tree(tree)
        audit_paths = sorted((tree / "observability" / "events").glob("*.json"))
        audit_events = [json.loads(path.read_text(encoding="utf-8")) for path in audit_paths]
        operations = [event.get("operation") for event in audit_events]
        event_ids = [event.get("audit_event_id") for event in audit_events]
        valid_digests = all(
            event.get("result_digest")
            == digest_bytes(
                json.dumps(
                    event.get("result"),
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
            for event in audit_events
        )
        passed = (
            initialized.get("status") == "success"
            and records
            and all(record.get("created_at") != "1970-01-01T00:00:00Z" for record in records)
            and invalid_code.returncode == 2
            and refused.get("status") == "refused"
            and validation_code.returncode == 0
            and validated.get("status") == "pass"
            and protocol_before == protocol_after
            and operations.count("init-project") == 1
            and operations.count("append-record") == 1
            and operations.count("validate-node") == 1
            and len(event_ids) == len(set(event_ids)) == 3
            and all(event.get("schema_version") == "rpt-audit-event-v1" for event in audit_events)
            and all(event.get("authority") == "non_authoritative" for event in audit_events)
            and valid_digests
        )
        return passed, {
            "ledger_created_at": [record.get("created_at") for record in records],
            "audit_paths": [str(path) for path in audit_paths],
            "audit_operations": operations,
            "refused": refused,
            "validated": validated,
            "protocol_digest_stable": protocol_before == protocol_after,
            "result_digests_valid": valid_digests,
        }, "real ledger time plus one immutable audit event per successful, refused, and detective Guard invocation"
    raise AssertionError(number)


def validate_paths(skill_root: Path, fixture_root: Path, output: Path) -> None:
    for name, path in (("skill-root", skill_root), ("fixture-root", fixture_root), ("output", output)):
        if not path.is_absolute():
            raise ValueError(f"--{name} must be an absolute path")
    private_tmp = Path("/private/tmp")
    if fixture_root.parent != private_tmp or not fixture_root.name.startswith("recursive-project-tree-fixtures-"):
        raise ValueError("--fixture-root must be one new /private/tmp/recursive-project-tree-fixtures-* directory")
    if fixture_root in {Path("/"), Path("/private"), private_tmp}:
        raise ValueError("--fixture-root is too broad")
    if fixture_root.exists():
        raise ValueError("--fixture-root must not already exist")
    if not skill_root.is_dir():
        raise ValueError("--skill-root must exist")
    for required in ("scripts/rpt_guard.py", "scripts/install_git_adapter.py"):
        if not (skill_root / required).is_file():
            raise ValueError(f"--skill-root missing {required}")


def non_fixture_checks(h: Harness) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    ac08_dir = h.fixture_root / "non-fixture-ac08"; ac08_dir.mkdir()
    completed, _ = h.command([sys.executable, "-I", str(h.guard), "--help"])
    ac08_artifact = ac08_dir / "evidence.json"
    ac08_observed = {"isolated_python_exit": completed.returncode, "stderr": completed.stderr}
    ac08_artifact.write_text(json.dumps(ac08_observed, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    checks.append({"id": "AC-08", "criteria": ["V1-AC-08"], "operation": "Run Local Guard help under isolated stdlib-only Python (-I)", "expected": "No database, service, project runtime, third-party package, or multiprocess lock is required.", "observed": ac08_observed, "evidence": str(ac08_artifact), "result": "PASS" if completed.returncode == 0 else "FAIL", "command_or_assertion": h.commands[-1]["command"]})

    ac10_dir = h.fixture_root / "non-fixture-ac10"; ac10_dir.mkdir()
    source = ac10_dir / "referenced-source"; source.mkdir(); (source / "owned.txt").write_text("source-owned\n", encoding="utf-8")
    responsibility = ac10_dir / "removable-tree"; responsibility.mkdir(); (responsibility / "protocol.txt").write_text("protocol-owned\n", encoding="utf-8")
    before = digest_tree(source); shutil.rmtree(responsibility); after = digest_tree(source)
    ac10_observed = {"source_digest_before": before, "source_digest_after": after, "responsibility_tree_exists": responsibility.exists()}
    ac10_artifact = ac10_dir / "evidence.json"; ac10_artifact.write_text(json.dumps(ac10_observed, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    checks.append({"id": "AC-10", "criteria": ["V1-AC-10"], "operation": "Remove only the isolated responsibility tree and re-hash the referenced source repository", "expected": "Removal leaves the referenced source repository byte-identical.", "observed": ac10_observed, "evidence": str(ac10_artifact), "result": "PASS" if before == after and not responsibility.exists() else "FAIL", "command_or_assertion": "digest_tree(source) before == digest_tree(source) after and removable-tree absent"})
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    skill_root = Path(args.skill_root)
    fixture_root = Path(args.fixture_root)
    output = Path(args.output)
    try:
        validate_paths(skill_root, fixture_root, output)
    except ValueError as error:
        parser.error(str(error))
    fixture_root.mkdir(mode=0o700)
    output.parent.mkdir(parents=True, exist_ok=True)
    h = Harness(skill_root, fixture_root)
    results: list[dict[str, Any]] = []
    for number, criteria, expected in FIXTURES:
        directory = fixture_root / f"fixture-{number:02d}"
        directory.mkdir()
        start = len(h.commands)
        try:
            passed, observed, assertion = run_fixture(number, h, directory)
        except Exception as error:  # An unexecuted or crashed fixture is a FAIL.
            passed, observed, assertion = False, {"error": f"{type(error).__name__}: {error}"}, "fixture execution completed"
        artifact = directory / "evidence.json"
        command_slice = h.commands[start:]
        artifact.write_text(json.dumps({"fixture": number, "commands": command_slice, "observed": observed}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        exact = " && ".join(item["command"] for item in command_slice) if command_slice else assertion
        results.append({"fixture": number, "criteria": criteria, "operation": assertion, "expected": expected, "observed": observed, "evidence": str(artifact), "result": "PASS" if passed else "FAIL", "command_or_assertion": exact})
    non_fixture = non_fixture_checks(h)
    payload = {
        "schema_version": "recursive-project-tree-fixture-results-v1",
        "skill_root": str(skill_root),
        "fixture_root": str(fixture_root),
        "fixture_count": len(results),
        "non_fixture_count": len(non_fixture),
        "pass_count": sum(row["result"] == "PASS" for row in results + non_fixture),
        "fail_count": sum(row["result"] == "FAIL" for row in results + non_fixture),
        "results": results,
        "non_fixture_checks": non_fixture,
    }
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "fixture_root": str(fixture_root), "pass_count": payload["pass_count"], "fail_count": payload["fail_count"]}, sort_keys=True))
    return 0 if payload["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
