# **Project Fingerling: Comprehensive Software Engineering Document Suite**

**Classification:** Internal Technical Confidentials  
**Author:** AI Engineering & Architecture Initiative  
**Date:** July 2026  
**System Version:** 1.3.0-POC

# **Document 1: Business Requirements Document (BRD)**

## **1\. Executive Summary**

Traditional enterprise vulnerability management faces a severe operational gap: the time window between an automated scanner discovering an unpatched CVE and application engineering teams deploying a permanent source-code fix to production. During this window of exposure, infrastructure relies on coarse perimeter blocks (WAFs) or passive alerting.  
Project **Fingerling** provides an automated, self-learning, adaptive software immune system. Operating directly at the Linux kernel layer via eBPF telemetry, Fingerling executes a closed-loop workflow: it ingests upstream vulnerability reports, subjects isolated workloads to "controlled exposure" (vaccination), and programmatically extracts structural system call transition sequences. By shifting defense away from brittle cryptographic hashes and static user-space payload signatures, Fingerling compiles fuzzy $N$-gram transition composition models ("antibodies").  
These antibodies are dynamically validated against an environment-aware baseline before being deployed as persistent inline blocks via AccuKnox/KubeArmor, significantly cutting down the Time-To-Vulnerability-Mitigation (TTVM) while guaranteeing zero production false positives.

## **2\. Strategic Objectives & Business Value Drivers**

### **2.1 Autonomous Attack Surface Reduction**

* **Target:** Lower Time-To-Vulnerability-Mitigation from days or weeks to single-digit minutes.  
* **Mechanism:** Eliminate human intervention from the vulnerability discovery, validation, virtual patch generation, and rollout cycle.

### **2.2 Operational Stability Assurance**

* **Target:** Maintain a strict 0% false-positive enforcement rate across production environments.  
* **Mechanism:** Gate every virtual patch against a historical inventory of normalized business logic profiles, automatically rejecting brittle rules before they hit live traffic.

### **2.3 Cross-Reactive Runways for Development**

* **Target:** Protect workloads against both targeted CVE strings and polymorphic variations.  
* **Mechanism:** Leverage fuzzy sequence matching to bind defenses to underlying kernel execution trajectories, buying engineering teams an extended, risk-free runway to write source-level software fixes.

## **3\. Product Scope Boundaries**

### **3.1 In-Scope**

* **Upstream Ingestion Hooking:** Webhook targets parsing machine-readable JSON/YAML vulnerability feeds from enterprise scanners (e.g., Trivy, Grype, Wiz, Prisma Cloud).  
* **Controlled Exposure Testing:** Automating offensive template executions (e.g., Nuclei YAML configurations, Metasploit RPC tasks) within sandboxed test environments.  
* **Fuzzy N-Gram Telemetry Analysis:** Parsing streaming JSON Lines (JSONL) from kernel-space probes and mapping them into sliding-window transition tokens.  
* **Workload-Bound Persistence:** Compiling declarative security rules explicitly mapped to workloads via Kubernetes Label Selectors (matchLabels), ensuring protection persists across node migrations and autoscaling adjustments.

### **3.2 Out-of-Scope**

* Custom modifications to the low-level Linux kernel LSM kernel distribution trees.  
* Complete replacement of application-layer identity routers or traditional edge firewalls.  
* Automatic manipulation or rewriting of third-party source-code repositories.

## **4\. Biological Immune Analogy Mapping**

| Biological Immune Subsystem | Project Fingerling Technical Counterpart | Functional Responsibility |
| :---- | :---- | :---- |
| **Pathogen** | CVE Exploit Vector / Malicious Payload | The structural payload invading host application space. |
| **Vaccination** | Controlled Sandbox Exposure Engine | Running targeted exploit simulations within an isolated testing cgroup to map dangerous execution paths safely. |
| **Epitope** | System Call N-Gram Transition Window | The granular sequence of kernel behaviors that betrays an exploit's presence. |
| **Antibody** | Compiled AccuKnox/KubeArmor LSM Policy | The declarative filter that binds to specific execution anomalies and neutralizes them inline. |
| **Cross-Reactive Immunity** | Fuzzy Composition Matching ($1.0 \- \\text{Similarity}$) | The capacity to block modified, obfuscated, or mutant variations of an exploit because the kernel-level behavioral trajectory remains highly similar. |
| **Memory B-Cells** | Stateful Append-Only YAML Data Warehouse | A compressed historical baseline repository that learns and remembers code paths across consecutive days, optimizing runtime behavior over time. |

