"""
Streamlit Interactive Dashboard for Grito Labs
Multi-Channel Marketing Analytics & Attribution Framework
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Grito Labs | Marketing Attribution & ROI Framework",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    summary_path = os.path.join(DATA_DIR, "summary_metrics.json")
    attr_path = os.path.join(DATA_DIR, "attribution_comparison.csv")
    camp_path = os.path.join(DATA_DIR, "campaign_rankings.csv")
    scen_path = os.path.join(DATA_DIR, "budget_scenarios.csv")
    
    with open(summary_path, "r") as f:
        summary = json.load(f)
        
    df_attr = pd.read_csv(attr_path)
    df_camp = pd.read_csv(camp_path)
    df_scen = pd.read_csv(scen_path)
    return summary, df_attr, df_camp, df_scen

summary, df_attr, df_camp, df_scen = load_data()

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2b5c8f;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-title { font-size: 13px; color: #6c757d; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 26px; font-weight: 700; color: #1e293b; margin-top: 4px; }
    .metric-sub { font-size: 12px; color: #10b981; margin-top: 4px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎯 Grito Labs: Multi-Channel Attribution & ROI Engine")
st.caption("Marketing Analytics & Business Intelligence Deliverable | EdTech Portfolio Assessment")

# Top KPI Scorecard
st.subheader("Executive KPI Overview (Jan - Sep 2026)")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Ad Spend</div>
        <div class="metric-value">${summary['total_spend']:,.0f}</div>
        <div class="metric-sub">6 Channels Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Attributed Revenue</div>
        <div class="metric-value">${summary['total_revenue']:,.0f}</div>
        <div class="metric-sub">4,879 Enrolled Students</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Blended ROAS</div>
        <div class="metric-value">{summary['blended_roas']:.2f}x</div>
        <div class="metric-sub">Target Benchmark: 3.0x</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Blended CAC</div>
        <div class="metric-value">${summary['blended_cac']:.2f}</div>
        <div class="metric-sub">Payback: < 30 Days</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Order Value</div>
        <div class="metric-value">${summary['average_order_value']:.2f}</div>
        <div class="metric-sub">Bootcamp & Cert Focus</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Projected CLV</div>
        <div class="metric-value">${summary['projected_clv']:.2f}</div>
        <div class="metric-sub">CLV:CAC = {summary['projected_clv']/summary['blended_cac']:.2f}x</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tab Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Attribution Model Comparison", 
    "📈 Campaign Efficiency Matrix", 
    "🛣️ Customer Journey & Conversion Paths", 
    "💰 Budget Reallocation Simulator"
])

with tab1:
    st.subheader("Attribution Model Discrepancy & Removal Effects")
    st.write(
        "Compare revenue credit allocation across First-Touch, Last-Touch, Linear, Position-Based (U-Shaped), "
        "Time-Decay, and Markov Chain models. Notice how Last-Touch over-credits Email and severely under-credits top-of-funnel channels."
    )
    
    # Model comparison chart
    rev_cols = {
        'First-Touch': 'First-Touch_revenue',
        'Last-Touch': 'Last-Touch_revenue',
        'Linear': 'Linear_revenue',
        'Position-Based': 'Position-Based_revenue',
        'Time-Decay': 'Time-Decay_revenue',
        'Markov Chain': 'markov_revenue'
    }
    
    chart_data = []
    for model_name, col in rev_cols.items():
        for _, row in df_attr.iterrows():
            chart_data.append({
                'Channel': row['channel'],
                'Model': model_name,
                'Attributed Revenue ($)': row[col]
            })
    df_chart = pd.DataFrame(chart_data)
    
    fig = px.bar(
        df_chart, 
        x="Channel", 
        y="Attributed Revenue ($)", 
        color="Model", 
        barmode="group",
        title="Attributed Revenue by Channel Across 6 Attribution Models",
        text_auto='.2s'
    )
    fig.update_layout(height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison table
    st.markdown("##### Detailed Metric Breakdown by Channel")
    display_df = df_attr[[
        'channel', 'total_spend', 'First-Touch_revenue', 'Last-Touch_revenue', 
        'Linear_revenue', 'markov_revenue', 'Linear_roas', 'removal_effect'
    ]].copy()
    display_df.columns = [
        'Channel', 'Spend ($)', 'First-Touch ($)', 'Last-Touch ($)', 
        'Linear ($)', 'Markov ($)', 'Linear ROAS', 'Markov Removal Effect'
    ]
    st.dataframe(
        display_df.style.format({
            'Spend ($)': '${:,.2f}',
            'First-Touch ($)': '${:,.2f}',
            'Last-Touch ($)': '${:,.2f}',
            'Linear ($)': '${:,.2f}',
            'Markov ($)': '${:,.2f}',
            'Linear ROAS': '{:.2f}x',
            'Markov Removal Effect': '{:.4f}'
        }), 
        use_container_width=True
    )

with tab2:
    st.subheader("Campaign Performance Tiers & Efficiency")
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        # Scatter: Spend vs ROAS
        fig_scatter = px.scatter(
            df_camp,
            x="total_spend",
            y="roas",
            size="linear_revenue",
            color="performance_tier",
            hover_name="campaign_name",
            text="campaign_id",
            title="Campaign Efficiency Matrix: Spend vs. Linear ROAS (Bubble Size = Attributed Revenue)",
            labels={"total_spend": "Campaign Spend ($)", "roas": "ROAS (Revenue / Spend)"}
        )
        fig_scatter.add_hline(y=3.0, line_dash="dash", line_color="green", annotation_text="Tier 1 Threshold (3.0x ROAS)")
        fig_scatter.add_hline(y=1.5, line_dash="dash", line_color="orange", annotation_text="Tier 2 Threshold (1.5x ROAS)")
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_c2:
        st.markdown("##### Performance Tier Breakdown")
        tier_counts = df_camp['performance_tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        fig_pie = px.pie(tier_counts, names='Tier', values='Count', hole=0.4, title="Campaign Distribution by Tier")
        fig_pie.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.info(
            "**Key Insight**: Brand Search and Email automation campaigns yield >25x-50x ROAS. "
            "Display campaigns struggle at ~3.0x ROAS, absorbing budget that could be redeployed to high-intent search."
        )

    st.markdown("##### Full Campaign Efficiency Leaderboard")
    st.dataframe(
        df_camp[[
            'campaign_id', 'campaign_name', 'channel', 'objective', 
            'total_spend', 'total_clicks', 'cpc', 'linear_conversions', 'linear_revenue', 'roas', 'cac', 'performance_tier'
        ]].style.format({
            'total_spend': '${:,.2f}',
            'total_clicks': '{:,.0f}',
            'cpc': '${:.2f}',
            'linear_conversions': '{:,.1f}',
            'linear_revenue': '${:,.2f}',
            'roas': '{:.2f}x',
            'cac': '${:.2f}'
        }),
        use_container_width=True
    )

with tab3:
    st.subheader("Customer Journey Paths & Multi-Touch Conversion Funnel")
    st.write(
        "Top converting touchpoint sequences identified from 15,593 pre-conversion customer interactions. "
        "Average conversion lag is 2.3 to 4.2 days across multi-touch journeys."
    )
    
    sample_paths = pd.DataFrame([
        {"Path": "Paid Search > Conversion", "Touches": 1, "Conversions": 144, "Revenue": "$127,656", "Avg Lag": "1.1 days", "% Total": "2.95%"},
        {"Path": "Paid Social > Conversion", "Touches": 1, "Conversions": 123, "Revenue": "$107,777", "Avg Lag": "1.0 days", "% Total": "2.52%"},
        {"Path": "Paid Search > Email > Conversion", "Touches": 2, "Conversions": 115, "Revenue": "$102,185", "Avg Lag": "2.4 days", "% Total": "2.36%"},
        {"Path": "Organic Social > Conversion", "Touches": 1, "Conversions": 103, "Revenue": "$88,397", "Avg Lag": "1.0 days", "% Total": "2.11%"},
        {"Path": "Paid Social > Email > Conversion", "Touches": 2, "Conversions": 98, "Revenue": "$87,302", "Avg Lag": "2.3 days", "% Total": "2.01%"},
        {"Path": "Paid Search > Email > Email > Conversion", "Touches": 3, "Conversions": 85, "Revenue": "$81,615", "Avg Lag": "4.2 days", "% Total": "1.74%"},
        {"Path": "Paid Social > Email > Email > Conversion", "Touches": 3, "Conversions": 72, "Revenue": "$58,928", "Avg Lag": "3.9 days", "% Total": "1.48%"},
        {"Path": "Organic Social > Email > Conversion", "Touches": 2, "Conversions": 69, "Revenue": "$64,031", "Avg Lag": "2.3 days", "% Total": "1.41%"},
        {"Path": "Paid Search > Paid Search > Conversion", "Touches": 2, "Conversions": 68, "Revenue": "$57,132", "Avg Lag": "2.5 days", "% Total": "1.39%"},
        {"Path": "Paid Social > Paid Search > Conversion", "Touches": 2, "Conversions": 63, "Revenue": "$56,837", "Avg Lag": "2.7 days", "% Total": "1.29%"}
    ])
    st.table(sample_paths)

with tab4:
    st.subheader("Quantitative Budget Reallocation Scenarios")
    st.write(
        "Simulate reallocating spend from low-ROAS channels (Display -30%, Paid Social -15%) "
        "to high-ROAS scalable channels (Email +40%, Referral +25%, Paid Search +10%)."
    )
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Status Quo Revenue", f"${summary['total_revenue']:,.0f}", f"ROAS: {summary['blended_roas']:.2f}x")
    with col_s2:
        st.metric("Conservative Projection", f"${summary['budget_scenario_results']['conservative_projected_revenue']:,.0f}", f"+${summary['budget_scenario_results']['conservative_revenue_lift']:,.0f} (+6.3%)")
    with col_s3:
        st.metric("Optimistic Projection", f"${summary['budget_scenario_results']['optimistic_projected_revenue']:,.0f}", f"+${summary['budget_scenario_results']['optimistic_revenue_lift']:,.0f} (+9.0%)")
        
    st.markdown("##### Channel Reallocation Impact Table")
    st.dataframe(
        df_scen[[
            'channel', 'current_spend', 'new_spend', 'spend_delta', 'baseline_roas', 
            'current_revenue', 'projected_revenue_conservative', 'conservative_lift', 'projected_revenue_optimistic', 'optimistic_lift'
        ]].style.format({
            'current_spend': '${:,.2f}',
            'new_spend': '${:,.2f}',
            'spend_delta': '${:,.2f}',
            'baseline_roas': '{:.2f}x',
            'current_revenue': '${:,.2f}',
            'projected_revenue_conservative': '${:,.2f}',
            'conservative_lift': '${:,.2f}',
            'projected_revenue_optimistic': '${:,.2f}',
            'optimistic_lift': '${:,.2f}'
        }),
        use_container_width=True
    )
