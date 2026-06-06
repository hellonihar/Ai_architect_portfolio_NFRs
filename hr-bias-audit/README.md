# HR Bias Audit

**Automated bias detection & mitigation for AI-driven resume screening platforms.**

Demonstrates a Responsible AI pipeline that audits hiring decisions across **gender, ethnicity, and age** dimensions, computes statistical fairness metrics, and provides actionable remediation strategies — all through an interactive Streamlit dashboard.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Walkthrough](#usage-walkthrough)
- [Data Models](#data-models)
- [Bias Detection Methodology](#bias-detection-methodology)
- [Remediation Strategies](#remediation-strategies)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Map](#project-map)
- [Dependencies](#dependencies)

---

## Features

| Feature | Description |
|---|---|
| **Bias Audit Report** | Disparate impact ratio + chi-square significance for gender, ethnicity, and age groups |
| **What-If Simulator** | Interactive sliders to adjust pass thresholds and score boosts; re-runs audit in real time |
| **Remediation Planner** | Side-by-side comparison of blind screening, weight recalibration, and human-in-the-loop review |
| **Compliance Dashboard** | Maps audit results to EEOC, GDPR Art. 22, NYC Local Law 144, and EU AI Act |
| **Resume Ingestion** | Parses plain text, PDF, and DOCX resumes; extracts demographic signals from text |
| **Demo Data Generator** | Generates 250 realistic resumes with controlled bias patterns for testing |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                        │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ ┌───────┐ │
│  │  Demo   │ │  Bias    │ │  What-If │ │Remedia│ │Comply │ │
│  │Overview │ │  Report  │ │Simulator │ │Planner│ │-iance │ │
│  └─────────┘ └──────────┘ └──────────┘ └───────┘ └───────┘ │
├──────────────────────────────────────────────────────────────┤
│                   Analysis Layer                              │
│  ┌──────────────┐ ┌────────────────┐ ┌───────────────────┐  │
│  │ BiasEngine   │ │FairnessMetrics │ │ DemographicParser │  │
│  │ (audit pipe) │ │ (DI, chi-sq)   │ │ (text signals)   │  │
│  └──────────────┘ └────────────────┘ └───────────────────┘  │
│  ┌────────────────┐ ┌────────────────────────────────────┐   │
│  │  Remediation   │ │  Demo Data Generator               │   │
│  │  (strategies)  │ │  (250 profiles, controlled bias)   │   │
│  └────────────────┘ └────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│                    Models Layer                               │
│  ┌──────────────────────┐  ┌──────────────────────────────┐  │
│  │   ResumeProfile      │  │  AuditResult / BiasScore     │  │
│  │   (pydantic)         │  │  (pydantic)                  │  │
│  └──────────────────────┘  └──────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│                    Ingestion Layer                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ResumeParser (.txt / .pdf / .docx → ResumeProfile) │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Key Modules

```
src/hr_bias_audit/
├── analysis/           # Core business logic
│   ├── bias_engine.py      # Orchestrates audit pipeline
│   ├── fairness_metrics.py # Disparate impact, chi-square
│   ├── demographic_parser.py # Text-based demographic inference
│   ├── remediation.py     # Mitigation strategy implementations
│   ├── sample_data.py     # 8-profile hand-crafted sample
│   └── demo_data.py       # 250-profile synthetic data generator
├── models/             # Pydantic data models
│   ├── resume.py          # ResumeProfile
│   └── audit_result.py    # AuditResult, BiasScore, GroupMetric
├── ingest/             # Resume file parsers
│   └── resume_parser.py   # .txt/.pdf/.docx extraction
├── ui/                 # Streamlit frontend
│   ├── dashboard.py       # Main entry point & sidebar
│   ├── pages/             # Tab content pages
│   │   ├── demo_landing.py
│   │   ├── bias_report.py
│   │   ├── what_if.py
│   │   ├── remediation.py
│   │   ├── resume_view.py
│   │   └── compliance.py
│   └── components/        # Reusable UI widgets
│       ├── charts.py      # Plotly chart helpers
│       └── metrics.py     # Metric cards & severity badges
└── config.py           # Application settings
```

---

## Installation

### Prerequisites

- Python 3.11+ (managed via `uv`)
- [`uv`](https://docs.astral.sh/uv/) — fast Python package manager

### Setup

```powershell
# Clone or navigate to the project directory
cd hr-bias-audit

# Create virtual environment and install all dependencies
uv sync

# (Optional) Install the package in editable mode for development
uv pip install -e .
```

All dependencies (Streamlit, pandas, scikit-learn, plotly, PyPDF2, python-docx, pydantic, etc.) are declared in `pyproject.toml` and are installed automatically by `uv sync`.

---

## Running the Application

### Quick start

```powershell
# Using the convenience script:
.\scripts\run.ps1

# Or manually:
uv run streamlit run src/hr_bias_audit/ui/dashboard.py
```

This starts the Streamlit dev server (default: `http://localhost:8501`). Open the URL in your browser.

### Getting started with demo data

1. Open the app in your browser
2. In the **sidebar**, click one of:
   - **"Load 8-profile sample"** — small hand-crafted dataset with known bias patterns
   - **"Load 250-profile demo (biased)"** — synthetic dataset with controlled bias (bias_scale=1.0)
   - **"Load 250-profile demo (fair)"** — same generator, bias_scale=0.0, for comparison
3. Navigate the tabs to explore results

### Uploading real resumes

1. In the sidebar, use the file uploader to select `.txt`, `.pdf`, or `.docx` files
2. Click **"Run Bias Audit"**
3. The app parses each file, infers demographic signals, computes screening scores (placeholder), and runs the full audit

---

## Usage Walkthrough

### 1. Demo Overview (🏠 tab)

Landing page with key KPIs (applicants processed, pass rate, bias flags, compliance status) and a description of each use case.

### 2. Bias Audit Report (📊 tab)

The core audit output. Displays:

- **Summary metrics**: total applicants, pass rate, bias flag count
- **Per-dimension expanders**: for gender, ethnicity, and age, showing:
  - **Disparate Impact (DI) Ratio** — ratio of the lowest to highest group pass rate
  - **p-value** from chi-square test of independence
  - **Severity badge** (HIGH / MEDIUM / LOW)
  - **Recommendation** text
  - **Group-level breakdown table** (applicants, pass rate, avg score per group)
- **Charts**:
  - Pass rate by demographic group (grouped bar chart)
  - Disparate impact ratio with threshold lines (0.8 = EEOC threshold, 1.0 = parity)

### 3. What-If Simulator (🔍 tab)

Interactive exploration tool:

- **Pass/Fail Threshold** slider — adjust the cutoff score (default 0.5)
- **Equity Adjustment sliders** — apply score boosts (positive or negative) per group:
  - Female boost
  - Under-30 boost
  - Over-50 boost
  - Diverse signal boost
- Results update in real time as sliders move:
  - Pass rate, bias flags, per-dimension DI ratios
  - Group-level detail tables
  - Charts: pass rates, DI ratios, score distributions

This answers questions like:
- *"What if we raise the bar to 0.6?"*
- *"What score boost for under-represented groups achieves DI ratio ≥ 0.8?"*

### 4. Remediation Planner (🛠️ tab)

Compares four strategies side by side:

| Strategy | Description |
|---|---|
| **Baseline** | Current state with no intervention |
| **Blind Screening** | Strips all demographic signals (gender, age, ethnicity set to "unknown") before scoring |
| **Weight Recalibration** | Applies score boosts: +0.10 for female, +0.08 for under_30, +0.05 for over_50, +0.10 for diverse ethnicity signals |
| **Human-in-the-Loop** | Flags borderline candidates (within 10% of threshold) for manual review; those candidates pass |

Each strategy tab shows:
- Passed count, pass rate, bias flags
- Per-dimension DI ratio, p-value, severity, and recommendation

A side-by-side bar chart compares DI ratios across strategies, and a recommended action plan is generated based on results.

### 5. Resume View (📄 tab)

Consolidated table of all group-level metrics across dimensions: group name, applicant count, pass rate, average score.

### 6. Compliance (🔒 tab)

Maps bias audit results to regulatory frameworks:

- **EEOC Uniform Guidelines** — DI ratio ≥ 0.8 threshold
- **GDPR Art. 22** — automated decision-making explainability
- **NYC Local Law 144** — annual bias audit requirement
- **EU AI Act (high-risk)** — conformity assessment, human oversight

Each regulation shows a compliance status (✅ Compliant / ⚠️ Needs Review) based on current audit results. Remediation actions are listed for reference.

---

## Data Models

### ResumeProfile

Defined in `src/hr_bias_audit/models/resume.py`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier (UUID) |
| `name` | `str` | Candidate name (from filename or parsed) |
| `email` | `str` | Extracted email address |
| `raw_text` | `str` | Full resume text content |
| `inferred_gender` | `Optional[str]` | "male", "female", or "unknown" |
| `inferred_age_group` | `Optional[str]` | "under_30", "30_50", "over_50", or "unknown" |
| `inferred_ethnicity` | `Optional[str]` | "hispanic", "asian", "diverse_signal", or "unknown" |
| `education` | `list[str]` | Extracted education entries |
| `skills` | `list[str]` | Extracted skill keywords |
| `years_experience` | `float` | Estimated years of experience |
| `screening_score` | `float` | Numerical screening score (0.0–1.0) |
| `passed_screen` | `bool` | Whether candidate passed screening (`score >= threshold`) |
| `source` | `str` | File path or data source identifier |

### AuditResult

Defined in `src/hr_bias_audit/models/audit_result.py`

| Field | Type | Description |
|---|---|---|
| `total_applicants` | `int` | Number of resumes analysed |
| `total_passed` | `int` | Number that passed screening |
| `overall_pass_rate` | `float` | `total_passed / total_applicants` |
| `bias_scores` | `list[BiasScore]` | One entry per bias dimension |
| `audit_timestamp` | `str` | ISO 8601 timestamp of the audit run |

### BiasScore

| Field | Type | Description |
|---|---|---|
| `dimension` | `BiasDimension` | `gender`, `ethnicity`, or `age` |
| `disparate_impact_ratio` | `float` | Ratio of lowest to highest group pass rate |
| `statistical_significance` | `float` | p-value from chi-square test |
| `is_biased` | `bool` | `True` if `DI < 0.8` or `p < 0.05` |
| `severity` | `str` | `"high"` (DI<0.5), `"medium"` (DI<0.8), `"low"` |
| `recommendation` | `str` | Human-readable action text |
| `group_metrics` | `list[GroupMetric]` | Per-group breakdown |

---

## Bias Detection Methodology

### Demographic Inference

Demographic signals are inferred from resume text using heuristic keyword matching (see `DemographicParser` in `analysis/demographic_parser.py`):

- **Gender**: pronoun counts ("he/him/his" → male, "she/her/hers" → female)
- **Age group**: experience keywords ("internship/entry-level" → under_30, "senior/manager/lead" → 30_50, "executive/VP/chief" → over_50)
- **Ethnicity signal**: presence of diversity-related language ("pronouns", "diverse", "minority", "women in tech", "underrepresented")
- **Ethnicity hint (demo data only)**: last-name-based heuristics (Garcia → hispanic, Nguyen → asian)

> **Important**: These are *simulated* inferences for demo purposes. A production system would use more sophisticated methods or rely on self-reported data.

### Fairness Metrics

Computed by `FairnessMetrics` in `analysis/fairness_metrics.py`:

**Disparate Impact Ratio (DIR)**

```
DIR = pass_rate(unprivileged) / pass_rate(privileged)
```

- DIR ≥ 0.8: generally considered fair (EEOC *Four-Fifths Rule*)
- DIR < 0.8: potential adverse impact
- DIR < 0.5: high-severity bias

**Chi-Square Test of Independence**

Tests whether pass/fail outcomes are independent of group membership:
- **p < 0.05**: statistically significant association between group and outcome
- **p ≥ 0.05**: no significant association detected

### Bias Classification

A dimension is flagged as **biased** if:
- `DIR < 0.8` (adverse impact), **OR**
- `p-value < 0.05` (statistical significance), **OR** both

---

## Remediation Strategies

Implemented in `analysis/remediation.py`:

### 1. Blind Screening
Strips all demographic fields (`inferred_gender`, `inferred_age_group`, `inferred_ethnicity`) to `"unknown"` before the audit. This simulates removing demographic information from the review process so the screener cannot discriminate even unconsciously.

### 2. Weight Recalibration
Applies score boosts to underrepresented groups to compensate for systemic disadvantages:
- Female candidates: +0.10 to score
- Under-30 candidates: +0.08
- Over-50 candidates: +0.05
- Diverse ethnicity signals: +0.10

The adjusted score is capped at 0.98.

### 3. Human-in-the-Loop Review
Candidates whose score falls within 10% of the pass threshold (e.g., 0.40–0.49 for threshold 0.5) are automatically flagged for manual human review and are considered passing. This reduces false rejections for borderline candidates.

---

## Configuration

`src/hr_bias_audit/config.py`:

```python
class Settings(BaseModel):
    app_name: str = "HR Bias Audit"
    debug: bool = False
    bias_threshold: float = 0.8   # EEOC four-fifths rule threshold
```

Settings are accessed via the singleton `settings` object. Extend as needed (e.g., `HR_BIAS_*` environment variable support can be added by switching to `pydantic-settings`).

---

## Testing

```powershell
# Run all tests
uv run pytest tests/ -v

# Run with coverage (if pytest-cov is installed)
uv run pytest tests/ --cov=src/hr_bias_audit --cov-report=term-missing
```

### Test suite

| Test | Description |
|---|---|
| `test_audit_empty` | Audit of an empty list returns zero counts |
| `test_audit_all_pass_same_group` | Homogeneous group with all passing produces no bias flags |
| `test_audit_detects_disparity` | Deliberately biased data (male high scores, female low scores) is correctly flagged |

---

## Project Map

```
hr-bias-audit/
├── .python-version                   # Python 3.12
├── pyproject.toml                    # Project metadata & dependencies (uv)
├── uv.lock                           # Locked dependency versions
├── README.md
├── scripts/
│   └── run.ps1                       # Launch script
├── src/
│   ├── data/                         # Uploaded resume storage
│   └── hr_bias_audit/
│       ├── __init__.py
│       ├── config.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── bias_engine.py
│       │   ├── demographic_parser.py
│       │   ├── demo_data.py
│       │   ├── fairness_metrics.py
│       │   ├── remediation.py
│       │   └── sample_data.py
│       ├── ingest/
│       │   ├── __init__.py
│       │   └── resume_parser.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── audit_result.py
│       │   └── resume.py
│       └── ui/
│           ├── __init__.py
│           ├── dashboard.py
│           ├── components/
│           │   ├── __init__.py
│           │   ├── charts.py
│           │   └── metrics.py
│           └── pages/
│               ├── __init__.py
│               ├── bias_report.py
│               ├── compliance.py
│               ├── demo_landing.py
│               ├── remediation.py
│               ├── resume_view.py
│               └── what_if.py
└── tests/
    ├── __init__.py
    └── test_bias_engine.py
```

---

## Dependencies

All managed by `uv` via `pyproject.toml`:

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.40 | Interactive web dashboard |
| `pandas` | ≥2.2 | Data manipulation & group-by operations |
| `numpy` | ≥1.26 | Numerical computations |
| `plotly` | ≥5.24 | Interactive charts (bar, scatter, annotations) |
| `scikit-learn` | ≥1.6 | Statistical utilities |
| `scipy` | *(transitive)* | Chi-square contingency test |
| `spacy` | ≥3.8 | NLP pipeline (extensible; not currently used in core pipeline) |
| `python-docx` | ≥1.1 | .docx resume parsing |
| `PyPDF2` | ≥3.0 | .pdf resume parsing |
| `pydantic` | ≥2.10 | Data models with validation |
| `pytest` | ≥8.0 *(dev)* | Test runner |

---

## License

For demonstration and educational purposes. Not intended for production use without further validation of demographic inference methods and fairness thresholds.
