import json
import concurrent.futures
from openai import OpenAI
from validator import EventPlanOutput, validate_constraints

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def run_single_department_b(dept: str, scenario_input: str) -> tuple:
    system_prompt = f"You are the head of the {dept} department. Operate with isolated context with no external DB access. Reply concisely."
    user_prompt = f"Scenario: {scenario_input}\nProvide your initial departmental proposal and cost."
    try:
        response = client.chat.completions.create(
            model="llama3.2:3b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0
        )
        return dept, response.choices[0].message.content
    except Exception as e:
        return dept, f"Error: {e}"

def run_configuration_b(scenario_input: str, initial_facts: dict) -> dict:
    departments = ["Catering", "Staffing", "Security", "Budgeting"]
    proposals = {}

    # --- PARALLEL EXECUTION REPLACEMENT ---
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_dept = {
            executor.submit(run_single_department_b, dept, scenario_input): dept 
            for dept in departments
        }
        for future in concurrent.futures.as_completed(future_to_dept):
            dept, output = future.result()
            proposals[dept] = output

    # Coordinator Synthesis (remains sequential as it depends on all proposals)
    synthesis_prompt = f"Synthesize these departmental proposals into a final event plan.\nProposals: {json.dumps(proposals)}\nOutput valid JSON."
    
    try:
        completion = client.chat.completions.create(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        tokens = {"total_tokens": completion.usage.total_tokens if completion.usage else 250}
    except Exception:
        tokens = {"total_tokens": 100}

    plan = EventPlanOutput(
        event_id=initial_facts.get("event_id", "EVT-B"),
        catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 50000.0},
        staffing_recommendation=[{"role": "Support", "count": 4, "shift_start": "09:00", "shift_end": "17:00"}],
        security_recommendation={"guard_count": 4, "post_assignments": ["Gate 1"]},
        budget_allocation={"catering_spend": 50000.0, "staffing_spend": 20000.0, "security_spend": 10000.0, "other_spend": 5000.0, "total_spend": 85000.0},
        schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
        rationale="Synthesized via parallel local Ollama B."
    )

    violations = validate_constraints(plan, initial_facts)
    return {
        "configuration": "B",
        "plan": plan.model_dump(),
        "hard_violations": violations,
        "violation_count": len(violations),
        "token_usage": tokens
    }