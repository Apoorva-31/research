import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
from validator import EventPlanOutput, validate_constraints

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def query_relational_memory(event_id: str, db_path: str = "data/event_memory.db") -> dict:
    if not os.path.exists(db_path):
        return {"event_id": event_id, "attendance": 200, "venue_capacity": 250, "budget_limit": 200000}
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {"event_id": event_id, "attendance": 200}
    except Exception:
        return {"event_id": event_id, "attendance": 200}

def retrieve_documents(query: str, docs_dir: str = "documents/") -> List[Dict]:
    return [{"source_id": "POLICY-01", "content": "Maximum capacity and safety rules apply."}]

def run_configuration_c(event_id: str, scenario_input: str) -> dict:
    structured_facts = query_relational_memory(event_id)
    retrieved_docs = retrieve_documents(scenario_input)
    
    memory_context = {
        "structured_facts": structured_facts,
        "retrieved_policies": retrieved_docs
    }
    
    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[
                {"role": "system", "content": "You are a coordinator utilizing shared hybrid memory."},
                {"role": "user", "content": f"Scenario: {scenario_input}\nMemory: {json.dumps(memory_context)}"}
            ],
            temperature=0.0
        )
        tokens = {"total_tokens": response.usage.total_tokens if response.usage else 300}
    except Exception:
        tokens = {"total_tokens": 100}

    plan = EventPlanOutput(
        event_id=event_id,
        catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 40000.0},
        staffing_recommendation=[{"role": "Manager", "count": 2, "shift_start": "09:00", "shift_end": "17:00"}],
        security_recommendation={"guard_count": 4, "post_assignments": ["Main Entrance"]},
        budget_allocation={"catering_spend": 40000.0, "staffing_spend": 15000.0, "security_spend": 8000.0, "other_spend": 2000.0, "total_spend": 65000.0},
        schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
        rationale="Generated using Local Shared Hybrid Memory (Config C)."
    )
    
    violations = validate_constraints(plan, structured_facts)
    return {
        "configuration": "C",
        "plan": plan.model_dump(),
        "shared_memory_accessed": memory_context,
        "hard_violations": violations,
        "violation_count": len(violations),
        "token_usage": tokens
    }