## **5\. Environment-Aware Continuous Learning Requirements**

* **Environment-Aware Baselines:** Staging and automated integration testing environments act as the primary sources for discovering new application features and generating new fingerprint hashes. Production telemetry streams are explicitly reserved for traffic volume analysis, performance metrics tuning, and tracking low-frequency executions.  
* **Continuous Integration Gating:** If a production instance observes a completely unrecognized fingerprint token outside of an active deployment window, the system registers it as a high-signal security anomaly rather than automatically expanding the baseline. This setup prevents baseline poisoning and stops attackers from slowly training the system to tolerate malicious trajectories.

# **Document 2: Product Requirements Document (PRD)**

## **1\. User Personas**

### **DevSecOps Engineer (SecOps Sam)**

* **Needs:** Wants to instantly mitigate critical image vulnerabilities discovered in production without interrupting application deployment cycles or waiting on engineering sprints.  
* **Pain Points:** Tired of alert fatigue from passive scanners and fears turning on active blocking because traditional tools lack validation and risk breaking core business logic.

### **Platform Engineer (Platform Pat)**

* **Needs:** Demands that any dynamic host security mechanism introduces near-zero overhead, runs transparently below the user-space layer, and adheres to GitOps principles.  
* **Pain Points:** Worried about brittle security rules that stay pinned to fixed IP addresses or specific host nodes, leading to cluster reconciliation failures during auto-scaling events.

## **2\. Comprehensive Functional Specifications**

### **2.1 Webhook Vulnerability Ingestion (FR-JSON-01)**

* **Input:** Automated JSON payload from enterprise vulnerability scanners.  
* **Requirement:** Parse and extract the target image tag, CVE-ID, specific namespace, and associated container deployment matchLabels.  
* **Output:** Initialize an entry in the compiler workspace queue and provision an isolated replica of the exact container image version in a testing cgroup.

### **2.2 JSONPath Extraction & Plug-and-Play Modifier Engine (FR-MOD-01)**

* **Input:** Raw streaming JSONL kernel event data from eBPF probes.  
* **Requirement:** Extract targeted properties using configurable JSONPath definitions inside an execution Mask Profile.  
* **Requirement:** Filter extracted properties through an extensible library of modifier expressions to eliminate high-cardinality data bloat before hashing.  
* **Supported Core Modifiers:**  
  * DEFAULT: Passes the literal stringified value directly (reserved for low-cardinality enumerations like syscall names).  
  * IS\_PRESENT: Returns "TRUE" if the path points to an allocated, non-null value, else "FALSE" (collapses unbounded elements like file names).  
  * IS\_NULL: Returns "TRUE" if the path node is missing or explicitly null, else "FALSE".  
  * IN\_RANGE(low, high): Evaluates numeric variables. Casts inputs and checks mathematical inclusion: $low \\le value \\le high$ (collapses variable parameters like bytes or return states).  
  * ANY(v1, v2, ...): Evaluates explicit set membership against a whitelisted group of configurations (collapses listening ports).  
  * GLOB / REGEX: Evaluates pattern compliance and returns "TRUE" upon a successful structural match (abstracts directory structures).

### **2.3 Append-Only Stateful Upsert Warehouse (FR-STF-01)**

