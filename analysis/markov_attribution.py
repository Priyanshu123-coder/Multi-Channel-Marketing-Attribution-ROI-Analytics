"""
Markov Chain Attribution Engine with Removal Effect for Grito Labs
Data-Driven Attribution using Absorbing Markov Chains.
Calculates transition matrices, absorption probabilities, removal effects, and normalized attribution.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

START_STATE = "(Start)"
CONV_STATE = "(Conversion)"
NULL_STATE = "(Null)"

def extract_customer_journeys(df_touchpoints: pd.DataFrame, df_conversions: pd.DataFrame) -> List[List[str]]:
    """
    Constructs ordered state paths for all users, including converting and non-converting paths.
    """
    tp = df_touchpoints.copy()
    conv = df_conversions.copy()
    
    tp['timestamp'] = pd.to_datetime(tp['timestamp'])
    conv['timestamp'] = pd.to_datetime(conv['timestamp'])
    
    # Identify converting users and their conversion time
    conv_users = conv.groupby('user_id')['timestamp'].min().to_dict()
    
    # Sort touchpoints
    tp = tp.sort_values(['user_id', 'timestamp'])
    
    journeys = []
    
    # Group by user
    for user_id, group in tp.groupby('user_id'):
        is_converted = user_id in conv_users
        if is_converted:
            conv_time = conv_users[user_id]
            # Keep only touches up to conversion
            valid_touches = group[group['timestamp'] <= conv_time]['channel'].tolist()
            if len(valid_touches) > 0:
                # Deduplicate consecutive identical touches to avoid self-loops (industry standard practice)
                deduped = [valid_touches[0]]
                for ch in valid_touches[1:]:
                    if ch != deduped[-1]:
                        deduped.append(ch)
                journeys.append([START_STATE] + deduped + [CONV_STATE])
        else:
            touches = group['channel'].tolist()
            if len(touches) > 0:
                deduped = [touches[0]]
                for ch in touches[1:]:
                    if ch != deduped[-1]:
                        deduped.append(ch)
                journeys.append([START_STATE] + deduped + [NULL_STATE])
                
    return journeys

def build_transition_matrix(journeys: List[List[str]]) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Builds the empirical transition probability matrix from observed state transitions.
    """
    # Count transitions
    transition_counts = {}
    
    all_channels = set()
    for path in journeys:
        for i in range(len(path) - 1):
            src, dst = path[i], path[i+1]
            if src not in [START_STATE, CONV_STATE, NULL_STATE]:
                all_channels.add(src)
            if dst not in [START_STATE, CONV_STATE, NULL_STATE]:
                all_channels.add(dst)
            transition_counts[(src, dst)] = transition_counts.get((src, dst), 0) + 1
            
    channels = sorted(list(all_channels))
    transient_states = [START_STATE] + channels
    absorbing_states = [CONV_STATE, NULL_STATE]
    all_states = transient_states + absorbing_states
    
    # Build transition probability matrix
    matrix = pd.DataFrame(0.0, index=all_states, columns=all_states)
    
    # Absorbing states transition to themselves with prob 1.0
    matrix.loc[CONV_STATE, CONV_STATE] = 1.0
    matrix.loc[NULL_STATE, NULL_STATE] = 1.0
    
    # Fill observed transitions for transient states
    for src in transient_states:
        row_counts = {dst: transition_counts.get((src, dst), 0) for dst in all_states}
        total = sum(row_counts.values())
        if total > 0:
            for dst, count in row_counts.items():
                matrix.loc[src, dst] = count / total
        else:
            # If no transitions out, absorbs to Null
            matrix.loc[src, NULL_STATE] = 1.0
            
    return matrix, transient_states, channels

