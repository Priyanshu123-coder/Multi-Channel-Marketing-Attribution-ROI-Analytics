# Marketing Attribution Methodology & Mathematical Framework

## 1. Executive Summary

Attribution modeling is the algorithmic process of assigning proportional credit (conversions and revenue) to marketing touchpoints encountered by prospective students throughout their decision journey. For **Grito Labs**, where education purchases require deep consideration ($299 to $1,299 course fees across 2 to 6 touchpoints over an average of 8 to 15 days), relying on a single heuristic (such as last-click) introduces severe strategic distortions.

This document details the mathematical formalization, weighting algorithms, edge-case protocols, and conservation laws for all six attribution models implemented in this framework.

---

## 2. Core Attribution Conservation Law

A foundational requirement of any mathematically valid attribution system is the **Attribution Conservation Law**. Credit cannot be artificially created or destroyed:

$$\sum_{c \in \text{Channels}} \text{Attributed Conversions}(c) = N_{\text{conversions}}$$

$$\sum_{c \in \text{Channels}} \text{Attributed Revenue}(c) = R_{\text{total}}$$

For every individual conversion event $k$ with gross revenue $R_k$ and a chronological sequence of $M_k$ pre-conversion touchpoints $(t_{k,1}, t_{k,2}, \dots, t_{k,M_k})$, the assigned weights $w_{k,j}$ across all touchpoints $j \in \{1, \dots, M_k\}$ must strictly satisfy:

$$\sum_{j=1}^{M_k} w_{k,j} = 1.0, \quad \forall w_{k,j} \ge 0$$

$$\text{Revenue Attribution: } R_{k,j} = w_{k,j} \times R_k$$

This property is verified automatically by our automated test suite (`tests/test_attribution.py`) to an absolute tolerance of $\epsilon < 10^{-4}$.

---

## 3. Heuristic Attribution Models

### 3.1 First-Touch Attribution (FTA)
Assigns 100% of the conversion and revenue credit to the earliest chronological touchpoint in the student's journey.

- **Weight Formula**:
  $$w_{k,j} = \begin{cases} 1.0 & \text{if } j = 1 \\ 0.0 & \text{if } j > 1 \end{cases}$$
- **Primary Use Case**: Top-of-funnel acquisition, brand awareness evaluation, discovery channel identification.
- **Biases**: Completely ignores all middle-funnel nurturing, email re-engagement, and closing campaigns.

### 3.2 Last-Touch Attribution (LTA)
Assigns 100% of the conversion and revenue credit to the final touchpoint occurring before the conversion event.

- **Weight Formula**:
  $$w_{k,j} = \begin{cases} 1.0 & \text{if } j = M_k \\ 0.0 & \text{if } j < M_k \end{cases}$$
- **Primary Use Case**: Direct-response closing efficiency, promotional flash sale effectiveness.
- **Biases**: Heavily over-credits branded search and automated retargeting/email workflows; severely discounts discovery channels (e.g. Organic Social and Display).

### 3.3 Linear Attribution
Distributes credit uniformly across all valid pre-conversion interactions.

- **Weight Formula**:
  $$w_{k,j} = \frac{1}{M_k}, \quad \forall j \in \{1, \dots, M_k\}$$
- **Primary Use Case**: Balanced baseline for multi-touch customer journeys.
- **Biases**: Assumes every interaction holds identical commercial influence regardless of depth, duration, or channel type.

### 3.4 Position-Based (U-Shaped) Attribution
Heuristically balances discovery and conversion by granting preferential weight to the introductory and concluding interactions, distributing the residual credit evenly among intermediate nurturing touchpoints.

- **Weight Formula**:
  - If $M_k = 1$: $w_{k,1} = 1.0$
  - If $M_k = 2$: $w_{k,1} = 0.50, \quad w_{k,2} = 0.50$
  - If $M_k > 2$:
    $$w_{k,1} = 0.40 \quad (\text{First Touch})$$
    $$w_{k,M_k} = 0.40 \quad (\text{Last Touch})$$
    $$w_{k,j} = \frac{0.20}{M_k - 2}, \quad \forall j \in \{2, \dots, M_k - 1\} \quad (\text{Middle Touches})$$
- **Primary Use Case**: High-consideration EdTech cycles where initiating discovery and sealing enrollment are the two hardest hurdles.

### 3.5 Time-Decay Attribution
Assigns exponentially increasing weight to touchpoints that occurred closer in time to the conversion event, reflecting diminishing cognitive relevance of distant past impressions.

- **Decay Formula** (Half-life $\lambda = 7.0$ days):
  $$\Delta t_{k,j} = \text{Time}(Conversion_k) - \text{Time}(Touchpoint_{k,j}) \quad (\text{in days})$$
  $$\tilde{w}_{k,j} = 2^{-\frac{\Delta t_{k,j}}{\lambda}} = \exp\left( - \frac{\ln(2) \cdot \Delta t_{k,j}}{\lambda} \right)$$
- **Normalization Step**:
  $$w_{k,j} = \frac{\tilde{w}_{k,j}}{\sum_{i=1}^{M_k} \tilde{w}_{k,i}}$$
- **Primary Use Case**: Short-lag promotional campaigns and rapid enrollment closing windows.

---

## 4. Data-Driven Attribution: Absorbing Markov Chains

To move beyond static heuristic rules, this framework implements an **Absorbing Markov Chain** that measures the empirical structural dependency of the conversion system on each channel via the **Removal Effect**.

