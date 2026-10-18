import os

def create_structure_here():
    # A single dot "." tells Python to create everything inside your current folder
    base_dir = "."

    directories = [
        "evaluation",
        "data",
        "documents/event_briefs",
        "documents/venue_rules",
        "documents/catering_policies",
        "documents/staffing_policies",
        "documents/budget_guidelines",
        "documents/change_notices",
        "answer_keys",
        "results/raw_outputs"
    ]

    files = [
        "evaluation/scoring_rubric_v1.md",
        "evaluation/retrieval_gold_labels.json",
        "data/events.csv",
        "data/budgets.csv",
        "data/staffing.csv",
        "data/catering.csv",
        "data/event_memory.db",
        "answer_keys/pilot_gold_answers.json",
        "results/scores.csv"
    ]

    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)

    for file in files:
        file_path = os.path.join(base_dir, file)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("{}" if file_path.endswith(".json") else "")

    print("Structure successfully added to your active workspace directory!")

if __name__ == "__main__":
    create_structure_here()
