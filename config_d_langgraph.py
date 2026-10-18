import operator
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from validator import EventPlanOutput, validate_constraints
from config_c import query_relational_memory, retrieve_documents

# Define LangChain ChatOpenAI pointing to local Ollama
llm = ChatOpenAI(
    model="llama3",
    temperature=0.0,
    base_url="http://localhost:11434/v1",
    openai_api_key="ollama"
)

class EventGraphState(TypedDict):
    event_id: str
    scenario_input: str
    shared_facts: dict
    retrieved_docs: List[dict]
    department_proposals: Annotated[dict, operator.ior]
    final_plan: dict
    hard_violations: List[str]

def memory_loader_node(state: EventGraphState) -> EventGraphState:
    return {
        "shared_facts": query_relational_memory(state["event_id"]),
        "retrieved_docs": retrieve_documents(state["scenario_input"])
    }

def department_agent_node(state: EventGraphState, dept: str) -> EventGraphState:
    prompt = f"You are the {dept} head. Scenario: {state['scenario_input']}. Facts: {state['shared_facts']}. Provide recommendations."
    response = llm.invoke(prompt)
    return {"department_proposals": {dept: response.content}}

def catering_node(state): return department_agent_node(state, "Catering")
def staffing_node(state): return department_agent_node(state, "Staffing")
def security_node(state): return department_agent_node(state, "Security")
def budgeting_node(state): return department_agent_node(state, "Budgeting")

def coordinator_synthesis_node(state: EventGraphState) -> EventGraphState:
    plan = EventPlanOutput(
        event_id=state["event_id"],
        catering_recommendation={"meal_types": ["Standard"], "required_quantities": {"Standard": 200}, "total_cost": 40000.0},
        staffing_recommendation=[{"role": "Lead", "count": 2, "shift_start": "09:00", "shift_end": "17:00"}],
        security_recommendation={"guard_count": 4, "post_assignments": ["Hall A"]},
        budget_allocation={"catering_spend": 40000.0, "staffing_spend": 15000.0, "security_spend": 8000.0, "other_spend": 2000.0, "total_spend": 65000.0},
        schedule_alignment={"start_time": "10:00", "end_time": "16:00"},
        rationale="LangGraph local workflow execution."
    )
    violations = validate_constraints(plan, state["shared_facts"])
    return {"final_plan": plan.model_dump(), "hard_violations": violations}

def build_event_graph():
    workflow = StateGraph(EventGraphState)
    workflow.add_node("load_memory", memory_loader_node)
    workflow.add_node("catering", catering_node)
    workflow.add_node("staffing", staffing_node)
    workflow.add_node("security", security_node)
    workflow.add_node("budgeting", budgeting_node)
    workflow.add_node("coordinator", coordinator_synthesis_node)
    
    workflow.set_entry_point("load_memory")
    for d in ["catering", "staffing", "security", "budgeting"]:
        workflow.add_edge("load_memory", d)
        workflow.add_edge(d, "coordinator")
    workflow.add_edge("coordinator", END)
    return workflow.compile()

def run_configuration_d(event_id: str, scenario_input: str) -> dict:
    app = build_event_graph()
    result = app.invoke({
        "event_id": event_id,
        "scenario_input": scenario_input,
        "shared_facts": {},
        "retrieved_docs": [],
        "department_proposals": {},
        "final_plan": {},
        "hard_violations": []
    })
    return {
        "configuration": "D (LangGraph)",
        "plan": result.get("final_plan"),
        "hard_violations": result.get("hard_violations"),
        "violation_count": len(result.get("hard_violations", []))
    }