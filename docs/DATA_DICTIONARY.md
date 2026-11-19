# Marketing Analytics Data Dictionary

This document provides a comprehensive technical schema specification for all raw entity tables and transformed analytical marts in the **Grito Labs Marketing Analytics Framework**.

---

## 1. Raw Entity Schemas (`data/raw/`)

### 1.1 `users` Table
Stores prospective and enrolled student profile records.

| Column Name | Data Type | Key Type | Nullable | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | `VARCHAR(32)` | **Primary Key** | No | Unique identifier for prospective student | `USR-000001` |
| `signup_date` | `DATE` | - | No | Date user registered on Grito Labs platform | `2026-02-14` |
| `acquisition_channel` | `VARCHAR(64)` | - | No | First-discovered marketing channel | `Paid Search` |
| `country` | `VARCHAR(64)` | - | No | Geographic residence of prospective student | `United States` |
| `segment` | `VARCHAR(64)` | - | No | Behavioral persona segment | `Career Switcher` |

*Personas*: `Career Switcher` (40%), `Upskiller Professional` (35%), `College Graduate` (15%), `Corporate Sponsored` (10%).

---

### 1.2 `campaigns` Table
Master metadata for all marketing campaigns across digital channels.

| Column Name | Data Type | Key Type | Nullable | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `campaign_id` | `VARCHAR(32)` | **Primary Key** | No | Unique campaign identifier | `CMP-PS-01` |
| `channel` | `VARCHAR(64)` | - | No | Parent marketing channel | `Paid Search` |
| `name` | `VARCHAR(128)` | - | No | Human-readable campaign title | `Brand Search Core` |
| `start_date` | `DATE` | - | No | Active deployment start date | `2026-01-01` |
| `end_date` | `DATE` | - | No | Scheduled campaign conclusion date | `2026-09-30` |
| `objective` | `VARCHAR(64)` | - | No | Strategic marketing goal | `Conversion` |

*Channels*: `Paid Search`, `Paid Social`, `Email`, `Organic Social`, `Referral`, `Display`.  
*Objectives*: `Conversion`, `Acquisition`, `Nurturing`, `Awareness`, `Lead Gen`, `Thought Leadership`, `Advocacy`.

---

### 1.3 `spend` Table
Daily marketing expenditure, impressions, and click volumes by campaign.

| Column Name | Data Type | Key Type | Nullable | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | `DATE` | **Composite PK** | No | Calendar date of media spend | `2026-03-15` |
| `campaign_id` | `VARCHAR(32)` | **Foreign Key** | No | References `campaigns(campaign_id)` | `CMP-PS-01` |
| `spend` | `DECIMAL(12,2)` | - | No | Total media spend in USD | `245.80` |
| `impressions` | `INTEGER` | - | No | Ad impressions logged | `4520` |
| `clicks` | `INTEGER` | - | No | Ad clicks registered | `248` |

---

### 1.4 `touchpoints` Table
Granular clickstream and impression interaction log across the student journey.

| Column Name | Data Type | Key Type | Nullable | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `touchpoint_id` | `VARCHAR(32)` | **Primary Key** | No | Unique event tracking identifier | `TP-00000001` |
| `user_id` | `VARCHAR(32)` | **Foreign Key** | No | References `users(user_id)` | `USR-000001` |
| `timestamp` | `TIMESTAMP` | - | No | Exact ISO timestamp of interaction | `2026-03-15 14:22:10` |
| `channel` | `VARCHAR(64)` | - | No | Channel through which touch occurred | `Paid Search` |
| `campaign_id` | `VARCHAR(32)` | **Foreign Key** | No | References `campaigns(campaign_id)` | `CMP-PS-01` |
| `device` | `VARCHAR(32)` | - | No | User hardware platform | `Desktop` |
| `interaction_type` | `VARCHAR(32)` | - | No | Type of engagement | `click` |

