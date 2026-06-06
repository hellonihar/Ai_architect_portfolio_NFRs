# Implementation Plan: HR Bias Audit

## Overview
Automated bias detection & mitigation for AI-driven resume screening. Streamlit dashboard + Python analysis pipeline.

---

## Phase 1 — Project Scaffold

### Step 1.1 — Repository structure
```
hr-bias-audit/
├── pyproject.toml              # uv-managed deps & metadata
├── .python-version             # 3.12
├── README.md
├── scripts/
│   └── run.ps1                 # uv sync && uv run streamlit run ...
├── src/
│   └── hr_bias_audit/
│       ├── __init__.py
│       ├── config.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── bias_engine.py         # Orchestrates audit pipeline
│       │   ├── fairness_metrics.py    # DI ratio, chi-square
│       │   ├── demographic_parser.py  # Text-based demographic inference
│       │   ├── remediation.py         # Mitigation strategies
│       │   ├── demo_data.py           # 250-profile synthetic generator
│       │   └── sample_data.py         # 8-profile hand-crafted sample
│       ├── ingest/
│       │   ├── __init__.py
│       │   └── resume_parser.py       # .txt / .pdf / .docx → ResumeProfile
│       ├── models/
│       │   ├── __init__.py
│       │   ├── resume.py              # ResumeProfile (pydantic)
│       │   └── audit_result.py        # AuditResult, BiasScore, etc.
│       └── ui/
│           ├── __init__.py
│           ├── dashboard.py           # Main entry + sidebar
│           ├── components/
│           │   ├── __init__.py
│           │   ├── charts.py          # Plotly chart helpers
│           │   └── metrics.py         # Metric cards + severity badges
│           └── pages/
│               ├── __init__.py
│               ├── demo_landing.py    # KPI overview
│               ├── bias_report.py     # Audit report tab
│               ├── what_if.py         # Interactive simulator
│               ├── remediation.py     # Strategy comparison
│               ├── resume_view.py     # Group metrics table
│               └── compliance.py      # Regulatory mapping
└── tests/
    ├── __init__.py
    └── test_bias_engine.py
```

### Step 1.2 — pyproject.toml
- Declare name, version, python version (>=3.11)
- Dependencies: streamlit, pandas, numpy, plotly, scikit-learn, spacy, python-docx, PyPDF2, pydantic
- Dev dependencies: pytest
- Build system: hatchling

### Step 1.3 — uv lock & venv
```powershell
cd hr-bias-audit
uv sync
```

---

## Phase 2 — Data Models (`models/`)

### Step 2.1 — ResumeProfile (models/resume.py)
Fields:
- `id: str` — UUID
- `name: str` — extracted name / filename
- `email: str` — extracted email
- `raw_text: str` — full resume text
- `inferred_gender: Optional[str]` — "male" / "female" / "unknown"
- `inferred_age_group: Optional[str]` — "under_30" / "30_50" / "over_50" / "unknown"
- `inferred_ethnicity: Optional[str]` — "hispanic" / "asian" / "diverse_signal" / "unknown"
- `education: list[str]`
- `skills: list[str]`
- `years_experience: float`
- `screening_score: float` — 0.0–1.0
- `passed_screen: bool`
- `source: str`

### Step 2.2 — AuditResult & supporting types (models/audit_result.py)
- `BiasDimension(str, Enum)` — GENDER, ETHNICITY, AGE
- `GroupMetric` — group, applicant_count, pass_rate, avg_score, std_score
- `BiasScore` — dimension, disparate_impact_ratio, statistical_significance, is_biased, severity, recommendation, group_metrics
- `AuditResult` — total_applicants, total_passed, overall_pass_rate, bias_scores, audit_timestamp
- `BiasReport` — title, summary, audit, compliance_status, remediation_actions

---

## Phase 3 — Configuration (`config.py`)

