"""
Rule-Based Attribution Modeling Engine for Grito Labs
Implements First-Touch, Last-Touch, Linear, Position-Based (U-Shaped), and Time-Decay Attribution.
Strictly verifies conservation of total conversions and total revenue.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple

def prepare_pre_conversion_touchpoints(df_touchpoints: pd.DataFrame, df_conversions: pd.DataFrame) -> pd.DataFrame:
    """
    Joins touchpoints with conversions on user_id where touchpoint timestamp <= conversion timestamp.
    Orders touchpoints chronologically per conversion and computes path attributes.
    """
    # Ensure datetime format
    tp = df_touchpoints.copy()
    conv = df_conversions.copy()
    tp['timestamp'] = pd.to_datetime(tp['timestamp'])
    conv['timestamp'] = pd.to_datetime(conv['timestamp'])
    
    # Merge on user_id
    merged = pd.merge(
        conv[['conversion_id', 'user_id', 'timestamp', 'revenue']],
        tp[['touchpoint_id', 'user_id', 'timestamp', 'channel', 'campaign_id']],
        on='user_id',
        suffixes=('_conv', '_touch')
    )
    
    # Filter only pre-conversion touchpoints
    valid_touches = merged[merged['timestamp_touch'] <= merged['timestamp_conv']].copy()
    
    # Sort chronologically
    valid_touches = valid_touches.sort_values(['conversion_id', 'timestamp_touch', 'touchpoint_id'])
    
    # Compute rank and total touches per conversion
    valid_touches['touch_rank_asc'] = valid_touches.groupby('conversion_id').cumcount() + 1
    valid_touches['total_touches'] = valid_touches.groupby('conversion_id')['touchpoint_id'].transform('count')
    valid_touches['touch_rank_desc'] = valid_touches['total_touches'] - valid_touches['touch_rank_asc'] + 1
    
    # Calculate days elapsed before conversion
    time_diff = valid_touches['timestamp_conv'] - valid_touches['timestamp_touch']
    valid_touches['days_before_conversion'] = time_diff.dt.total_seconds() / 86400.0
    
    return valid_touches

def compute_attribution_weights(df_valid_touches: pd.DataFrame, half_life_days: float = 7.0) -> pd.DataFrame:
    """
    Computes exact fractional weights for all 5 rule-based attribution models.
    """
    df = df_valid_touches.copy()
    
    # 1. First-Touch Attribution
    df['weight_first_touch'] = np.where(df['touch_rank_asc'] == 1, 1.0, 0.0)
    
    # 2. Last-Touch Attribution
    df['weight_last_touch'] = np.where(df['touch_rank_desc'] == 1, 1.0, 0.0)
    
    # 3. Linear Attribution
    df['weight_linear'] = 1.0 / df['total_touches']
    
    # 4. Position-Based (U-Shaped: 40% First, 40% Last, 20% Middle)
    def calculate_position_weight(row):
        n = row['total_touches']
        if n == 1:
            return 1.0
        elif n == 2:
            return 0.5
        else:
            if row['touch_rank_asc'] == 1:
                return 0.40
            elif row['touch_rank_desc'] == 1:
                return 0.40
            else:
                return 0.20 / (n - 2)
                
    df['weight_position_based'] = df.apply(calculate_position_weight, axis=1)
    
    # 5. Time-Decay Attribution (Exponential half-life decay)
    raw_decay = np.power(2.0, - (df['days_before_conversion'] / half_life_days))
    df['raw_decay_weight'] = raw_decay
    sum_decay = df.groupby('conversion_id')['raw_decay_weight'].transform('sum')
    df['weight_time_decay'] = df['raw_decay_weight'] / sum_decay
    
    return df

def aggregate_channel_attribution(df_weighted: pd.DataFrame, total_conversions_expected: int, total_revenue_expected: float) -> Tuple[pd.DataFrame, Dict[str, bool]]:
    """
    Aggregates conversion counts and revenue by channel for each model.
    Verifies the Attribution Conservation Law.
    """
    models = {
        'First-Touch': 'weight_first_touch',
        'Last-Touch': 'weight_last_touch',
        'Linear': 'weight_linear',
        'Position-Based': 'weight_position_based',
        'Time-Decay': 'weight_time_decay',
    }
    
    channels = sorted(df_weighted['channel'].unique().tolist())
    records = []
    conservation_results = {}
    
    for ch in channels:
        ch_df = df_weighted[df_weighted['channel'] == ch]
        row = {'channel': ch}
        for model_name, weight_col in models.items():
            row[f'{model_name}_conversions'] = ch_df[weight_col].sum()
            row[f'{model_name}_revenue'] = (ch_df[weight_col] * ch_df['revenue']).sum()
        records.append(row)
        
    df_results = pd.DataFrame(records)
    
    # Verification checks
    for model_name, weight_col in models.items():
        total_conv = df_results[f'{model_name}_conversions'].sum()
        total_rev = df_results[f'{model_name}_revenue'].sum()
        
        conv_diff = abs(total_conv - total_conversions_expected)
        rev_diff = abs(total_rev - total_revenue_expected)
        
        is_conserved = (conv_diff < 1e-4) and (rev_diff < 1e-2)
        conservation_results[model_name] = {
            'is_conserved': is_conserved,
            'total_conversions': total_conv,
            'total_revenue': total_rev,
            'conv_diff': conv_diff,
            'rev_diff': rev_diff
        }
        
    return df_results, conservation_results

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tp_path = os.path.join(base_dir, "data", "raw", "touchpoints.csv")
    conv_path = os.path.join(base_dir, "data", "raw", "conversions.csv")
    
    if os.path.exists(tp_path) and os.path.exists(conv_path):
        df_tp = pd.read_csv(tp_path)
        df_conv = pd.read_csv(conv_path)
        
        print(f"Loaded {len(df_tp)} touchpoints and {len(df_conv)} conversions.")
        df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
        print(f"Matched {len(df_valid)} valid pre-conversion touchpoints.")
        
        df_weighted = compute_attribution_weights(df_valid)
        results, checks = aggregate_channel_attribution(df_weighted, len(df_conv), df_conv['revenue'].sum())
        
        print("\n--- Attribution Conservation Verification ---")
        for m, c in checks.items():
            status = "PASSED" if c['is_conserved'] else "FAILED"
            print(f"[{status}] {m}: Attributed Conversions = {c['total_conversions']:.2f} (diff: {c['conv_diff']:.6f}), Revenue = ${c['total_revenue']:,.2f}")
            
        print("\n--- Model Comparison Summary by Channel ---")
        print(results.to_string(index=False))
