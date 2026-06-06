from pydantic import BaseModel
from enum import Enum


class BiasDimension(str, Enum):
    GENDER = "gender"
    ETHNICITY = "ethnicity"
    AGE = "age"


class GroupMetric(BaseModel):
    group: str
    applicant_count: int
    pass_rate: float
    avg_score: float
    std_score: float


class BiasScore(BaseModel):
    dimension: BiasDimension
    disparate_impact_ratio: float
    statistical_significance: float
    is_biased: bool
    severity: str
    recommendation: str
    group_metrics: list[GroupMetric]


class AuditResult(BaseModel):
    total_applicants: int
    total_passed: int
    overall_pass_rate: float
    bias_scores: list[BiasScore]
    audit_timestamp: str


class BiasReport(BaseModel):
    title: str
    summary: str
    audit: AuditResult
    compliance_status: str
    remediation_actions: list[str]
