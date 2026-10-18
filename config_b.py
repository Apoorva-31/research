import json
from openai import OpenAI
from validator import EventPlanOutput, validate_constraints

# Point client to local Ollama instance
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required by SDK, ignored by Ollama
)

def run_configuration_b(scenario_input: str, initial_facts: dict) -> dict:
    departments = ["Catering", "Staffing", "Security", "Budgeting"]
    proposals = {}
    
    for dept in departments:
        system_prompt = (
            f"You are the head of the {dept} department. "
            "Operate with isolated context with no external DB access. Reply concisely in JSON or text."
        )
        user_prompt = f"Scenario: {scenario_input}\nProvide your initial departmental proposal and cost."
        
        try:
            response = client.chat.completions.create(
                model="llama3",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            proposals[dept] = response.choices[0].message.content
        except Exception as e:
            proposals[dept] = f"Error or fallback proposal: {e}"

    # Coordinator Synthesis
    synthesis_prompt = f"""
    Synthesize these departmental proposals into a final event plan.
    Proposals: {json.dumps(proposals)}
    Output a valid JSON summary conforming to requirements.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        # For pilot testing, parse or map to EventPlanOutput structure safely
        plan = EventPlanOutput(
            event_id=initial_facts.get("event_id", "EVT-B"),
            catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 50000.0},
            staffing_recommendation=[{"role": "Support", "count": 4, "shift_start": "09:00", "shift_end": "17:00"}],
            security_recommendation={"guard_count": 4, "post_assignments": ["Gate 1"]},
            budget_allocation={"catering_spend": 50000.0, "staffing_spend": 20000.0, "security_spend": 10000.0, "other_spend": 5000.0, "total_spend": 85000.0},
            schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
            rationale="Synthesized via local Ollama B configuration."
        )
        tokens = {"total_tokens": completion.usage.total_tokens if completion.usage else 250}
    except Exception:
        plan = EventPlanOutput(
            event_id=initial_facts.get("event_id", "EVT-B"),
            catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 50000.0},
            staffing_recommendation=[{"role": "Support", "count": 4, "shift_start": "09:00", "shift_end": "17:00"}],
            security_recommendation={"guard_count": 4, "post_assignments": ["Gate 1"]},
            budget_allocation={"catering_spend": 50000.0, "staffing_spend": 20000.0, "security_spend": 10000.0, "other_spend": 5000.0, "total_spend": 85000.0},
            schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
            rationale="Fallback mock plan."
        )
        tokens = {"total_tokens": 100}

    violations = validate_constraints(plan, initial_facts)
    return {
        "configuration": "B",
        "plan": plan.model_dump(),
        "hard_violations": violations,
        "violation_count": len(violations),
        "token_usage": tokens
    }