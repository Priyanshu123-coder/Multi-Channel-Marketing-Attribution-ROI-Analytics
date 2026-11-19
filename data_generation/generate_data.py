"""
Synthetic Marketing Data Generator for Grito Labs
Multi-Channel Marketing Analytics & Attribution Framework
Author: Marketing Analytics Engineer
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Set reproducible random seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Output directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_RAW_DIR, exist_ok=True)

# Date range: 9 months (Jan 1, 2026 to Sep 30, 2026)
START_DATE = datetime(2026, 1, 1, 0, 0, 0)
END_DATE = datetime(2026, 9, 30, 23, 59, 59)
TOTAL_DAYS = (END_DATE - START_DATE).days + 1

# Product Catalog
PRODUCTS = [
    {"product": "Data Analytics Bootcamp", "revenue": 1299.0, "weight": 0.35},
    {"product": "Business Intelligence Specialist", "revenue": 899.0, "weight": 0.30},
    {"product": "SQL & Python Immersion", "revenue": 499.0, "weight": 0.25},
    {"product": "Analytics Engineering Foundation", "revenue": 299.0, "weight": 0.10},
]

# Channels and Campaigns configuration
CHANNELS = ["Paid Search", "Paid Social", "Email", "Organic Social", "Referral", "Display"]

CAMPAIGNS_DEF = [
    # Paid Search
    {"campaign_id": "CMP-PS-01", "channel": "Paid Search", "name": "Brand Search Core", "objective": "Conversion", "base_daily_spend": 220, "cpc": 1.40, "ctr": 0.055, "cr_weight": 2.2},
    {"campaign_id": "CMP-PS-02", "channel": "Paid Search", "name": "NonBrand Analytics Bootcamp", "objective": "Acquisition", "base_daily_spend": 380, "cpc": 3.80, "ctr": 0.032, "cr_weight": 1.2},
    {"campaign_id": "CMP-PS-03", "channel": "Paid Search", "name": "NonBrand BI SQL Competitor", "objective": "Acquisition", "base_daily_spend": 260, "cpc": 4.20, "ctr": 0.028, "cr_weight": 0.9},
    
    # Paid Social
    {"campaign_id": "CMP-SO-01", "channel": "Paid Social", "name": "Meta Prospecting Video", "objective": "Awareness", "base_daily_spend": 320, "cpc": 1.60, "ctr": 0.018, "cr_weight": 0.8},
    {"campaign_id": "CMP-SO-02", "channel": "Paid Social", "name": "Meta Retargeting Testimonials", "objective": "Conversion", "base_daily_spend": 200, "cpc": 2.10, "ctr": 0.035, "cr_weight": 1.8},
    {"campaign_id": "CMP-SO-03", "channel": "Paid Social", "name": "LinkedIn B2B Upskilling", "objective": "Lead Gen", "base_daily_spend": 350, "cpc": 6.50, "ctr": 0.015, "cr_weight": 1.1},
    
    # Email
    {"campaign_id": "CMP-EM-01", "channel": "Email", "name": "Welcome Nurture Flow", "objective": "Nurturing", "base_daily_spend": 35, "cpc": 0.15, "ctr": 0.120, "cr_weight": 2.6},
    {"campaign_id": "CMP-EM-02", "channel": "Email", "name": "Weekly Analytics Newsletter", "objective": "Engagement", "base_daily_spend": 25, "cpc": 0.10, "ctr": 0.085, "cr_weight": 1.4},
    {"campaign_id": "CMP-EM-03", "channel": "Email", "name": "Flash Promo Bootcamp Discount", "objective": "Conversion", "base_daily_spend": 45, "cpc": 0.25, "ctr": 0.140, "cr_weight": 3.0},
    
    # Organic Social
    {"campaign_id": "CMP-OS-01", "channel": "Organic Social", "name": "LinkedIn Founder Insights", "objective": "Thought Leadership", "base_daily_spend": 0, "cpc": 0.0, "ctr": 0.040, "cr_weight": 1.3},
    {"campaign_id": "CMP-OS-02", "channel": "Organic Social", "name": "YouTube Project Walkthroughs", "objective": "Education", "base_daily_spend": 0, "cpc": 0.0, "ctr": 0.060, "cr_weight": 1.7},
    {"campaign_id": "CMP-OS-03", "channel": "Organic Social", "name": "Community Discord Tips", "objective": "Engagement", "base_daily_spend": 0, "cpc": 0.0, "ctr": 0.050, "cr_weight": 1.2},
    
    # Referral
    {"campaign_id": "CMP-RF-01", "channel": "Referral", "name": "Alumni Ambassador Program", "objective": "Advocacy", "base_daily_spend": 90, "cpc": 1.10, "ctr": 0.075, "cr_weight": 2.5},
    {"campaign_id": "CMP-RF-02", "channel": "Referral", "name": "Partner Edtech Affiliate", "objective": "Acquisition", "base_daily_spend": 120, "cpc": 1.80, "ctr": 0.045, "cr_weight": 1.5},
    
    # Display
    {"campaign_id": "CMP-DP-01", "channel": "Display", "name": "GDN Prospecting Banners", "objective": "Awareness", "base_daily_spend": 280, "cpc": 0.65, "ctr": 0.006, "cr_weight": 0.4},
    {"campaign_id": "CMP-DP-02", "channel": "Display", "name": "Programmatic Course Retargeting", "objective": "Retargeting", "base_daily_spend": 190, "cpc": 1.20, "ctr": 0.012, "cr_weight": 0.7},
]

COUNTRIES = ["United States", "India", "United Kingdom", "Canada", "Germany"]
COUNTRY_WEIGHTS = [0.45, 0.25, 0.15, 0.10, 0.05]

SEGMENTS = ["Career Switcher", "Upskiller Professional", "College Graduate", "Corporate Sponsored"]
SEGMENT_WEIGHTS = [0.40, 0.35, 0.15, 0.10]

DEVICES = ["Desktop", "Mobile", "Tablet"]
DEVICE_WEIGHTS = [0.65, 0.30, 0.05]

def get_seasonality_factor(date: datetime) -> float:
    """Edtech seasonality factor by month and day of week."""
    month = date.month
    day_of_week = date.weekday() # 0 = Monday, 6 = Sunday
    
    # Month multipliers
    month_mult = {
        1: 1.35, # New Year resolutions
        2: 1.15,
        3: 1.20, # Spring cohort
        4: 1.05,
        5: 0.95,
        6: 0.85, # Summer lull
        7: 0.80,
        8: 1.10, # Fall prep
        9: 1.30, # Back to school / Q3 corporate budget
    }.get(month, 1.0)
    
    # Midweek vs weekend: Professionals study and convert Tue-Thu
    day_mult = 1.10 if day_of_week in [1, 2, 3] else (0.85 if day_of_week in [5, 6] else 1.0)
    
    return month_mult * day_mult

def generate_campaigns_and_spend():
    """Generate campaigns master table and daily spend records."""
    campaigns_rows = []
    for c in CAMPAIGNS_DEF:
        campaigns_rows.append({
            "campaign_id": c["campaign_id"],
            "channel": c["channel"],
            "name": c["name"],
            "start_date": "2026-01-01",
            "end_date": "2026-09-30",
            "objective": c["objective"]
        })
    df_campaigns = pd.DataFrame(campaigns_rows)
    
    # Daily spend, impressions, clicks
    spend_rows = []
    current_date = START_DATE
    while current_date <= END_DATE:
        seasonality = get_seasonality_factor(current_date)
        date_str = current_date.strftime("%Y-%m-%d")
        
        for c in CAMPAIGNS_DEF:
            base_spend = c["base_daily_spend"]
            if base_spend == 0:
                # Organic channel has zero ad spend but generates impressions and clicks
                daily_impressions = int(np.random.normal(1200, 200) * seasonality)
                daily_impressions = max(200, daily_impressions)
                ctr = np.random.normal(c["ctr"], 0.005)
                ctr = max(0.01, min(0.15, ctr))
                daily_clicks = int(daily_impressions * ctr)
                daily_spend = 0.0
            else:
                spend_noise = np.random.normal(1.0, 0.08)
                daily_spend = round(base_spend * seasonality * spend_noise, 2)
                cpc = max(0.10, np.random.normal(c["cpc"], c["cpc"] * 0.12))
                daily_clicks = max(1, int(daily_spend / cpc))
                ctr = max(0.002, np.random.normal(c["ctr"], c["ctr"] * 0.10))
                daily_impressions = max(daily_clicks * 2, int(daily_clicks / ctr))
                
            spend_rows.append({
                "date": date_str,
                "campaign_id": c["campaign_id"],
                "spend": daily_spend,
                "impressions": daily_impressions,
                "clicks": daily_clicks
            })
            
        current_date += timedelta(days=1)
        
    df_spend = pd.DataFrame(spend_rows)
    return df_campaigns, df_spend

def generate_users_and_journeys(df_campaigns):
    """Generate users, multi-touch journeys, and conversions."""
    # Target: 25,000 users, leading to ~75,000 - 100,000 touchpoints and ~4,200 conversions
    NUM_USERS = 25000
    
    users_rows = []
    touchpoints_rows = []
    conversions_rows = []
    
    campaign_by_channel = {}
    for ch in CHANNELS:
        campaign_by_channel[ch] = df_campaigns[df_campaigns["channel"] == ch]["campaign_id"].tolist()
        
    touchpoint_counter = 1
    conversion_counter = 1
    
    # Channel distribution for initial discovery (first touch)
    first_touch_probs = [0.28, 0.25, 0.05, 0.20, 0.08, 0.14] # PS, SO, EM, OS, RF, DP
    
    # Transition likelihood matrix from Channel i to Channel j (simulating natural marketing funnels)
    # Channels: ["Paid Search", "Paid Social", "Email", "Organic Social", "Referral", "Display"]
    transition_weights = {
        "Paid Search":    {"Paid Search": 0.20, "Paid Social": 0.15, "Email": 0.40, "Organic Social": 0.10, "Referral": 0.05, "Display": 0.10},
        "Paid Social":    {"Paid Search": 0.25, "Paid Social": 0.20, "Email": 0.35, "Organic Social": 0.10, "Referral": 0.02, "Display": 0.08},
        "Email":          {"Paid Search": 0.20, "Paid Social": 0.10, "Email": 0.50, "Organic Social": 0.10, "Referral": 0.05, "Display": 0.05},
        "Organic Social": {"Paid Search": 0.25, "Paid Social": 0.15, "Email": 0.35, "Organic Social": 0.15, "Referral": 0.05, "Display": 0.05},
        "Referral":       {"Paid Search": 0.20, "Paid Social": 0.05, "Email": 0.45, "Organic Social": 0.10, "Referral": 0.15, "Display": 0.05},
        "Display":        {"Paid Search": 0.30, "Paid Social": 0.25, "Email": 0.25, "Organic Social": 0.08, "Referral": 0.02, "Display": 0.10},
    }
    
    for user_idx in range(1, NUM_USERS + 1):
        user_id = f"USR-{user_idx:06d}"
        
        # User first active date spread across 9 months
        # Skew slightly towards Jan, Mar, Aug/Sep
        day_offset = int(np.random.beta(1.3, 1.2) * (TOTAL_DAYS - 20))
        user_start_time = START_DATE + timedelta(days=day_offset, hours=random.randint(6, 22), minutes=random.randint(0, 59))
        
        # User attributes
        country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS)[0]
        segment = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        
        # Initial acquisition channel
        first_channel = random.choices(CHANNELS, weights=first_touch_probs)[0]
        
        users_rows.append({
            "user_id": user_id,
            "signup_date": user_start_time.strftime("%Y-%m-%d"),
            "acquisition_channel": first_channel,
            "country": country,
            "segment": segment
        })
        
        # Journey generation
        seg_boost = {"Career Switcher": 1.25, "Upskiller Professional": 1.15, "College Graduate": 0.75, "Corporate Sponsored": 1.40}[segment]
        base_conversion_prob = 0.17 * seg_boost
        converts = random.random() < base_conversion_prob
        
        # Number of touchpoints: 1 to 6 touchpoints typically
        if converts:
            num_touches = random.choices([1, 2, 3, 4, 5, 6], weights=[0.10, 0.22, 0.30, 0.20, 0.12, 0.06])[0]
        else:
            num_touches = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.30, 0.20, 0.10, 0.05])[0]
            
        current_touch_time = user_start_time
        curr_channel = first_channel
        user_touches = []
        
        for touch_step in range(num_touches):
            if touch_step > 0:
                # Transition to next channel
                next_channel_dist = transition_weights[curr_channel]
                curr_channel = random.choices(list(next_channel_dist.keys()), weights=list(next_channel_dist.values()))[0]
                
                # Time gap between touches: log-normal with median ~2-4 days
                gap_hours = int(np.random.lognormal(mean=3.2, sigma=0.9))
                gap_hours = max(1, min(gap_hours, 24 * 30)) # Cap at 30 days
                current_touch_time += timedelta(hours=gap_hours)
                if current_touch_time > END_DATE:
                    break
                    
            # Pick a campaign for this channel
            campaign_id = random.choice(campaign_by_channel[curr_channel])
            device = random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0]
            
            # Interaction type: impressions common in display/social; clicks/visits elsewhere
            if curr_channel in ["Display", "Paid Social"] and random.random() < 0.35:
                interaction = "impression"
            elif curr_channel == "Email":
                interaction = "click" if random.random() < 0.75 else "visit"
            else:
                interaction = "click" if random.random() < 0.60 else "visit"
                
            touchpoint_id = f"TP-{touchpoint_counter:08d}"
            touchpoint_counter += 1
            
            touch_record = {
                "touchpoint_id": touchpoint_id,
                "user_id": user_id,
                "timestamp": current_touch_time.strftime("%Y-%m-%d %H:%M:%S"),
                "channel": curr_channel,
                "campaign_id": campaign_id,
                "device": device,
                "interaction_type": interaction
            }
            touchpoints_rows.append(touch_record)
            user_touches.append(touch_record)
            
        # Conversion event
        if converts and len(user_touches) > 0:
            # Conversion happens between 5 minutes and 48 hours after final touchpoint
            conv_lag_minutes = random.randint(5, 2880)
            conv_time = current_touch_time + timedelta(minutes=conv_lag_minutes)
            if conv_time <= END_DATE:
                # Select product
                prod = random.choices(PRODUCTS, weights=[p["weight"] for p in PRODUCTS])[0]
                
                conversion_id = f"CNV-{conversion_counter:06d}"
                conversion_counter += 1
                
                conversions_rows.append({
                    "conversion_id": conversion_id,
                    "user_id": user_id,
                    "timestamp": conv_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "product": prod["product"],
                    "revenue": prod["revenue"]
                })
                
    df_users = pd.DataFrame(users_rows)
    df_touchpoints = pd.DataFrame(touchpoints_rows)
    df_conversions = pd.DataFrame(conversions_rows)
    
    return df_users, df_touchpoints, df_conversions

def main():
    print("=== Generating Synthetic Marketing Analytics Data for Grito Labs ===")
    df_campaigns, df_spend = generate_campaigns_and_spend()
    print(f"Generated {len(df_campaigns)} campaigns and {len(df_spend)} daily spend records.")
    
    df_users, df_touchpoints, df_conversions = generate_users_and_journeys(df_campaigns)
    print(f"Generated {len(df_users)} users, {len(df_touchpoints)} touchpoints, and {len(df_conversions)} conversions.")
    
    # Save CSVs
    df_campaigns.to_csv(os.path.join(DATA_RAW_DIR, "campaigns.csv"), index=False)
    df_spend.to_csv(os.path.join(DATA_RAW_DIR, "spend.csv"), index=False)
    df_users.to_csv(os.path.join(DATA_RAW_DIR, "users.csv"), index=False)
    df_touchpoints.to_csv(os.path.join(DATA_RAW_DIR, "touchpoints.csv"), index=False)
    df_conversions.to_csv(os.path.join(DATA_RAW_DIR, "conversions.csv"), index=False)
    
    print("All CSVs saved successfully to data/raw/!")
    
    # Sanity verification
    print("\n--- Integrity Verification ---")
    print(f"Unique users: {df_users['user_id'].nunique()}")
    print(f"Touchpoints date range: {df_touchpoints['timestamp'].min()} to {df_touchpoints['timestamp'].max()}")
    print(f"Conversions count: {len(df_conversions)}, Total Revenue: ${df_conversions['revenue'].sum():,.2f}")
    print(f"Total Ad Spend: ${df_spend['spend'].sum():,.2f}")
    overall_roas = df_conversions['revenue'].sum() / df_spend['spend'].sum()
    print(f"Blended ROAS: {overall_roas:.2f}x")
    
    # Check referential integrity
    assert df_touchpoints["user_id"].isin(df_users["user_id"]).all(), "Orphan touchpoints found!"
    assert df_conversions["user_id"].isin(df_users["user_id"]).all(), "Orphan conversions found!"
    assert df_touchpoints["campaign_id"].isin(df_campaigns["campaign_id"]).all(), "Invalid campaign in touchpoints!"
    assert df_spend["campaign_id"].isin(df_campaigns["campaign_id"]).all(), "Invalid campaign in spend!"
    print("Referential integrity assertions passed 100%!")

if __name__ == "__main__":
    main()
