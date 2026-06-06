import re
from hr_bias_audit.models.resume import ResumeProfile


class DemographicParser:
    GENDER_KEYWORDS = {
        "male": ["he", "his", "him", "mr."],
        "female": ["she", "her", "hers", "ms.", "mrs."],
    }

    AGE_KEYWORDS = {
        "under_30": [
            "recent graduate", "bachelor", "internship", "entry-level",
            "junior", "0-2 years",
        ],
        "30_50": [
            "senior", "lead", "manager", "director", "3-5 years",
            "5-10 years", "10+ years",
        ],
        "over_50": [
            "executive", "vp", "chief", "c-level", "20+ years",
            "board",
        ],
    }

    ETHNICITY_SIGNALS = [
        "pronouns", "diverse", "minority", "scholarship",
        "women in tech", "underrepresented",
    ]

    @staticmethod
    def infer_gender(resume: ResumeProfile) -> str:
        text = resume.raw_text.lower()
        male_count = sum(
            1 for kw in DemographicParser.GENDER_KEYWORDS["male"]
            if kw in text
        )
        female_count = sum(
            1 for kw in DemographicParser.GENDER_KEYWORDS["female"]
            if kw in text
        )
        if male_count > female_count:
            return "male"
        if female_count > male_count:
            return "female"
        return "unknown"

    @staticmethod
    def infer_age_group(resume: ResumeProfile) -> str:
        text = resume.raw_text.lower()
        for group, keywords in DemographicParser.AGE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return group
        return "unknown"

    @staticmethod
    def infer_ethnicity(resume: ResumeProfile) -> str:
        text = resume.raw_text.lower()
        if any(signal in text for signal in DemographicParser.ETHNICITY_SIGNALS):
            return "diverse_signal"
        return "unknown"

    @staticmethod
    def enrich(resume: ResumeProfile) -> ResumeProfile:
        resume.inferred_gender = DemographicParser.infer_gender(resume)
        resume.inferred_age_group = DemographicParser.infer_age_group(resume)
        resume.inferred_ethnicity = DemographicParser.infer_ethnicity(resume)
        return resume
