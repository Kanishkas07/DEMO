"""
triage.py
Transparent rule-based digital triage decision support for RuralCare Maharashtra.

This is a DECISION-SUPPORT PROTOTYPE only. It does NOT diagnose patients.
Final clinical decisions must always be made by qualified healthcare professionals.

The triage logic is intentionally transparent and explainable: each decision
includes a human-readable reason and recommended action.
"""


def run_triage(
    temperature,
    systolic_bp,
    diastolic_bp,
    heart_rate,
    spo2,
    blood_glucose,
    age,
    symptoms,
    pregnancy_status,
    existing_conditions,
):
    """
    Evaluate vitals and return a triage category (RED / YELLOW / GREEN),
    a reason string, and a recommended action string.

    Returns:
        dict with keys: category, reason, recommended_action
    """
    reasons = []
    category = "GREEN"

    # ---- RED conditions (urgent escalation) --------------------------------
    if spo2 is not None and spo2 < 90:
        reasons.append("Low oxygen saturation (SpO2 < 90%) detected.")
        category = "RED"

    if temperature is not None and temperature >= 40.0:
        reasons.append("Very high fever (>= 40.0°C) detected.")
        category = "RED"

    if systolic_bp is not None and systolic_bp >= 180:
        reasons.append("Severely high blood pressure (systolic >= 180) detected.")
        category = "RED"

    if diastolic_bp is not None and diastolic_bp >= 120:
        reasons.append("Severely high blood pressure (diastolic >= 120) detected.")
        category = "RED"

    if systolic_bp is not None and systolic_bp < 90:
        reasons.append("Very low blood pressure (systolic < 90) detected.")
        category = "RED"

    if heart_rate is not None and (heart_rate > 130 or heart_rate < 45):
        reasons.append("Very abnormal heart rate detected.")
        category = "RED"

    if blood_glucose is not None and blood_glucose >= 400:
        reasons.append("Critically high blood glucose (>= 400) detected.")
        category = "RED"

    if pregnancy_status == "Pregnant" and age is not None and age >= 35:
        reasons.append("Advanced maternal age (>= 35) with pregnancy detected.")
        if category != "RED":
            category = "YELLOW"

    # Chest pain symptom -> RED
    if symptoms and "chest pain" in symptoms.lower():
        reasons.append("Chest pain reported - possible cardiac event.")
        category = "RED"

    # ---- YELLOW conditions (doctor consultation required) ------------------
    if category != "RED":
        yellow_reasons = []

        if spo2 is not None and 90 <= spo2 < 94:
            yellow_reasons.append("Borderline oxygen saturation (90-93%) detected.")

        if temperature is not None and 38.5 <= temperature < 40.0:
            yellow_reasons.append("High fever (38.5-39.9°C) detected.")

        if systolic_bp is not None and (140 <= systolic_bp < 180):
            yellow_reasons.append("Elevated blood pressure (140-179 systolic) detected.")

        if diastolic_bp is not None and (90 <= diastolic_bp < 120):
            yellow_reasons.append("Elevated blood pressure (90-119 diastolic) detected.")

        if heart_rate is not None and (100 < heart_rate <= 130):
            yellow_reasons.append("Elevated heart rate (101-130) detected.")

        if blood_glucose is not None and (200 <= blood_glucose < 400):
            yellow_reasons.append("High blood glucose (200-399) detected.")

        if age is not None and age >= 65:
            yellow_reasons.append("Elderly patient - requires closer monitoring.")

        if existing_conditions and existing_conditions.strip().lower() not in ("none", "", "nil"):
            yellow_reasons.append("Existing chronic condition noted.")

        if symptoms and any(
            s in symptoms.lower()
            for s in ["breath", "dizz", "vomit", "bleed", "severe", "weak"]
        ):
            yellow_reasons.append("Potentially concerning symptom reported.")

        if yellow_reasons:
            category = "YELLOW"
            reasons.extend(yellow_reasons)

    # ---- GREEN (routine) ---------------------------------------------------
    if not reasons:
        reasons.append("Vital signs within normal range. No urgent indicators.")
        category = "GREEN"

    # ---- Recommended actions -----------------------------------------------
    if category == "RED":
        action = "Immediate clinical evaluation required. Escalate to doctor / higher facility without delay."
    elif category == "YELLOW":
        action = "Doctor consultation required. Queue patient for next available consultation."
    else:
        action = "Routine care. Basic advice and follow-up as needed."

    return {
        "category": category,
        "reason": " ".join(reasons),
        "recommended_action": action,
    }


# -----------------------------------------------------------------------------
# Display metadata for each category
# -----------------------------------------------------------------------------
CATEGORY_META = {
    "RED": {
        "label": "RED - Urgent Escalation",
        "color": "#d32f2f",
        "icon": "🔴",
    },
    "YELLOW": {
        "label": "YELLOW - Doctor Consultation Required",
        "color": "#f9a825",
        "icon": "🟡",
    },
    "GREEN": {
        "label": "GREEN - Routine",
        "color": "#2e7d32",
        "icon": "🟢",
    },
}

REFERRAL_STATUSES = [
    "Created",
    "Accepted",
    "Appointment Scheduled",
    "Patient Attended",
    "Consultation Completed",
    "Follow-up Scheduled",
]