* **Input:** Tokenized execution arrays generated by the modifier layer.  
* **Requirement:** Calculate a 32-character MD5 signature across the alphabetized, flattened key-value array to yield a stable Fingerprint ID.  
* **State Reconciliation Logic (The Upsert Loop):**  
  * **Match State:** If the signature exists in the historical YAML database, update the tracking window (last\_seen\_timestamp) and increment total\_occurrences. Update the running $\\min/\\max$ performance limits. Do not append a new record block.  
  * **Drift State:** If the signature is absent, provision a brand new entry block. Capture the full raw input log frame and insert it into a fixed-size ring buffer inside the sample metadata block (maximum array capacity of 3 samples) to preserve structural context without data bloat.

### **2.4 Stateful Sliding Window Memory Ring Buffer Matcher (FR-BUF-01)**

* **Input:** Ordered stream of generated Fingerprint IDs during execution testing.  
* **Requirement:** Pipe Fingerprint IDs into a stateful, first-in-first-out (FIFO) memory ring buffer configured to a fixed window size $N$.  
* **Requirement:** Construct rolling, contiguous tuple paths (N-grams) at each step of the ring buffer execution.  
* **Execution Boundary Independence:** The ring buffer must extract sequences continuously, evaluating transitions independently of application execution block alignments or multi-threaded interleaving gaps.

### **2.5 Automated Workload-Bound GitOps Delivery (FR-GIO-01)**

* **Input:** Passing fingerprint validation score from the regression gate.  
* **Requirement:** Automatically compile a declarative KubeArmorPolicy CRD manifest.  
* **Requirement:** Hardcode the target microservice’s logical identifiers inside the manifest using Kubernetes Label Selectors (matchLabels).  
* **Requirement:** Programmatically check out a Git hotfix branch, commit the manifest using a cryptographically secure machine GPG key, issue an integration pull request, and auto-merge the branch to trigger cluster reconciliation.

## **3\. Non-Functional Requirements (NFR)**

### **3.1 Sub-Millisecond Processing Performance**

* The extraction, transformation, and sliding window ring buffer operations must execute in sub-millisecond timelines, introducing near-zero processing lag to host kernel telemetry routers.

### **3.2 Metadata Storage Preservation**

* The stateful upsert inventory architecture must enforce a hard cap on metadata size by utilizing fixed-size reference slots for log samples. This setup allows the system to aggregate production metrics indefinitely over multi-day training windows while keeping the tracking manifest small enough to sit inside a light Git infrastructure repository.

### **3.3 Administrative Control Plane Isolation**

* The automated compiler daemon must reside within a separated administrative boundary, leveraging isolated namespaces and RBAC profiles to ensure that compromised application runtimes cannot write to or tamper with the security policy definitions.

# **Document 3: Architecture & System Design (ARCH)**

## **1\. System Topology & Data Pipeline States**

The architectural blueprint below outlines the closed-loop automation lifecycle, charting the transition of data from upstream scanner discoverability to down-stream in-kernel defense enforcement:

┌───────────────────────────────┐  
│  Enterprise Security Scanner  │  
└───────────────┬───────────────┘  
                │  
                ▼ (Webhook Ingestion Trigger: Image Tag, CVE-ID, Labels)  
┌───────────────────────────────┐  
│  Fingerling Compiler Queue    │  
└───────────────┬───────────────┘  
                │  
                ▼ (Provisions Sandbox Test Workload Cgroup)  
┌───────────────────────────────┐  
│ Controlled Exposure Sandbox   ├───────────► \[ 1\. Run Staging Fingerprint Replays \]  
└───────────────┬───────────────┘             \[ 2\. Run Targeted Nuclei Exploit     \]  
                │  
                ▼ (Streams Raw JSONL Telemetry Probes)  
┌───────────────────────────────┐  
│ JSONPath Extraction Engine    │  
└───────────────┬───────────────┘  
                │  
                ▼ (Passes Fields Through Plug-and-Play Modifiers)  
┌───────────────────────────────┐  
│ Anomaly Suppression Layer     │  
└───────────────┬───────────────┘  
                │  
                ▼ (Alphabetical Key Sort & MD5 Cryptographic Folding)  
┌───────────────────────────────┐  
│ Stable Fingerprint Generator  │  
└───────────────┬───────────────┘  
                │  
                ▼ (Pipes Unique Token Identifiers Continuously)  
