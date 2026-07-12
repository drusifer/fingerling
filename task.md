# Task Board — Sprint: POC Fingerling

**Status:** Planning complete, ready for Phase 1 (Neo)
**Source:** `docs/USER_STORIES.md` + `docs/ARCH.md`
**Sprint Log:** `agents/mouse.docs/sprint_log.md`

## Phase 1 — Scaffolding & Telemetry Tokenizer (STORY-FING-01)
- [ ] 1.1 Scaffold package: `fingerling/__init__.py`, `tests/__init__.py`, `requirements.txt` (PyYAML)
- [ ] 1.2 Implement `fingerling/tokenizer.py` (path resolver + modifier registry: `DEFAULT`,
      `IS_PRESENT`, `IS_NULL`, `IN_RANGE`, `ANY`; missing/null → stable `"FALSE"`/`"NULL"`, never raises)
      + `tests/test_tokenizer.py` covering AC1-4 and both Verification Tasks.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 2 — Stateful Upsert Warehouse (STORY-FING-02)
- [ ] 2.1 Implement `fingerling/warehouse.py` (`fingerprint_id()` alphabetical MD5 fold,
      `Warehouse.upsert()` match/drift reconciliation, sample ring capped at 3, `load`/`save` YAML)
      + `tests/test_warehouse.py` covering AC1-3 and both Verification Tasks.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 3 — Sliding Window Ring Buffer Matcher (STORY-FING-03)
- [ ] 3.1 Implement `fingerling/ringbuffer.py` (`SlidingWindowMatcher`: FIFO window, `warm`
      property, `push()` → 0.0/1.0 whitelist match) + `tests/test_ringbuffer.py` covering AC1-4
      and both Verification Tasks (N=3 warm-up, off-whitelist anomaly).

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 4 — KubeArmor Policy Compiler (STORY-FING-04)
- [ ] 4.1 Implement `fingerling/policy.py` (`compile_policy()`: `matchLabels`, explicit
      `action: Literal["Block","Post"] = "Block"`) + `tests/test_policy.py` covering AC1-3 and
      both Verification Tasks (schema shape, matchLabels mapping).

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus (last phase → hands to Oracle for `*ora groom`)

---

## Definition of Done (per phase)
- [ ] `make test` passes (full suite, since each phase is additive and cheap for this POC size)
- [ ] Trin UAT confirms all AC + Verification Tasks for the story
- [ ] Morpheus confirms architectural alignment with `docs/ARCH.md`

## Out of scope this sprint (tracked, not planned)
Webhook ingestion server, sandbox/cgroup provisioning, live Nuclei/Metasploit execution, GPG-signed
Git commit/PR automation, AccuKnox/KubeArmor cluster deployment.
