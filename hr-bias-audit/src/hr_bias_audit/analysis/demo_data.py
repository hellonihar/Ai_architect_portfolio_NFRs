import random
from uuid import uuid4

from hr_bias_audit.models.resume import ResumeProfile

FIRST_NAMES: dict[str, list[str]] = {
    "male": ["James", "Michael", "Robert", "David", "Daniel", "Alexander", "Benjamin", "William", "Ethan", "Lucas",
             "Samuel", "Joseph", "John", "Andrew", "Christopher", "Ryan", "Brandon", "Tyler", "Kevin", "Steven",
             "Jacob", "Nicholas", "Jonathan", "Matthew", "Joshua", "Jason", "Justin", "Eric", "Brian", "Scott"],
    "female": ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Maria", "Susan", "Sarah", "Karen",
               "Lisa", "Nancy", "Margaret", "Betty", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
               "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Amy"],
}

LAST_NAMES: list[str] = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
]

AGE_GROUPS = ["under_30", "30_50", "over_50"]

DEPARTMENTS = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]

ETHNICITY_SIGNAL_WEIGHT = 0.62


def _last_name_ethnicity_hint(last: str) -> str:
    hispanic = {"Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Perez", "Sanchez", "Rivera", "Torres", "Flores", "Ramirez"}
    asian = {"Lee", "Nguyen", "Kim", "Chen", "Wong", "Patel", "Shah", "Tan"}
    if last in hispanic:
        return "hispanic"
    if last in asian:
        return "asian"
    return "unknown"


def _generate_text(gender: str, age_group: str, dept: str) -> str:
    pronoun = "he" if gender == "male" else "she"
    lines = [f"{pronoun.capitalize()} is a professional in {dept.lower()}."]

    if age_group == "under_30":
        lines.append(f"{pronoun.capitalize()} is an entry-level candidate with internship experience.")
        lines.append("Recent graduate with strong academic record.")
    elif age_group == "30_50":
        years = random.randint(4, 14)
        title = random.choice(["Senior", "Lead", "Manager", "Principal"])
        lines.append(f"{pronoun.capitalize()} is a {title.lower()} with {years}+ years of experience.")
        lines.append(f"{pronoun.capitalize()} has led multiple successful projects.")
    else:
        years = random.randint(18, 30)
        title = random.choice(["Director", "VP", "Executive", "Chief"])
        lines.append(f"{pronoun.capitalize()} is a {title.lower()} with {years}+ years of executive experience.")
        lines.append(f"{pronoun.capitalize()} has overseen large teams and strategic initiatives.")

    skills_pool = {
        "Engineering": ["Python", "Java", "SQL", "AWS", "React", "Docker", "Kubernetes", "CI/CD"],
        "Marketing": ["SEO", "Content Strategy", "Analytics", "Social Media", "Brand Management", "CRM"],
        "Sales": ["CRM", "Negotiation", "Account Management", "Sales Pipeline", "Cold Outreach"],
        "HR": ["Recruiting", "Onboarding", "Employee Relations", "Payroll", "Compliance", "ATS"],
        "Finance": ["Financial Modeling", "Excel", "QuickBooks", "Audit", "Forecasting", "ERP"],
        "Operations": ["Supply Chain", "Logistics", "Process Optimization", "Vendor Management", "Lean"],
    }
    skills = random.sample(skills_pool.get(dept, skills_pool["Engineering"]), k=min(4, len(skills_pool.get(dept, []))))
    lines.append(f"Skills: {', '.join(skills)}.")
    return "\n".join(lines)


def _compute_score(gender: str, age_group: str, ethnicity: str, dept: str, *, bias_scale: float = 1.0) -> float:
    base = random.gauss(0.6, 0.18)
    base -= bias_scale * 0.18 if gender == "female" else 0.0
    base -= bias_scale * 0.12 if age_group == "under_30" else 0.0
    base -= bias_scale * 0.08 if age_group == "over_50" else 0.0
    base -= bias_scale * 0.15 if ethnicity != "unknown" else 0.0
    return max(0.05, min(0.98, base))


def generate(batch_size: int = 250, bias_scale: float = 1.0) -> list[ResumeProfile]:
    random.seed(42)
    profiles: list[ResumeProfile] = []

    gender_dist = ["female"] * 4 + ["male"] * 6

    for _ in range(batch_size):
        gender = random.choice(gender_dist)
        first = random.choice(FIRST_NAMES[gender])
        last = random.choice(LAST_NAMES)
        age_group = random.choice(AGE_GROUPS)
        dept = random.choice(DEPARTMENTS)
        ethnicity = _last_name_ethnicity_hint(last)
        score = _compute_score(gender, age_group, ethnicity, dept, bias_scale=bias_scale)
        passed = score >= 0.5

        profiles.append(ResumeProfile(
            id=str(uuid4()),
            name=f"{first} {last}",
            email=f"{first.lower()}.{last.lower()}@example.com",
            raw_text=_generate_text(gender, age_group, dept),
            inferred_gender=gender,
            inferred_age_group=age_group,
            inferred_ethnicity=ethnicity,
            screening_score=round(score, 3),
            passed_screen=passed,
            source="demo",
        ))

    return profiles
