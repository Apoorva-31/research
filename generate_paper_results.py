import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set strict publication styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

def generate_advanced_visuals(csv_path="results/scores.csv"):
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(path)
    
    # Numeric conversion
    numeric_cols = ['decision_accuracy_pct', 'hard_violations', 'latency_seconds', 'cost_usd']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print(" GENERATING HIGHLY PICTORIAL VISUALIZATIONS FOR RESEARCH PAPER")
    print("="*70)

    # -----------------------------------------------------------------
    # FIGURE 1: STATISTICAL DISTRIBUTION (Box + Stripplot Hybrid)
    # -----------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Accuracy Boxplot with raw data overlay
    sns.boxplot(data=df, x='configuration', y='decision_accuracy_pct', ax=ax1, palette='pastel', width=0.4, showfliers=False)
    sns.stripplot(data=df, x='configuration', y='decision_accuracy_pct', ax=ax1, color='0.3', size=4, jitter=0.15, alpha=0.7)
    ax1.set_title('Distribution of Decision Accuracy', fontweight='bold', pad=15)
    ax1.set_ylabel('Accuracy (%)')
    ax1.set_xlabel('Architecture Configuration')
    ax1.set_ylim(min(df['decision_accuracy_pct'].dropna().min() - 5, 0), 105)

    # Right: Hard Violations with actual data distribution density
    sns.violinplot(data=df, x='configuration', y='hard_violations', ax=ax2, palette='muted', inner='quartile', bw_method=0.4)
    ax2.set_title('Hard Constraint Violations Spread', fontweight='bold', pad=15)
    ax2.set_ylabel('Violations per Run')
    ax2.set_xlabel('Architecture Configuration')
    
    plt.tight_layout()
    plt.savefig(fig_dir / "fig1_advanced_distributions.png", dpi=300)
    plt.close()

    # -----------------------------------------------------------------
    # FIGURE 2: 4-DIMENSIONAL PARETO TRADE-OFF SCATTER PLOT
    # -----------------------------------------------------------------
    # Calculate means for the trade-off map
    agg = df.groupby('configuration').agg({
        'latency_seconds': 'mean',
        'cost_usd': 'mean',
        'decision_accuracy_pct': 'mean',
        'hard_violations': 'mean'
    }).reset_index()

    plt.figure(figsize=(10, 7))
    
    # 4D Encoding: X=Latency, Y=Cost, Size=Accuracy, Color=Violations
    scatter = plt.scatter(
        data=agg,
        x='latency_seconds',
        y='cost_usd',
        s=agg['decision_accuracy_pct'] * 5,  # Size scaled by accuracy
        c='hard_violations',                 # Color mapped to violations
        cmap='coolwarm',
        alpha=0.75,
        edgecolors='black',
        linewidth=1.5
    )
    
    # Annotate architecture names on the points
    for idx, row in agg.iterrows():
        plt.annotate(
            row['configuration'], 
            (row['latency_seconds'], row['cost_usd']),
            textcoords="offset points", 
            xytext=(0,10), 
            ha='center', 
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3)
        )

    plt.title('Multi-Objective Pareto Analysis\n(Optimal models sit toward Bottom-Left with larger bubbles)', pad=20, fontweight='bold')
    plt.xlabel('Execution Latency (Seconds) → Less is Better')
    plt.ylabel('Compute Cost ($USD) → Less is Better')
    
    # Colorbar for violations
    cbar = plt.colorbar(scatter)
    cbar.set_label('Mean Hard Violations (Red is worse)', rotation=270, labelpad=15)
    
    # Add grid layout
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(fig_dir / "fig2_4d_pareto_tradeoff.png", dpi=300)
    plt.close()

    print(f"[Success] Graphical visualizations generated and stored in: {fig_dir}/")
    print("="*70)

if __name__ == "__main__":
    generate_advanced_visuals()