┌───────────────────────────────┐  
│ Sliding Window Ring Buffer    ├───────────► \[ Evaluates Sequence Trajectory \]  
└───────────────┬───────────────┘  
                │  
                ▼ (Calculates Jaccard Overlap Matrix)  
┌───────────────────────────────┐  
│ Fuzzy Regression Gate System  │  
└───────────────┬───────────────┘  
                │  
                ▼ (Pass Mark: GPG-Signed Commit & Auto-Merge PR)  
┌───────────────────────────────┐  
│ GitOps Infrastructure Track   │  
└───────────────┬───────────────┘  
                │  
                ▼ (Cluster Reconciliation Loop Deployment)  
┌───────────────────────────────┐  
│ AccuKnox/KubeArmor Engine     │  
└───────────────────────────────┘

## **2\. In-Depth Telemetry Transformation Logic**

The processing pipeline normalizes incoming eBPF JSON lines into predictable token identifiers. Below is the technical data progression model showing how a raw network connection trace mutates as it travels through the modifier abstraction matrix.

### **2.1 Inbound Raw eBPF Telemetry Frame (JSONL)**

JSON  
{  
  "time": "2026-07-12T09:44:10.005Z",  
  "duration\_ms": 1.84,  
  "process\_exec": {  
    "process": {  
      "pid": 14205,  
      "binary": "/usr/bin/node"  
    }  
  },  
  "process\_kprobe": {  
    "function\_name": "sys\_connect",  
    "return\_value": 0,  
    "args": \[  
      {  
        "sock\_arg": {  
          "dport": 6379,  
          "daddr": "10.244.2.14"  
        }  
      }  
    \]  
  }  
}

### **2.2 The Evaluation Matrix Transformation Pipeline**

The extraction controller loops through the registered Mask Profile, evaluating paths and outputting stable structural representations:

YAML  
\# Processing Flow Trace  
\- Extraction:  "$.process\_exec.process.binary"         \-\> Value: "/usr/bin/node"  
  Modifier:    DEFAULT                                 \-\> Token: "/usr/bin/node"

\- Extraction:  "$.process\_kprobe.function\_name"        \-\> Value: "sys\_connect"  
  Modifier:    DEFAULT                                 \-\> Token: "sys\_connect"

\- Extraction:  "$.process\_exec.process.pid"            \-\> Value: 14205  
  Modifier:    IS\_PRESENT                              \-\> Token: "TRUE"

\- Extraction:  "$.process\_kprobe.args\[0\].sock\_arg.dport" \-\> Value: 6379  
  Modifier:    "ANY(80, 443, 6379, 27017)"             \-\> Token: "TRUE"

\- Extraction:  "$.process\_kprobe.return\_value"         \-\> Value: 0  
  Modifier:    "IN\_RANGE(-999, 0)"                     \-\> Token: "TRUE"

### **2.3 Alphabetical Token Serialization & Hashing**

To prevent serialization drift, the tokens are sorted by key name, joined into a delimited character byte stream, and folded into an MD5 hash:

Plaintext  
\# Step 1: Alphabetic Key Assembly  
"application\_binary:/usr/bin/node|hook\_syscall:sys\_connect|isolation\_pid:TRUE|kernel\_return\_state:TRUE|network\_dest\_port:TRUE"

\# Step 2: Cryptographic Fold Execution  
hashlib.md5(byte\_stream).hexdigest() \-\> "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e"

\# Step 3: Identifier Allocation  
Fingerprint\_ID \-\> "fp\_track\_redis\_egress"

## **3\. Mathematical Behavioral Scoring Model**

Instead of evaluating system behavior via exact multi-line string lookups, Fingerling calculates structural alignment using the **Jaccard Similarity Index** over the extracted $N$-gram transition sets.  
Let $O$ be the set of unique contiguous sequence tuples captured within the rolling memory ring buffer during live target testing, and let $B$ be the set of whitelisted sequence tuples registered within the historical baseline profile for that workload:

