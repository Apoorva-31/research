import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

def generate_research_results(csv_path="results/scores.csv"):
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: {csv_path} not found. Please execute your experiment harness first.")
        return
        
    df = pd.read_csv(path)
    
    # Ensure proper numeric typing
    numeric_cols = [
        'decision_accuracy_pct', 'hard_violations', 'applicable_constraints', 
        'contradictions', 'latency_seconds', 'cost_usd'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df['retrieval_recall_numeric'] = pd.to_numeric(df['retrieval_recall_at_5'], errors='coerce')
    df['retrieval_precision_numeric'] = pd.to_numeric(df['retrieval_precision_at_5'], errors='coerce')

    print("="*70)
    print(" EXPERIMENTAL RESULTS ANALYSIS FOR B.TECH THESIS / RESEARCH PAPER")
    print("="*70)
    
    # 1. Statistical Aggregates (Mean ± Std Dev across runs and scenarios)
    agg_df = df.groupby('configuration').agg(
        mean_accuracy=('decision_accuracy_pct', 'mean'),
        std_accuracy=('decision_accuracy_pct', 'std'),
        mean_violations=('hard_violations', 'mean'),
        std_violations=('hard_violations', 'std'),
        mean_contradictions=('contradictions', 'mean'),
        std_contradictions=('contradictions', 'std'),
        mean_latency=('latency_seconds', 'mean'),
        std_latency=('latency_seconds', 'std'),
        mean_cost=('cost_usd', 'mean'),
        mean_recall=('retrieval_recall_numeric', 'mean'),
        mean_precision=('retrieval_precision_numeric', 'mean')
    ).reset_index()
    
    print("\n--- TABLE 1: Quantitative Performance Comparison (Mean ± Std. Dev.) ---")
    formatted_table = pd.DataFrame({
        "Configuration": agg_df['configuration'],
        "Accuracy (%)": agg_df.apply(lambda r: f"{r['mean_accuracy']:.2f} ± {r['std_accuracy']:.2f}", axis=1),
        "Hard Violations": agg_df.apply(lambda r: f"{r['mean_violations']:.2f} ± {r['std_violations']:.2f}", axis=1),
        "Contradictions": agg_df.apply(lambda r: f"{r['mean_contradictions']:.2f} ± {r['std_contradictions']:.2f}", axis=1),
        "Latency (s)": agg_df.apply(lambda r: f"{r['mean_latency']:.2f} ± {r['std_latency']:.2f}", axis=1),
        "Cost ($USD)": agg_df['mean_cost'].apply(lambda x: f"${x:.4f}"),
        "Recall@5": agg_df['mean_recall'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A"),
        "Precision@5": agg_df['mean_precision'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A")
    })
    print(formatted_table.to_string(index=False))
    
    # Export table for LaTeX / Paper inclusion
    formatted_table.to_csv("results/paper_summary_table.csv", index=False)
    
    # 2. Pictorial Generation (High-DPI Figures for Paper)
    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    # Figure 1: Decision Accuracy & Constraint Violations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.barplot(data=agg_df, x='configuration', y='mean_accuracy', ax=ax1, palette='Blues_d', ci=None)
    ax1.set_title('Decision Accuracy by Architecture', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Mean Accuracy (%)', fontsize=11)
    ax1.set_xlabel('Configuration', fontsize=11)
    ax1.set_ylim(0, 105)
    
    sns.barplot(data=agg_df, x='configuration', y='mean_violations', ax=ax2, palette='Reds_d', ci=None)
    ax2.set_title('Hard Constraint Violations by Architecture', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Mean Violations per Scenario', fontsize=11)
    ax2.set_xlabel('Configuration', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(fig_dir / "fig1_accuracy_violations.png", dpi=300)
    plt.close()
    
    # Figure 2: Latency and Cost Trade-offs
    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.barplot(data=agg_df, x='configuration', y='mean_latency', ax=ax3, palette='Purples_d', ci=None)
    ax3.set_title('Execution Latency Trade-off', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Wall-Clock Latency (seconds)', fontsize=11)
    ax3.set_xlabel('Configuration', fontsize=11)
    
    sns.barplot(data=agg_df, x='configuration', y='mean_cost', ax=ax4, palette='Greens_d', ci=None)
    ax4.set_title('Compute & API Cost Trade-off', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Cost per Scenario ($USD)', fontsize=11)
    ax4.set_xlabel('Configuration', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(fig_dir / "fig2_latency_cost.png", dpi=300)
    plt.close()
    
    print(f"\n[Success] High-resolution charts saved to: {fig_dir}/")
    print("Exported summary table to: results/paper_summary_table.csv")
    print("="*70)

if __name__ == "__main__":
    generate_research_results()