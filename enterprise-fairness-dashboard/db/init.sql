CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS loan_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id VARCHAR(50) NOT NULL,
    gender VARCHAR(20),
    age INT,
    income DECIMAL(12,2),
    region VARCHAR(100),
    loan_amount DECIMAL(12,2),
    loan_purpose VARCHAR(100),
    approved BOOLEAN,
    decision_date TIMESTAMP DEFAULT NOW(),
    risk_score DECIMAL(5,2),
    actual_default BOOLEAN,
    predicted_default BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fairness_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,6) NOT NULL,
    group_a VARCHAR(100),
    group_b VARCHAR(100),
    threshold DECIMAL(10,6),
    passed BOOLEAN,
    computed_at TIMESTAMP DEFAULT NOW(),
    batch_id VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS bias_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('Review', 'Investigate', 'Escalate')),
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'Acknowledged', 'Resolved')),
    dimension VARCHAR(50),
    affected_group VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,6),
    threshold DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS demographic_parity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_name VARCHAR(100) NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    approval_rate DECIMAL(5,2),
    total_applications INT,
    approved_count INT,
    parity_threshold DECIMAL(5,2),
    below_threshold BOOLEAN,
    computed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compliance_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    badge_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Passed', 'Failed', 'Pending', 'In Progress')),
    description TEXT,
    last_audit_date TIMESTAMP,
    next_audit_date TIMESTAMP,
    evidence_url TEXT,
    requires_retraining BOOLEAN DEFAULT FALSE,
    retraining_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Cancelled')),
    alert_id UUID REFERENCES bias_alerts(id),
    assigned_to VARCHAR(100),
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_loan_applications_gender ON loan_applications(gender);
CREATE INDEX idx_loan_applications_region ON loan_applications(region);
CREATE INDEX idx_fairness_metrics_name ON fairness_metrics(metric_name);
CREATE INDEX idx_bias_alerts_severity ON bias_alerts(severity);
CREATE INDEX idx_bias_alerts_status ON bias_alerts(status);
CREATE INDEX idx_demographic_parity_dimension ON demographic_parity(dimension);
