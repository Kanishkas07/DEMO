"""
utils.py
Shared helpers for RuralCare Maharashtra:
- Multilingual label translations (English / Marathi / Hindi)
- Reusable UI styling helpers (cards, badges, timeline)
- Session state defaults
"""

import streamlit as st
from datetime import datetime, date

# -----------------------------------------------------------------------------
# Multilingual translations
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "English": {
        "dashboard": "Dashboard",
        "patients": "Patients",
        "triage": "Digital Triage",
        "appointments": "Appointments",
        "teleconsultation": "Teleconsultation",
        "health_records": "Health Records",
        "referrals": "Referrals",
        "medicines": "Medicines",
        "diagnostics": "Diagnostics",
        "followups": "Follow-ups",
        "reports": "Reports",
        "login": "Login",
        "logout": "Logout",
        "logged_in_as": "Logged in as",
        "language": "Language",
        "online": "Online",
        "offline": "Offline Mode",
        "sync_now": "Sync Now",
        "simulate_offline": "Simulate Offline Mode",
        "register_patient": "Register New Patient",
        "run_triage": "Run Triage",
        "create_referral": "Create Referral",
        "save_consultation": "Save Consultation",
        "schedule_followup": "Schedule Follow-up",
        "search": "Search",
        "patient_id": "Patient ID",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "village": "Village",
        "district": "District",
        "phone": "Phone",
        "welcome": "Welcome to RuralCare Maharashtra",
        "better_access": "Better Access",
        "better_continuity": "Better Continuity",
        "better_accountability": "Better Accountability",
        "prototype_notice": "Prototype system. Not for production clinical use.",
        "triage_notice": "Decision-support prototype only. Final clinical decisions must be made by qualified healthcare professionals.",
        "patients_today": "Patients Today",
        "avg_waiting": "Avg Waiting Time",
        "teleconsultations": "Teleconsultations",
        "pending_referrals": "Pending Referrals",
        "referral_completion": "Referral Completion",
        "pending_followups": "Pending Follow-ups",
        "low_stock_meds": "Low Stock Medicines",
        "available_diagnostics": "Available Diagnostics",
        "overdue_followups": "Overdue Follow-ups",
        "travel_avoided": "Travel Avoided",
        "impact": "Impact",
        "quality_monitoring": "Public Healthcare Quality Monitoring",
        "enter_demo": "Enter Demo",
    },
    "मराठी": {
        "dashboard": "डॅशबोर्ड",
        "patients": "रुग्ण",
        "triage": "डिजिटल ट्रiage",
        "appointments": "अपॉइंटमेंट",
        "teleconsultation": "टेलीकन्सल्टेशन",
        "health_records": "आरोग्य नोंदी",
        "referrals": "रेफरल",
        "medicines": "औषधे",
        "diagnostics": "निदान",
        "followups": "फॉलो-अप",
        "reports": "अहवाल",
        "login": "लॉगिन",
        "logout": "लॉगआउट",
        "logged_in_as": "लॉगिन केले",
        "language": "भाषा",
        "online": "ऑनलाइन",
        "offline": "ऑफलाइन मोड",
        "sync_now": "सिंक करा",
        "simulate_offline": "ऑफलाइन मोड सिम्युलेट करा",
        "register_patient": "नवीन रुग्ण नोंदवा",
        "run_triage": "ट्रiage चालवा",
        "create_referral": "रेफरल तयार करा",
        "save_consultation": "कन्सल्टेशन जतन करा",
        "schedule_followup": "फॉलो-अप शेड्यूल करा",
        "search": "शोधा",
        "patient_id": "रुग्ण आयडी",
        "name": "नाव",
        "age": "वय",
        "gender": "लिंग",
        "village": "गाव",
        "district": "जिल्हा",
        "phone": "फोन",
        "welcome": "RuralCare Maharashtra मध्ये स्वागत",
        "better_access": "चांगला प्रवेश",
        "better_continuity": "चांगली सातत्यता",
        "better_accountability": "चांगली जबाबदारी",
        "prototype_notice": "प्रोटोटाइप प्रणाली. नैदानिक वापरासाठी नाही.",
        "triage_notice": "निर्णय-सहाय्य प्रोटोटाइप फक्त. अंतिम नैदानिक निर्णय तज्ज्ञांकडून हवा.",
        "patients_today": "आजचे रुग्ण",
        "avg_waiting": "सरासरी थांबा वेळ",
        "teleconsultations": "टेलीकन्सल्टेशन",
        "pending_referrals": "प्रलंबित रेफरल",
        "referral_completion": "रेफरल पूर्णता",
        "pending_followups": "प्रलंबित फॉलो-अप",
        "low_stock_meds": "कमी स्टॉक औषधे",
        "available_diagnostics": "उपलब्ध निदान",
        "overdue_followups": "मुदत गेलेले फॉलो-अप",
        "travel_avoided": "प्रवास वाचला",
        "impact": "परिणाम",
        "quality_monitoring": "सार्वजनिक आरोग्य गुणवत्ता निरीक्षण",
        "enter_demo": "डेमो प्रवेश",
    },
    "हिंदी": {
        "dashboard": "डैशबोर्ड",
        "patients": "मरीज",
        "triage": "डिजिटल ट्रiage",
        "appointments": "अपॉइंटमेंट",
        "teleconsultation": "टेलीकंसल्टेशन",
        "health_records": "स्वास्थ्य रिकॉर्ड",
        "referrals": "रेफरल",
        "medicines": "दवाइयां",
        "diagnostics": "निदान",
        "followups": "फॉलो-अप",
        "reports": "रिपोर्ट",
        "login": "लॉगिन",
        "logout": "लॉगआउट",
        "logged_in_as": "लॉगिन के रूप में",
        "language": "भाषा",
        "online": "ऑनलाइन",
        "offline": "ऑफलाइन मोड",
        "sync_now": "अभी सिंक करें",
        "simulate_offline": "ऑफलाइन मोड सिम्युलेट करें",
        "register_patient": "नया मरीज रजिस्टर करें",
        "run_triage": "ट्रiage चलाएं",
        "create_referral": "रेफरल बनाएं",
        "save_consultation": "कंसल्टेशन सेव करें",
        "schedule_followup": "फॉलो-अप शेड्यूल करें",
        "search": "खोजें",
        "patient_id": "मरीज आईडी",
        "name": "नाम",
        "age": "उम्र",
        "gender": "लिंग",
        "village": "गांव",
        "district": "जिला",
        "phone": "फोन",
        "welcome": "RuralCare Maharashtra में स्वागत",
        "better_access": "बेहतर पहुंच",
        "better_continuity": "बेहतर निरंतरता",
        "better_accountability": "बेहतर जवाबदेही",
        "prototype_notice": "प्रोटोटाइप प्रणाली. नैदानिक उपयोग के लिए नहीं।",
        "triage_notice": "निर्णय-सहायता प्रोटोटाइप मात्र. अंतिम नैदानिक निर्णय योग्य पेशेवर से होना चाहिए।",
        "patients_today": "आज के मरीज",
        "avg_waiting": "औसत प्रतीक्षा समय",
        "teleconsultations": "टेलीकंसल्टेशन",
        "pending_referrals": "लंबित रेफरल",
        "referral_completion": "रेफरल पूर्णता",
        "pending_followups": "लंबित फॉलो-अप",
        "low_stock_meds": "कम स्टॉक दवाइयां",
        "available_diagnostics": "उपलब्ध निदान",
        "overdue_followups": "अतिदेय फॉलो-अप",
        "travel_avoided": "यात्रा बची",
        "impact": "प्रभाव",
        "quality_monitoring": "सार्वजनिक स्वास्थ्य गुणवत्ता निगरानी",
        "enter_demo": "डेमो दर्ज करें",
    },
}