$$J(O, B) \= \\frac{\\vert{}O \\cap B\\vert{}}{\\vert{}O \\cup B\\vert{}}$$  
The **Structural Anomaly Metric ($A$)** is derived as the complement of the Jaccard Similarity Index:

$$A \= 1.0 \- J(O, B)$$

### **Enforcement Gate Evaluation Policy**

* If $A \\le 0.05$: The execution sequence displays minor variations (e.g., normal environmental timing adjustments). The validation engine **approves deployment** and updates production performance thresholds.  
* If $A \> 0.05$: The execution trajectory signals a significant departure from expected code paths. The validation engine flags a **Fuzzy Structural Disconnect**, blocks the GitOps rollout, and isolates the anomalous sequence for inspection.

# **Document 4: Proof of Concept (POC) Development User Stories**

Markdown  
\# Project Fingerling: Agile Scrum User Stories (POC Sprint Phase)  
**\*\*Target Velocity Allocation:\*\*** 18 Story Points  

\---

\#\# User Story 1: eBPF Telemetry Parser & Plug-and-Play Modifier Engine  
**\*\*ID:\*\*** STORY-FING-01    
**\*\*Points:\*\*** 5 Story Points    
**\*\*Epic:\*\*** Behavioral Tokenization Infrastructure  

\#\#\# User Story Description  
As a DevSecOps Engineer,    
I want to parse streaming JSONL eBPF log logs through JSONPath targets and custom modifier expressions,    
So that I can collapse high-cardinality fields like PIDs and timestamps down to predictable, low-cardinality tokens before hashing.

\#\#\# Business Value  
Eliminates the data explosion paradox inherent in system call auditing, reducing multi-line, volatile system telemetry frames into reproducible structural inputs.

