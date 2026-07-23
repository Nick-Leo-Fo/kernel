# Local Guard test evidence

Date: 2026-07-23

## Installed subjects

| Subject | SHA-256 |
|---|---|
| `/Users/evan/.codex/skills/recursive-project-tree/scripts/rpt_guard.py` | `d1c89e85209ba36c82cecb42900dd4755df9f1b420a429e65f097ea899723200` |
| `/Users/evan/.codex/skills/recursive-project-tree/scripts/install_git_adapter.py` | `b5099fa49e3524f741dd6b017f72e0f7c358a651beff3ec2aef5e24011341f5c` |
| `/private/tmp/test_rpt_guard.py` | `f94a1cd87c8b9c7c5580120775efe42caadaf5f4cde771dc3f0b67fd4e2480ff` |
| `/private/tmp/test_rpt_guard_commands.py` | `9c6035e3a3d4617fb2d04c36d26490e69750e650be656871cc8f44cfe2df6cdc` |
| `/private/tmp/test_rpt_guard_security.py` | `075c1da38d1a459e88ed6dce886742a880b87cdbc45ba4a8a172cfabb83e80ca` |

The test modules are temporary authoring evidence. Fixture trees and Git
repositories were created only below the system temporary directory and were
removed by `TemporaryDirectory`; no hook or CI adapter was installed into
Kernel or another real repository.

## RED

The plan's literal command was run first:

```bash
python3 -m unittest -v /private/tmp/test_rpt_guard.py
```

On the installed Python 3.14.6 this exited `1` before discovery because
`unittest` interpreted the absolute path as a module name:
`ModuleNotFoundError: No module named '/private/tmp/test_rpt_guard'`. This was
an invocation error, not accepted as the TDD RED.

The equivalent direct-file invocation was therefore used:

```bash
python3 /private/tmp/test_rpt_guard.py -v
```

It exited `1`, ran exactly twelve tests, and reported twelve failures. Every
failure was caused by the absent production subject:

```text
can't open file '/Users/evan/.codex/skills/recursive-project-tree/scripts/rpt_guard.py':
[Errno 2] No such file or directory
Ran 12 tests in 1.653s
FAILED (failures=12)
```

No production code existed before this observed feature-missing RED.

## GREEN

```bash
python3 /private/tmp/test_rpt_guard.py -v
```

Exit `0`:

```text
Ran 12 tests in 12.630s
OK
```

## Command-completion RED/GREEN

`/private/tmp/test_rpt_guard_commands.py` adds three subprocess-only command
tests. Its initial RED observed the missing command implementations: independent
`activate-child` still dispatched to spawn, while `submit-return` and
`adjudicate-return` returned `INV-001` / `not implemented`.

After the minimal command implementation, each command test passed directly:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/rpt-guard-pycache \
  python3 /private/tmp/test_rpt_guard_commands.py \
  GuardCommandTests.test_activate_is_an_independent_command -v
# Ran 1 test ... OK

PYTHONPYCACHEPREFIX=/private/tmp/rpt-guard-pycache \
  python3 /private/tmp/test_rpt_guard_commands.py \
  GuardCommandTests.test_submit_creates_an_immutable_packet -v
# Ran 1 test ... OK

PYTHONPYCACHEPREFIX=/private/tmp/rpt-guard-pycache \
  python3 /private/tmp/test_rpt_guard_commands.py \
  GuardCommandTests.test_adjudicate_requires_the_direct_parent -v
# Ran 1 test ... OK
```

The baseline suite was then rerun unchanged:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/rpt-guard-pycache \
  python3 /private/tmp/test_rpt_guard.py -v
# Ran 12 tests in 15.557s
# OK
```

| ID | Command result |
|---|---|
| GUARD-CMD-01 | PASS — `activate-child` has its own request schema/dispatch and verifies the existing direct-child/intent binding without re-running spawn. |
| GUARD-CMD-02 | PASS — `submit-return` exclusively creates `returns/RETURN-NNNN.md`, returns its SHA-256 digest, and moves the child to `parent_verdict: pending` under the direct parent writer. |
| GUARD-CMD-03 | PASS — `adjudicate-return` checks the direct parent identity and writer, binds the immutable packet digest, records a child-ledger approval with criterion verification, and releases the writer on accepted closure. |

## Security review RED/GREEN

Three public-interface subprocess tests in
`/private/tmp/test_rpt_guard_security.py` reproduced the reviewer findings.
Each selector was run independently so inherited baseline tests were not
duplicated. The initial RED established that symlinked roots/targets could
escape, Return packet mutation was not validated and could be rebound with a
caller digest, and duplicate or unknown criterion IDs were accepted.

After the minimal repair, the exact selectors passed:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/rpt-guard-pycache \
  python3 /private/tmp/test_rpt_guard_security.py \
  GuardSecurityTests.test_symlink_escape_is_refused_for_spawn_and_adapter_targets \
  GuardSecurityTests.test_packet_tampering_fails_validation_and_cannot_rebind_digest \
  GuardSecurityTests.test_adjudication_requires_exact_contract_criterion_set -v
