from pydantic import BaseModel, Field
from typing import List


class LegislativeAnalysis(BaseModel):
    definitions: str = Field(
        description="Key terms defined in the text. If none, 'Not mentioned'."
    )
    obligations: str = Field(
        description="Duties that must be performed. If none, 'Not mentioned'."
    )
    responsibilities: str = Field(
        description="Specific areas of authority or accountability. If none, 'Not mentioned'."
    )
    eligibility: str = Field(
        description="Criteria for qualification. If none, 'Not mentioned'."
    )
    payments_entitlements: str = Field(
        description="Financial details, fees, or rights to benefits. If none, 'Not mentioned'."
    )
    penalties_enforcement: str = Field(
        description="Consequences for non-compliance. If none, 'Not mentioned'."
    )
    record_keeping_reporting: str = Field(
        description="Requirements for maintaining data or submitting reports. If none, 'Not mentioned'."
    )


class RuleCheck(BaseModel):
    rule: str = Field(
        description="The specific rule being checked (e.g., 'Act must define key terms')"
    )
    status: str = Field(description="Must be either 'pass' or 'fail'")
    evidence: str = Field(
        description="Cite the Section number or quote. If missing, write 'Not found'"
    )
    confidence: int = Field(description="Confidence score between 0 and 100")


class ComplianceReport(BaseModel):
    audit_results: List[RuleCheck] = Field(
        description="A list of checks for all 6 mandatory rules"
    )
