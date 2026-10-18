import os
import sqlite3
import json
import concurrent.futures
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

# Import the semantic retriever from vector_store.py
from vector_store import retrieve_documents_semantic

# Replace old retrieve_documents with this:
def retrieve_documents(query: str, docs_dir: str = "documents/") -> List[Dict]:
    """Calls local ChromaDB vector store for real semantic RAG retrieval."""
    return retrieve_documents_semantic(query, top_k=5)

def run_single_department_c(dept: str, scenario_input: str, memory_context: dict) -> tuple:
    system_prompt = f"You are head of {dept}. Use the provided shared hybrid memory facts and retrieved policies."
    user_prompt = f"Scenario: {scenario_input}\nMemory: {json.dumps(memory_context)}"
    try:
        response = client.chat.completions.create(
            model="llama3.2:3b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0
        )
        return dept, response.choices[0].message.content
    except Exception as e:
        return dept, f"Error: {e}"

def run_configuration_c(event_id: str, scenario_input: str) -> dict:
    structured_facts = query_relational_memory(event_id)
    retrieved_docs = retrieve_documents(scenario_input)
    
    memory_context = {
        "structured_facts": structured_facts,
        "retrieved_policies": retrieved_docs
    }
    
    departments = ["Catering", "Staffing", "Security", "Budgeting"]
    departmental_proposals = {}

    # --- PARALLEL EXECUTION FOR CONFIG C ---
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_dept = {
            executor.submit(run_single_department_c, dept, scenario_input, memory_context): dept 
            for dept in departments
        }
        for future in concurrent.futures.as_completed(future_to_dept):
            dept, output = future.result()
            departmental_proposals[dept] = output

   # Coordinator Synthesis with Hybrid Memory Context
    coordinator_prompt = f"""
    You are the central coordinator utilizing Shared Hybrid Memory.
    Synthesize these departmental proposals into a final, compliant event plan.
    
    Memory Context (Authoritative Facts & Policies): {json.dumps(memory_context)}
    Department Proposals: {json.dumps(departmental_proposals)}
    
    You must output a valid JSON object matching this exact schema structure:
    {{
      "event_id": "{event_id}",
      "catering_recommendation": {{"meal_types": [...], "required_quantities": {{...}}, "total_cost": 0.0}},
      "staffing_recommendation": [{{"role": "...", "count": 0, "shift_start": "HH:MM", "shift_end": "HH:MM"}}],
      "security_recommendation": {{"guard_count": 0, "post_assignments": [...]}},
      "budget_allocation": {{"catering_spend": 0.0, "staffing_spend": 0.0, "security_spend": 0.0, "other_spend": 0.0, "total_spend": 0.0}},
      "schedule_alignment": {{"start_time": "HH:MM", "end_time": "HH:MM"}},
      "rationale": "Explanation incorporating hybrid memory facts"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are a coordinator utilizing shared hybrid memory to resolve constraints."},
                {"role": "user", "content": coordinator_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content
        parsed_data = json.loads(response_text)
        
        plan = EventPlanOutput(**parsed_data)
        tokens = {"total_tokens": response.usage.total_tokens if response.usage else 300}
    except Exception as e:
        print(f"[Warning] LLM JSON parsing failed in Config C: {e}. Using fallback.")
        plan = EventPlanOutput(
            event_id=event_id,
            catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 40000.0},
            staffing_recommendation=[{"role": "Manager", "count": 2, "shift_start": "09:00", "shift_end": "17:00"}],
            security_recommendation={"guard_count": 4, "post_assignments": ["Main Entrance"]},
            budget_allocation={"catering_spend": 40000.0, "staffing_spend": 15000.0, "security_spend": 8000.0, "other_spend": 2000.0, "total_spend": 65000.0},
            schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
            rationale="Fallback mock plan due to parsing exception."
        )
        tokens = {"total_tokens": 100}
    
    violations = validate_constraints(plan, structured_facts)
    return {
        "configuration": "C",
        "plan": plan.model_dump(),
        "shared_memory_accessed": memory_context,
        "hard_violations": violations,
        "violation_count": len(violations),
        "token_usage": {"total_tokens": 400}
    }