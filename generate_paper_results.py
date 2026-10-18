import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configure publication-grade styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10
})

def generate_comprehensive_comparisons(csv_path="results/scores.csv"):
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: {csv_path} not found. Please verify directory.")
        return
        
    df = pd.read_csv(path)
    
    # Enforce precise numeric data casting
    numeric_cols = ['decision_accuracy_pct', 'hard_violations', 'latency_seconds', 'cost_usd']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print(" PROCESSING ADVANCED PUBLICATION-GRADE ANALYSIS FOR CONFIGURATIONS A, B, C, D")
    print("="*80)

    target_configs = ['A', 'B', 'C', 'D']
    df_filtered = df[df['configuration'].isin(target_configs)].copy()

    # 1. Compute Quantitative Aggregates (Mean ± Std Dev) for Paper Table
    agg_table = df_filtered.groupby('configuration').agg(
        mean_acc=('decision_accuracy_pct', 'mean'),
        std_acc=('decision_accuracy_pct', 'std'),
        mean_vio=('hard_violations', 'mean'),
        std_vio=('hard_violations', 'std'),
        mean_lat=('latency_seconds', 'mean'),
        std_lat=('latency_seconds', 'std'),
        mean_cost=('cost_usd', 'mean')
    ).reset_index()

    print("\n--- GENERATED LATEX TABLE CODE (Ready for Overleaf) ---")
    print(r"\begin{table*}[t]")
    print(r"\centering")
    print(r"\caption{Quantitative Performance Summary Across Architectures (Mean $\pm$ Std. Dev.)}")
    print(r"\label{tab:performance_summary}")
    print(r"\begin{tabular}{|l|c|c|c|c|}")
    print(r"\hline")
    print(r"\textbf{Architecture} & \textbf{Decision Accuracy (\%)} & \textbf{Hard Violations} & \textbf{Latency (s)} & \textbf{Cost (\$USD)} \\ \hline")
    for _, r in agg_table.iterrows():
        print(f"Config {r['configuration']} & ${r['mean_acc']:.2f} \\pm {r['std_acc']:.2f}$ & ${r['mean_vio']:.2f} \\pm {r['std_vio']:.2f}$ & ${r['mean_lat']:.2f} \\pm {r['std_lat']:.2f}$ & \\${r['mean_cost']:.4f}$ \\\\ \\hline")
    print(r"\end{tabular}")
    print(r"\end{table*}")
    print("-" * 55)

    # 2. Compute Normalized Data for Radar Chart
    agg = df_filtered.groupby('configuration').agg({
        'decision_accuracy_pct': 'mean',
        'hard_violations': 'mean',
        'latency_seconds': 'mean',
        'cost_usd': 'mean'
    }).reset_index()

    norm_df = pd.DataFrame()
    norm_df['configuration'] = agg['configuration']
    
    a_min, a_max = agg['decision_accuracy_pct'].min(), agg['decision_accuracy_pct'].max()
    norm_df['Accuracy'] = (agg['decision_accuracy_pct'] - a_min) / (a_max - a_min) if a_max != a_min else 1.0
    
    v_min, v_max = agg['hard_violations'].min(), agg['hard_violations'].max()
    norm_df['Fewer Violations'] = 1 - ((agg['hard_violations'] - v_min) / (v_max - v_min)) if v_max != v_min else 1.0
    
    l_min, l_max = agg['latency_seconds'].min(), agg['latency_seconds'].max()
    norm_df['Lower Latency'] = 1 - ((agg['latency_seconds'] - l_min) / (l_max - l_min)) if l_max != l_min else 1.0
    
    c_min, c_max = agg['cost_usd'].min(), agg['cost_usd'].max()
    norm_df['Lower Cost'] = 1 - ((agg['cost_usd'] - c_min) / (c_max - c_min)) if c_max != c_min else 1.0

    # -----------------------------------------------------------------
    # VISUAL 1: MULTI-AXIS RADAR CHART
    # -----------------------------------------------------------------
    labels = ['Accuracy', 'Fewer Violations', 'Lower Latency', 'Lower Cost']
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] 

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = {'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c', 'D': '#d62728'}
    
    for _, row in norm_df.iterrows():
        config = row['configuration']
        values = [row['Accuracy'], row['Fewer Violations'], row['Lower Latency'], row['Lower Cost']]
        values += values[:1] 
        ax.plot(angles, values, color=colors[config], linewidth=2, label=f"Config {config}")
        ax.fill(angles, values, color=colors[config], alpha=0.15)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], labels, fontweight='bold')
    ax.set_rlim(0, 1.05)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0 (Best)"], color="grey", size=9)

    plt.title("Holistic Architecture Profile Comparison\n(Outer bounds represent optimal operational status)", pad=30, fontweight='bold', fontsize=14)
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    
    plt.tight_layout()
    plt.savefig(fig_dir / "fig1_radar_comprehensive.pdf", format='pdf', dpi=300)
    plt.savefig(fig_dir / "fig1_radar_comprehensive.png", dpi=300)
    plt.close()

    # -----------------------------------------------------------------
    # VISUAL 2: 2x2 FACETED DISCRETE BOX-PLOT MATRIX
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    metrics = [
        ('decision_accuracy_pct', 'Decision Accuracy (%)', 'Blues_r'),
        ('hard_violations', 'Hard Violations Count', 'Reds'),
        ('latency_seconds', 'Execution Latency (s)', 'Purples'),
        ('cost_usd', 'Compute Cost ($USD)', 'Greens')
    ]
    
    for i, (col, title, palette) in enumerate(metrics):
        sns.boxplot(data=df_filtered, x='configuration', y=col, ax=axes[i], order=target_configs, palette=palette, width=0.5, showfliers=False)
        sns.stripplot(data=df_filtered, x='configuration', y=col, ax=axes[i], order=target_configs, color='0.2', size=4, jitter=0.2, alpha=0.6)
        
        axes[i].set_title(title, fontweight='bold')
        axes[i].set_xlabel('Configuration Architecture')
        axes[i].set_ylabel('')
        axes[i].grid(True, linestyle=':', alpha=0.6)

    plt.suptitle("Complete Micro-Benchmark Statistical Profile (A vs B vs C vs D)", fontweight='bold', y=0.98, fontsize=15)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig2_faceted_matrix.pdf", format='pdf', dpi=300)
    plt.savefig(fig_dir / "fig2_faceted_matrix.png", dpi=300)
    plt.close()

    print(f"\n[Success] All-aspect structural charts and LaTeX code generated successfully!")
    print("="*80)

if __name__ == "__main__":
    generate_comprehensive_comparisons()