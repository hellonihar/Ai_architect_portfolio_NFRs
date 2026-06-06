from hr_bias_audit.models.resume import ResumeProfile


def load() -> list[ResumeProfile]:
    return [
        ResumeProfile(
            id="s1", name="Alice Chen", email="alice@example.com",
            raw_text="She has 5 years experience. Senior software engineer.",
            inferred_gender="female", inferred_age_group="30_50",
            inferred_ethnicity="unknown",
            screening_score=0.85, passed_screen=True, source="sample",
        ),
        ResumeProfile(
            id="s2", name="Bob Smith", email="bob@example.com",
            raw_text="He is a lead architect with 10+ years.",
            inferred_gender="male", inferred_age_group="30_50",
            inferred_ethnicity="unknown",
            screening_score=0.82, passed_screen=True, source="sample",
        ),
        ResumeProfile(
            id="s3", name="Carol Davis", email="carol@example.com",
            raw_text="She is an entry-level developer. Recent graduate.",
            inferred_gender="female", inferred_age_group="under_30",
            inferred_ethnicity="unknown",
            screening_score=0.45, passed_screen=False, source="sample",
        ),
        ResumeProfile(
            id="s4", name="David Lee", email="david@example.com",
            raw_text="He has 20+ years executive experience at VP level.",
            inferred_gender="male", inferred_age_group="over_50",
            inferred_ethnicity="unknown",
            screening_score=0.90, passed_screen=True, source="sample",
        ),
        ResumeProfile(
            id="s5", name="Eva Martinez", email="eva@example.com",
            raw_text="She is a junior developer with internship background.",
            inferred_gender="female", inferred_age_group="under_30",
            inferred_ethnicity="diverse_signal",
            screening_score=0.38, passed_screen=False, source="sample",
        ),
        ResumeProfile(
            id="s6", name="Frank Kim", email="frank@example.com",
            raw_text="He is a director-level engineer with 15 years.",
            inferred_gender="male", inferred_age_group="30_50",
            inferred_ethnicity="unknown",
            screening_score=0.88, passed_screen=True, source="sample",
        ),
        ResumeProfile(
            id="s7", name="Grace Okafor", email="grace@example.com",
            raw_text="Pronouns: she/her. Diverse background.",
            inferred_gender="female", inferred_age_group="under_30",
            inferred_ethnicity="diverse_signal",
            screening_score=0.42, passed_screen=False, source="sample",
        ),
        ResumeProfile(
            id="s8", name="Henry Brown", email="henry@example.com",
            raw_text="He is a manager with 7 years experience.",
            inferred_gender="male", inferred_age_group="30_50",
            inferred_ethnicity="unknown",
            screening_score=0.75, passed_screen=True, source="sample",
        ),
    ]
