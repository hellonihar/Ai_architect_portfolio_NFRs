# AI Architect Portfolio — Non-Functional Requirements for AI Systems

A portfolio demonstrating how **Non-Functional Requirements (NFRs)** shape the architecture, design, and operation of AI systems in production.

---

## Why NFRs Matter for AI Systems

Non-Functional Requirements define *how* an AI system behaves, not just *what* it does. In AI/ML systems, NFRs are especially critical because model behavior is probabilistic, data-dependent, and often opaque.

### Key NFR Dimensions for AI

| NFR | Why It Matters for AI |
|-----|-----------------------|
| **Fairness & Bias** | Models can amplify historical biases. Without explicit fairness constraints, automated decisions may discriminate against protected groups. Requires continuous auditing, disparate impact analysis, and remediation strategies. |
| **Explainability** | Regulations (GDPR Art. 22, NYC Local Law 144, EU AI Act) grant individuals the right to understand automated decisions. Black-box models need surrogate explainers, feature attribution, or inherently interpretable designs. |
| **Reliability** | AI systems degrade gracefully. Data drift, concept drift, and distribution shifts must be monitored. Confidence calibration, fallback logic, and human-in-the-loop thresholds maintain reliability. |
| **Security & Robustness** | Models are vulnerable to adversarial inputs, prompt injection, and data poisoning. Secure pipelines, input sanitization, and adversarial training are architectural requirements. |
| **Performance & Scalability** | Inference latency, throughput, and cost vary with model size, hardware, and batching strategy. Trade-offs between accuracy and speed must be architected upfront. |
| **Privacy** | Models can memorize training data. Differential privacy, data minimization, and on-device inference protect user data. Compliance with GDPR, CCPA, and other frameworks is non-negotiable. |
| **Observability** | ML systems fail differently than traditional software. Drift detection, model logging, performance monitoring, and alerting pipelines are first-class architectural components. |
| **Governance** | Model versioning, approval gates, audit trails, and rollback capabilities are required for regulated environments. ML pipelines must support lineage tracking and reproducibility. |

### Architectural Implications

- NFRs drive **technology choices** (interpretable models vs. black-box, batch vs. real-time inference)
- NFRs define **pipeline topology** (where human review gates, drift detectors, and audit checkpoints live)
- NFRs determine **deployment strategy** (shadow mode, canary releases, A/B evaluation before full rollout)
- NFRs influence **data architecture** (feature stores, labeling pipelines, consent management)

---

## Portfolio Projects

| Project | NFR Focus | Tech Stack |
|---------|-----------|------------|
| [HR Bias Audit](./hr-bias-audit) | Fairness, Explainability, Compliance | Python, Streamlit, pandas, scikit-learn, Plotly |
| *(more coming)* | | |

---

## Repository Structure

```
Ai_architect_portfolio_NFRs/
├── README.md
└── hr-bias-audit/       # Bias detection & mitigation platform
    ├── implementationplan.md
    ├── src/
    └── tests/
```