def t(key, lang=None):
    """Translate a key for the given (or session) language. Falls back to English."""
    if lang is None:
        lang = st.session_state.get("language", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)


# -----------------------------------------------------------------------------
# Session state defaults
# -----------------------------------------------------------------------------
def init_session_state():
    """Ensure all expected session state keys exist."""
    defaults = {
        "logged_in": False,
        "role": None,
        "username": None,
        "user_id": None,
        "facility_id": None,
        "page": "Dashboard",
        "language": "English",
        "offline_mode": False,
        "offline_records": [],  # list of pending records created while "offline"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------
def style_card(title, body, icon="", color="#1a73e8"):
    """Render a simple colored info card using inline HTML."""
    st.markdown(
        f"""
        <div style="border-left:5px solid {color}; background:#f8f9fa; padding:16px;
                    border-radius:8px; margin-bottom:10px;">
            <h4 style="margin:0; color:{color};">{icon} {title}</h4>
            <p style="margin:6px 0 0 0; color:#333;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_kpi(label, value, icon="", color="#1a73e8"):
    """Render a KPI metric card."""
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{color}22,{color}08);
                    border:1px solid {color}44; padding:16px; border-radius:12px;
                    text-align:center; margin-bottom:8px;">
            <div style="font-size:28px;">{icon}</div>
            <div style="font-size:24px; font-weight:700; color:{color};">{value}</div>
            <div style="font-size:13px; color:#555;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status):
    """Return an icon+text badge for a status string."""
    s = status.lower()
    if "red" in s or "urgent" in s or "overdue" in s or "out of stock" in s or "out" in s:
        return f"🔴 {status}"
    if "yellow" in s or "due" in s or "low" in s or "soon" in s:
        return f"🟡 {status}"
    if "green" in s or "completed" in s or "available" in s or "routine" in s:
        return f"🟢 {status}"
    return status


def format_date(d):
    """Format a date string (YYYY-MM-DD) to a readable form."""
    if not d:
        return ""
    try:
        return datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d %b %Y")
    except Exception:
        return str(d)


def is_overdue(appointment_date_str, status):
    """Check if a referral is overdue (appt date passed and not completed)."""
    if not appointment_date_str:
        return False
    completed_statuses = {"Consultation Completed", "Follow-up Scheduled"}
    if status in completed_statuses:
        return False
    try:
        appt = datetime.strptime(str(appointment_date_str)[:10], "%Y-%m-%d").date()
        return appt < date.today()
    except Exception:
        return False


def generate_patient_code(conn):
    """Generate the next patient code like MH-P-10XX."""
    row = conn.execute("SELECT COUNT(*) FROM patients").fetchone()
    n = row[0] + 1001
    return f"MH-P-{n}"
