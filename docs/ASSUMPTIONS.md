# Modeling Assumptions & Engineering Specifications

This document outlines all operational, technical, and commercial assumptions underlying the **Grito Labs Multi-Channel Marketing Analytics Framework**.

---

## 1. Attribution & Journey Tracking Assumptions

### 1.1 Attribution Lookback Window (30 Days)
- **Standard**: A maximum lookback window of **30 days** prior to conversion is enforced. Any historical interactions that occurred more than 30 days before enrollment are excluded from the conversion path.
- **EdTech Justification**: The typical consideration cycle for professional data analytics bootcamps ($299 to $1,299) spans 1 to 3 weeks. Touchpoints older than 30 days are considered brand background noise rather than direct causal drivers.

### 1.2 Identity Resolution & Cookie Stitching
- **User Identifier (`user_id`)**: The framework assumes deterministic identity resolution. Web visits, mobile impressions, email clicks, and webinar attendances are stitched to a unified `user_id` upon account creation or email submission.
- **Cross-Device Tracking**: Multi-device interactions (e.g., initial impression on Mobile, checkout on Desktop) are unified under the same user profile via first-party cookie and login persistence.

### 1.3 Pre-Conversion Sequence Enforcement
- **Chronology**: Only touchpoints timestamped **strictly on or before** the conversion timestamp are eligible for attribution:
  $$\text{Timestamp}_{\text{touch}} \le \text{Timestamp}_{\text{conversion}}$$
- **Post-Conversion Activity**: Subsequent touchpoints (e.g. post-purchase onboarding emails or course portal visits) are partitioned into a retention/LTV track and excluded from acquisition attribution.

### 1.4 State Deduplication in Markov Modeling
- **Consecutive Touchpoint Collapsing**: In the Markov chain transition model, consecutive repeated clicks on the same channel (e.g., `Email > Email > Email`) within the same session are collapsed into a single state visit (`Email`).
- **Rationale**: Prevents artificial self-loop inflation which can bias absorbing transition matrices in data-driven attribution models.

---

## 2. Financial & Unit Economic Assumptions

### 2.1 Currency & Product Catalog
- **Base Currency**: United States Dollars (USD, `$`).
- **Course Catalog & Price Points**:
  - *Data Analytics Bootcamp*: $1,299.00 (Flagship career-transition cohort)
  - *Business Intelligence Specialist*: $899.00 (Mid-level professional upskilling)
  - *SQL & Python Immersion*: $499.00 (Foundational technical track)
  - *Analytics Engineering Foundation*: $299.00 (Specialized modular workshop)
- **Blended Gross Margin**: Assumed at **75%**, reflecting edtech SaaS/cohort cost of delivery (mentor stipends, LMS hosting, grading operations).

### 2.2 Spend-to-Touchpoint Mapping
- **Direct Ad Spend**: Paid Search, Paid Social, Display, and Referral spend are tracked daily at the `campaign_id` level.
- **Zero-Ad-Spend Channels**: Organic Social (LinkedIn posts, YouTube tutorials, Discord community) is modeled with zero direct media spend ($0.00). In ROI calculations, its ROAS is represented as $\infty$ (or 999.0 for numerical stability).
- **Email Channel Cost**: Modeled as direct software/infrastructure delivery costs ($0.10 - $0.25 effective cost per engaged click).

### 2.3 Customer Lifetime Value (CLV) Proxy
- **Formula**:
  $$\text{CLV} = \text{AOV} \times \text{Repeat Purchase Multiplier} \times \text{Gross Margin}$$
- **Assumed Repeat Multiplier**: **1.25x** over a 12-month horizon (25% of students enroll in an advanced second elective or modular workshop).
- **Benchmark Threshold**: A healthy EdTech business maintains a $\text{CLV} : \text{CAC} \ge 3.0\text{x}$. Grito Labs currently tracks at **5.37x**, indicating exceptional unit profitability.

---

## 3. Budget Reallocation Assumptions

### 3.1 Diminishing Marginal Returns (The 85% Rule)
- When expanding ad spend into a channel, marginal ROAS rarely remains constant due to audience saturation and auction bidding dynamics.
- **Conservative Scenario**: Assumes **85% marginal efficiency** ($\eta = 0.85$) on all expanded budgets. If Paid Search baseline ROAS is 4.26x, incremental spend operates at $4.26 \times 0.85 = 3.62\text{x}$.
- **Optimistic Scenario**: Assumes **100% efficiency retention** ($\eta = 1.00$), valid when scaling broad, uncapped high-intent channels like Brand Search.

### 3.2 Channel Trimming Elasticity
- When trimming spend by 30% on low-performing channels (Display, GDN banners), we assume 100% of the lowest-intent traffic is eliminated first, minimizing downstream revenue loss.

---

## 4. Synthetic Data Generation & Real-World Dataset Migration

### 4.1 Synthetic Data Declaration
> [!NOTE]
> The dataset included in this repository was synthetically generated using a fixed random seed (`seed=42`) via `data_generation/generate_data.py`. While the distributions, seasonality curves, conversion lags, and unit economics reflect real-world EdTech operational benchmarks, all customer identities and records are simulated.

### 4.2 How to Swap in a Real Production Dataset
To deploy this framework against real production data:

1. **Replace CSVs in `data/raw/`**:
   - `users.csv`: Provide customer profile records matching the schema in [`DATA_DICTIONARY.md`](file:///C:/Users/asusl/.gemini/antigravity/scratch/marketing-attribution-roi/docs/DATA_DICTIONARY.md).
   - `campaigns.csv`: Export marketing campaign metadata from your ad accounts.
   - `spend.csv`: Export daily cost, impressions, and clicks from Google Ads, Meta Ads Manager, LinkedIn Ads, etc.
   - `touchpoints.csv`: Export event tracking logs from your Customer Data Platform (Segment, RudderStack, Snowplow, GA4 BigQuery export).
   - `conversions.csv`: Export transactional purchase logs from Stripe, Recurly, or your internal billing database.

2. **Re-run the Automated Pipeline**:
   ```bash
   python analysis/run_pipeline.py
   ```
   The pipeline will automatically re-ingest the data into SQLite, execute the data quality test suite, run the attribution models, re-estimate Markov removal effects, and update all dashboard and presentation metrics.

3. **Connecting Directly to a Cloud Data Warehouse (Snowflake / BigQuery / DuckDB)**:
   The SQL models in `sql/` use ANSI-standard SQL. To run against BigQuery or Snowflake, simply point the database connection in `analysis/run_pipeline.py` to your warehouse driver (e.g. `snowflake-connector-python` or `google-cloud-bigquery`).