def calculate_conversion_probability(matrix: pd.DataFrame, transient_states: List[str]) -> float:
    """
    Calculates absorbing probability from (Start) to (Conversion) using fundamental matrix:
    Q = transitions between transient states
    R = transitions from transient to absorbing states
    N = (I - Q)^(-1)
    B = N * R
    """
    Q = matrix.loc[transient_states, transient_states].values
    R = matrix.loc[transient_states, [CONV_STATE, NULL_STATE]].values
    
    I = np.identity(len(transient_states))
    
    try:
        N = np.linalg.inv(I - Q)
        B = np.dot(N, R)
        start_idx = transient_states.index(START_STATE)
        conv_idx = 0 # (Conversion) is first in [CONV_STATE, NULL_STATE]
        return float(B[start_idx, conv_idx])
    except np.linalg.LinAlgError:
        return 0.0

def compute_markov_removal_effects(
    matrix: pd.DataFrame, 
    transient_states: List[str], 
    channels: List[str], 
    total_conversions: float, 
    total_revenue: float
) -> pd.DataFrame:
    """
    Computes removal effect for each channel and allocates conversions and revenue.
    """
    baseline_p = calculate_conversion_probability(matrix, transient_states)
    
    removal_effects = {}
    
    for ch in channels:
        # Create modified matrix where transitions to ch go to NULL_STATE
        mod_matrix = matrix.copy()
        
        # When channel ch is removed, any transitions to ch are redirected to NULL_STATE
        for src in transient_states:
            prob_to_ch = mod_matrix.loc[src, ch]
            if prob_to_ch > 0:
                mod_matrix.loc[src, ch] = 0.0
                mod_matrix.loc[src, NULL_STATE] += prob_to_ch
                
        # Also remove transitions out of ch
        mod_matrix.loc[ch, :] = 0.0
        mod_matrix.loc[ch, NULL_STATE] = 1.0
        
        mod_p = calculate_conversion_probability(mod_matrix, transient_states)
        re = max(0.0, (baseline_p - mod_p) / baseline_p) if baseline_p > 0 else 0.0
        removal_effects[ch] = re
        
    total_re = sum(removal_effects.values())
    
    results = []
    for ch in channels:
        re = removal_effects[ch]
        weight = re / total_re if total_re > 0 else (1.0 / len(channels))
        attributed_conv = weight * total_conversions
        attributed_rev = weight * total_revenue
        results.append({
            'channel': ch,
            'removal_effect': re,
            'markov_weight': weight,
            'markov_conversions': attributed_conv,
            'markov_revenue': attributed_rev
        })
        
    df_markov = pd.DataFrame(results)
    return df_markov, baseline_p

def run_markov_attribution(df_touchpoints: pd.DataFrame, df_conversions: pd.DataFrame):
    """Full execution of Markov attribution."""
    journeys = extract_customer_journeys(df_touchpoints, df_conversions)
    matrix, transient_states, channels = build_transition_matrix(journeys)
    
    total_conv = len(df_conversions)
    total_rev = df_conversions['revenue'].sum()
    
    df_markov, baseline_p = compute_markov_removal_effects(
        matrix, transient_states, channels, total_conv, total_rev
    )
    
    return df_markov, matrix, baseline_p

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tp_path = os.path.join(base_dir, "data", "raw", "touchpoints.csv")
    conv_path = os.path.join(base_dir, "data", "raw", "conversions.csv")
    
    df_tp = pd.read_csv(tp_path)
    df_conv = pd.read_csv(conv_path)
    
    df_markov, matrix, baseline_p = run_markov_attribution(df_tp, df_conv)
    
    print(f"\n--- Markov Chain Attribution Analysis ---")
    print(f"Baseline Conversion Probability P(Conv): {baseline_p:.4f} ({baseline_p*100:.2f}%)")
    print("\nRemoval Effects & Attribution Allocations:")
    print(df_markov.to_string(index=False))
    
    print("\n--- Conservation Verification ---")
    print(f"Total Attributed Conversions: {df_markov['markov_conversions'].sum():.2f} (Target: {len(df_conv)})")
    print(f"Total Attributed Revenue: ${df_markov['markov_revenue'].sum():,.2f} (Target: ${df_conv['revenue'].sum():,.2f})")
