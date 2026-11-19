"""
Unit Tests for Marketing Attribution Models
Tests Conservation of Conversions, Conservation of Revenue, Edge Cases, and Markov Properties.
"""

import os
import pytest
import pandas as pd
import numpy as np

from analysis.attribution import (
    prepare_pre_conversion_touchpoints,
    compute_attribution_weights,
    aggregate_channel_attribution
)
from analysis.markov_attribution import (
    extract_customer_journeys,
    build_transition_matrix,
    calculate_conversion_probability,
    compute_markov_removal_effects,
    START_STATE, CONV_STATE, NULL_STATE
)

@pytest.fixture(scope="module")
def dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tp_path = os.path.join(base_dir, "data", "raw", "touchpoints.csv")
    conv_path = os.path.join(base_dir, "data", "raw", "conversions.csv")
    
    assert os.path.exists(tp_path), f"Missing {tp_path}"
    assert os.path.exists(conv_path), f"Missing {conv_path}"
    
    df_tp = pd.read_csv(tp_path)
    df_conv = pd.read_csv(conv_path)
    return df_tp, df_conv

def test_heuristic_attribution_conservation(dataset):
    """
    Core Unit Test: Verifies that for every heuristic attribution model,
    the total attributed conversions equal the exact total conversions,
    and total attributed revenue equals the exact total revenue (no credit created or lost).
    """
    df_tp, df_conv = dataset
    total_conversions = len(df_conv)
    total_revenue = df_conv['revenue'].sum()
    
    df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
    df_weighted = compute_attribution_weights(df_valid)
    df_results, conservation_checks = aggregate_channel_attribution(df_weighted, total_conversions, total_revenue)
    
    for model_name, check in conservation_checks.items():
        assert check['is_conserved'], (
            f"Model {model_name} failed conservation! "
            f"Conv diff: {check['conv_diff']}, Rev diff: {check['rev_diff']}"
        )
        assert abs(check['total_conversions'] - total_conversions) < 1e-4
        assert abs(check['total_revenue'] - total_revenue) < 1e-2

def test_markov_attribution_conservation(dataset):
    """
    Verifies that the data-driven Markov chain model conserves total conversions and revenue.
    """
    df_tp, df_conv = dataset
    total_conversions = len(df_conv)
    total_revenue = df_conv['revenue'].sum()
    
    journeys = extract_customer_journeys(df_tp, df_conv)
    matrix, transient_states, channels = build_transition_matrix(journeys)
    df_markov, baseline_p = compute_markov_removal_effects(
        matrix, transient_states, channels, total_conversions, total_revenue
    )
    
    assert baseline_p > 0.0, "Baseline conversion probability must be positive."
    assert abs(df_markov['markov_conversions'].sum() - total_conversions) < 1e-4, "Markov conversions not conserved!"
    assert abs(df_markov['markov_revenue'].sum() - total_revenue) < 1e-2, "Markov revenue not conserved!"

def test_single_touch_journey_edge_case():
    """
    Edge Case: For a single-touch journey, all 5 heuristic models must assign 100% of the credit to the sole touchpoint.
    """
    df_tp = pd.DataFrame([{
        'touchpoint_id': 'TP-01',
        'user_id': 'USR-1',
        'timestamp': '2026-03-01 10:00:00',
        'channel': 'Paid Search',
        'campaign_id': 'CMP-PS-01'
    }])
    df_conv = pd.DataFrame([{
        'conversion_id': 'CNV-01',
        'user_id': 'USR-1',
        'timestamp': '2026-03-01 12:00:00',
        'product': 'Bootcamp',
        'revenue': 1299.0
    }])
    
    df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
    df_weighted = compute_attribution_weights(df_valid)
    
    row = df_weighted.iloc[0]
    assert row['weight_first_touch'] == 1.0
    assert row['weight_last_touch'] == 1.0
    assert row['weight_linear'] == 1.0
    assert row['weight_position_based'] == 1.0
    assert abs(row['weight_time_decay'] - 1.0) < 1e-6

def test_two_touch_position_based_edge_case():
    """
    Edge Case: In a 2-touch journey, position-based attribution must split credit 50% / 50%.
    """
    df_tp = pd.DataFrame([
        {'touchpoint_id': 'TP-01', 'user_id': 'USR-2', 'timestamp': '2026-03-01 10:00:00', 'channel': 'Paid Social', 'campaign_id': 'CMP-SO-01'},
        {'touchpoint_id': 'TP-02', 'user_id': 'USR-2', 'timestamp': '2026-03-05 15:00:00', 'channel': 'Email', 'campaign_id': 'CMP-EM-01'}
    ])
    df_conv = pd.DataFrame([{
        'conversion_id': 'CNV-02',
        'user_id': 'USR-2',
        'timestamp': '2026-03-06 10:00:00',
        'product': 'Bootcamp',
        'revenue': 899.0
    }])
    
    df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
    df_weighted = compute_attribution_weights(df_valid)
    
    weights = df_weighted['weight_position_based'].tolist()
    assert weights == [0.5, 0.5]

def test_time_decay_monotonicity():
    """
    Verifies that touchpoints closer in time to conversion receive greater weight than older touches.
    """
    df_tp = pd.DataFrame([
        {'touchpoint_id': 'TP-01', 'user_id': 'USR-3', 'timestamp': '2026-01-01 10:00:00', 'channel': 'Display', 'campaign_id': 'CMP-DP-01'},
        {'touchpoint_id': 'TP-02', 'user_id': 'USR-3', 'timestamp': '2026-01-15 10:00:00', 'channel': 'Paid Social', 'campaign_id': 'CMP-SO-01'},
        {'touchpoint_id': 'TP-03', 'user_id': 'USR-3', 'timestamp': '2026-01-20 10:00:00', 'channel': 'Email', 'campaign_id': 'CMP-EM-01'}
    ])
    df_conv = pd.DataFrame([{
        'conversion_id': 'CNV-03',
        'user_id': 'USR-3',
        'timestamp': '2026-01-21 10:00:00',
        'product': 'Immersion',
        'revenue': 499.0
    }])
    
    df_valid = prepare_pre_conversion_touchpoints(df_tp, df_conv)
    df_weighted = compute_attribution_weights(df_valid)
    
    weights = df_weighted['weight_time_decay'].tolist()
    # TP-03 is 1 day before, TP-02 is 6 days before, TP-01 is 20 days before
    assert weights[2] > weights[1] > weights[0]

def test_markov_matrix_stochasticity():
    """
    Verifies that every transient row in the Markov transition matrix sums to 1.0 (row stochasticity).
    """
    journeys = [
        [START_STATE, 'Paid Search', 'Email', CONV_STATE],
        [START_STATE, 'Paid Social', NULL_STATE],
        [START_STATE, 'Organic Social', 'Paid Search', CONV_STATE]
    ]
    matrix, transient_states, channels = build_transition_matrix(journeys)
    
    for state in transient_states:
        row_sum = matrix.loc[state, :].sum()
        assert abs(row_sum - 1.0) < 1e-6, f"State {state} row sum is {row_sum}, expected 1.0"
