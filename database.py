"""
database.py
SQLite database setup and demo-data seeding for RuralCare Maharashtra.

This module is responsible for:
- Creating the SQLite database file (healthcare.db)
- Creating all required tables
- Seeding fictional demo data on first run

IMPORTANT: All patient/personal data here is FICTIONAL and generated for
hackathon prototype demonstration only. No real patient data is used.
"""

import os
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthcare.db")


# -----------------------------------------------------------------------------
# Connection helper
# -----------------------------------------------------------------------------
def get_connection():
    """Return a SQLite connection. Creates the DB file if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# -----------------------------------------------------------------------------
# Schema creation
# -----------------------------------------------------------------------------
def create_tables():
    """Create all application tables if they do not already exist."""
    conn = get_connection()
    c = conn.cursor()

    # ---- Users (role-based login) -------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            facility_id INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
        """
    )

    # ---- Facilities (public health facilities) ------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            district TEXT NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
        """
    )

    # ---- Doctors ------------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            facility_id INTEGER NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
        """
    )

    # ---- Patients -----------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            village TEXT NOT NULL,
            district TEXT NOT NULL,
            language TEXT DEFAULT 'English',
            blood_group TEXT,
            existing_conditions TEXT,
            allergies TEXT,
            current_medications TEXT,
            emergency_contact TEXT,
            risk_status TEXT DEFAULT 'GREEN',
            registered_by INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (registered_by) REFERENCES users(id)
        )
        """
    )

    # ---- Appointments -------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            facility_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            token_number INTEGER,
            status TEXT DEFAULT 'Scheduled',
            reason TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
        """
    )

    # ---- Triage records -----------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS triage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            temperature REAL,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            heart_rate INTEGER,
            spo2 INTEGER,
            blood_glucose INTEGER,
            symptoms TEXT,
            pregnancy_status TEXT DEFAULT 'Not Applicable',
            suggested_category TEXT NOT NULL,
            final_category TEXT NOT NULL,
            override_reason TEXT,
            reason TEXT,
            recommended_action TEXT,
            recorded_by INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (recorded_by) REFERENCES users(id)
        )
        """
    )

    # ---- Consultations ------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            triage_id INTEGER,
            consultation_notes TEXT,
            diagnosis TEXT,
            is_teleconsultation INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (triage_id) REFERENCES triage_records(id)
        )
        """
    )

    # ---- Prescriptions ------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            consultation_id INTEGER,
            medicine TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id),
            FOREIGN KEY (consultation_id) REFERENCES consultations(id)
        )
        """
    )

    # ---- Referrals ----------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            referring_facility_id INTEGER NOT NULL,
            destination_facility_id INTEGER NOT NULL,
            department TEXT,
            reason TEXT,
            priority TEXT DEFAULT 'NORMAL',
            status TEXT DEFAULT 'Created',
            referral_date TEXT NOT NULL,
            appointment_date TEXT,
            created_by INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (referring_facility_id) REFERENCES facilities(id),
            FOREIGN KEY (destination_facility_id) REFERENCES facilities(id)
        )
        """
    )

    # ---- Medicines (stock per facility) -------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            facility_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 50,
            last_updated TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
        """
    )

    # ---- Diagnostics --------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS diagnostics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            facility_id INTEGER NOT NULL,
            available INTEGER DEFAULT 1,
            waiting_time_min INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
        """
    )

    # ---- Follow-ups ---------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            condition_label TEXT,
            last_visit TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'Due Soon',
            assigned_worker_id INTEGER,
            referral_id INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (assigned_worker_id) REFERENCES users(id),
            FOREIGN KEY (referral_id) REFERENCES referrals(id)
        )
        """
    )

    # ---- Notifications ------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'info',
            patient_id INTEGER,
            referral_id INTEGER,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
        """
    )

    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# Password hashing