# Ran 3 tests in 10.043s
# OK
```

| ID | Security result |
|---|---|
| GUARD-SEC-01 | PASS — root aliases, symlinked node paths, spawn targets, and hook/CI adapter targets are refused before out-of-tree writes. |
| GUARD-SEC-02 | PASS — `RET-003` validates submitted packets against the authoritative ledger digest; adjudication must match that digest and current bytes. |
| GUARD-SEC-03 | PASS — verification IDs equal the unique active Contract criterion set; accepted verdicts are passed and cite the bound packet. |

Final explicitly selected regression results:

```text
baseline: Ran 12 tests in 13.104s — OK
commands: Ran 3 tests in 4.709s — OK
security: Ran 3 tests in 10.043s — OK
```

The fixture digest column below records the SHA-256 relation asserted by the
black-box test. Fixtures are intentionally ephemeral, so their random-path-
dependent raw hashes are not retained after teardown; `same` means the test
computed both hashes with `stable_tree_digest` and required byte-for-byte
equality.

| ID | Black-box result | Guard/adapter exits | Fixture SHA-256 relation |
|---|---|---|---|
| GUARD-01 | PASS — versioned read-only validation returned `pass` and `changed:false` | `init-project=0`, `validate-tree=0` | initialized tree: `same -> same` |
| GUARD-02 | PASS — illegal `active -> proposed` transition was refused with `LIF-001` before mutation | `append-record=2` | canonical tree: `same -> same` |
| GUARD-03 | PASS — decision, approval, and five Attempt records received one contiguous cross-ledger order | seven `append-record=0` | ordered ledgers: `before != after`; sequences exactly `1..N` |
| GUARD-04 | PASS — malformed JSONL produced `STR-002` refusal and its malformed bytes were not rewritten | `append-record=2` | malformed ledger bytes: `same -> same` |
| GUARD-05 | PASS — an unresolved persisted intent resumed the same child ID; a repeat produced no duplicate | intent append `3`, spawn `0`, repeat `0` | first completion `before != after`; repeat child set `same -> same` |
| GUARD-06 | PASS — injected `os.replace` failure left the previous canonical ledger intact | `append-record=3` | canonical ledger bytes: `same -> same` |
| GUARD-07 | PASS — deterministic post-replace corruption failed postcondition validation and emitted a recovery artifact | `append-record=3` | canonical digest changed; artifact binds pre-write digests and observed paths |
| GUARD-08 | PASS — a second declared writer was refused with `REC-006` | `append-record=2` | canonical tree: `same -> same` |
| GUARD-09 | PASS — raw sequence drift was detected as detective, with no prevention claim | `validate-node=2` | validator: `same -> same` after the prior raw edit |
| GUARD-10 | PASS — dry-run changed nothing; applied local hook was reported present and bypassable | inspect `0`, dry-run `0`, apply `0`, inspect `0` | inspect calls `same -> same`; fixture hook apply changed only the temporary repo |
| GUARD-11 | PASS — workflow presence without external requirement remained detective | inspect `0`, CI apply `0`, inspect `0` | inspect calls `same -> same`; fixture CI apply changed only the temporary repo |
| GUARD-12 | PASS — verified externally required, non-bypassable CI reported preventive at the integration boundary | inspect `0`, CI apply `0`, inspect-with-evidence `0` | final inspect `same -> same` |

GUARD-06 and GUARD-07 inject failures through a temporary
`sitecustomize.py` supplied only to the subprocess. The production scripts
contain no test-only fault switch.

## Compilation and dependency checks

```bash
python3 -m py_compile \
  /Users/evan/.codex/skills/recursive-project-tree/scripts/rpt_guard.py \
  /Users/evan/.codex/skills/recursive-project-tree/scripts/install_git_adapter.py
```

Exit `0`.

```bash
rg -n '^(import|from) ' \
  /Users/evan/.codex/skills/recursive-project-tree/scripts
```

The Python scripts import only `argparse`, `hashlib`, `json`, `os`, `pathlib`,
`shutil`, `subprocess`, and `tempfile`, all from the standard library. There is
no database, daemon, network service, project runtime, third-party package, or
multi-process lock.

## Enforcement boundary

Standalone validation and ordinary CI are detective. A repository-local hook
is explicitly marked bypassable. A Guard precondition is preventive only for
the named Guard-routed mutation. CI becomes preventive only at the integration
boundary when separately supplied evidence establishes both that an external
authority requires the check and that the executor cannot bypass it.

The residual bypass condition remains:

```text
direct_same_authority_filesystem_write
```

V1 detects surviving drift evidence but does not claim to prevent arbitrary
same-user raw filesystem writes.

## Bounded command coverage

The twelve baseline scenarios exercise `init-project`, `spawn-child`,
`append-record`, `validate-node`, `validate-tree`, `inspect-enforcement`, and
both Git adapter modes. The additional command and security subprocess
scenarios cover independent child activation, immutable return submission,
direct-parent adjudication, canonical-path containment, packet-digest
validation, and exact criterion verification. They do not claim broader
workflow coverage beyond those concrete command contracts.
