# Multi-Channel Marketing Analytics & Attribution Framework

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20ANSI--SQL-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Pytest-6%2F6%20Passing-brightgreen?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Interactive Dashboard](https://img.shields.io/badge/Dashboard-Streamlit%20%26%20HTML5-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Client Context](https://img.shields.io/badge/Client-Grito%20Labs-10B981?style=flat)](https://gritolabs.com/)

An enterprise-grade, end-to-end marketing analytics and multi-touch attribution engineering project built for **Grito Labs** (EdTech for Data and Business Analytics). 

This framework analyzes multi-channel acquisition funnels, models customer journeys, compares 6 attribution models (including an absorbing **Markov Chain Removal Effect** model), enforces the **Attribution Conservation Law** via automated unit tests, and translates findings into quantitative budget reallocation scenarios for executive decision-makers.

---

## 📌 Executive Summary of Findings

| Metric | Baseline Performance | Recommended Reallocation (Conservative) | Commercial Lift |
| :--- | :--- | :--- | :--- |
| **Total Media Spend** | **$742,905** | **$715,958** | -$26,947 (Spend Reduction) |
| **Attributed Revenue** | **$4,258,621** | **$4,526,150** | **+$267,529 (+6.3% Lift)** |
| **Blended ROAS** | **5.73x** | **6.32x** | **+0.59x ROAS Improvement** |
| **Optimistic Revenue** | - | **$4,641,813** | **+$383,192 (+9.0% Lift)** |
| **Blended CAC** | **$152.27** | **$144.10** | Lower Acquisition Cost |
| **Projected 12-Mo CLV** | **$818.29** | **$818.29** | CLV:CAC Ratio = 5.68x |

### Key Strategic Takeaways:
1. **Top 3 Channels by Linear ROAS**:
   - **Email Nurturing & Promo**: **34.99x ROAS** ($30,980 spend, $1,083,832 attributed revenue).
   - **Paid Search (Google Ads)**: **4.26x ROAS** ($254,078 spend, $1,082,524 attributed revenue; Brand Search delivers **5.57x**).
   - **Referral Network**: **4.14x ROAS** ($62,083 spend, $256,950 attributed revenue).
2. **Attribution Model Discrepancies**:
   - **Last-Touch Attribution Distortion**: Last-Touch awards **$1,538,836 (36.1%)** to Email and over-credits bottom-funnel closers, while undervaluing **Organic Social** by 46% ($468k vs $864k First-Touch) and **Display** ($335k vs $575k First-Touch).
   - **Markov Removal Discovery**: The absorbing Markov model validates that removing **Paid Search** drops conversion probability by **47.6%**, while removing **Email** causes a **45.1%** collapse. **Organic Social** acts as a crucial $641k uncredited assist catalyst.
3. **Recommended Budget Shift**:
   - Trim spend on low-intent channels: **Display (-30%)** and **Paid Social (-15%)**.
   - Reallocate into high-intent and retention channels: **Email (+40%)**, **Paid Search (+10%)**, and **Referral (+25%)**.
   - Result: Generates **+$267,529 (Conservative)** to **+$383,192 (Optimistic)** in gross revenue with zero overall budget increase.

---

## 📂 Repository Structure

```
marketing-attribution-roi/
├── README.md                                  # Executive overview, architecture & quickstart
├── requirements.txt                           # Pinned Python package dependencies
├── .gitignore                                 # Exclusions for virtualenvs, caches, and files >50MB
├── run_all.sh                                 # Bash single-command reproduction script (Linux/macOS)
├── run_all.ps1                                # PowerShell single-command reproduction script (Windows)
│
├── docs/                                      # Complete Analytical Documentation
│   ├── METHODOLOGY.md                         # Mathematical formulations of all 6 attribution models
│   ├── ASSUMPTIONS.md                         # Operational, lookback (30-day), and financial assumptions
│   ├── DATA_DICTIONARY.md                     # Entity schemas, constraints, data types & samples
│   └── RECOMMENDATIONS.md                     # Quantified budget shift recommendations & executive roadmap
│
├── data/
│   ├── raw/                                   # Generated synthetic CSVs (users, touchpoints, conversions, spend)
│   ├── db/                                    # SQLite database (marketing_analytics.db)
│   ├── attribution_comparison.csv             # 6-model cross-comparison table by channel
│   ├── campaign_rankings.csv                  # Campaign-level efficiency and performance tiers
│   ├── budget_scenarios.csv                   # Conservative & optimistic reallocation scenarios
│   └── summary_metrics.json                   # Machine-readable high-level KPI outputs
│
├── data_generation/
│   └── generate_data.py                       # Seeded (seed=42) synthetic data generator (~60k touchpoints)
│
├── sql/                                       # Pure SQL Analytics Layer (Numbered execution order)
│   ├── 01_data_quality.sql                    # Nulls, duplicates, orphans, chronologies, range tests
│   ├── 02_channel_performance.sql             # Volume, reach, CTR, CPC, and spend share
│   ├── 03_kpis.sql                            # Core business formulas: CR, CAC, ROAS, AOV, CLV
│   ├── 04_journey_paths.sql                   # Multi-touch path strings, path lengths, conversion lag
│   ├── 05_attribution_models.sql              # First, Last, Linear, U-Shaped, and Time-Decay in SQL
│   ├── 06_campaign_efficiency.sql             # Campaign ROAS, CAC, and Tier 1/2/3 classification
│   └── 07_budget_scenarios.sql                # Quantitative budget shift & lift projection in SQL
│
├── analysis/                                  # Python Mathematical Engines & Orchestrator
│   ├── attribution.py                         # Rule-based attribution engine with conservation verification
│   ├── markov_attribution.py                  # Absorbing Markov chain removal effect engine
│   └── run_pipeline.py                        # Master pipeline orchestrator (DB load, SQL runs, exports)
│
├── dashboard/                                 # Interactive Dashboards
│   ├── app.py                                 # Streamlit application with interactive sliders and charts
│   └── index.html                             # Zero-dependency, offline-ready HTML5/Chart.js dashboard
│
├── deck/                                      # Executive Stakeholder Presentation
│   ├── generate_deck.py                       # Script to programmatically build PowerPoint presentation
│   └── Marketing_Attribution_Findings.pptx    # 10-slide executive presentation for leadership
│
└── tests/                                     # Automated Test Suite
    └── test_attribution.py                   # Pytest suite verifying 100% conservation & edge cases
```

---

## ⚡ Quickstart: One-Command Reproduction

### Option A: Using the Automated Shell Script
```bash
# Clone the repository
git clone https://github.com/Priyanshu123-coder/marketing-attribution-roi.git
cd marketing-attribution-roi

# Install dependencies
pip install -r requirements.txt

# Run the entire pipeline end-to-end
chmod +x run_all.sh
./run_all.sh
```

### Option B: Windows PowerShell
```powershell
.\run_all.ps1
```

### Option C: Manual Step-by-Step Execution
```bash
# 1. Generate synthetic dataset
python data_generation/generate_data.py

# 2. Execute database ingestion, SQL suite, and attribution models
python analysis/run_pipeline.py

# 3. Run automated unit tests
python -m pytest tests/test_attribution.py -v

# 4. Generate the 10-slide executive PowerPoint deck
python deck/generate_deck.py

# 5. Launch the Streamlit dashboard
streamlit run dashboard/app.py
```
*(Or simply double-click `dashboard/index.html` to view the interactive dashboard in any browser with zero installation!)*

---

## 🧪 Automated Unit Tests & Attribution Conservation

A critical feature of this framework is the enforcement of the **Attribution Conservation Law**: no conversion or revenue dollar is created or destroyed.

Run the test suite with:
```bash
python -m pytest tests/test_attribution.py -v
```

### Test Suite Coverage:
1. `test_heuristic_attribution_conservation`: Verifies that First-Touch, Last-Touch, Linear, Position-Based (U-Shaped), and Time-Decay each conserve exactly 4,879 conversions and $4,258,621 in revenue ($\Delta < 10^{-4}$).
2. `test_markov_attribution_conservation`: Verifies that the data-driven Markov removal model conserves 100% of conversions and revenue.
3. `test_single_touch_journey_edge_case`: Confirms that 1-touch journeys assign 100% credit across all models.
4. `test_two_touch_position_based_edge_case`: Confirms that 2-touch journeys assign exact 50% / 50% splits under position-based attribution.
5. `test_time_decay_monotonicity`: Asserts that touchpoints closer to conversion receive strictly higher weights.
6. `test_markov_matrix_stochasticity`: Validates that all transient states in the Markov transition matrix sum to 1.0 (row-stochasticity).

---

## 📊 Attribution Models Evaluated

| Model | Weight Allocation Strategy | Best Suited For | Key Bias |
| :--- | :--- | :--- | :--- |
| **First-Touch** | 100% to first touchpoint | Top-of-funnel discovery, brand awareness | Ignores all mid/bottom-funnel nurturing |
| **Last-Touch** | 100% to final touchpoint | Closing efficiency, promotional flash sales | Over-credits branded search and email |
| **Linear** | Equal split ($1/M_k$ across all touches) | Multi-touch baseline balance | Treats all touchpoints as equally valuable |
| **Position-Based** | 40% First, 40% Last, 20% Middle | High-consideration customer journeys | Heuristic weights lack mathematical derivation |
| **Time-Decay** | Exponential half-life ($2^{-\Delta t / 7}$) | Short sales cycles, rapid decision funnels | Penalizes long-term educational branding |
| **Markov Chain** | Data-driven **Removal Effect** | Objective cross-channel portfolio optimization | Requires complete customer journey path logs |

See [`docs/METHODOLOGY.md`](file:///C:/Users/asusl/.gemini/antigravity/scratch/marketing-attribution-roi/docs/METHODOLOGY.md) for complete mathematical proofs and equations.

---

## 🔄 How to Swap in a Real Dataset

This repository was designed for frictionless production deployment. To use with your own marketing data:

1. Place your CSVs in `data/raw/` matching the schemas detailed in [`docs/DATA_DICTIONARY.md`](file:///C:/Users/asusl/.gemini/antigravity/scratch/marketing-attribution-roi/docs/DATA_DICTIONARY.md):
   - `users.csv`, `campaigns.csv`, `spend.csv`, `touchpoints.csv`, `conversions.csv`
2. Run `python analysis/run_pipeline.py`.
3. The pipeline will automatically validate referential integrity, ingest into SQLite, execute the SQL analytical layer, recompute Markov transition probabilities, and export updated reports!

---

## 📄 License & Attribution

Developed as a professional analytics engineering submission for **Grito Labs**.  
Authored by **Priyanshu Singh** (`Priyanshu123-coder`). Open-source under the MIT License.
