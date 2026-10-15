# CHAT_SPRINT_17 — Sprint Archive

## Summary

Sprint 17, Duplicate Protection (Tier 2, 5 pts). Owner asked for protection against re-runs and overlapping sources via a sequence path. FING-49: profile declares sequence: <JSONPath>. FING-50: the set keeps {path, max}; later runs drop events at or below the run-start mark; missing sequence is a line error. Tank's close check found tests/test_e2e.py broken by fix/run-id (already pushed); fixed, lesson recorded. No release (mainline).

---
[<small>2026-10-14 20:05:59</small>] [**make**]->[**all**] *build*:
 Build PASSED | make gharchive | /home/drusifer/Projects/fingerling/build/build.out
updated data/gharchive/gh.fingerprints.yaml (profile 1db067a46a15e0ab287cd8c8e3321c22)
history: data/gharchive/gh.fingerprints.history/2026-10-15T000358Z.yaml

---
[<small>2026-10-14 20:06:11</small>] [**Neo**]->[**all**] *swe fix*:
 Owner: built-in samples 1 first + 1 last (was 3 each). Done on fix/one-sample: builtin.yaml, test, README/USER_GUIDE, DECISIONS. GH Archive run file 6.2 MB -> 2.1 MB; merge time unchanged (~119 s). 204 tests OK, lint clean.

---
[<small>2026-10-14 20:22:53</small>] [**make**]->[**all**] *build*:
 Build PASSED | make run | /home/drusifer/Projects/fingerling/build/build.out

---
[<small>2026-10-14 20:23:03</small>] [**Neo**]->[**all**] *swe fix*:
 Owner *fix: run ids YYMMDD-SEQ (UTC date + per-set sequence). Set stores last_run; first_seen/last_seen = first/last run id; envelope {meta: {run}} with no per-event time; history files named <run id>.yaml with run.id; -o uses no id; next SEQ counts history too. show: FIRST RUN/LAST RUN. 208 tests, lint, quality, smoke OK; GH Archive x2 from clean gives 261015-0001/0002.

---
[<small>2026-10-14 20:27:40</small>] [**make**]->[**all**] *build*:
 Build PASSED | make clean | /home/drusifer/Projects/fingerling/build/build.out
=== make clean @ 2026-10-14 20:27:40 ===

---
[<small>2026-10-14 20:38:31</small>] [**User**]->[**all**] *request*:
 Owner: duplicate protection via a sequence path; drop events <= captured max. Clarified: in the profile; compare to the mark at run start; missing seq is an error.

---
[<small>2026-10-14 20:38:31</small>] [**Cypher**]->[**Smith**] *pm handoff*:
 Sprint 17 (Duplicate Protection, Tier 2, 5 pts): FING-49 sequence in profile, FING-50 drop <= stored max, report, history header. docs/sprints/USER_STORIES_SPRINT17.md. Self-check rubric STORIES: OUT=S TEST=S FAIL=S SCOPE=S SIZE=S DESIGN=A. @Smith *user review sprint-17

---
[<small>2026-10-14 20:38:31</small>] [**Morpheus**]->[**Smith**] *lead handoff*:
 Arch D1-D4: Profile.sequence Path (schema top-level, id unchanged); FingerprintSet.sequence {path,max} saved/loaded; _Sequencer in _fold_stream (keep/DROP/None), path change resets mark with a notice; dropped: summary line. No build-env change. @Smith *user feedback

---
[<small>2026-10-14 20:38:31</small>] [**Smith**]->[**Mouse**] *user approve*:
 *user approve. rubric STORIES: OUT=S TEST=S FAIL=S SCOPE=S SIZE=S DESIGN=A. Arch approved: the dropped line states the mark, so a user sees why events vanished; path-change notice prevents a silent drop-all. Flag assumption 1 (line error vs abort) to the owner at the end. @Mouse *sm plan sprint

---
[<small>2026-10-14 20:38:31</small>] [**Mouse**]->[**Morpheus**] *sm handoff*:
 Sprint 17 planned in task.md: Phase 1 FING-49 + set mark storage, Phase 2 FING-50 filtering and reporting; close with Tank sdlc-check. @Morpheus *lead review sprint plan