### Step 3.1 — Settings pydantic model
```python
class Settings(BaseModel):
    app_name: str = "HR Bias Audit"
    debug: bool = False
    bias_threshold: float = 0.8  # EEOC four-fifths rule

settings = Settings()  # singleton
```

---

## Phase 4 — Analysis Layer (`analysis/`)

### Step 4.1 — DemographicParser (analysis/demographic_parser.py)
- `infer_gender(resume)` — count "he/him/his/mr." vs "she/her/hers/ms./mrs."
- `infer_age_group(resume)` — keyword matching for under_30 (internship, entry-level, junior), 30_50 (senior, lead, manager), over_50 (executive, VP, chief)
- `infer_ethnicity(resume)` — check for diversity signal keywords (pronouns, diverse, minority, women in tech, underrepresented)
- `enrich(resume)` — calls all three and returns updated ResumeProfile

### Step 4.2 — FairnessMetrics (analysis/fairness_metrics.py)
- `disparate_impact_ratio(privileged_pass_rate, unprivileged_pass_rate)` — ratio of lowest to highest pass rate
- `chi_square_p_value(group_labels, pass_flags)` — chi-square test of independence via scipy
- `compute_group_metrics(groups, scores, pass_flags)` — groupby into list[GroupMetric]

### Step 4.3 — BiasEngine (analysis/bias_engine.py)
- For each BiasDimension (gender, ethnicity, age):
  1. Extract group labels and pass flags from profiles
  2. Compute per-group metrics
  3. Find privileged/unprivileged group pass rates (ignore "unknown")
  4. Compute DI ratio and chi-square p-value
  5. Determine severity: high (DI<0.5), medium (DI<0.8), low
  6. Build recommendation text
- `audit(profiles)` → AuditResult (or empty result for empty list)

### Step 4.4 — Remediation Strategies (analysis/remediation.py)
- `apply_blind_screening(profiles)` — set all demographic fields to "unknown"
- `apply_weight_recalibration(profiles, boost_factors)` — add boosts: female +0.10, under_30 +0.08, over_50 +0.05, diverse +0.10 (cap at 0.98)
- `apply_human_review(profiles, review_margin=0.10)` — borderline candidates within 10% of threshold auto-pass
- `compare_strategies(original, threshold)` → dict of strategy_name → AuditResult

### Step 4.5 — Sample Data (analysis/sample_data.py)
- 8 hard-coded ResumeProfile entries with known bias patterns
  3 female (2 under_30, low scores), 5 male (mostly high scores)

### Step 4.6 — Demo Data Generator (analysis/demo_data.py)
- Name pools: 30 male + 30 female first names, 50 last names
- `_last_name_ethnicity_hint(last)` → hispanic/asian/unknown
- `_generate_text(gender, age_group, dept)` → realistic resume text
- `_compute_score(gender, age_group, ethnicity, dept, bias_scale)` — base gaussian + penalty for female/under_30/over_50/diverse when bias_scale > 0
- `generate(batch_size=250, bias_scale=1.0)` → list[ResumeProfile] with reproducible seed 42

---

## Phase 5 — Ingestion Layer (`ingest/`)

### Step 5.1 — ResumeParser (ingest/resume_parser.py)
- `extract_text(filepath)` — read .txt directly, .pdf via PyPDF2, .docx via python-docx
- `parse(filepath)` — extract text + email regex → ResumeProfile (no demographics yet)

---

## Phase 6 — UI Components (`ui/components/`)

### Step 6.1 — Charts (ui/components/charts.py)
- `pass_rate_by_group_chart(bias_scores)` → grouped Plotly bar chart
- `disparate_impact_chart(bias_scores)` → bar chart with threshold lines at 0.8 (red dashed) and 1.0 (green dotted)
- `score_distribution_chart(bias_scores)` → grouped bar of avg scores

### Step 6.2 — Metrics (ui/components/metrics.py)
- `metric_card(label, value, delta, color)` → HTML-styled card with colored background
- `severity_badge(severity)` → inline colored badge (green/orange/red)