*Interaction Types*: `impression`, `click`, `visit`.  
*Devices*: `Desktop` (65%), `Mobile` (30%), `Tablet` (5%).

---

### 1.5 `conversions` Table
Transactional record of confirmed course enrollments and tuition revenue.

| Column Name | Data Type | Key Type | Nullable | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `conversion_id` | `VARCHAR(32)` | **Primary Key** | No | Unique transaction identifier | `CNV-000001` |
| `user_id` | `VARCHAR(32)` | **Foreign Key** | No | References `users(user_id)` | `USR-000001` |
| `timestamp` | `TIMESTAMP` | - | No | Exact purchase confirmation timestamp | `2026-03-17 11:05:42` |
| `product` | `VARCHAR(128)` | - | No | Enrolled course track | `Data Analytics Bootcamp`|
| `revenue` | `DECIMAL(10,2)` | - | No | Gross course tuition paid in USD | `1299.00` |

*Course Products*:
- `Data Analytics Bootcamp` ($1,299.00)
- `Business Intelligence Specialist` ($899.00)
- `SQL & Python Immersion` ($499.00)
- `Analytics Engineering Foundation` ($299.00)

---

## 2. Transformed Analytical Marts (`data/`)

### 2.1 `attribution_comparison.csv`
Consolidated cross-model attribution dataset comparing all 6 methodologies.

- `channel`: Channel name.
- `First-Touch_conversions`, `First-Touch_revenue`: Metrics under First-Touch model.
- `Last-Touch_conversions`, `Last-Touch_revenue`: Metrics under Last-Touch model.
- `Linear_conversions`, `Linear_revenue`: Metrics under Linear model.
- `Position-Based_conversions`, `Position-Based_revenue`: Metrics under Position-Based (U-Shaped) model.
- `Time-Decay_conversions`, `Time-Decay_revenue`: Metrics under Time-Decay model.
- `removal_effect`: Marginal conversion probability drop upon channel removal in Markov model.
- `markov_weight`: Normalized Markov attribution share ($\sum W = 1.0$).
- `markov_conversions`, `markov_revenue`: Metrics under Absorbing Markov Chain.
- `total_spend`: Total media spend across active campaigns in the channel.
- `[Model]_roas`, `[Model]_cac`: Financial efficiency metrics per model.

### 2.2 `campaign_rankings.csv`
Campaign-level efficiency matrix and classification tiers.

- `campaign_id`, `campaign_name`, `channel`, `objective`: Campaign metadata.
- `total_spend`, `total_clicks`, `cpc`, `ctr_pct`: Media cost and engagement metrics.
- `linear_conversions`, `linear_revenue`: Attributed performance.
- `roas`: Attributed Revenue / Total Spend.
- `cac`: Total Spend / Attributed Conversions.
- `performance_tier`: Classification:
  - `Tier 1 - High Performer (Scale Up)`: ROAS $\ge 3.0$x, CAC $\le \$250$.
  - `Tier 1 - Organic Star (Zero Ad Spend)`: Uncapped organic ROI.
  - `Tier 2 - Moderate (Maintain / Optimize)`: $1.5\text{x} \le \text{ROAS} < 3.0\text{x}$.
  - `Tier 3 - Underperformer (Reduce / Reallocate)`: ROAS $< 1.5\text{x}$ or high CAC.

### 2.3 `budget_scenarios.csv`
Scenario forecasting model projecting revenue and ROAS shifts.

- `channel`: Channel name.
- `current_spend`: Baseline spend ($).
- `new_spend`: Projected reallocated spend ($).
- `spend_delta`: Net budget shift ($).
- `baseline_roas`: Historical Linear ROAS.
- `current_revenue`: Baseline attributed revenue ($).
- `projected_revenue_conservative`: Revenue under 85% marginal efficiency factor.
- `conservative_lift`: Net revenue gain/loss ($).
- `projected_revenue_optimistic`: Revenue under 100% retained efficiency.
- `optimistic_lift`: Net revenue gain/loss ($).
