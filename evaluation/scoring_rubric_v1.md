# Evaluation Scoring Rubric (v1.0)
**Project:** Shared Hybrid Memory for Multi-Agent Event Management  
**Status:** Frozen  
**Date:** October 17, 2026  

---

## 1. Overview & Evaluation Principles

This evaluation framework assesses the decision accuracy, constraint satisfaction, cross-agent consistency, retrieval performance, latency, and operational costs across three experimental configurations:
1. **Configuration A:** Single Agent Baseline (Centralized Planning)[cite: 1]
2. **Configuration B:** Multi-Agent, Isolated Memory Baseline (Message-based Coordination)[cite: 1]
3. **Configuration C:** Multi-Agent, Shared Hybrid Memory Treatment (Relational DB + RAG)[cite: 1]

### Core Evaluation Directives
* **Separate Retrieval from Generation:** Retrieval quality is evaluated independently from answer quality to isolate RAG failures from reasoning errors[cite: 1].
* **Safety Rules Over Average Scores:** Any proposed plan that violates a hard safety/compliance constraint is marked as **infeasible**, regardless of its composite score[cite: 1].
* **Determinism & Freeze Rule:** All evaluations must run against this frozen rubric. Rules must not be modified retroactively after inspecting performance outputs[cite: 1].

---

## 2. Core Metrics & Measurement Rules

| Metric | Measured Parameter | Evaluation Method / Scale |
| :--- | :--- | :--- |
| **Decision Accuracy** | Match rate against predefined answer key | 0–100% of required decision fields[cite: 1] |
| **Hard Constraint Violations** | Breaches of mandatory operational rules | Absolute count & percentage of applicable constraints violated[cite: 1] |
| **Cross-Agent Contradictions** | Recommendation mismatches across departments | Count of incompatible departmental recommendation pairs[cite: 1] |
| **Retrieval Quality** | Relevance and completeness of retrieved passages | Recall@5 and Precision@5 against ground truth labels[cite: 1] |
| **Latency** | End-to-end plan generation time | Wall-clock execution time in seconds[cite: 1] |
| **Cost** | Monetary computational overhead | Total API / token costs in USD per scenario[cite: 1] |

---

## 3. Detailed Scoring Rules

### Metric 1: Decision Accuracy ($A$)
* **Score:** Percentage of predefined fields correctly populated[cite: 1].
* **Rules:**
  * **1 Point:** Value matches the gold standard exactly or falls within the predefined acceptable numeric range[cite: 1].
  * **0 Points:** Incorrect value, missing field, unsupported recommendation, or value outside the acceptable range[cite: 1].
* **Formula:**
  $$\text{Decision Accuracy } (A) = \frac{\text{Correct Decision Fields}}{\text{Total Required Decision Fields}} \times 100$$
[cite: 1]

### Metric 2: Hard Constraint Violations ($V$)
* **Definition:** Mandatory operational constraints (e.g., maximum venue capacity, budget caps, safety exits, minimum guard ratios)[cite: 1].
* **Rules:**
  * Count each distinct violated rule **once** per scenario plan[cite: 1].
  * Do **not** double-count the same violation across multiple departmental outputs[cite: 1].
  * Any plan with $V > 0$ on critical safety/policy constraints is flagged as **INFEASIBLE**[cite: 1].
* **Constraint Compliance Component ($C$):**
  $$C = 100 \times \left(1 - \frac{V}{H}\right)$$
[cite: 1]
  *(Where $V$ = violated hard constraints, $H$ = total applicable hard constraints. If $H = 0$, $C = 100$ and is flagged N/A)[cite: 1].*

### Metric 3: Cross-Agent Contradictions ($D$)
* **Definition:** Conflicting final decisions between different functional departments (e.g., Security vs. Staffing)[cite: 1].
* **Rules:**
  * Evaluated across configurations B and C (Marked **N/A** for Single-Agent Configuration A)[cite: 1].
  * Count each distinct pair of incompatible recommendations once[cite: 1].
  * Compatible differences in wording, nuance, or detail do **not** count as contradictions[cite: 1].
* **Consistency Component ($K$):**
  $$K = 100 \times \left(1 - \frac{D}{P}\right)$$
[cite: 1]
  *(Where $D$ = contradictory recommendation pairs, $P$ = total comparable departmental decision pairs. If $P = 0$, $K = 100$ and is flagged N/A)[cite: 1].*

### Metric 4: Retrieval Quality (Recall@5 & Precision@5)
* **Rules:**
  * Evaluated **only** for configurations/runs utilizing active retrieval (Configuration C or retrieval-enabled modules)[cite: 1]. Marked **N/A** for retrieval-free runs[cite: 1].
  * Evaluated against `evaluation/retrieval_gold_labels.json`[cite: 1].
* **Formulas:**
  $$\text{Recall@5} = \frac{\text{Relevant Gold Chunks Retrieved in Top 5}}{\text{Total Relevant Gold Chunks in Corpus}}$$
[cite: 1]
  $$\text{Precision@5} = \frac{\text{Relevant Gold Chunks Retrieved in Top 5}}{5}$$
[cite: 1]

### Metric 5: Latency
* Measured as total elapsed wall-clock time (seconds) from initial prompt submission to final schema-validated output[cite: 1].
* Fixed timeout: **120 seconds**. A run exceeding timeout is recorded as a **Timeout Failure** (not 0 seconds)[cite: 1].

### Metric 6: Execution Cost
* Total cost in USD combining input tokens, output tokens, embedding generation, and vector retrieval calls[cite: 1].
* Evaluated based on actual provider API pricing tiers[cite: 1].

---

## 4. Secondary Composite Score ($S$)

To summarize overall efficiency while retaining raw performance visibility, calculate the composite score $S$:

$$S = 0.60 A + 0.25 C + 0.15 K$$
[cite: 1]

* **$A$** = Decision Accuracy (0–100)[cite: 1]
* **$C$** = Constraint Compliance Score (0–100)[cite: 1]
* **$K$** = Consistency Score (0–100)[cite: 1]

> **CRITICAL COMPLIANCE NOTICE:**  
> The composite score $S$ is a secondary metric for ranking valid plans[cite: 1]. A high composite score **never** overrides a safety failure[cite: 1]. If a plan has any hard safety constraint violation ($V > 0$), it is classified as **INFEASIBLE** regardless of $S$[cite: 1].

---

## 5. Primary Reporting Format

Results across experimental runs must be aggregated and presented in the following format:

1. **Mean Decision Accuracy (%)** across all test scenarios[cite: 1].
2. **Total Hard Constraint Violations** and **Infeasibility Rate (%)**[cite: 1].
3. **Mean Contradictions per Scenario** (Configurations B & C)[cite: 1].
4. **Mean Recall@5 and Precision@5** (Configuration C)[cite: 1].
5. **Median Latency (seconds)** and **Mean Cost per Scenario ($)**[cite: 1].