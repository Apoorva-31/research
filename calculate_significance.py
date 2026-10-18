import pandas as pd
from scipy import stats
from pathlib import Path

def compute_statistical_significance(csv_path="results/scores.csv"):
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: {csv_path} not found. Please run your experiments first.")
        return
        
    df = pd.read_csv(path)
    
    # Ensure proper numeric typing
    df['decision_accuracy_pct'] = pd.to_numeric(df['decision_accuracy_pct'], errors='coerce')
    df['latency_seconds'] = pd.to_numeric(df['latency_seconds'], errors='coerce')
    
    # Pivot data so each scenario_id has matching rows across configurations for paired testing
    # We average across run_id per scenario first to get a single mean per scenario per config
    scenario_cfg_mean = df.groupby(['scenario_id', 'configuration'])[['decision_accuracy_pct', 'latency_seconds']].mean().reset_index()
    
    pivot_acc = scenario_cfg_mean.pivot(index='scenario_id', columns='configuration', values='decision_accuracy_pct')
    pivot_lat = scenario_cfg_mean.pivot(index='scenario_id', columns='configuration', values='latency_seconds')
    
    print("="*70)
    print(" STATISTICAL SIGNIFICANCE REPORT (PAIRED T-TESTS)")
    print("="*70)
    
    comparisons = [('C', 'A'), ('C', 'B'), ('C', 'D')]
    
    print("\n--- 1. DECISION ACCURACY COMPARISONS ---")
    for base, ref in comparisons:
        if base in pivot_acc.columns and ref in pivot_acc.columns:
            # Drop rows with NaN in either column for a paired test
            paired = pivot_acc[[base, ref]].dropna()
            t_stat, p_val = stats.ttest_rel(paired[base], paired[ref])
            
            sig_label = "Statistically Significant (p < 0.05)" if p_val < 0.05 else "Not Significant"
            print(f"Config {base} vs Config {ref}:")
            print(f"  Mean {base}: {paired[base].mean():.2f}% | Mean {ref}: {paired[ref].mean():.2f}%")
            print(f"  t-statistic: {t_stat:.4f} | p-value: {p_val:.5e} -> {sig_label}\n")

    print("\n--- 2. LATENCY COMPARISONS ---")
    for base, ref in comparisons:
        if base in pivot_lat.columns and ref in pivot_lat.columns:
            paired = pivot_lat[[base, ref]].dropna()
            t_stat, p_val = stats.ttest_rel(paired[base], paired[ref])
            
            sig_label = "Statistically Significant (p < 0.05)" if p_val < 0.05 else "Not Significant"
            print(f"Config {base} vs Config {ref}:")
            print(f"  Mean {base}: {paired[base].mean():.2f}s | Mean {ref}: {paired[ref].mean():.2f}s")
            print(f"  t-statistic: {t_stat:.4f} | p-value: {p_val:.5e} -> {sig_label}\n")
            
    print("="*70)

if __name__ == "__main__":
    compute_statistical_significance()