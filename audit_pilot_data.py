import json
import os
from pathlib import Path

def run_audit():
    print("Starting Pilot Data Cross-Validation Audit...\n")
    errors = []
    warnings = []

    # 1. Load core JSON files
    try:
        with open("scenarios.json", "r", encoding="utf-8") as f:
            scenarios_data = json.load(f)
    except Exception as e:
        errors.append(f"Could not load scenarios.json: {e}")
        scenarios_data = {}

    try:
        with open("answer_keys/pilot_gold_answers.json", "r", encoding="utf-8") as f:
            gold_answers = json.load(f)
    except Exception as e:
        errors.append(f"Could not load answer_keys/pilot_gold_answers.json: {e}")
        gold_answers = {}

    try:
        with open("evaluation/retrieval_gold_labels.json", "r", encoding="utf-8") as f:
            retrieval_labels = json.load(f)
    except Exception as e:
        errors.append(f"Could not load evaluation/retrieval_gold_labels.json: {e}")
        retrieval_labels = {}

    # Extract scenario IDs from scenarios.json
    scenario_list = scenarios_data.get("scenarios", [])
    scenario_ids = {s.get("scenario_id") for s in scenario_list if "scenario_id" in s}
    
    print(f"Found {len(scenario_ids)} scenarios in scenarios.json.")

    # Extract gold answer IDs
    gold_list = gold_answers.get("answers", [])
    gold_ids = {g.get("scenario_id") for g in gold_list if "scenario_id" in g}
    print(f"Found {len(gold_ids)} records in pilot_gold_answers.json.")

    # 2. Check Scenario ID parity
    missing_in_gold = scenario_ids - gold_ids
    extra_in_gold = gold_ids - scenario_ids
    if missing_in_gold:
        errors.append(f"Scenarios present in scenarios.json but missing gold answers: {missing_in_gold}")
    if extra_in_gold:
        errors.append(f"Gold answers present for non-existent scenarios: {extra_in_gold}")

    # 3. Check Document & Evidence ID references
    # Scan document directories for existing document IDs
    doc_root = Path("documents")
    existing_doc_ids = set()
    if doc_root.exists():
        for doc_path in doc_root.rglob("*.md"):
            # You can parse file headers or filenames as doc IDs
            existing_doc_ids.add(doc_path.stem)
        for doc_path in doc_root.rglob("*.txt"):
            existing_doc_ids.add(doc_path.stem)
    else:
        warnings.append("Directory 'documents/' not found or empty.")

    print(f"Found {len(existing_doc_ids)} document files in documents/.")

    # Validate evidence keys in gold answers & retrieval labels
    for item in gold_list:
        s_id = item.get("scenario_id")
        evidence_ids = item.get("evidence_ids", [])
        for ev_id in evidence_ids:
            # Check if evidence matches document collection or known format
            if existing_doc_ids and not any(ev_id.startswith(d_id) for d_id in existing_doc_ids):
                warnings.append(f"Scenario {s_id} references evidence ID '{ev_id}' which may not match local document filenames.")

    # 4. Summary Report
    print("\n--- AUDIT RESULTS ---")
    if errors:
        print(f"[FAIL] Audit completed with {len(errors)} critical error(s):")
        for err in errors:
            print(f"  - {err}")
    else:
        print("[PASS] No structural or ID parity errors detected between scenarios and gold answers!")

    if warnings:
        print(f"\n[WARN] {len(warnings)} warning(s) to review:")
        for warn in warnings:
            print(f"  - {warn}")
    else:
        print("[PASS] All document reference checks passed cleanly.")

if __name__ == "__main__":
    run_audit()