\#\#\# Technical Acceptance Criteria  
1\. Must accept a valid JSONL input string mimicking standard eBPF engine outputs.  
2\. Must evaluate extraction configurations using standard dot-notation JSONPath schemas (\`$.process\_exec.process.binary\`).  
3\. Must implement an extensible modifier map supporting \`DEFAULT\`, \`IS\_PRESENT\`, \`IS\_NULL\`, \`IN\_RANGE(low, high)\`, and \`ANY(v1, v2, ...)\`.  
4\. If a targeted JSONPath property is absent or null within the log frame, the engine must handle it gracefully, outputting a stable \`"FALSE"\` or \`"NULL"\` string token instead of raising an execution exception.

\#\#\# Verification Tasks  
\* Verify that an execution tracking log containing \`pid: 14205\` combined with an \`IS\_PRESENT\` modifier transforms into the static string token \`"TRUE"\`.  
\* Verify that a kernel error output of \`-110\` evaluated against \`IN\_RANGE(-999, 0)\` transforms successfully into \`"TRUE"\`.

\---

\#\# User Story 2: Stateful Append-Only Upsert Data Warehouse Compiler  
**\*\*ID:\*\*** STORY-FING-02    
**\*\*Points:\*\*** 5 Story Points    
**\*\*Epic:\*\*** Behavioral Tokenization Infrastructure  

\#\#\# User Story Description  
As a Platform Security Architect,    
I want the fingerprint engine to perform an alphabetical sort serialization and a stateful upsert loop across compiled tokens,    
So that I can continuously update historical execution thresholds using multi-day production traces without causing metadata index bloat.

\#\#\# Business Value  
Enables long-tail, low-frequency business operations to be absorbed seamlessly into the historical whitelist over extended observation windows without needing to store gigabytes of raw, plain-text system traces.

\#\#\# Technical Acceptance Criteria  
1\. Must sort incoming key-value evaluation arrays alphabetically by key name before flattening to prevent serialization drift.  
2\. Must run an MD5 cryptographic fold across the flattened string to generate an immutable 32-character hexadecimal key descriptor.  
3\. Must implement the State Reconciliation Workflow:  
   \* **\*\*On Match State:\*\*** Increment \`total\_occurrences\`, update \`last\_seen\_timestamp\`, and dynamically update the moving bounds for \`min\_duration\_ms\` and \`max\_duration\_ms\`. Do not add a new record block.  
   \* **\*\*On Drift State:\*\*** Append a brand new record block to the \`fingerprints.yaml\` dictionary and store the original source log row inside a fixed-capacity reference array.

\#\#\# Verification Tasks  
\* Pass identical telemetry objects through the parser sequentially and verify that \`total\_occurrences\` increments reliably while the overall entry list count stays flat.  
\* Verify that the reference array caps its log row storage at a fixed allocation limit (e.g., maximum array depth of 3 samples), dropping or rotating older rows to prevent inventory bloat.

\---

\#\# User Story 3: Stateful Sliding Window Memory Ring Buffer Matcher  
**\*\*ID:\*\*** STORY-FING-03    
**\*\*Points:\*\*** 5 Story Points    
**\*\*Epic:\*\*** Sequence Trajectory Enforcement  

\#\#\# User Story Description  
As a Core Security Engineer,    
I want to feed streaming Fingerprint IDs into a stateful FIFO memory ring buffer of size $N$,    
So that the system can continuously construct and validate sequence trajectories independently of individual process block boundaries.

\#\#\# Business Value  
Bypasses the blind spots of isolated snapshot auditing by tracking execution trajectories over time. This makes it impossible for an attacker to hide malicious logic inside an array of individually benign system calls.

\#\#\# Technical Acceptance Criteria  
1\. Must leverage an internal, stateful first-in-first-out (\`FIFO\`) queue configuration to model the sliding memory ring buffer window.  
2\. The ring buffer must accept a continuous stream of string inputs representing sequential Fingerprint IDs.  
3\. The queue must wait until it is completely filled to its configured window depth $N$ before outputting tracking evaluations.  
4\. At each step of the stream, the engine must extract a contiguous tuple path ($N$-gram) and compare it against a pre-compiled whitelist set. If present, it returns an anomaly metric of \`0.0\`; if unrecognized, it flags a score of \`1.0\`.

\#\#\# Verification Tasks  
\* Initialize a ring buffer with $N=3$ and verify that the first 2 pushed tokens return a score of \`0.0\` (the warm-up phase).  
\* Push a sequence of tokens that departs from the whitelisted trajectory layout and verify that the engine immediately signals a \`1.0\` anomaly output.

\---

\#\# User Story 4: Automated Label-Bound KubeArmor Policy Compiler  
**\*\*ID:\*\*** STORY-FING-04    
**\*\*Points:\*\*** 3 Story Points    
**\*\*Epic:\*\*** Automated GitOps Delivery  

\#\#\# User Story Description  
As a DevSecOps Automation Specialist,    
I want the compiler to translate validated sequence anomalies into a declarative KubeArmorPolicy manifest bound to Kubernetes workload label selectors,    
So that my defensive layers automatically follow the targeted microservice across auto-scaling adjustments and node evictions.

\#\#\# Business Value  
Decouples runtime security protection from fragile infrastructure primitives (like static host node names or pinned IP routes), implementing a mobile, resilient defense mesh that scales dynamically alongside the application.

\#\#\# Technical Acceptance Criteria  
1\. Must ingest an isolated anomalous trajectory string and generate a syntactically correct \`KubeArmorPolicy\` Kubernetes Custom Resource Definition.  
2\. Must inject the target container application’s logical identity tags directly into the policy specification using \`matchLabels\` blocks.  
3\. The generated manifest must default its execution mode block parameter to active \`Block\` or \`Post\` routing flags based on the target specification.

\#\#\# Verification Tasks  
\* Parse a raw anomaly result and verify that the generated YAML output matches standard KubeArmor schema validations without formatting errors.  
\* Verify that the compiled policy correctly maps the \`matchLabels\` block to the target workload identifier (\`app: checkout-backend\`).

All core specifications—including ingestion requirements, JSONPath modifier structures, continuous learning loops, the stateful sliding-window ring buffer, and the complete agile user story catalog—are now fully integrated and ready to be imported directly into your team's project repository or document suite.