"""
app.py
RuralCare Maharashtra - Streamlit web application
SIH26133 - Accessibility & Quality of Public Healthcare Services in Rural Maharashtra

Run with:
    streamlit run app.py

Prototype system. Not for production clinical use.
All patient data is fictional and generated for demonstration only.
"""

import os
import random
import sqlite3
from datetime import datetime, date, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database as db
import triage as triage_mod
from utils import (
    t,
    init_session_state,
    style_card,
    style_kpi,
    status_badge,
    format_date,
    is_overdue,
    generate_patient_code,
)

# -----------------------------------------------------------------------------
# Page config & global CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RuralCare Maharashtra",
    page_icon="🏥",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Global typography for accessibility */
    html, body, [class*="css"] {
        font-size: 16px;
    }
    /* Larger buttons for rural / mobile users */
    .stButton button {
        font-size: 16px !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
    }
    /* Sidebar branding */
    [data-testid="stSidebar"] {
        background: #0d4f4f;
    }
    [data-testid="stSidebar"] * {
        color: #f0f8f8 !important;
    }
    /* Section heading spacing */
    h1, h2, h3 { margin-top: 0.4em !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize DB + session state on every run
db.init_db()
init_session_state()


# -----------------------------------------------------------------------------
# DB connection helper (local to this module)
# -----------------------------------------------------------------------------
def conn():
    return db.get_connection()


# =============================================================================
# LANDING / LOGIN PAGE
# =============================================================================
def landing_page():
    st.markdown(
        """
        <div style='text-align:center; padding:30px 10px 10px;'>
            <h1 style='color:#0d4f4f; font-size:42px;'>🏥 RuralCare Maharashtra</h1>
            <p style='font-size:20px; color:#555;'>
                Connecting rural patients to timely, continuous and quality
                public healthcare.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        style_card(
            t("better_access"),
            "Reduce unnecessary travel and waiting.",
            "🩺",
            "#1a73e8",
        )
    with col2:
        style_card(
            t("better_continuity"),
            "Connect health records, referrals and follow-ups.",
            "🔄",
            "#2e7d32",
        )
    with col3:
        style_card(
            t("better_accountability"),
            "Monitor facility performance, medicines and diagnostics.",
            "📊",
            "#e8710a",
        )

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color:#0d4f4f;'>{t('enter_demo')}</h3>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    roles = [
        ("Patient", "🧑‍🤝‍🧑", c1),
        ("Health Worker", "🧑‍⚕️", c2),
        ("Doctor", "👨‍⚕️", c3),
        ("Facility Admin", "🏥", c4),
    ]
    for role_name, icon, col in roles:
        with col:
            if st.button(f"{icon}  Login as {role_name}", key=f"login_{role_name}", use_container_width=True):
                _do_login(role_name)

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center; color:#888; font-size:14px;'>⚠️ {t('prototype_notice')}</p>",
        unsafe_allow_html=True,
    )


def _do_login(role_name):
    """Set up session for a demo role login."""
    user_map = {
        "Patient": ("patient_demo", "patient123"),
        "Health Worker": ("worker_demo", "worker123"),
        "Doctor": ("doctor_demo", "doctor123"),
        "Facility Admin": ("admin_demo", "admin123"),
    }
    username, password = user_map[role_name]
    c = conn()
    row = c.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=?",
        (username, db.hash_password(password)),
    ).fetchone()
    c.close()
    if row:
        st.session_state.logged_in = True
        st.session_state.role = row["role"]
        st.session_state.username = row["username"]
        st.session_state.user_id = row["id"]
        st.session_state.facility_id = row["facility_id"]
        st.session_state.page = "Dashboard"
        st.rerun()


# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏥 RuralCare Maharashtra")

        # ---- Navigation (role-aware) ----
        all_pages = [
            "Dashboard", "Patients", "Digital Triage", "Appointments",
            "Teleconsultation", "Health Records", "Referrals",
            "Medicines", "Diagnostics", "Follow-ups", "Reports",
        ]
        # Filter pages visible to each role
        role = st.session_state.role
        if role == "Patient":
            visible = ["Dashboard", "Health Records", "Appointments", "Referrals", "Medicines", "Diagnostics", "Follow-ups"]
        elif role == "Health Worker":
            visible = ["Dashboard", "Patients", "Digital Triage", "Appointments", "Teleconsultation", "Health Records", "Referrals", "Follow-ups", "Medicines", "Diagnostics"]
        elif role == "Doctor":
            visible = ["Dashboard", "Patients", "Appointments", "Teleconsultation", "Health Records", "Referrals", "Follow-ups"]
        else:  # Facility Admin
            visible = all_pages

        for page in visible:
            if st.button(page, key=f"nav_{page}", use_container_width=True,
                         type="primary" if st.session_state.page == page else "secondary"):
                st.session_state.page = page
                st.rerun()

        st.markdown("---")

        # ---- Language selector ----
        st.markdown(f"**{t('language')}**")
        lang = st.radio("Language", ["English", "मराठी", "हिंदी"],
                        index=["English", "मराठी", "हिंदी"].index(st.session_state.language),
                        label_visibility="collapsed")
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()

        st.markdown("---")

        # ---- Offline mode simulation ----
        if st.session_state.offline_mode:
            st.markdown(f"🟠 **{t('offline')}**")
            st.markdown(f"Records created offline: **{len(st.session_state.offline_records)}**")
            st.markdown(f"Pending synchronization: **{len(st.session_state.offline_records)}**")
            if st.button(f"🔄 {t('sync_now')}", use_container_width=True):
                with st.spinner("Synchronizing..."):
                    import time
                    time.sleep(1.5)
                    n = len(st.session_state.offline_records)
                    st.session_state.offline_records = []
                    st.session_state.offline_mode = False
                    st.success(f"✅ {n} records synchronized successfully.")
                    st.rerun()
            if st.button("Go Online", use_container_width=True):
                st.session_state.offline_mode = False
                st.rerun()
        else:
            st.markdown(f"🟢 **{t('online')}**")
            if st.checkbox(t("simulate_offline")):
                st.session_state.offline_mode = True
                st.rerun()

        st.markdown("---")

        # ---- User info & logout ----
        st.markdown(f"**{t('logged_in_as')}:**\n{st.session_state.role}")
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            for k in ["logged_in", "role", "username", "user_id", "facility_id", "page"]:
                st.session_state[k] = None if k != "page" else "Dashboard"
            st.session_state.logged_in = False
            st.rerun()


# =============================================================================
# PAGE: DASHBOARD (role-aware)
# =============================================================================
def page_dashboard():
    role = st.session_state.role

    if role == "Facility Admin":
        facility_dashboard()
        quality_monitoring_section()
        impact_section()
    elif role == "Health Worker":
        st.title("📊 Health Worker Dashboard")
        notifications_panel()
        st.subheader("Quick Actions")
        c1, c2, c3 = st.columns(3)
        c1.button("Register Patient", on_click=lambda: st.session_state.update(page="Patients"))
        c2.button("Run Triage", on_click=lambda: st.session_state.update(page="Digital Triage"))
        c3.button("Start Teleconsultation", on_click=lambda: st.session_state.update(page="Teleconsultation"))
        worker_followup_summary()
    elif role == "Doctor":
        st.title("👨‍⚕️ Doctor Dashboard")
        doctor_queue()
        notifications_panel()
    else:
        st.title("🧑 Patient Dashboard")
        patient_home()


def facility_dashboard():
    st.title("🏥 Facility Overview")

    c = conn()
    today_str = date.today().isoformat()

    # KPIs
    patients_today = c.execute(
        "SELECT COUNT(*) FROM appointments WHERE appointment_date=?", (today_str,)
    ).fetchone()[0]
    pending_ref = c.execute("SELECT COUNT(*) FROM referrals WHERE status NOT IN ('Consultation Completed','Follow-up Scheduled')").fetchone()[0]
    completed_ref = c.execute("SELECT COUNT(*) FROM referrals WHERE status IN ('Consultation Completed','Follow-up Scheduled')").fetchone()[0]
    total_ref = c.execute("SELECT COUNT(*) FROM referrals").fetchone()[0]
    ref_completion = int((completed_ref / total_ref * 100)) if total_ref else 0
    pending_fu = c.execute("SELECT COUNT(*) FROM followups WHERE status != 'Completed'").fetchone()[0]
    low_stock = c.execute("SELECT COUNT(*) FROM medicines WHERE quantity <= min_stock AND quantity > 0").fetchone()[0]
    avail_diag = c.execute("SELECT COUNT(*) FROM diagnostics WHERE available=1").fetchone()[0]
    tele_count = c.execute("SELECT COUNT(*) FROM consultations WHERE is_teleconsultation=1").fetchone()[0]
    overdue_fu = c.execute("SELECT COUNT(*) FROM followups WHERE status='Overdue'").fetchone()[0]

    kpis = [
        (t("patients_today"), patients_today, "👥", "#1a73e8"),
        (t("avg_waiting"), "32 min", "⏳", "#e8710a"),
        (t("teleconsultations"), tele_count, "📹", "#2e7d32"),
        (t("pending_referrals"), pending_ref, "🔄", "#d32f2f"),
        (t("referral_completion"), f"{ref_completion}%", "✅", "#2e7d32"),
        (t("pending_followups"), pending_fu, "❤️", "#e8710a"),
        (t("low_stock_meds"), low_stock, "💊", "#d32f2f"),
        (t("available_diagnostics"), avail_diag, "🧪", "#1a73e8"),
    ]
    cols = st.columns(4)
    for i, (label, val, icon, color) in enumerate(kpis):
        with cols[i % 4]:
            style_kpi(label, val, icon, color)

    st.markdown("---")
    st.subheader("Patient Load (last 7 days)")
    days = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
    loads = [random_load(d) for d in days]
    fig_load = px.bar(x=[d.strftime("%a") for d in days], y=loads, labels={"x": "Day", "y": "Patients"})
    fig_load.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_load, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Referral Performance")
        ref_data = referral_performance(c)
        fig_ref = px.bar(ref_data, x="status", y="count", labels={"status": "Status", "count": "Count"})
        fig_ref.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_ref, use_container_width=True)

    with col_r:
        st.subheader("Medicine Stock Status")
        med_status = medicine_stock_summary(c)
        fig_med = px.pie(values=list(med_status.values()), names=list(med_status.keys()),
                         hole=0.4)
        fig_med.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_med, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.subheader("Follow-up Status")
        fu_status = followup_status_summary(c)
        fig_fu = px.pie(values=list(fu_status.values()), names=list(fu_status.keys()),
                        hole=0.4, color_discrete_sequence=["#2e7d32", "#e8710a", "#d32f2f"])
        fig_fu.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_fu, use_container_width=True)

    with col_r2:
        st.subheader("Waiting Time Trend (min)")
        waits = [random.randint(25, 65) for _ in days]
        fig_wait = px.line(x=[d.strftime("%a") for d in days], y=waits, labels={"x": "Day", "y": "Min"})
        fig_wait.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_wait, use_container_width=True)

    c.close()


def random_load(d):
    """Deterministic-ish demo patient load per day."""
    import random as _r
    return _r.randint(60, 110)


def referral_performance(c):
    rows = c.execute("SELECT status, COUNT(*) as cnt FROM referrals GROUP BY status").fetchall()
    if not rows:
        return pd.DataFrame({"status": ["Created"], "count": [0]})
    return pd.DataFrame([{"status": r["status"], "count": r["cnt"]} for r in rows])


def medicine_stock_summary(c):
    rows = c.execute("SELECT quantity, min_stock FROM medicines").fetchall()
    avail = low = out = 0
    for r in rows:
        if r["quantity"] == 0:
            out += 1
        elif r["quantity"] <= r["min_stock"]:
            low += 1
        else:
            avail += 1
    return {"Available": avail, "Low Stock": low, "Out of Stock": out}


def followup_status_summary(c):
    rows = c.execute("SELECT status, COUNT(*) as cnt FROM followups GROUP BY status").fetchall()
    d = {"Completed": 0, "Due Soon": 0, "Overdue": 0}
    for r in rows:
        d[r["status"]] = r["cnt"]
    return d


def quality_monitoring_section():
    st.markdown("---")
    st.title("📊 Public Healthcare Quality Monitoring")

    c = conn()
    facilities = c.execute("SELECT id, name FROM facilities").fetchall()

    rows = []
    for f in facilities:
        pats = c.execute("SELECT COUNT(*) FROM appointments WHERE facility_id=?", (f["id"],)).fetchone()[0]
        meds = c.execute("SELECT quantity, min_stock FROM medicines WHERE facility_id=?", (f["id"],)).fetchall()
        med_avail = (sum(1 for m in meds if m["quantity"] > m["min_stock"]) / len(meds) * 100) if meds else 0
        diags = c.execute("SELECT available FROM diagnostics WHERE facility_id=?", (f["id"],)).fetchall()
        diag_avail = (sum(1 for d in diags if d["available"]) / len(diags) * 100) if diags else 0
        refs = c.execute("SELECT status FROM referrals WHERE referring_facility_id=?", (f["id"],)).fetchall()
        ref_comp = (sum(1 for r in refs if r["status"] in ("Consultation Completed", "Follow-up Scheduled")) / len(refs) * 100) if refs else 0
        fus = c.execute("SELECT status FROM followups WHERE patient_id IN (SELECT id FROM patients)", ()).fetchall()
        fu_comp = 84  # demo
        wait = random.randint(20, 55)
        rows.append({
            "Facility": f["name"], "Patients": pats, "Avg Waiting (min)": wait,
            "Referral Completion %": int(ref_comp), "Follow-up Completion %": fu_comp,
            "Medicine Availability %": int(med_avail), "Diagnostic Availability %": int(diag_avail),
        })
    c.close()

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    fig = px.bar(df, x="Facility", y=["Referral Completion %", "Medicine Availability %", "Diagnostic Availability %"],
                 barmode="group")
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # Facilities requiring attention
    st.subheader("⚠️ Facilities Requiring Attention")
    flagged = df[(df["Referral Completion %"] < 60) | (df["Avg Waiting (min)"] > 45) | (df["Medicine Availability %"] < 60)]
    if flagged.empty:
        st.info("All facilities are within acceptable targets.")
    else:
        for _, row in flagged.iterrows():
            issues = []
            if row["Referral Completion %"] < 60:
                issues.append("Referral completion below target")
            if row["Avg Waiting (min)"] > 45:
                issues.append("High waiting time")
            if row["Medicine Availability %"] < 60:
                issues.append("Low medicine availability")
            style_card(row["Facility"], "; ".join(issues), "⚠️", "#d32f2f")


def impact_section():
    st.markdown("---")
    st.title("📈 Impact")
    st.caption("Demo metrics for prototype evaluation.")

    c1, c2, c3 = st.columns(3)
    c1.metric(t("travel_avoided"), "128 patients", "via teleconsultation")
    c2.metric(t("avg_waiting"), "32 min", "↓ from 65 min")
    c3.metric(t("referral_completion"), "78%")

    c4, c5, c6 = st.columns(3)
    c4.metric("Follow-up Completion", "84%")
    c5.metric(t("teleconsultations"), "156")
    c6.metric("Medicine Availability", "91%")

    st.info("These are demo metrics for prototype evaluation, not real government statistics.")


def patient_home():
    """Patient dashboard - show their own record summary."""
    c = conn()
    # patient_demo linked to first patient
    pat = c.execute("SELECT * FROM patients ORDER BY id LIMIT 1").fetchone()
    if not pat:
        st.warning("No patient record found.")
        c.close()
        return
    st.markdown(f"### Welcome, {pat['name']}")
    style_card("Your Patient ID", pat["patient_code"], "🪪", "#1a73e8")

    # Latest triage
    tri = c.execute("SELECT * FROM triage_records WHERE patient_id=? ORDER BY id DESC LIMIT 1", (pat["id"],)).fetchone()
    if tri:
        style_card("Latest Triage", f"{status_badge(tri['final_category'])} - {format_date(tri['created_at'])}", "🩺", "#0d4f4f")

    # Upcoming appointment
    appt = c.execute("SELECT * FROM appointments WHERE patient_id=? AND status='Scheduled' ORDER BY appointment_date LIMIT 1", (pat["id"],)).fetchone()
    if appt:
        doc = c.execute("SELECT name FROM doctors WHERE id=?", (appt["doctor_id"],)).fetchone()
        style_card("Next Appointment", f"{format_date(appt['appointment_date'])} - {doc['name'] if doc else 'Doctor'}", "📅", "#2e7d32")
    else:
        style_card("Next Appointment", "No upcoming appointments", "📅", "#888")

    # Active referral
    ref = c.execute("SELECT * FROM referrals WHERE patient_id=? AND status NOT IN ('Consultation Completed','Follow-up Scheduled') ORDER BY id DESC LIMIT 1", (pat["id"],)).fetchone()
    if ref:
        dest = c.execute("SELECT name FROM facilities WHERE id=?", (ref["destination_facility_id"],)).fetchone()
        style_card("Active Referral", f"To {dest['name'] if dest else '?'} - {ref['status']}", "🔄", "#e8710a")

    notifications_panel()
    c.close()


def doctor_queue():
    """Show patients assigned / waiting for this doctor."""
    c = conn()
    st.subheader("Your Patient Queue")
    appts = c.execute(
        """SELECT a.*, p.name as patient_name, p.patient_code, t.final_category
           FROM appointments a
           JOIN patients p ON a.patient_id=p.id
           LEFT JOIN triage_records t ON t.patient_id=p.id
           WHERE a.doctor_id IN (SELECT id FROM doctors WHERE facility_id=?)
           ORDER BY a.appointment_date DESC LIMIT 15""",
        (st.session_state.facility_id,),
    ).fetchall()
    if not appts:
        st.info("No appointments in your queue.")
    else:
        for a in appts:
            triage_lbl = status_badge(a["final_category"]) if a["final_category"] else "No triage"
            st.markdown(f"**{a['patient_code']} - {a['patient_name']}** | {format_date(a['appointment_date'])} | Triage: {triage_lbl} | Token #{a['token_number'] or '-'}")
    c.close()


def worker_followup_summary():
    c = conn()
    st.subheader("Overdue Follow-ups Requiring Action")
    rows = c.execute(
        """SELECT f.*, p.name as patient_name, p.patient_code
           FROM followups f JOIN patients p ON f.patient_id=p.id
           WHERE f.status='Overdue' LIMIT 10"""
    ).fetchall()
    if not rows:
        st.success("No overdue follow-ups. Great job!")
    else:
        for r in rows:
            st.markdown(f"🔴 **{r['patient_code']} - {r['patient_name']}** | {r['category']} | Due: {format_date(r['due_date'])}")
    c.close()


def notifications_panel():
    st.subheader("🔔 Notifications")
    c = conn()
    rows = c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 8").fetchall()
    if not rows:
        st.info("No notifications.")
    for n in rows:
        icon = "🔴" if n["severity"] == "warning" else "ℹ️"
        st.markdown(f"{icon} {n['message']}")
    c.close()


# =============================================================================
# PAGE: PATIENTS (registration + profile)
# =============================================================================
def page_patients():
    st.title("🧑 Patients")
    role = st.session_state.role

    if role == "Health Worker":
        tab_reg, tab_list, tab_profile = st.tabs(["Register New Patient", "Patient List", "Patient Profile"])
        with tab_reg:
            register_patient_form()
        with tab_list:
            patient_list_view()
        with tab_profile:
            patient_profile_view()
    else:
        patient_list_view()
        st.markdown("---")
        patient_profile_view()


def register_patient_form():
    st.header(t("register_patient"))
    c = conn()
    code = generate_patient_code(c)

    with st.form("register_patient", clear_on_submit=True):
        st.markdown(f"**{t('patient_id')}:** `{code}`")
        name = st.text_input(t("name"))
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(t("age"), 0, 120, 25)
        with col2:
            gender = st.selectbox(t("gender"), ["Male", "Female", "Other"])
        phone = st.text_input(t("phone"))
        col3, col4 = st.columns(2)
        with col3:
            village = st.text_input(t("village"))
        with col4:
            district = st.text_input(t("district"), value="Madurai")
        language = st.selectbox("Preferred Language", ["English", "मराठी", "हिंदी"])
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"])
        existing = st.text_area("Existing Conditions", placeholder="e.g. Diabetes, Hypertension, or 'None'")
        allergies = st.text_area("Allergies", placeholder="e.g. Penicillin, or 'None'")
        meds = st.text_area("Current Medications", placeholder="e.g. Metformin, or 'None'")
        emergency = st.text_input("Emergency Contact")
        submitted = st.form_submit_button("✅ Register Patient", use_container_width=True)

        if submitted:
            if not name or not village or not phone:
                st.error("Please fill in Name, Phone and Village.")
            else:
                c.execute(
                    """INSERT INTO patients
                       (patient_code, name, age, gender, phone, village, district,
                        language, blood_group, existing_conditions, allergies,
                        current_medications, emergency_contact, registered_by)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (code, name, age, gender, phone, village, district, language,
                     blood_group, existing or "None", allergies or "None",
                     meds or "None", emergency, st.session_state.user_id),
                )
                c.commit()
                st.success(f"✅ Patient successfully registered\n\nPatient ID: {code}")

                # Offline simulation: track record
                if st.session_state.offline_mode:
                    st.session_state.offline_records.append(f"Patient {code}")

                # Auto notification
                c.execute(
                    "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
                    ("registration", f"New patient {code} ({name}) registered.", "info"),
                )
                c.commit()
    c.close()


def patient_list_view():
    st.subheader("Patient List")
    c = conn()
    rows = c.execute("SELECT patient_code, name, age, gender, village, risk_status FROM patients ORDER BY id").fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    df["risk_status"] = df["risk_status"].apply(status_badge)
    st.dataframe(df, use_container_width=True, hide_index=True)
    c.close()


def patient_profile_view():
    st.subheader("Patient Profile")
    c = conn()
    patients = c.execute("SELECT id, patient_code, name FROM patients ORDER BY id").fetchall()
    if not patients:
        st.info("No patients registered yet.")
        c.close()
        return
    options = {f"{p['patient_code']} - {p['name']}": p["id"] for p in patients}
    selected = st.selectbox("Select Patient", list(options.keys()))
    pid = options[selected]
    pat = c.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    if not pat:
        c.close()
        return

    st.markdown("### Patient Information")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Name:** {pat['name']}")
    col1.markdown(f"**Age:** {pat['age']}")
    col1.markdown(f"**Gender:** {pat['gender']}")
    col2.markdown(f"**Village:** {pat['village']}")
    col2.markdown(f"**District:** {pat['district']}")
    col2.markdown(f"**Language:** {pat['language']}")
    col3.markdown(f"**Phone:** {pat['phone']}")
    col3.markdown(f"**Blood Group:** {pat['blood_group']}")
    col3.markdown(f"**Emergency Contact:** {pat['emergency_contact'] or '-'}")

    st.markdown("### Medical Summary")
    style_card("Existing Conditions", pat["existing_conditions"] or "None", "📋", "#1a73e8")
    style_card("Allergies", pat["allergies"] or "None", "⚠️", "#d32f2f")
    style_card("Current Medications", pat["current_medications"] or "None", "💊", "#2e7d32")
    style_card("Risk Status", status_badge(pat["risk_status"]), "🚦", "#0d4f4f")

    st.markdown("### Current Visit")
    tri = c.execute("SELECT * FROM triage_records WHERE patient_id=? ORDER BY id DESC LIMIT 1", (pid,)).fetchone()
    appt = c.execute("SELECT a.*, d.name as doc_name FROM appointments a JOIN doctors d ON a.doctor_id=d.id WHERE a.patient_id=? ORDER BY a.id DESC LIMIT 1", (pid,)).fetchone()
    ref = c.execute("SELECT * FROM referrals WHERE patient_id=? ORDER BY id DESC LIMIT 1", (pid,)).fetchone()
    cc = st.columns(4)
    cc[0].markdown(f"**Triage:** {status_badge(tri['final_category']) if tri else 'None'}")
    cc[1].markdown(f"**Doctor:** {appt['doc_name'] if appt else '-'}")
    cc[2].markdown(f"**Appointment:** {format_date(appt['appointment_date']) if appt else '-'}")
    cc[3].markdown(f"**Referral:** {ref['status'] if ref else 'None'}")

    st.markdown("### Medical Timeline")
    render_timeline(c, pid)

    c.close()


def render_timeline(c, pid):
    """Render a vertical timeline of events for a patient."""
    events = []

    for con in c.execute("SELECT * FROM consultations WHERE patient_id=? ORDER BY id", (pid,)).fetchall():
        events.append((con["created_at"][:10], "🟢", "PHC consultation" + (" (Tele)" if con["is_teleconsultation"] else "")))

    for rx in c.execute("SELECT * FROM prescriptions WHERE patient_id=? ORDER BY id", (pid,)).fetchall():
        events.append((rx["created_at"][:10], "💊", f"Prescribed {rx['medicine']}"))

    for tr in c.execute("SELECT * FROM triage_records WHERE patient_id=? ORDER BY id", (pid,)).fetchall():
        events.append((tr["created_at"][:10], "🩺", f"Triage: {tr['final_category']}"))

    for r in c.execute("SELECT * FROM referrals WHERE patient_id=? ORDER BY id", (pid,)).fetchall():
        events.append((r["referral_date"][:10], "🟡" if r["status"] != "Consultation Completed" else "🔵", f"Referral {r['status']}"))

    for f in c.execute("SELECT * FROM followups WHERE patient_id=? ORDER BY id", (pid,)).fetchall():
        events.append((f["due_date"][:10], "🟣", f"Follow-up ({f['category']})"))

    events.sort(key=lambda x: x[0])

    if not events:
        st.info("No timeline events yet.")
        return

    timeline_html = ""
    for i, (dt, icon, label) in enumerate(events):
        arrow = "↓" if i < len(events) - 1 else ""
        timeline_html += f"""
        <div style='margin:8px 0; padding:10px; background:#f8f9fa; border-radius:8px; border-left:4px solid #0d4f4f;'>
            <span style='font-size:20px;'>{icon}</span>
            <b>{format_date(dt)}</b> — {label}
        </div>
        <div style='text-align:center; color:#888; font-size:18px;'>{arrow}</div>
        """
    st.markdown(timeline_html, unsafe_allow_html=True)


# =============================================================================
# PAGE: DIGITAL TRIAGE
# =============================================================================
def page_triage():
    st.title("🩺 Digital Triage")
    st.warning(t("triage_notice"))

    role = st.session_state.role
    if role not in ("Health Worker", "Doctor"):
        st.info("Triage is performed by Health Workers or Doctors.")
        return

    c = conn()
    patients = c.execute("SELECT id, patient_code, name, age FROM patients ORDER BY id").fetchall()
    if not patients:
        st.info("Register a patient first.")
        c.close()
        return

    options = {f"{p['patient_code']} - {p['name']}": p for p in patients}
    selected = st.selectbox("Select Patient", list(options.keys()))
    pat = options[selected]

    with st.form("triage_form"):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.number_input("Temperature (°C)", 30.0, 45.0, 37.0, step=0.1)
            systolic = st.number_input("Systolic BP (mmHg)", 40, 250, 120)
            diastolic = st.number_input("Diastolic BP (mmHg)", 20, 150, 80)
            heart_rate = st.number_input("Heart Rate (bpm)", 20, 220, 75)
        with col2:
            spo2 = st.number_input("SpO2 (%)", 50, 100, 98)
            glucose = st.number_input("Blood Glucose (mg/dL)", 30, 600, 110)
            pregnancy = st.selectbox("Pregnancy Status", ["Not Applicable", "Pregnant", "Postpartum"])
            symptoms = st.text_input("Symptoms", placeholder="e.g. fever, cough, chest pain")
        existing = st.text_input("Existing Conditions", value=pat_get_conditions(c, pat["id"]))

        submitted = st.form_submit_button(f"🩺 {t('run_triage')}", use_container_width=True)

    if submitted:
        result = triage_mod.run_triage(
            temperature, systolic, diastolic, heart_rate, spo2, glucose,
            pat["age"], symptoms, pregnancy, existing,
        )
        triage_id = save_triage_record(c, pat, result, temperature, systolic, diastolic,
                                       heart_rate, spo2, glucose, symptoms, pregnancy, existing)
        st.session_state["last_triage_id"] = triage_id
        st.session_state["last_triage_result"] = result
        st.session_state["last_triage_patient"] = {"id": pat["id"]}

    # Display the most recent triage result with override option
    if (
        "last_triage_result" in st.session_state
        and st.session_state.get("last_triage_patient", {}).get("id") == pat["id"]
    ):
        result = st.session_state["last_triage_result"]
        meta = triage_mod.CATEGORY_META[result["category"]]
        st.markdown(
            f"""<div style='background:{meta['color']}22; border:2px solid {meta['color']};
            padding:20px; border-radius:12px; text-align:center; margin:16px 0;'>
            <h2 style='color:{meta['color']}; margin:0;'>{meta['icon']} {meta['label']}</h2>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Reason:** {result['reason']}")
        st.markdown(f"**Recommended action:** {result['recommended_action']}")

        with st.expander("Override Triage Category (health worker discretion)"):
            override_cat = st.selectbox("Override Category", ["", "GREEN", "YELLOW", "RED"], key="ov_cat")
            override_reason = st.text_input("Override Reason", key="ov_reason")
            if st.button("Apply Override", key="ov_apply"):
                final = override_cat if override_cat else result["category"]
                c.execute(
                    "UPDATE triage_records SET final_category=?, override_reason=? WHERE id=?",
                    (final, override_reason, st.session_state["last_triage_id"]),
                )
                c.execute("UPDATE patients SET risk_status=? WHERE id=?", (final, pat["id"]))
                c.commit()
                st.success(f"Override applied: {final}")
                st.rerun()

        if result["category"] == "RED":
            emergency_escalation(pat, result)

    # Recent triage records
    st.markdown("---")
    st.subheader("Recent Triage Records")
    rows = c.execute(
        """SELECT t.*, p.patient_code, p.name FROM triage_records t
           JOIN patients p ON t.patient_id=p.id ORDER BY t.id DESC LIMIT 10"""
    ).fetchall()
    if rows:
        df = pd.DataFrame([{
            "Patient": f"{r['patient_code']} - {r['name']}",
            "Category": status_badge(r["final_category"]),
            "SpO2": r["spo2"], "BP": f"{r['systolic_bp']}/{r['diastolic_bp']}",
            "Date": format_date(r["created_at"]),
        } for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)
    c.close()


def pat_get_conditions(c, pid):
    p = c.execute("SELECT existing_conditions FROM patients WHERE id=?", (pid,)).fetchone()
    return p["existing_conditions"] if p else ""


def save_triage_record(c, pat, result, temp, sys_bp, dia, hr, spo2, gluc, symp, preg, existing):
    c.execute(
        """INSERT INTO triage_records
           (patient_id, temperature, systolic_bp, diastolic_bp, heart_rate, spo2,
            blood_glucose, symptoms, pregnancy_status, suggested_category,
            final_category, reason, recommended_action, recorded_by)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pat["id"], temp, sys_bp, dia, hr, spo2, gluc, symp, preg,
         result["category"], result["category"], result["reason"],
         result["recommended_action"], st.session_state.user_id),
    )
    triage_id = c.lastrowid
    c.execute("UPDATE patients SET risk_status=? WHERE id=?", (result["category"], pat["id"]))
    c.commit()
    st.success("Triage record saved.")
    if st.session_state.offline_mode:
        st.session_state.offline_records.append(f"Triage {pat['patient_code']}")
    return triage_id