### 4.1 State Space Formulation
The customer journey is modeled as a discrete stochastic process over states $S$:
$$S = \{ (Start) \} \cup C \cup \{ (Conversion), (Null) \}$$
where:
- $C = \{\text{Email}, \text{Paid Search}, \text{Paid Social}, \text{Organic Social}, \text{Display}, \text{Referral}\}$ represent transient marketing channel states.
- $(Start)$ is the transient entry state.
- $(Conversion)$ is an absorbing target state (terminal enrollment).
- $(Null)$ is an absorbing drop-off state (student disengagement / exit).

### 4.2 Transition Probability Matrix
For any pair of states $(i, j) \in S \times S$, the empirical transition probability is:
$$P(i, j) = \frac{N(i \to j)}{\sum_{s \in S} N(i \to s)}$$
The overall transition matrix $P$ is structured in canonical absorbing form:
$$P = \begin{pmatrix} Q & R \\ 0 & I \end{pmatrix}$$
where:
- $Q$ is a $|T| \times |T|$ matrix of transitions between transient states (Start and Channels).
- $R$ is a $|T| \times 2$ matrix of transitions from transient states to absorbing states (Conversion and Null).
- $I$ is a $2 \times 2$ identity matrix (absorbing self-loops).
- $0$ is a $2 \times |T|$ zero matrix.

### 4.3 Baseline Absorption Probability
Using the fundamental matrix $N$ of absorbing Markov chains:
$$N = (I - Q)^{-1} = \sum_{k=0}^{\infty} Q^k$$
The absorption probability matrix $B$ is:
$$B = N \cdot R$$
The baseline probability of starting at $(Start)$ and reaching $(Conversion)$ is given by:
$$P(\text{Conversion}) = B_{(Start), (Conversion)}$$

### 4.4 Channel Removal Effect & Weight Normalization
To measure the true marginal contribution of channel $c \in C$, we simulate its total removal from the ecosystem. In the modified transition matrix $P^{(-c)}$, all transitions into channel $c$ are rerouted to $(Null)$:
$$P^{(-c)}(i, Null) = P(i, Null) + P(i, c), \quad P^{(-c)}(i, c) = 0, \quad \forall i \in T$$
Recomputing the fundamental matrix yields the conditional conversion probability $P^{(-c)}(\text{Conversion})$.

The **Removal Effect ($RE_c$)** represents the relative drop in total conversions caused by eliminating channel $c$:
$$RE_c = \frac{P(\text{Conversion}) - P^{(-c)}(\text{Conversion})}{P(\text{Conversion})}$$

Normalizing across all channels produces the definitive Markov attribution share:
$$W_c^{\text{Markov}} = \frac{RE_c}{\sum_{k \in C} RE_k}$$

Attributed conversions and revenue are then:
$$\text{Attributed Conversions}(c) = W_c^{\text{Markov}} \times N_{\text{conversions}}$$
$$\text{Attributed Revenue}(c) = W_c^{\text{Markov}} \times R_{\text{total}}$$

---

## 5. Performance KPI Definitions & Formulations

| KPI Metric | Mathematical Formula | Business Purpose |
| :--- | :--- | :--- |
| **Conversion Rate (CR)** | $\frac{\text{Conversions}}{\text{Unique Visitors Reached}} \times 100$ | Measures overall visitor qualification and landing page resonance. |
| **Click-Through Rate (CTR)** | $\frac{\text{Clicks}}{\text{Impressions}} \times 100$ | Evaluates creative copy, ad relevance, and audience targeting. |
| **Cost Per Click (CPC)** | $\frac{\text{Total Ad Spend}}{\text{Total Clicks}}$ | Evaluates media buying efficiency and competitive auction pressure. |
| **Return On Ad Spend (ROAS)** | $\frac{\text{Attributed Revenue}}{\text{Ad Spend}}$ | Measures commercial return generated per marketing dollar invested. |
| **Customer Acquisition Cost (CAC)** | $\frac{\text{Ad Spend}}{\text{Attributed Conversions}}$ | Unit economic cost to acquire an active enrolled student. |
| **Average Order Value (AOV)** | $\frac{\text{Total Revenue}}{\text{Total Conversions}}$ | Revenue intensity per purchase event across course catalog. |
| **Customer Lifetime Value (CLV)** | $\text{AOV} \times \text{Repeat Multiplier} \times \text{Gross Margin}$ | Long-term commercial ceiling for sustainable acquisition CAC. |

---

## 6. Budget Reallocation Formulation

Let $S_c$ be current spend and $R_c$ be attributed revenue for channel $c$. The baseline ROAS is $\rho_c = R_c / S_c$.
When shifting budget by $\Delta S_c = \alpha_c S_c$:

1. **For Budget Cuts ($\alpha_c < 0$)**:
   $$\Delta R_c = \Delta S_c \times \rho_c$$
2. **For Budget Expansion ($\alpha_c > 0$)**:
   - **Conservative Case** (85% marginal efficiency factor $\eta = 0.85$ accounting for diminishing returns):
     $$\Delta R_c^{\text{cons}} = \Delta S_c \times \rho_c \times \eta$$
   - **Optimistic Case** (100% marginal efficiency $\eta = 1.00$):
     $$\Delta R_c^{\text{opt}} = \Delta S_c \times \rho_c$$

Net projected portfolio revenue:
$$R_{\text{projected}} = R_{\text{baseline}} + \sum_{c \in C} \Delta R_c$$