---
[<small>2026-10-14 20:38:31</small>] [**Morpheus**]->[**Neo**] *lead handoff*:
 Plan approved. @Neo *swe impl phase-1

---
[<small>2026-10-14 20:38:31</small>] [**Mouse**]->[**all**] *phase 1*:
 Phase 1: sequence in the profile and the set (FING-49, D1-D2)

---
[<small>2026-10-14 20:38:57</small>] [**make**]->[**all**] *build*:
 Build PASSED | make lint | /home/drusifer/Projects/fingerling/build/build.out
=== make lint @ 2026-10-14 20:38:57 ===
All checks passed!
42 files already formatted

---
[<small>2026-10-14 20:39:05</small>] [**Neo**]->[**Trin**] *swe handoff*:
 Phase 1 done, tests first: schema top-level sequence; Profile.sequence (Path, problem 'sequence: <reason>'); FingerprintSet.sequence {path,max} saved after last_run and loaded; gharchive example sequence: $.id. 212 OK, lint clean. @Trin *qa uat phase-1

---
[<small>2026-10-14 20:39:05</small>] [**Trin**]->[**Morpheus**] *qa handoff*:
 UAT phase 1 pass: FING-49 AC1 optional path, AC2 invalid JSONPath located under sequence, AC3 profile id unchanged, AC4 example passes schema test; mark round-trips and is absent when unset. @Morpheus *lead review phase-1

---
[<small>2026-10-14 20:39:05</small>] [**Morpheus**]->[**Neo**] *lead handoff*:
 Phase 1 approved: D1-D2 as designed. @Neo *swe impl phase-2

---
[<small>2026-10-14 20:39:05</small>] [**Mouse**]->[**all**] *phase 2*:
 Phase 2: drop already-merged events (FING-50, D3-D4)

---
[<small>2026-10-14 20:40:33</small>] [**make**]->[**all**] *build*:
 Build PASSED | make lint | /home/drusifer/Projects/fingerling/build/build.out
=== make lint @ 2026-10-14 20:40:33 ===
All checks passed!
42 files already formatted

---
[<small>2026-10-14 20:40:43</small>] [**Neo**]->[**Trin**] *swe handoff*:
 Phase 2 done, tests first: _Sequencer (keep/DROP/None vs run-start mark), path-change notice, set mark updated after the fold, dropped: summary line, run header sequence {min,max}, help/README/USER_GUIDE, DECISIONS. History step extracted after radon C. 218 OK, lint and quality clean. @Trin *qa uat phase-2

---
[<small>2026-10-14 20:40:43</small>] [**Trin**]->[**Morpheus**] *qa handoff*:
 UAT phase 2 pass: AC1 mark stored; AC2 3,5,6,8 vs 5 merges 6,8 -> max 8; AC3 dropped line (incl. no earlier mark); AC4 missing/abc/bool ids are line errors, exit 1; AC6 path change notice; AC7 header range, omitted when none merged; AC8 no-sequence profile keeps mark. AC5 at Smith's GH Archive test. @Morpheus *lead review phase-2

---
[<small>2026-10-14 20:40:43</small>] [**Morpheus**]->[**Tank**] *lead handoff*:
 Phase 2 approved: D3-D4 as designed; _Sequencer keeps the fold readable. All phases reviewed. @Tank *devops sdlc-check

---
[<small>2026-10-14 20:40:44</small>] [**Mouse**]->[**all**] *phase close*:
 Close: Tank SDLC check, Oracle groom, Smith user test, retro, launch

---
[<small>2026-10-14 20:41:10</small>] [**make**]->[**all**] *build*:
 Build FAILED exit=2 | make test-fingerling | /home/drusifer/Projects/fingerling/build/build.out
127.0.0.1 - - [14/Oct/2026 20:41:10] "GET /ping?host=127.0.0.1;id HTTP/1.1" 200 -

---
[<small>2026-10-14 20:41:21</small>] [**Tank**]->[**Neo**] *devops reject*:
 SDLC check FAILED: make test-fingerling, 3 errors in tests/test_e2e.py - upsert(timestamp=) removed by fix/run-id (already on origin/main; that fix ran test-fingerprint only). @Neo *swe fix rename to run=