def emergency_escalation(pat, result):
    st.markdown(
        f"""
        <div style='background:#d32f2f22; border:2px solid #d32f2f; padding:20px;
                    border-radius:12px; margin:16px 0;'>
            <h2 style='color:#d32f2f; margin:0;'>🚨 URGENT ESCALATION</h2>
            <p><b>Patient:</b> {pat['patient_code']}</p>
            <p><b>Priority:</b> 🔴 RED</p>
            <p><b>Reason:</b> {result['reason']}</p>
            <p><b>Action:</b> {result['recommended_action']}</p>
            <p><b>Destination:</b> District Hospital</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c = conn()
    # Auto-create emergency referral
    if st.button("🚨 Create Emergency Referral", type="primary"):
        dest = c.execute("SELECT id FROM facilities WHERE type='District Hospital' LIMIT 1").fetchone()
        ref_fac = c.execute("SELECT id FROM facilities WHERE type='PHC' LIMIT 1").fetchone()
        if dest and ref_fac:
            c.execute(
                """INSERT INTO referrals
                   (patient_id, referring_facility_id, destination_facility_id,
                    department, reason, priority, status, referral_date,
                    appointment_date, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (pat["id"], ref_fac["id"], dest["id"], "Emergency",
                 result["reason"], "URGENT", "Created", date.today().isoformat(),
                 (date.today() + timedelta(days=1)).isoformat(), st.session_state.user_id),
            )
            c.execute(
                "INSERT INTO notifications (type, message, severity, patient_id) VALUES (?,?,?,?)",
                ("emergency", f"🚨 Emergency escalation for {pat['patient_code']}: {result['reason']}", "warning", pat["id"]),
            )
            c.commit()
            st.success("Emergency referral created to District Hospital.")
    c.close()


# =============================================================================
# PAGE: APPOINTMENTS
# =============================================================================
def page_appointments():
    st.title("📅 Appointments")
    c = conn()
    role = st.session_state.role

    if role in ("Health Worker", "Doctor"):
        with st.expander("Schedule New Appointment"):
            patients = c.execute("SELECT id, patient_code, name FROM patients ORDER BY id").fetchall()
            doctors = c.execute("SELECT id, name, specialty FROM doctors ORDER BY id").fetchall()
            facilities = c.execute("SELECT id, name FROM facilities ORDER BY id").fetchall()
            if patients and doctors and facilities:
                p_opt = {f"{p['patient_code']} - {p['name']}": p["id"] for p in patients}
                d_opt = {f"{d['name']} ({d['specialty']})": d["id"] for d in doctors}
                f_opt = {f["name"]: f["id"] for f in facilities}
                with st.form("appt_form"):
                    ap = st.selectbox("Patient", list(p_opt.keys()))
                    ad = st.selectbox("Doctor", list(d_opt.keys()))
                    af = st.selectbox("Facility", list(f_opt.keys()))
                    adate = st.date_input("Appointment Date", date.today() + timedelta(days=1))
                    reason = st.text_input("Reason")
                    token = st.number_input("Token Number", 1, 999, 1)
                    submit = st.form_submit_button("Schedule Appointment")
                    if submit:
                        c.execute(
                            """INSERT INTO appointments
                               (patient_id, doctor_id, facility_id, appointment_date,
                                token_number, reason) VALUES (?,?,?,?,?,?)""",
                            (p_opt[ap], d_opt[ad], f_opt[af], adate.isoformat(), token, reason),
                        )
                        c.commit()
                        st.success(f"Appointment scheduled. Token #{token}")

    st.subheader("Appointments")
    rows = c.execute(
        """SELECT a.appointment_date, a.token_number, a.status, a.reason,
                  p.patient_code, p.name as patient_name,
                  d.name as doctor_name, f.name as facility_name
           FROM appointments a
           JOIN patients p ON a.patient_id=p.id
           JOIN doctors d ON a.doctor_id=d.id
           JOIN facilities f ON a.facility_id=f.id
           ORDER BY a.appointment_date DESC LIMIT 30"""
    ).fetchall()
    if rows:
        df = pd.DataFrame([{
            "Date": format_date(r["appointment_date"]),
            "Token": r["token_number"], "Patient": f"{r['patient_code']} - {r['patient_name']}",
            "Doctor": r["doctor_name"], "Facility": r["facility_name"],
            "Status": r["status"], "Reason": r["reason"],
        } for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments yet.")
    c.close()


# =============================================================================
# PAGE: TELECONSULTATION
# =============================================================================
def page_teleconsultation():
    st.title("📹 Assisted Teleconsultation")
    st.caption("Demo Teleconsultation - not a real video calling system.")

    c = conn()
    role = st.session_state.role
    if role not in ("Health Worker", "Doctor"):
        st.info("Only Health Workers and Doctors can conduct teleconsultations.")
        c.close()
        return

    patients = c.execute("SELECT id, patient_code, name, age, village, existing_conditions FROM patients ORDER BY id").fetchall()
    if not patients:
        st.info("No patients available.")
        c.close()
        return

    p_opt = {f"{p['patient_code']} - {p['name']}": p for p in patients}
    selected = st.selectbox("Select Patient", list(p_opt.keys()))
    pat = p_opt[selected]
    doctors = c.execute("SELECT id, name FROM doctors ORDER BY id").fetchall()
    d_opt = {d["name"]: d["id"] for d in doctors}

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Patient Information")
        st.markdown(f"**Name:** {pat['name']}")
        st.markdown(f"**Age:** {pat['age']}")
        st.markdown(f"**Village:** {pat['village']}")
        st.markdown(f"**History:** {pat['existing_conditions']}")

        tri = c.execute("SELECT * FROM triage_records WHERE patient_id=? ORDER BY id DESC LIMIT 1", (pat["id"],)).fetchone()
        st.markdown("### Vitals")
        if tri:
            st.markdown(f"**BP:** {tri['systolic_bp']}/{tri['diastolic_bp']}")
            st.markdown(f"**SpO2:** {tri['spo2']}%")
            st.markdown(f"**Heart Rate:** {tri['heart_rate']}")
            st.markdown(f"**Temp:** {tri['temperature']}°C")
            st.markdown(f"**Glucose:** {tri['blood_glucose']}")
            st.markdown(f"**Triage:** {status_badge(tri['final_category'])}")
        else:
            st.info("No vitals recorded.")

        st.markdown("### Previous History")
        render_timeline(c, pat["id"])

    with col2:
        st.markdown("### Consultation Area")
        st.markdown(
            """
            <div style='background:#1a1a2e; color:#fff; padding:40px; border-radius:12px;
                        text-align:center; min-height:250px;'>
                <h3>DEMO VIDEO CONSULTATION</h3>
                <p style='font-size:48px;'>👨‍⚕️</p>
                <p>Doctor video feed (simulated)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        bc1, bc2 = st.columns(2)
        started = bc1.button("▶️ Start Consultation")
        ended = bc2.button("⏹️ End Consultation")
        if started:
            st.session_state["tele_started"] = True
        if ended:
            st.session_state["tele_started"] = False
        if st.session_state.get("tele_started"):
            st.info("Consultation in progress... (demo)")

        st.markdown("### Doctor Notes")
        notes = st.text_area("Consultation Notes", height=100, key="tele_notes")
        diagnosis = st.text_input("Diagnosis")

        st.markdown("### Prescription")
        pc1, pc2, pc3, pc4 = st.columns(4)
        med = pc1.text_input("Medicine")
        dose = pc2.text_input("Dosage")
        freq = pc3.text_input("Frequency")
        dur = pc4.text_input("Duration")

        doc_name = st.selectbox("Consulting Doctor", list(d_opt.keys()))

        st.markdown("### Actions")
        ac1, ac2 = st.columns(2)
        if ac1.button("💾 Save Consultation", use_container_width=True):
            if not notes:
                st.warning("Please enter consultation notes.")
            else:
                c.execute(
                    """INSERT INTO consultations
                       (patient_id, doctor_id, triage_id, consultation_notes, diagnosis, is_teleconsultation)
                       VALUES (?,?,?,?,?,1)""",
                    (pat["id"], d_opt[doc_name], tri["id"] if tri else None, notes, diagnosis),
                )
                c.commit()
                st.success("Consultation saved.")
                if st.session_state.offline_mode:
                    st.session_state.offline_records.append(f"Consultation {pat['patient_code']}")

        if ac2.button("💊 Create Prescription", use_container_width=True):
            if not med:
                st.warning("Please enter a medicine.")
            else:
                c.execute(
                    """INSERT INTO prescriptions
                       (patient_id, doctor_id, medicine, dosage, frequency, duration)
                       VALUES (?,?,?,?,?,?)""",
                    (pat["id"], d_opt[doc_name], med, dose, freq, dur),
                )
                c.commit()
                st.success(f"Prescription created: {med}")

        with st.expander("🔄 Create Referral"):
            facs = c.execute("SELECT id, name FROM facilities ORDER BY id").fetchall()
            fac_opt = {f["name"]: f["id"] for f in facs}
            with st.form("tele_ref_form"):
                dest = st.selectbox("Destination Facility", list(fac_opt.keys()), key="tele_dest")
                dept = st.text_input("Department", key="tele_dept")
                rreason = st.text_area("Reason", key="tele_rreason")
                prio = st.selectbox("Priority", ["NORMAL", "HIGH", "URGENT"], key="tele_prio")
                rdate = st.date_input("Appointment Date", date.today() + timedelta(days=2), key="tele_rdate")
                rsubmit = st.form_submit_button("Create Referral")
                if rsubmit:
                    ref_fac = st.session_state.facility_id or facs[0]["id"]
                    c.execute(
                        """INSERT INTO referrals
                           (patient_id, referring_facility_id, destination_facility_id,
                            department, reason, priority, status, referral_date,
                            appointment_date, created_by)
                           VALUES (?,?,?,?,?,?, 'Created', ?,?,?)""",
                        (pat["id"], ref_fac, fac_opt[dest], dept, rreason, prio,
                         date.today().isoformat(), rdate.isoformat(), st.session_state.user_id),
                    )
                    c.commit()
                    st.success(f"Referral created to {dest}.")

        with st.expander("📅 Schedule Follow-up"):
            with st.form("tele_fu_form"):
                cat = st.selectbox("Category", ["Maternal health", "Child health", "Diabetes", "Hypertension", "Elderly", "Other high-risk"], key="tele_cat")
                fdate = st.date_input("Follow-up Due Date", date.today() + timedelta(days=14), key="tele_fdate")
                fsubmit = st.form_submit_button("Schedule Follow-up")
                if fsubmit:
                    c.execute(
                        """INSERT INTO followups
                           (patient_id, category, condition_label, last_visit, due_date,
                            status, assigned_worker_id)
                           VALUES (?,?,?,?, 'Due Soon', ?)""",
                        (pat["id"], cat, cat, date.today().isoformat(), fdate.isoformat(), st.session_state.user_id),
                    )
                    c.commit()
                    st.success("Follow-up scheduled.")
    c.close()


# =============================================================================
# PAGE: HEALTH RECORDS
# =============================================================================
def page_health_records():
    st.title("📋 Health Records")
    c = conn()
    patients = c.execute("SELECT id, patient_code, name FROM patients ORDER BY id").fetchall()
    if not patients:
        st.info("No patients.")
        c.close()
        return
    p_opt = {f"{p['patient_code']} - {p['name']}": p["id"] for p in patients}
    selected = st.selectbox("Select Patient", list(p_opt.keys()))
    pid = p_opt[selected]

    tab1, tab2, tab3, tab4 = st.tabs(["Triage", "Consultations", "Prescriptions", "Timeline"])
    with tab1:
        rows = c.execute("SELECT * FROM triage_records WHERE patient_id=? ORDER BY id DESC", (pid,)).fetchall()
        if rows:
            df = pd.DataFrame([{
                "Date": format_date(r["created_at"]), "Category": status_badge(r["final_category"]),
                "SpO2": r["spo2"], "BP": f"{r['systolic_bp']}/{r['diastolic_bp']}",
                "Reason": r["reason"],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No triage records.")
    with tab2:
        rows = c.execute(
            """SELECT con.*, d.name as doc_name FROM consultations con
               JOIN doctors d ON con.doctor_id=d.id WHERE con.patient_id=? ORDER BY con.id DESC""",
            (pid,),
        ).fetchall()
        if rows:
            df = pd.DataFrame([{
                "Date": format_date(r["created_at"]), "Doctor": r["doc_name"],
                "Tele": "Yes" if r["is_teleconsultation"] else "No",
                "Diagnosis": r["diagnosis"], "Notes": r["consultation_notes"],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No consultations.")
    with tab3:
        rows = c.execute(
            """SELECT pr.*, d.name as doc_name FROM prescriptions pr
               JOIN doctors d ON pr.doctor_id=d.id WHERE pr.patient_id=? ORDER BY pr.id DESC""",
            (pid,),
        ).fetchall()
        if rows:
            df = pd.DataFrame([{
                "Date": format_date(r["created_at"]), "Medicine": r["medicine"],
                "Dosage": r["dosage"], "Frequency": r["frequency"], "Duration": r["duration"],
                "Doctor": r["doc_name"],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No prescriptions.")
    with tab4:
        render_timeline(c, pid)
    c.close()


# =============================================================================
# PAGE: REFERRALS
# =============================================================================
def page_referrals():
    st.title("🔄 Referral Management")
    c = conn()
    role = st.session_state.role

    if role in ("Health Worker", "Doctor"):
        with st.expander("Create New Referral"):
            patients = c.execute("SELECT id, patient_code, name FROM patients ORDER BY id").fetchall()
            facs = c.execute("SELECT id, name FROM facilities ORDER BY id").fetchall()
            if patients and facs:
                p_opt = {f"{p['patient_code']} - {p['name']}": p["id"] for p in patients}
                f_opt = {f["name"]: f["id"] for f in facs}
                with st.form("ref_form"):
                    rp = st.selectbox("Patient", list(p_opt.keys()))
                    rf = st.selectbox("Referring Facility", list(f_opt.keys()))
                    df_ = st.selectbox("Destination Facility", list(f_opt.keys()), index=len(f_opt)-1)
                    dept = st.text_input("Department")
                    reason = st.text_area("Reason")
                    prio = st.selectbox("Priority", ["NORMAL", "HIGH", "URGENT"])
                    rdate = st.date_input("Referral Date", date.today())
                    adate = st.date_input("Appointment Date", date.today() + timedelta(days=3))
                    submit = st.form_submit_button("Create Referral")
                    if submit:
                        if rf == df_:
                            st.error("Referring and destination facilities must differ.")
                        else:
                            c.execute(
                                """INSERT INTO referrals
                                   (patient_id, referring_facility_id, destination_facility_id,
                                    department, reason, priority, status, referral_date,
                                    appointment_date, created_by)
                                   VALUES (?,?,?,?,?,?, 'Created', ?,?,?)""",
                                (p_opt[rp], f_opt[rf], f_opt[df_], dept, reason, prio,
                                 rdate.isoformat(), adate.isoformat(), st.session_state.user_id),
                            )
                            c.commit()
                            st.success("Referral created.")

    st.subheader("Referrals")
    rows = c.execute(
        """SELECT r.*, p.patient_code, p.name as patient_name,
                  rf.name as ref_name, df.name as dest_name
           FROM referrals r
           JOIN patients p ON r.patient_id=p.id
           JOIN facilities rf ON r.referring_facility_id=rf.id
           JOIN facilities df ON r.destination_facility_id=df.id
           ORDER BY r.id DESC"""
    ).fetchall()

    if not rows:
        st.info("No referrals yet.")
        c.close()
        return

    for r in rows:
        overdue = is_overdue(r["appointment_date"], r["status"])
        badge = "🔴 OVERDUE REFERRAL" if overdue else status_badge(r["status"])
        with st.expander(f"{r['patient_code']} - {r['patient_name']} → {r['dest_name']} | {badge}"):
            st.markdown(f"**Referring Facility:** {r['ref_name']}")
            st.markdown(f"**Destination:** {r['dest_name']}")
            st.markdown(f"**Department:** {r['department'] or '-'}")
            st.markdown(f"**Reason:** {r['reason']}")
            st.markdown(f"**Priority:** {r['priority']}")
            st.markdown(f"**Referral Date:** {format_date(r['referral_date'])}")
            st.markdown(f"**Appointment Date:** {format_date(r['appointment_date'])}")
            if overdue:
                st.error("🔴 OVERDUE REFERRAL - appointment date passed without completion.")

            # Progress tracker
            render_referral_tracker(r["status"])

            # Status update
            if role in ("Health Worker", "Doctor", "Facility Admin"):
                new_status = st.selectbox(
                    "Update Status",
                    triage_mod.REFERRAL_STATUSES,
                    index=triage_mod.REFERRAL_STATUSES.index(r["status"]) if r["status"] in triage_mod.REFERRAL_STATUSES else 0,
                    key=f"st_{r['id']}",
                )
                if st.button("Update Referral", key=f"up_{r['id']}"):
                    c.execute("UPDATE referrals SET status=? WHERE id=?", (new_status, r["id"]))
                    if new_status == "Follow-up Scheduled":
                        c.execute(
                            """INSERT INTO followups (patient_id, category, condition_label,
                               last_visit, due_date, status, assigned_worker_id, referral_id)
                               VALUES (?, 'Other high-risk', 'Post-referral', ?, ?, 'Due Soon', ?, ?)""",
                            (r["patient_id"], date.today().isoformat(),
                             (date.today() + timedelta(days=14)).isoformat(),
                             st.session_state.user_id, r["id"]),
                        )
                    c.commit()
                    st.success(f"Referral updated to: {new_status}")
                    st.rerun()
    c.close()


def render_referral_tracker(status):
    """Visual progress tracker for a referral."""
    statuses = triage_mod.REFERRAL_STATUSES
    try:
        current_idx = statuses.index(status)
    except ValueError:
        current_idx = 0
    html = "<div style='font-family:monospace; padding:10px;'>"
    html += "<b>Referral Progress</b><br>"
    for i, s in enumerate(statuses):
        done = i <= current_idx
        marker = "●" if done else "○"
        color = "#2e7d32" if done else "#888"
        html += f"<span style='color:{color}; font-size:18px;'>{marker}</span> <span style='color:{'#333' if done else '#888'}'>{s}</span><br>"
        if i < len(statuses) - 1:
            html += "<span style='color:#888;'>│</span><br>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# =============================================================================
# PAGE: MEDICINES
# =============================================================================
def page_medicines():
    st.title("💊 Medicine Availability")
    c = conn()
    role = st.session_state.role

    search = st.text_input(f"🔍 {t('search')} medicine", key="med_search")

    rows = c.execute(
        """SELECT m.*, f.name as facility_name FROM medicines m
           JOIN facilities f ON m.facility_id=f.id
           WHERE m.name LIKE ? ORDER BY m.name""",
        (f"%{search}%",),
    ).fetchall()

    if not rows:
        st.info("No medicines found.")
        c.close()
        return

    if search:
        # Group by medicine, show facilities
        st.subheader(f"Results for '{search}'")
        from collections import defaultdict
        groups = defaultdict(list)
        for r in rows:
            groups[r["name"]].append(r)
        for med, items in groups.items():
            st.markdown(f"#### {med}")
            for it in items:
                status = med_stock_status(it["quantity"], it["min_stock"])
                st.markdown(f"- {it['facility_name']} — {status} (Qty: {it['quantity']})")
    else:
        # Full table
        data = []
        for r in rows:
            data.append({
                "Medicine": r["name"],
                "Facility": r["facility_name"],
                "Quantity": r["quantity"],
                "Min Stock": r["min_stock"],
                "Last Updated": format_date(r["last_updated"]),
                "Status": med_stock_status(r["quantity"], r["min_stock"]),
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Admin update
    if role == "Facility Admin":
        st.markdown("---")
        st.subheader("Update Medicine Stock")
        med_names = sorted(set(r["name"] for r in rows))
        fac_names = sorted(set(r["facility_name"] for r in rows))
        with st.form("med_update"):
            um = st.selectbox("Medicine", med_names)
            uf = st.selectbox("Facility", fac_names)
            uq = st.number_input("New Quantity", 0, 10000, 100)
            submit = st.form_submit_button("Update Stock")
            if submit:
                fid = c.execute("SELECT id FROM facilities WHERE name=?", (uf,)).fetchone()
                c.execute("UPDATE medicines SET quantity=?, last_updated=datetime('now','localtime') WHERE name=? AND facility_id=?",
                          (uq, um, fid["id"]))
                c.commit()
                st.success(f"Updated {um} at {uf} to {uq} units.")
    c.close()


def med_stock_status(qty, min_s):
    if qty == 0:
        return "🔴 Out of Stock"
    if qty <= min_s:
        return "🟡 Low Stock"
    return "🟢 Available"


# =============================================================================
# PAGE: DIAGNOSTICS
# =============================================================================
def page_diagnostics():
    st.title("🧪 Diagnostic Services")
    c = conn()
    role = st.session_state.role

    search = st.text_input(f"🔍 {t('search')} test", key="diag_search")

    rows = c.execute(
        """SELECT d.*, f.name as facility_name FROM diagnostics d
           JOIN facilities f ON d.facility_id=f.id
           WHERE d.test_name LIKE ? ORDER BY d.test_name""",
        (f"%{search}%",),
    ).fetchall()

    if not rows:
        st.info("No diagnostics found.")
        c.close()
        return

    data = []
    for r in rows:
        data.append({
            "Test": r["test_name"],
            "Facility": r["facility_name"],
            "Availability": "🟢 Available" if r["available"] else "🔴 Unavailable",
            "Waiting (min)": r["waiting_time_min"] if r["available"] else "-",
            "Last Updated": format_date(r["last_updated"]),
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if role == "Facility Admin":
        st.markdown("---")
        st.subheader("Update Diagnostic Availability")
        test_names = sorted(set(r["test_name"] for r in rows))
        fac_names = sorted(set(r["facility_name"] for r in rows))
        with st.form("diag_update"):
            ut = st.selectbox("Test", test_names)
            uf = st.selectbox("Facility", fac_names)
            ua = st.checkbox("Available", value=True)
            uw = st.number_input("Waiting Time (min)", 0, 600, 30)
            submit = st.form_submit_button("Update Availability")
            if submit:
                fid = c.execute("SELECT id FROM facilities WHERE name=?", (uf,)).fetchone()
                c.execute("UPDATE diagnostics SET available=?, waiting_time_min=?, last_updated=datetime('now','localtime') WHERE test_name=? AND facility_id=?",
                          (1 if ua else 0, uw, ut, fid["id"]))
                c.commit()
                st.success(f"Updated {ut} at {uf}.")
    c.close()


# =============================================================================
# PAGE: FOLLOW-UPS
# =============================================================================
def page_followups():
    st.title("❤️ Follow-up Management")
    c = conn()

    overdue_count = c.execute("SELECT COUNT(*) FROM followups WHERE status='Overdue'").fetchone()[0]
    style_kpi(t("overdue_followups"), overdue_count, "❤️", "#d32f2f")

    st.markdown("---")

    rows = c.execute(
        """SELECT f.*, p.patient_code, p.name as patient_name, u.full_name as worker
           FROM followups f
           JOIN patients p ON f.patient_id=p.id
           LEFT JOIN users u ON f.assigned_worker_id=u.id
           ORDER BY f.due_date"""
    ).fetchall()

    if not rows:
        st.info("No follow-ups.")
        c.close()
        return

    for r in rows:
        badge = status_badge(r["status"])
        with st.expander(f"{r['patient_code']} - {r['patient_name']} | {r['category']} | {badge}"):
            st.markdown(f"**Condition:** {r['condition_label']}")
            st.markdown(f"**Last Visit:** {format_date(r['last_visit'])}")
            st.markdown(f"**Follow-up Due:** {format_date(r['due_date'])}")
            st.markdown(f"**Assigned Health Worker:** {r['worker'] or 'Unassigned'}")

            ac1, ac2, ac3, ac4 = st.columns(4)
            if ac1.button("📞 Contacted", key=f"c_{r['id']}"):
                st.info("Marked as contacted. Patient reached successfully.")
            if ac2.button("📅 Schedule Appointment", key=f"s_{r['id']}"):
                c.execute(
                    """INSERT INTO appointments (patient_id, doctor_id, facility_id, appointment_date, reason)
                       SELECT ?, d.id, d.facility_id, ?, 'Follow-up'
                       FROM doctors d LIMIT 1""",
                    (r["patient_id"], (date.today() + timedelta(days=3)).isoformat()),
                )
                c.execute("UPDATE followups SET status='Due Soon' WHERE id=?", (r["id"],))
                c.commit()
                st.success("Appointment scheduled for follow-up.")
            if ac3.button("✅ Mark Completed", key=f"m_{r['id']}"):
                c.execute("UPDATE followups SET status='Completed' WHERE id=?", (r["id"],))
                c.commit()
                st.success("Follow-up marked completed.")
                st.rerun()
            if ac4.button("❌ Unable to Reach", key=f"u_{r['id']}"):
                c.execute(
                    "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
                    ("followup", f"Unable to reach {r['patient_code']} - {r['patient_name']} for follow-up.", "warning"),
                )
                c.commit()
                st.warning("Marked as unable to reach. Notification added.")
    c.close()


# =============================================================================
# PAGE: REPORTS
# =============================================================================
def page_reports():
    st.title("📑 Reports")
    st.caption("Demo metrics for prototype evaluation.")
    c = conn()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Referral Summary")
        rows = c.execute("SELECT status, COUNT(*) as cnt FROM referrals GROUP BY status").fetchall()
        df = pd.DataFrame([{"Status": r["status"], "Count": r["cnt"]} for r in rows])
        fig = px.bar(df, x="Status", y="Count")
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Follow-up Summary")
        rows = c.execute("SELECT status, COUNT(*) as cnt FROM followups GROUP BY status").fetchall()
        df = pd.DataFrame([{"Status": r["status"], "Count": r["cnt"]} for r in rows])
        fig = px.pie(df, values="Count", names="Status", hole=0.4)
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Patient Risk Distribution")
    rows = c.execute("SELECT risk_status, COUNT(*) as cnt FROM patients GROUP BY risk_status").fetchall()
    df = pd.DataFrame([{"Risk": r["risk_status"], "Count": r["cnt"]} for r in rows])
    fig = px.bar(df, x="Risk", y="Count", color="Risk",
                 color_discrete_map={"GREEN": "#2e7d32", "YELLOW": "#e8710a", "RED": "#d32f2f"})
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    c.close()


# =============================================================================
# MAIN ROUTER
# =============================================================================
def main():
    if not st.session_state.logged_in:
        landing_page()
        return

    render_sidebar()

    page = st.session_state.page
    pages_map = {
        "Dashboard": page_dashboard,
        "Patients": page_patients,
        "Digital Triage": page_triage,
        "Appointments": page_appointments,
        "Teleconsultation": page_teleconsultation,
        "Health Records": page_health_records,
        "Referrals": page_referrals,
        "Medicines": page_medicines,
        "Diagnostics": page_diagnostics,
        "Follow-ups": page_followups,
        "Reports": page_reports,
    }
    fn = pages_map.get(page, page_dashboard)
    fn()

    # Footer notice
    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center; color:#888; font-size:13px;'>"
        f"🏥 RuralCare Maharashtra | SIH26133 | ⚠️ {t('prototype_notice')}</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
