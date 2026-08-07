# Combined Orchestrator Panes and Visual Narratives Summary

**Date:** 2026-07-23T12:09
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - Unified Ingestion Dashboard

## Work Completed
1. **Middle Panel Consolidation**:
   - Combined `telemetry` (Whitelist/Bigrams Table) and `raw_traces` (eBPF Capture logs) into a single full-width middle row layout panel named `orchestrator` in [examples/demo.py](file:///home/drusifer/Projects/fingerling/examples/demo.py).
   - In Step 5, the `orchestrator` panel displays the compiled KubeArmorPolicy YAML manifest and analysis explanation.
   - In all other active walkthrough steps, it runs a unified dashboard widget `get_orchestrator_widget()`. This widget contains a borderless grid displaying:
     * **Left Column (40% width):** Active eBPF Daemon Status, live analytics metrics (Warehouse Size, Matcher window state, current anomaly score), the most recently captured syscall events list, and the dynamic Transitions Whitelist Map table.
     * **Right Column (60% width):** The scrolling eBPF capture logs and Webhook server access logs (`[SRV:WHK]`).
2. **ASCII/Unicode Flowcharts & Diagrams**:
   - Integrated detailed step-by-step Unicode flowcharts directly inside `get_narrative_text()` to visually outline:
     * **Step 1:** High-Level eBPF-driven Architecture Loop.
     * **Step 3:** Whitelist baseline ingestion mapping logic.
     * **Step 4:** Attacker command execution exploit flow and anomaly trigger.
     * **Step 5:** GitOps mitigation reconciliation loop.
     * **Step 7:** Active kernel-level process execution enforcement.
   - Relocated all port allocations, process PIDs, and GitOps checkout paths into the `orchestrator` status and Narrative Guide description blocks.
3. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