# -----------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (sufficient for a prototype)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# -----------------------------------------------------------------------------
# Seed demo data
# -----------------------------------------------------------------------------
def seed_data_if_empty():
    """Insert fictional demo data only if the users table is empty."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    today = datetime.now().date()

    # ---- Users --------------------------------------------------------------
    demo_users = [
        ("patient_demo", "patient123", "Patient", "Demo Patient", None),
        ("worker_demo", "worker123", "Health Worker", "Anita Deshmukh", None),
        ("doctor_demo", "doctor123", "Doctor", "Dr. Rajesh Kulkarni", None),
        ("admin_demo", "admin123", "Facility Admin", "Suresh Patil", None),
    ]
    for username, pwd, role, name, fid in demo_users:
        c.execute(
            "INSERT INTO users (username, password_hash, role, full_name, facility_id) "
            "VALUES (?,?,?,?,?)",
            (username, hash_password(pwd), role, name, fid),
        )

    # ---- Facilities ---------------------------------------------------------
    facilities = [
        ("Sub-Centre Melur", "Sub-centre", "Madurai", "9000010001"),
        ("PHC Usilampatti", "PHC", "Madurai", "9000010002"),
        ("PHC Thirumangalam", "PHC", "Madurai", "9000010003"),
        ("Rural Hospital Vadipatti", "Rural Hospital", "Madurai", "9000010004"),
        ("District Hospital Madurai", "District Hospital", "Madurai", "9000010005"),
    ]
    for name, ftype, district, phone in facilities:
        c.execute(
            "INSERT INTO facilities (name, type, district, phone) VALUES (?,?,?,?)",
            (name, ftype, district, phone),
        )
    facility_ids = [r[0] for r in c.execute("SELECT id FROM facilities").fetchall()]

    # Assign users to facilities
    c.execute("UPDATE users SET facility_id=? WHERE username='worker_demo'", (facility_ids[1],))
    c.execute("UPDATE users SET facility_id=? WHERE username='doctor_demo'", (facility_ids[1],))
    c.execute("UPDATE users SET facility_id=? WHERE username='admin_demo'", (facility_ids[1],))

    # ---- Doctors ------------------------------------------------------------
    doctors = [
        ("Dr. Rajesh Kulkarni", "General Medicine", facility_ids[1]),
        ("Dr. Meera Nair", "Pediatrics", facility_ids[1]),
        ("Dr. Sunil Joshi", "Gynecology", facility_ids[3]),
        ("Dr. Priya Sharma", "Cardiology", facility_ids[4]),
        ("Dr. Arjun Reddy", "Dermatology", facility_ids[4]),
    ]
    for name, spec, fid in doctors:
        c.execute(
            "INSERT INTO doctors (name, specialty, facility_id, phone) VALUES (?,?,?,?)",
            (name, spec, fid, "90000" + str(random.randint(10000, 99999))),
        )
    doctor_ids = [r[0] for r in c.execute("SELECT id FROM doctors").fetchall()]

    # Link doctor_demo to Dr. Rajesh
    c.execute("UPDATE users SET full_name='Dr. Rajesh Kulkarni' WHERE username='doctor_demo'")

    # ---- Patients (20 fictional) -------------------------------------------
    first_names = [
        "Ramesh", "Sunita", "Karthik", "Lakshmi", "Mohan", "Deepa", "Arjun",
        "Kavita", "Suresh", "Geeta", "Vijay", "Meena", "Anil", "Radha",
        "Prakash", "Jyoti", "Naveen", "Shanti", "Ganesh", "Usha",
    ]
    last_names = [
        "Yadav", "Patil", "Reddy", "Sharma", "Iyer", "Deshmukh", "Nair",
        "Kulkarni", "Pillai", "Menon",
    ]
    villages = ["Melur", "Usilampatti", "Thirumangalam", "Vadipatti", "Kottampatti"]
    conditions_list = ["Diabetes", "Hypertension", "Asthma", "None", "None", "Arthritis"]
    blood_groups = ["A+", "B+", "O+", "AB+", "A-", "O-"]
    languages = ["English", "मराठी", "हिंदी"]

    patient_ids = []
    for i in range(20):
        code = f"MH-P-{1001 + i}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(5, 78)
        gender = random.choice(["Male", "Female"])
        phone = "90000" + str(random.randint(10000, 99999))
        village = random.choice(villages)
        risk = random.choices(["GREEN", "YELLOW", "RED"], weights=[70, 25, 5])[0]
        c.execute(
            """INSERT INTO patients
               (patient_code, name, age, gender, phone, village, district,
                language, blood_group, existing_conditions, allergies,
                current_medications, emergency_contact, risk_status, registered_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                code, name, age, gender, phone, village, "Madurai",
                random.choice(languages), random.choice(blood_groups),
                random.choice(conditions_list),
                random.choice(["None", "Penicillin", "Dust", "Peanuts"]),
                random.choice(["None", "Metformin", "Amlodipine", "Insulin"]),
                "90000" + str(random.randint(10000, 99999)),
                risk, 2,  # worker_demo
            ),
        )
        patient_ids.append(c.lastrowid)

    # Link patient_demo to first patient
    c.execute("UPDATE users SET full_name=(SELECT name FROM patients WHERE id=?) WHERE username='patient_demo'", (patient_ids[0],))

    # ---- Triage records (demo) ---------------------------------------------
    for i in range(8):
        pid = patient_ids[i]
        spo2 = random.choice([96, 97, 98, 92, 88, 95, 94, 99])
        cat = "RED" if spo2 < 90 else ("YELLOW" if spo2 < 94 else "GREEN")
        c.execute(
            """INSERT INTO triage_records
               (patient_id, temperature, systolic_bp, diastolic_bp, heart_rate,
                spo2, blood_glucose, symptoms, pregnancy_status,
                suggested_category, final_category, reason, recommended_action,
                recorded_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                pid,
                round(random.uniform(97, 102), 1),
                random.randint(110, 150),
                random.randint(70, 95),
                random.randint(60, 110),
                spo2,
                random.randint(80, 180),
                random.choice(["Fever", "Cough", "Chest pain", "Fatigue", "Headache"]),
                "Not Applicable",
                cat, cat,
                "Demo triage record",
                "See doctor" if cat != "GREEN" else "Routine",
                2,
            ),
        )

    # ---- Appointments (demo) -----------------------------------------------
    import random as _r
    for i in range(12):
        pid = patient_ids[i % 20]
        did = doctor_ids[i % len(doctor_ids)]
        fid = facility_ids[1]
        adate = (today + timedelta(days=_r.randint(-2, 7))).isoformat()
        c.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, facility_id, appointment_date, token_number,
                status, reason)
               VALUES (?,?,?,?,?,?,?)""",
            (pid, did, fid, adate, i + 1,
             "Scheduled" if adate >= today.isoformat() else "Completed",
             _r.choice(["Fever", "Check-up", "Follow-up", "Hypertension"])),
        )

    # ---- Consultations ------------------------------------------------------
    for i in range(5):
        c.execute(
            """INSERT INTO consultations
               (patient_id, doctor_id, consultation_notes, diagnosis, is_teleconsultation)
               VALUES (?,?,?,?,?)""",
            (
                patient_ids[i],
                doctor_ids[0],
                "Patient examined. Symptoms consistent with viral fever.",
                "Viral fever" if i % 2 == 0 else "Hypertension",
                1 if i % 2 == 0 else 0,
            ),
        )

    # ---- Prescriptions ------------------------------------------------------
    med_names = ["Paracetamol", "Amoxicillin", "Metformin", "Amlodipine", "Cetrizine"]
    for i in range(5):
        c.execute(
            """INSERT INTO prescriptions
               (patient_id, doctor_id, medicine, dosage, frequency, duration)
               VALUES (?,?,?,?,?,?)""",
            (
                patient_ids[i],
                doctor_ids[0],
                med_names[i],
                "500mg",
                "Twice daily",
                "5 days",
            ),
        )

    # ---- Referrals (15) -----------------------------------------------------
    statuses = [
        "Created", "Accepted", "Appointment Scheduled", "Patient Attended",
        "Consultation Completed", "Follow-up Scheduled",
    ]
    for i in range(15):
        pid = patient_ids[i % 20]
        ref_date = (today - timedelta(days=random.randint(1, 30))).isoformat()
        appt_date = (today + timedelta(days=random.randint(-5, 10))).isoformat()
        status = statuses[i % len(statuses)]
        c.execute(
            """INSERT INTO referrals
               (patient_id, referring_facility_id, destination_facility_id,
                department, reason, priority, status, referral_date,
                appointment_date, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                pid,
                facility_ids[random.randint(0, 3)],
                facility_ids[4],
                random.choice(["Cardiology", "Pediatrics", "Gynecology", "General Medicine"]),
                random.choice(["Needs specialist evaluation", "Advanced diagnostics required", "Suspected complication"]),
                random.choice(["NORMAL", "HIGH", "URGENT"]),
                status,
                ref_date,
                appt_date,
                2,
            ),
        )
    referral_ids = [r[0] for r in c.execute("SELECT id FROM referrals").fetchall()]

    # ---- Medicines (15 medicines across facilities) ------------------------
    all_meds = [
        "Paracetamol", "Amoxicillin", "Metformin", "Amlodipine", "Cetrizine",
        "Azithromycin", "Ranitidine", "Omeprazole", "Aspirin", "Insulin",
        "Iron Tablets", "ORS Sachets", "Ciprofloxacin", "Diclofenac", "Pantoprazole",
    ]
    for med in all_meds:
        # Distribute each medicine to 2-3 facilities
        for fid in random.sample(facility_ids, random.randint(2, 3)):
            qty = random.choice([0, 25, 80, 200, 450, 600])
            c.execute(
                "INSERT INTO medicines (name, facility_id, quantity, min_stock) VALUES (?,?,?,?)",
                (med, fid, qty, 50),
            )

    # ---- Diagnostics (10 tests across facilities) --------------------------
    tests = ["CBC", "Blood Glucose", "Urine Test", "X-ray", "Ultrasound", "ECG", "Hemoglobin", "Widal", "Malaria Smear", "Dengue Test"]
    for test in tests:
        for fid in facility_ids:
            avail = random.choice([0, 1])
            wait = random.randint(0, 120) if avail else 0
            c.execute(
                "INSERT INTO diagnostics (test_name, facility_id, available, waiting_time_min) VALUES (?,?,?,?)",
                (test, fid, avail, wait),
            )

    # ---- Follow-ups (15) ---------------------------------------------------
    cats = ["Maternal health", "Child health", "Diabetes", "Hypertension", "Elderly", "Other high-risk"]
    fstatuses = ["Completed", "Due Soon", "Overdue"]
    for i in range(15):
        pid = patient_ids[i % 20]
        last_visit = (today - timedelta(days=random.randint(5, 40))).isoformat()
        due = (today + timedelta(days=random.randint(-15, 20))).isoformat()
        if due < today.isoformat():
            fstat = "Overdue"
        elif (today.isoformat() <= due <= (today + timedelta(days=7)).isoformat()):
            fstat = "Due Soon"
        else:
            fstat = "Completed"
        c.execute(
            """INSERT INTO followups
               (patient_id, category, condition_label, last_visit, due_date,
                status, assigned_worker_id)
               VALUES (?,?,?,?,?,?,?)""",
            (pid, cats[i % len(cats)], cats[i % len(cats)], last_visit, due, fstat, 2),
        )

    # ---- Notifications ------------------------------------------------------
    c.execute(
        "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
        ("referral", "Referral #1 appointment date passed without completion.", "warning"),
    )
    c.execute(
        "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
        ("followup", "3 follow-ups are overdue and require contact.", "warning"),
    )
    c.execute(
        "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
        ("medicine", "Amoxicillin stock is low at PHC Usilampatti.", "info"),
    )
    c.execute(
        "INSERT INTO notifications (type, message, severity) VALUES (?,?,?)",
        ("diagnostic", "X-ray unavailable at Sub-Centre Melur.", "info"),
    )

    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# Initialize on import
# -----------------------------------------------------------------------------
def init_db():
    """Create tables and seed demo data. Called once on app startup."""
    create_tables()
    seed_data_if_empty()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
