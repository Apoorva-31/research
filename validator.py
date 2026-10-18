from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ==========================================
# 1. Common JSON Output Schema (Pydantic)
# ==========================================

class CateringRecommendation(BaseModel, extra="allow"):
    meal_types: List[str] = Field(..., description="List of meal types (e.g., standard, vegetarian, vegan)")
    required_quantities: Dict[str, int] = Field(..., description="Quantity required per meal type")
    total_cost: float = Field(..., description="Total projected cost for catering")


class StaffingRole(BaseModel, extra="allow"):
    role: str = Field(..., description="Staff role (e.g., coordinator, usher, support)")
    count: int = Field(..., description="Number of staff assigned")
    shift_start: str = Field(..., description="Start time of shift")
    shift_end: str = Field(..., description="End time of shift")


class SecurityRecommendation(BaseModel, extra="allow"):
    guard_count: int = Field(..., description="Total number of security guards allocated")
    post_assignments: List[str] = Field(..., description="Key posts or zones covered")


class BudgetAllocation(BaseModel, extra="allow"):
    catering_spend: float = Field(..., description="Allocated budget for catering")
    staffing_spend: float = Field(..., description="Allocated budget for staffing")
    security_spend: float = Field(..., description="Allocated budget for security")
    other_spend: float = Field(0.0, description="Any miscellaneous or venue expenses")
    total_spend: float = Field(..., description="Total sum of all departmental spending")


class ScheduleAlignment(BaseModel, extra="allow"):
    start_time: str = Field(..., description="Official event start time")
    end_time: str = Field(..., description="Official event end time")


class EventPlanOutput(BaseModel, extra="allow"):
    event_id: str = Field(..., description="Unique identifier for the event")
    catering_recommendation: CateringRecommendation
    staffing_recommendation: List[StaffingRole]
    security_recommendation: SecurityRecommendation
    budget_allocation: BudgetAllocation
    schedule_alignment: ScheduleAlignment
    rationale: str = Field(..., description="Summary justification for the coordinated plan")


# ==========================================
# 2. Deterministic Constraint Validator
# ==========================================

def validate_constraints(plan: EventPlanOutput, scenario_data: dict) -> List[str]:
    """
    Evaluates the plan against hard operational constraints without 
    silently repairing mistakes. Returns a list of distinct violation descriptions.
    """
    violations = []
    
    # Extract hard limits from scenario / database gold data
    max_capacity = scenario_data.get("venue_capacity", float("inf"))
    planned_attendance = scenario_data.get("attendance", 0)
    budget_limit = scenario_data.get("budget_limit", float("inf"))
    min_guard_ratio = scenario_data.get("min_guard_ratio_per_attendees", 50) # e.g., 1 guard per 50 attendees
    
    # Constraint 1: Venue Capacity Check
    # Check if proposed attendance or venue limit is breached
    if planned_attendance > max_capacity:
        violations.append(f"Capacity Violation: Attendance ({planned_attendance}) exceeds maximum venue capacity ({max_capacity}).")
        
    # Constraint 2: Budget Ceiling Check
    total_spend = plan.budget_allocation.total_spend
    if total_spend > budget_limit:
        violations.append(f"Budget Violation: Total spend ({total_spend}) exceeds budget ceiling ({budget_limit}).")
        
    # Constraint 3: Mandatory Security Staffing Check
    import math
    required_guards = math.ceil(planned_attendance / min_guard_ratio)
    allocated_guards = plan.security_recommendation.guard_count
    if allocated_guards < required_guards:
        violations.append(f"Security Staffing Violation: Allocated guards ({allocated_guards}) is below the mandatory minimum ({required_guards}).")

    # Constraint 4: Emergency Exit Obstruction Check (if specified in layout/notes)
    if scenario_data.get("blocks_emergency_exit", False):
        violations.append("Safety Violation: Proposed stage or seating layout blocks a required emergency exit.")

    return violations