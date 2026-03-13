# 📘 Step C – Storytelling Framework (Re-Structured Version)

## 1Executive Objective

### Why Step C Needs Restructuring

The existing workflow:

**Statistic Analysis (e.g. Correlation / Lead / Lag)  → Backtest → Strategy**

is technically sound but lacks economic narrative coherence.

The new objective is:

**Economic Structure → Indicator Meaning → Evidence → Identity → Strategy**

Step C must evolve from a data-display dashboard into an **Investment Thesis Generator**.

---

## 2 Core Philosophy: Narrative-Driven Architecture

An indicator study should follow a three-act structure:

###  Act 1 – Economic Thesis (Why Should I Care?)

Each indicator must answer:

- What economic phenomenon does it represent?
- Through what transmission mechanism does it affect markets?
- Does it influence direction, volatility, or regime?
- Which asset classes should theoretically be affected?

**Output:**  
→ **Economic Thesis Card**

This prevents the dashboard from becoming a pure data container.

*Step C - Story Telling Framework*

---

### Act 2 – Empirical Validation (Does It Actually Work?)

Research must test:

- Structural relationship (correlation)
- Stability (rolling)
- Predictive nature (Granger, lead-lag)
- Nonlinearity (threshold, Z-score)
- Dynamic impact (VAR, IRF, FEVD)

**Output:**  
→ **Evidence Profile**

This is the validation and conflict stage.

---

### Act 3 – Indicator Identity (What Is It Really?)

Based on Act 1 + Act 2, classify indicator into:

- **Alpha Generator**
- **Risk Overlay**
- **Regime Filter**
- **No Material Value**

**Output:**  
→ **Indicator Identity Panel**

This is the core narrative bridge between research and strategy.

---

## 3 Dashboard Layering Architecture

Step C Dashboard should contain three structural layers:

###  Layer 1 – Narrative Layer (User Reasoning Flow)

User flow must guide reasoning:

1. Why This Indicator Matters  
2. What Data Says  
3. What Its Identity Is  
4. How To Use It  

The goal is not more charts.  
The goal is: **User understands what judgment is being made.**

---

###  Layer 2 – Strategy Layer (Constrained Sandbox)

Sandbox is **NOT** Act 3.  
Sandbox is: **Validation engine for Act 3.**

| Identity        | Allowed Modes                                      |
|----------------|-----------------------------------------------------|
| Risk Overlay   | Only Defensive / Exposure Reduction modes allowed   |
| Alpha          | Tactical strategies allowed                         |
| Regime Filter  | Allocation tilt strategies allowed                  |

This is called: **Constrained Strategy Design** (not brute force search).

---

### Layer 3 – Investment Application Layer

**Indicator → Asset Mapping** must be explicit.

Example mapping:

| Indicator Type | Affected Assets              |
|----------------|------------------------------|
| Credit Spread  | Equity, HY, Financials       |
| Yield Curve    | Banks, Small Caps            |
| Inflation      | Commodities, TIPS            |
| Volatility     | Equity Beta                  |

Each study must specify:

- **Primary ETF**
- **Secondary ETF**
- **Minimal Impact ETF**

This reconnects research to asset allocation.

---

## 4 Claude Multi-Agent Architecture

To operationalize this framework, Claude Agents should be structured as:

### Economist Agent (Act 1)

**Responsible for:**

- Economic definition
- Transmission mechanism
- Asset class mapping
- Theoretical implication

**Output:** → Indicator Thesis Card

---

### Research Agents (Act 2)

**Responsible for:**

- Correlation
- Rolling
- Lead-lag
- Granger
- Threshold
- VAR / FEVD

**Output:** → Evidence Profile

---

### Evaluator Agent

**Responsible for:**

- Reject low sample size
- Reject unstable strategies
- Generate ranking table
- Flag overfitting

---

### Strategy Agent

**Responsible for:**

- Strategy Constraint Engine
- Allowed transformation filtering
- Allowed threshold filtering
- Allowed position logic filtering

---

## 5 Strategic Design Principles

1. Research must **not** precede economic thesis.  
2. Strategy must **not** ignore indicator identity.  
3. Sandbox must be **constrained by identity**.  
4. Asset mapping must reconnect to **Investment Clock** objective.  
5. Dashboard must **guide reasoning**, not only display output.

---

## 6 Long-Term Vision

Step C becomes:

**Investment Thesis Factory**

*not*

**Backtest Result Factory.**

---

## 7 What This Restructure Solves

- Fixes Layer 1 & Layer 2 disconnect  
- Introduces storytelling coherence  
- Improves user interpretability  
- Reduces overfitting risk  
- Aligns with asset allocation objective  
