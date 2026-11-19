# Strategic Marketing Recommendations & Budget Optimization

**Prepared For**: Grito Labs Executive Leadership (Chief Marketing Officer & Head of Growth)  
**Deliverable**: Multi-Channel Marketing Analytics & Attribution Framework  
**Timeframe Analyzed**: January 1, 2026 – September 30, 2026  

---

## 1. Executive Summary: The $267k+ Growth Opportunity

Across the 9-month assessment period, Grito Labs deployed **$742,905** in marketing spend, generating **4,879 student enrollments** and **$4,258,621** in tuition revenue at a healthy blended **5.73x ROAS** and **$152.27 CAC**.

However, our attribution models reveal deep operational misallocations:
1. **Last-Touch Attribution is Distorting Strategy**: Last-touch assigns **$1.54M (36.1%)** of revenue to Email, masking the reality that Email rarely originates leads. Meanwhile, **Organic Social** ($864k in first-touch discovery) and **Display** ($575k in top-of-funnel reach) receive minimal closing credit.
2. **Display Advertising Underperforms**: Display generates a weak **3.01x Linear ROAS** with high effective CAC ($288.70), functioning largely as passive banner awareness with negligible conversion intent.
3. **High-ROI Headroom**: High-intent Brand Search (5.57x ROAS) and Alumni Referral programs (5.22x ROAS) are constrained by conservative budgets, leaving high-converting traffic uncaptured.

By executing a targeted **20% portfolio reallocation**—transferring spend from underperforming Display and Paid Social campaigns into Email infrastructure, Paid Search, and Referral partnerships—Grito Labs can unlock an estimated **+$267,529 (Conservative)** to **+$383,192 (Optimistic)** in incremental gross revenue **without increasing total ad budget by a single dollar**.

---

## 2. Quantitative Budget Reallocation Blueprint

### 2.1 Reallocation Matrix (Spend Shift & Projected Lift)

| Marketing Channel | Current Spend | Shift (%) | Reallocated Spend | Historical ROAS | Current Revenue | Conservative Lift (+85% Eff.) | Optimistic Lift (+100% Eff.) | New ROAS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Advertising** | $139,353 | **-30.0%** | $97,547 | 3.01x | $419,689 | -$125,907 | -$125,907 | 3.01x |
| **Paid Social (Meta/LinkedIn)**| $256,411 | **-15.0%** | $217,949 | 3.16x | $811,222 | -$121,683 | -$121,683 | 3.16x |
| **Email Nurturing & Promo** | $30,980 | **+40.0%** | $43,372 | 34.99x | $1,083,832 | **+$368,503** | **+$433,533** | 33.48x |
| **Paid Search (Google Ads)** | $254,078 | **+10.0%** | $279,486 | 4.26x | $1,082,524 | **+$92,028** | **+$108,252** | 4.20x |
| **Referral Network** | $62,083 | **+25.0%** | $77,604 | 4.14x | $256,950 | **+$54,588** | **+$64,222** | 4.01x |
| **Organic Social (Content)** | $0 | 0.0% | $0 | $\infty$ | $604,405 | $0 | $0 | $\infty$ |
| **PORTFOLIO TOTAL** | **$742,905** | **-3.6% net** | **$715,958** | **5.73x** | **$4,258,621** | **+$267,529** | **+$383,192** | **6.32x** |

### 2.2 Key Financial Outcomes
- **Conservative Scenario**: Portfolio revenue reaches **$4,526,150** (+6.3% lift). Blended ROAS improves from **5.73x to 6.32x**.
- **Optimistic Scenario**: Portfolio revenue reaches **$4,641,813** (+9.0% lift). Blended ROAS improves to **6.48x**.
- **Capital Efficiency**: Reallocation actually reduces required gross spend by **$26,947**, leaving reserve budget for creative production.

---

## 3. Four Core Strategic Action Pillars

### Pillar 1: Shift to Data-Driven Attribution Governance
- **Deprecate Last-Click KPIs**: Cease evaluating channel managers on last-click conversions in weekly performance reviews.
- **Institutionalize Markov Removal Effects**: Adopt Markov weights as the executive source of truth:
  - Paid Search (0.4757 RE) and Email (0.4507 RE) are validated as non-negotiable closing and nurturing engines.
  - Organic Social (0.2887 RE) receives credit for **$641,298** in revenue, justifying dedicated investment in developer relations and technical content marketing.
- **Implement Position-Based (U-Shaped) as Operating Model**: For real-time bid adjustments, deploy a 40/20/40 position-based model that honors both discovery intent and closing velocity.

### Pillar 2: Paid Channel Optimization & Creative Hygiene
- **Prune High-CPC Display Campaigns**:
  - Cut `CMP-DP-01` (GDN Prospecting Banners) by 30%. Reallocate capital into High-Intent Brand and Competitor Search keywords (`CMP-PS-01` and `CMP-PS-03`).
- **Mitigate Paid Social Ad Fatigue**:
  - Implement a mandatory **14-day creative refresh cycle** for Meta Prospecting Video (`CMP-SO-01`).
  - Introduce dynamic video testimonials featuring alumni salary outcomes to combat click-through decay.
- **Strict Audience Exclusion Rules**:
  - Immediately suppress registered student emails (`user_id` in `conversions`) from all paid retargeting custom audiences to eliminate wasted ad spend on existing buyers.

### Pillar 3: Scale High-Leverage Nurturing & Advocacy
- **Expand Email Automation Infrastructure**:
  - With a 34.99x ROAS, email is severely underfunded relative to its revenue impact ($30.9k spend vs $1.08M revenue).
  - Deploy automated behavioral triggers based on student syllabus downloads, course preview interactions, and webinar attendance.
- **Gamify Alumni Referral Program (`CMP-RF-01`)**:
  - The Alumni Ambassador program generates a 5.22x ROAS with $176 CAC (well below the $873 AOV).
  - Increase referral incentives from $50 Amazon gift cards to $150 course tuition credits for existing students and alumni, expanding inventory without adding ad auction friction.

### Pillar 4: Advanced Analytics Engineering Roadmap
- **Marketing Mix Modeling (MMM)**: Implement open-source MMM (e.g. Google LightweightMMM or Meta Robyn) to measure cross-channel saturation curves and halo effects of un-tracked word-of-mouth.
- **First-Party Data Protection**: Implement Meta Conversions API (CAPI) and Google Enhanced Conversions to counter browser cookie deprecation and iOS privacy tracking restrictions.
- **Post-Enrollment CLV Expansion**: Build predictive churn and upsell models targeting Bootcamp graduates for advanced executive certifications, raising the repeat purchase factor from 1.25x to 1.45x.