---
[<small>2026-10-14 20:41:40</small>] [**make**]->[**all**] *build*:
 Build PASSED | make test-all | /home/drusifer/Projects/fingerling/build/build.out
== Python 3.14 ==
Ran 218 tests in 2.073s
OK
Ran 50 tests in 3.293s
OK
== Python 3.15 ==
Ran 218 tests in 2.040s
OK
Ran 50 tests in 3.300s
OK

---
[<small>2026-10-14 20:41:53</small>] [**Neo**]->[**Tank**] *swe handoff*:
 Fix: tests/test_e2e.py upsert(timestamp=) -> run=. make test 218+50 OK, test-all OK on 3.14+3.15. @Tank *devops sdlc-check

---
[<small>2026-10-14 20:41:53</small>] [**Tank**]->[**Oracle**] *devops handoff*:
 SDLC re-check passed: test + test-all green after the e2e fix; rest unchanged from the first pass (from-clean build, lint, secrets, build, smoke, lock, venv, hooks). Last verified updated. @Oracle *ora groom

---
[<small>2026-10-14 20:41:54</small>] [**Oracle**]->[**Smith**] *ora handoff*:
 Docs groomed: DECISIONS entry (sequence dedup, run-start mark, line errors), LESSONS: run full make test when a signature changes (fix/run-id broke test_e2e, pushed). @Smith *user test sprint-17

---
[<small>2026-10-14 20:44:07</small>] [**make**]->[**all**] *build*:
 Build PASSED | make gharchive | /home/drusifer/Projects/fingerling/build/build.out
updated data/gharchive/gh.fingerprints.yaml (profile 1db067a46a15e0ab287cd8c8e3321c22)
history: data/gharchive/gh.fingerprints.history/261015-0002.yaml

---
[<small>2026-10-14 20:44:21</small>] [**Smith**]->[**all**] *user approve*:
 *user approve. GH Archive x2: run 2 read 180387, dropped 180387 (sequence <= 34503170055), 0 new/0 updated - AC5 holds. Summary explains the drop. rubric LESSON (2026-10-14 full make test): specific, cause shown, action checkable - all A or better. Owner check: assumption 1 (missing seq = line error, not abort). @all *sprint retro

---
[<small>2026-10-14 20:44:21</small>] [**Neo**]->[**Cypher**] *retro*:
 Neo retro: _Sequencer kept the fold flat; radon caught _cmd_merge at C again (history step extracted). I broke test_e2e in fix/run-id by running one suite. Backlog items: none

---
[<small>2026-10-14 20:44:22</small>] [**Trin**]->[**Cypher**] *retro*:
 Trin retro: +10 tests (208->218 fingerprint); Tank's from-clean run caught a pushed regression the per-package suite missed. Backlog items: none

---
[<small>2026-10-14 20:44:22</small>] [**Morpheus**]->[**Cypher**] *retro*:
 Morpheus retro: profile-declared sequence + run-start mark is simple and safe. Backlog items: in-run duplicate detection if a stream needs it

---
[<small>2026-10-14 20:44:22</small>] [**Oracle**]->[**Cypher**] *retro*:
 Oracle retro: lesson recorded for the fix/run-id miss. Backlog items: none

---
[<small>2026-10-14 20:44:22</small>] [**Mouse**]->[**Cypher**] *retro*:
 Mouse retro: 2 phases, 5/5 pts, 1 close fix cycle (pre-existing break). Backlog items: none

---
[<small>2026-10-14 20:44:22</small>] [**Smith**]->[**Cypher**] *retro*:
 Smith retro: dedup is visible and explained. Backlog items: confirm missing-seq policy with owner

---
[<small>2026-10-14 20:44:22</small>] [**Cypher**]->[**Cypher**] *retro*:
 Cypher retro: owner answers up front kept stories stable. Backlog items: in-run duplicates; missing-seq policy check

---
[<small>2026-10-14 20:44:34</small>] [**Cypher**]->[**all**] *pm launch*:
 *pm launch sprint-17. Duplicate protection: a profile can declare sequence: $.id; the set keeps the highest merged and later runs drop events at or below it (re-running a GH Archive hour drops all 180387). 5/5 pts. Also fixed test_e2e broken by fix/run-id. No release (mainline). Sprint complete.

