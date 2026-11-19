"""
End-to-End Orchestrator Pipeline for Grito Labs Marketing Analytics Framework
Ingests data into SQLite, executes SQL validation and analytics suite,
runs heuristic & Markov attribution models, evaluates budget scenarios,
and generates structured analytical outputs.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analysis.attribution import (
    prepare_pre_conversion_touchpoints,
    compute_attribution_weights,
    aggregate_channel_attribution
)
from analysis.markov_attribution import run_markov_attribution

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DB_PATH = os.path.join(DB_DIR, "marketing_analytics.db")

os.makedirs(DB_DIR, exist_ok=True)

def init_sqlite_db():
    """Load raw CSV files into SQLite database with indexes."""
    print("--> Initializing SQLite database at:", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read CSVs
    df_campaigns = pd.read_csv(os.path.join(DATA_RAW_DIR, "campaigns.csv"))
    df_spend = pd.read_csv(os.path.join(DATA_RAW_DIR, "spend.csv"))
    df_users = pd.read_csv(os.path.join(DATA_RAW_DIR, "users.csv"))
    df_touchpoints = pd.read_csv(os.path.join(DATA_RAW_DIR, "touchpoints.csv"))
    df_conversions = pd.read_csv(os.path.join(DATA_RAW_DIR, "conversions.csv"))
    
    # Write tables
    df_campaigns.to_sql("campaigns", conn, if_exists="replace", index=False)
    df_spend.to_sql("spend", conn, if_exists="replace", index=False)
    df_users.to_sql("users", conn, if_exists="replace", index=False)
    df_touchpoints.to_sql("touchpoints", conn, if_exists="replace", index=False)
    df_conversions.to_sql("conversions", conn, if_exists="replace", index=False)
    
    # Create indexes for fast joins
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tp_user ON touchpoints(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tp_camp ON touchpoints(campaign_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tp_time ON touchpoints(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversions(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_spend_camp ON spend(campaign_id);")
    conn.commit()
    conn.close()
    print("--> SQLite database successfully populated with tables and indexes.")

def run_sql_file(sql_filename: str):
    """Executes a standalone SQL file against SQLite and displays output."""
    file_path = os.path.join(SQL_DIR, sql_filename)
    if not os.path.exists(file_path):
        print(f"SQL file not found: {file_path}")
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
        
    conn = sqlite3.connect(DB_PATH)
    
    # If the file contains multiple semicolons (e.g. data quality tests), split and run
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
    last_df = None
    
    print(f"\n=======================================================")
    print(f"EXECUTING SQL FILE: {sql_filename}")
    print(f"=======================================================")
    
    for idx, stmt in enumerate(statements):
        # Ignore comments-only blocks
        clean_lines = [line for line in stmt.split("\n") if not line.strip().startswith("--") and not line.strip().startswith("/*")]
        clean_stmt = "\n".join(clean_lines).strip()
        if not clean_stmt:
            continue
            
        try:
            df = pd.read_sql_query(clean_stmt, conn)
            last_df = df
            if len(df) > 0:
                print(f"[Query {idx+1} Output]:")
                print(df.head(10).to_string(index=False))
        except Exception as e:
            print(f"Error executing statement in {sql_filename}: {e}")
            
    conn.close()
    return last_df

def run_analytics_and_export():
    """Runs Python attribution models, compiles comparison tables, and exports artifacts."""
    print("\n--> Running Attribution Modeling Suite...")
    df_tp = pd.read_csv(os.path.join(DATA_RAW_DIR, "touchpoints.csv"))
    df_conv = pd.read_csv(os.path.join(DATA_RAW_DIR, "conversions.csv"))
    df_spend = pd.read_csv(os.path.join(DATA_RAW_DIR, "spend.csv"))
    df_campaigns = pd.read_csv(os.path.join(DATA_RAW_DIR, "campaigns.csv"))
    
    total_conversions = len(df_conv)
    total_revenue = df_conv['revenue'].sum()
    total_spend = df_spend['spend'].sum()
    
    # 1. Heuristic Attribution Models
    df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
    df_weighted = compute_attribution_weights(df_valid)
    df_heuristic, checks = aggregate_channel_attribution(df_weighted, total_conversions, total_revenue)
    
    # 2. Markov Chain Removal Effect
    df_markov, matrix, baseline_p = run_markov_attribution(df_tp, df_conv)
    
    # 3. Merge all models into consolidated comparison
    df_all_models = pd.merge(df_heuristic, df_markov[['channel', 'removal_effect', 'markov_weight', 'markov_conversions', 'markov_revenue']], on='channel')
    
    # Add Channel Spend & Impressions/Clicks
    camp_channel = df_campaigns.set_index('campaign_id')['channel'].to_dict()
    df_spend_ch = df_spend.copy()
    df_spend_ch['channel'] = df_spend_ch['campaign_id'].map(camp_channel)
    spend_by_ch = df_spend_ch.groupby('channel').agg(
        total_spend=('spend', 'sum'),
        total_impressions=('impressions', 'sum'),
        total_clicks=('clicks', 'sum')
    ).reset_index()
    
    df_all_models = pd.merge(df_all_models, spend_by_ch, on='channel', how='left').fillna(0)
    
    # Compute ROAS & CAC for each model
    model_prefixes = ['First-Touch', 'Last-Touch', 'Linear', 'Position-Based', 'Time-Decay', 'markov']
    for pfx in model_prefixes:
        conv_col = f'{pfx}_conversions'
        rev_col = f'{pfx}_revenue'
        df_all_models[f'{pfx}_roas'] = np.where(df_all_models['total_spend'] > 0, df_all_models[rev_col] / df_all_models['total_spend'], 999.0)
        df_all_models[f'{pfx}_cac'] = np.where(df_all_models[conv_col] > 0, df_all_models['total_spend'] / df_all_models[conv_col], 0.0)
        
    df_all_models.to_csv(os.path.join(DATA_DIR, "attribution_comparison.csv"), index=False)
    print("--> Exported data/attribution_comparison.csv")
    
    # 4. Campaign Efficiency Table
    # Campaign spend
    camp_spend = df_spend.groupby('campaign_id').agg(
        total_spend=('spend', 'sum'),
        total_impressions=('impressions', 'sum'),
        total_clicks=('clicks', 'sum')
    ).reset_index()
    camp_summary = pd.merge(df_campaigns, camp_spend, on='campaign_id', how='left').fillna(0)
    camp_summary['ctr_pct'] = np.where(camp_summary['total_impressions'] > 0, (camp_summary['total_clicks'] / camp_summary['total_impressions']) * 100, 0.0)
    camp_summary['cpc'] = np.where(camp_summary['total_clicks'] > 0, camp_summary['total_spend'] / camp_summary['total_clicks'], 0.0)
    
    # Attribute conversions to campaign (Linear & Last-Touch)
    df_weighted['linear_rev_contrib'] = df_weighted['weight_linear'] * df_weighted['revenue']
    df_weighted['last_touch_rev_contrib'] = df_weighted['weight_last_touch'] * df_weighted['revenue']
    camp_linear = df_weighted.groupby('campaign_id').agg(
        linear_conversions=('weight_linear', 'sum'),
        linear_revenue=('linear_rev_contrib', 'sum'),
        last_touch_conversions=('weight_last_touch', 'sum'),
        last_touch_revenue=('last_touch_rev_contrib', 'sum')
    ).reset_index()
    
    camp_summary = pd.merge(camp_summary, camp_linear, on='campaign_id', how='left').fillna(0)
    camp_summary['roas'] = np.where(camp_summary['total_spend'] > 0, camp_summary['linear_revenue'] / camp_summary['total_spend'], 999.0)
    camp_summary['cac'] = np.where(camp_summary['linear_conversions'] > 0, camp_summary['total_spend'] / camp_summary['linear_conversions'], 0.0)
    
    # Tier assignment
    def assign_tier(row):
        if row['total_spend'] == 0:
            return 'Tier 1 - Organic Star (Zero Ad Spend)'
        elif row['roas'] >= 3.0 and row['cac'] <= 250:
            return 'Tier 1 - High Performer (Scale Up)'
        elif row['roas'] >= 1.5:
            return 'Tier 2 - Moderate (Maintain / Optimize)'
        else:
            return 'Tier 3 - Underperformer (Reduce / Reallocate)'
            
    camp_summary['performance_tier'] = camp_summary.apply(assign_tier, axis=1)
    camp_summary = camp_summary.sort_values('roas', ascending=False)
    camp_summary.to_csv(os.path.join(DATA_DIR, "campaign_rankings.csv"), index=False)
    print("--> Exported data/campaign_rankings.csv")
    
    # 5. Budget Reallocation Scenarios
    # Baseline by channel
    scenarios = []
    # Display: -30%, Paid Social: -15%, Email: +40%, Referral: +25%, Paid Search: +10%
    realloc_rules = {
        'Display': -0.30,
        'Paid Social': -0.15,
        'Email': +0.40,
        'Referral': +0.25,
        'Paid Search': +0.10,
        'Organic Social': 0.0
    }
    
    for idx, row in df_all_models.iterrows():
        ch = row['channel']
        curr_spend = row['total_spend']
        curr_rev = row['Linear_revenue']
        base_roas = curr_rev / curr_spend if curr_spend > 0 else 0.0
        shift_pct = realloc_rules.get(ch, 0.0)
        new_spend = curr_spend * (1 + shift_pct)
        spend_delta = curr_spend * shift_pct
        
        # Conservative: 85% efficiency on positive shift
        if shift_pct > 0:
            cons_rev = curr_rev + (spend_delta * base_roas * 0.85)
            opt_rev = curr_rev + (spend_delta * base_roas * 1.00)
        else:
            cons_rev = curr_rev + (spend_delta * base_roas * 1.00)
            opt_rev = curr_rev + (spend_delta * base_roas * 0.90) # Only 90% lost if trimmed efficiently
            
        scenarios.append({
            'channel': ch,
            'current_spend': curr_spend,
            'new_spend': new_spend,
            'spend_delta': spend_delta,
            'baseline_roas': base_roas,
            'current_revenue': curr_rev,
            'projected_revenue_conservative': cons_rev,
            'projected_revenue_optimistic': opt_rev,
            'conservative_lift': cons_rev - curr_rev,
            'optimistic_lift': opt_rev - curr_rev
        })
        
    df_scenarios = pd.DataFrame(scenarios)
    df_scenarios.to_csv(os.path.join(DATA_DIR, "budget_scenarios.csv"), index=False)
    print("--> Exported data/budget_scenarios.csv")
    
    # 6. High-level Summary Metrics JSON
    summary_metrics = {
        "client": "Grito Labs",
        "domain": "EdTech Analytics",
        "timeframe": "2026-01-01 to 2026-09-30",
        "total_spend": float(total_spend),
        "total_revenue": float(total_revenue),
        "total_conversions": int(total_conversions),
        "unique_users": int(len(df_tp['user_id'].unique())),
        "total_touchpoints": int(len(df_tp)),
        "blended_roas": round(float(total_revenue / total_spend), 2),
        "blended_cac": round(float(total_spend / total_conversions), 2),
        "average_order_value": round(float(total_revenue / total_conversions), 2),
        "projected_clv": round(float((total_revenue / total_conversions) * 1.25 * 0.75), 2),
        "top_channels_by_roas": [
            {"channel": "Email", "roas": round(float(df_all_models.loc[df_all_models['channel']=='Email', 'Linear_roas'].values[0]), 2)},
            {"channel": "Referral", "roas": round(float(df_all_models.loc[df_all_models['channel']=='Referral', 'Linear_roas'].values[0]), 2)},
            {"channel": "Paid Search", "roas": round(float(df_all_models.loc[df_all_models['channel']=='Paid Search', 'Linear_roas'].values[0]), 2)}
        ],
        "markov_baseline_conversion_rate": round(float(baseline_p * 100), 2),
        "budget_scenario_results": {
            "current_spend": float(df_scenarios['current_spend'].sum()),
            "new_spend": float(df_scenarios['new_spend'].sum()),
            "current_revenue": float(df_scenarios['current_revenue'].sum()),
            "conservative_projected_revenue": float(df_scenarios['projected_revenue_conservative'].sum()),
            "conservative_revenue_lift": float(df_scenarios['conservative_lift'].sum()),
            "conservative_projected_roas": round(float(df_scenarios['projected_revenue_conservative'].sum() / df_scenarios['new_spend'].sum()), 2),
            "optimistic_projected_revenue": float(df_scenarios['projected_revenue_optimistic'].sum()),
            "optimistic_revenue_lift": float(df_scenarios['optimistic_lift'].sum()),
            "optimistic_projected_roas": round(float(df_scenarios['projected_revenue_optimistic'].sum() / df_scenarios['new_spend'].sum()), 2)
        }
    }
    
    with open(os.path.join(DATA_DIR, "summary_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(summary_metrics, f, indent=2)
    print("--> Exported data/summary_metrics.json")
    print("\n=== PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY ===")

def main():
    print("==============================================================")
    print("GRITO LABS MARKETING ANALYTICS & ATTRIBUTION PIPELINE")
    print("==============================================================")
    
    # 1. Ingest SQLite DB
    init_sqlite_db()
    
    # 2. Run All SQL Files
    sql_files = [
        "01_data_quality.sql",
        "02_channel_performance.sql",
        "03_kpis.sql",
        "04_journey_paths.sql",
        "05_attribution_models.sql",
        "06_campaign_efficiency.sql",
        "07_budget_scenarios.sql"
    ]
    for sf in sql_files:
        run_sql_file(sf)
        
    # 3. Run Attribution Modeling and Export Analytical Datasets
    run_analytics_and_export()

if __name__ == "__main__":
    main()