---

## Phase 7 — UI Pages (`ui/pages/`)

### Step 7.1 — Demo Landing (ui/pages/demo_landing.py)
- KPIs: applicants processed, pass rate, bias flags, compliance status
- Use case descriptions with icons
- "How it works" caption

### Step 7.2 — Bias Report (ui/pages/bias_report.py)
- Summary metrics row (total, passed, pass rate, flags)
- Per-dimension expander with severity badge, p-value, recommendation, group breakdown table
- Charts: pass rate by group, disparate impact ratio

### Step 7.3 — What-If Simulator (ui/pages/what_if.py)
- Pass/fail threshold slider (0.0–1.0, default 0.5)
- Equity adjustment sliders: female boost, under-30 boost, over-50 boost, diverse signal boost (-0.2 to +0.3)
- Real-time simulation results (same layout as Bias Report)
- Three charts: pass rate, DI ratio, score distribution

### Step 7.4 — Remediation Planner (ui/pages/remediation.py)
- Threshold slider
- Runs compare_strategies() for Baseline, Blind Screening, Weight Recalibration, Human-in-the-Loop
- Tab per strategy showing pass rate, bias flags, per-dimension details
- Side-by-side DI ratio comparison bar chart
- Recommended action plan (conditional on baseline bias)

### Step 7.5 — Resume View (ui/pages/resume_view.py)
- Consolidated table: Dimension | Group | Applicants | Pass Rate | Avg Score

### Step 7.6 — Compliance (ui/pages/compliance.py)
- Warning banners for each biased dimension
- Regulatory checklist: EEOC, GDPR Art. 22, NYC Local Law 144, EU AI Act
- Remediation actions list

---

## Phase 8 — Dashboard Entry Point (`ui/dashboard.py`)

### Step 8.1 — Session state
- `st.session_state.audit_result` — default empty AuditResult
- `st.session_state.profiles` — default []

### Step 8.2 — Sidebar
- File uploader (.txt, .pdf, .docx)
- "Run Bias Audit" button: parse → score (placeholder 0.5) → enrich demographics → audit
- Sample data buttons: 8-profile sample, 250 biased, 250 fair

### Step 8.3 — Tab layout
Six tabs: 🏠 Demo Overview, 📊 Bias Audit Report, 🔍 What-If Simulator, 🛠️ Remediation Planner, 📄 Resume View, 🔒 Compliance

---

## Phase 9 — Testing (`tests/`)

### Step 9.1 — test_bias_engine.py
- `test_audit_empty` — empty list → zero counts
- `test_audit_all_pass_same_group` — homogeneous group → no bias flags
- `test_audit_detects_disparity` — male-high-scores vs female-low-scores → bias detected

Run with:
```powershell
uv run pytest tests/ -v
```

---

## Phase 10 — Launch

### Step 10.1 — scripts/run.ps1
```powershell
uv sync
uv run streamlit run src/hr_bias_audit/ui/dashboard.py
```

### Step 10.2 — Start
```powershell
.\scripts\run.ps1
```
Opens at `http://localhost:8501`

---

## Implementation Order Summary

| Order | Phase | Estimated Effort |
|-------|-------|------------------|
| 1 | Project scaffold + pyproject.toml | Small |
| 2 | Pydantic models (resume.py, audit_result.py) | Small |
| 3 | Config (config.py) | Tiny |
| 4 | DemographicParser | Small |
| 5 | FairnessMetrics | Small |
| 6 | BiasEngine | Medium |
| 7 | Remediation strategies | Medium |
| 8 | Sample + demo data | Medium |
| 9 | ResumeParser | Small |
| 10 | UI charts + metrics components | Small |
| 11 | UI pages (all 6) | Large |
| 12 | Dashboard entry point | Medium |
| 13 | Tests | Small |
| 14 | run.ps1 + smoke test | Tiny |
