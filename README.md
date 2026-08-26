# 🏥 RuralCare Maharashtra

**Connecting rural patients to timely, continuous and quality public healthcare.**

A Streamlit-based hackathon prototype for the **Smart India Hackathon 2026** problem
**SIH26133 – Accessibility & Quality of Public Healthcare Services in Rural Maharashtra**.

> ⚠️ **Prototype system. Not for production clinical use.**
> All patient data is fictional and generated for demonstration only.

---

## Project Overview

RuralCare Maharashtra demonstrates how technology can strengthen the existing
public healthcare system in rural areas by improving **access**, **continuity**,
**referral tracking**, **triage**, **specialist consultation**, **medicine /
diagnostic visibility** and **follow-up**.

The central workflow maps directly to the SIH26133 problem statement:

```
Patient Registration → Vitals → Digital Triage → Doctor Consultation
→ Prescription / Referral → Referral Tracking → Follow-up
```

This is **not** a generic hospital management system. It is an integrated rural
healthcare support platform built around continuity of care.

---

## SIH Problem Addressed

**SIH26133 – Accessibility & Quality of Public Healthcare Services in Rural Maharashtra**

Key themes addressed:

- **Access** — teleconsultation, triage, medicine/diagnostic search across facilities
- **Continuity** — longitudinal health records, referrals, follow-ups
- **Accountability** — facility dashboards, quality monitoring, rankings
- **Low connectivity** — offline simulation with sync
- **Multilingual** — English, Marathi (मराठी), Hindi (हिंदी)

---

## Features

1. **Patient Registration** — Health Worker registers patients with auto-generated IDs
2. **Patient Profile** — detailed info, medical summary, medical timeline
3. **Digital Triage** — transparent rule-based decision support (RED/YELLOW/GREEN) with override
4. **Assisted Teleconsultation** — realistic demo interface with notes, prescription, referral, follow-up
5. **Referral Tracking** — visual progress tracker, status updates, overdue detection
6. **Medicine Availability** — search medicines across facilities, stock status, admin updates
7. **Diagnostic Availability** — search tests, waiting times, admin updates
8. **Follow-up Management** — categories, overdue tracking, contact actions
9. **Facility Dashboard** — KPIs and Plotly charts (patient load, referrals, stock, follow-ups)
10. **Quality Monitoring** — facility comparison and "facilities requiring attention" flags
11. **Impact Dashboard** — demo metrics for prototype evaluation
12. **Multilingual Support** — English / Marathi / Hindi
13. **Low-Connectivity Demo** — offline simulation with pending sync
14. **Emergency Escalation** — auto-triggered on RED triage, emergency referral creation
15. **Notifications** — overdue referrals, follow-ups, low stock, emergencies

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| UI Framework | Streamlit |
| Database | SQLite |
| Data handling | Pandas |
| Charts | Plotly |
| Passwords | hashlib (SHA-256) |

No React. No Node.js. No separate backend server. Runs entirely with Streamlit.

---

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

```bash
streamlit run app.py
```

The SQLite database (`healthcare.db`) is created automatically on first run and
populated with fictional demo data.

---

## Demo Accounts

On the landing page, click any of the four demo role buttons to enter instantly:

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| Patient | `patient_demo` | `patient123` | View own records, appointments, prescriptions, referrals, follow-ups, search medicines/diagnostics |
| Health Worker | `worker_demo` | `worker123` | Register patients, record vitals, triage, referrals, follow-ups, assist teleconsultations |
| Doctor | `doctor_demo` | `doctor123` | View patients, consultations, prescriptions, referrals, follow-ups |
| Facility Admin | `admin_demo` | `admin123` | Facility dashboard, quality monitoring, medicine/diagnostic updates |

No password entry needed for the demo — just click the role button.

---

## File Structure

```
ruralcare/
├── app.py              # Main Streamlit application (all pages)
├── database.py         # SQLite schema + demo data seeding
├── triage.py           # Rule-based triage decision logic
├── utils.py            # i18n translations, styling helpers, session state
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── healthcare.db       # Auto-created SQLite database
```

---

## Database Structure

Tables created automatically:

| Table | Purpose |
|-------|---------|
| `users` | Role-based login (Patient, Health Worker, Doctor, Facility Admin) |
| `patients` | Patient demographics and medical summary |
| `facilities` | Public health facilities (Sub-centre, PHC, Rural Hospital, District Hospital) |
| `doctors` | Doctors with specialties |
| `appointments` | Appointment scheduling with tokens |
| `triage_records` | Vitals + triage category + reasons |
| `consultations` | Consultation notes + diagnosis |
| `prescriptions` | Medicine prescriptions |
| `referrals` | Referrals with status tracking |
| `medicines` | Medicine stock per facility |
| `diagnostics` | Diagnostic test availability per facility |
| `followups` | Follow-up tracking with categories |
| `notifications` | System notifications |

### Demo Data (auto-seeded on first run)

- 20 fictional patients across rural villages (Melur, Usilampatti, Thirumangalam, Vadipatti)
- 5 doctors (General Medicine, Pediatrics, Gynecology, Cardiology, Dermatology)
- 5 facilities (Sub-centre, 2 PHCs, Rural Hospital, District Hospital)
- 15 medicines with varied stock levels
- 10 diagnostic services
- 15 referrals with different statuses
- 15 follow-ups (completed, due, overdue)

---

## Main Demo Workflow

The application is designed for easy demonstration to SIH judges:

1. **Health Worker** logs in
2. **Registers** a new patient → gets auto-generated Patient ID
3. **Records vitals** via Digital Triage page
4. **Runs triage** → system identifies 🟡 Consultation Required
5. **Starts assisted teleconsultation** — doctor sees patient history, vitals, triage
6. **Doctor** records consultation notes
7. **Doctor** creates prescription
8. **Doctor** creates referral to District Hospital
9. **Patient/Health Worker** tracks referral through status stages
10. **Follow-up** is scheduled automatically on referral completion
11. **Facility Admin** dashboard reflects all activity

---

## Limitations

- **Prototype only** — not for production clinical use
- Teleconsultation is a **simulated UI**, not real video calling
- Offline mode is a **simulation**, not a production sync architecture
- Triage is **decision-support only** — final decisions rest with qualified professionals
- Demo metrics are **illustrative**, not real government statistics
- No real integration with government health systems

---

## Future Improvements

- Real video teleconsultation via WebRTC
- Production offline-first architecture with conflict resolution
- ABDM (Ayushman Bharat Digital Mission) compliant health records
- Integration with HMIS / DHIS2 government systems
- SMS/WhatsApp notifications for rural users
- Mobile app for health workers (field offline data collection)
- Multi-tenant facility management
- Role-based audit logging

---

## Future Production Integration

This prototype is built to **demonstrate** the workflow and value of an integrated
rural healthcare platform. It does **not** currently integrate with any government
or public-health system.

Potential future integrations (subject to approval and compliance):

- **ABDM (Ayushman Bharat Digital Mission)** — for interoperable health records
  via ABHA IDs and FHIR-compliant data exchange
- **HMIS / DHIS2** — for facility reporting and government dashboards
- **eSanjeevani** — for national teleconsultation integration
- **State Health Society Maharashtra** data standards
- **HL7 FHIR** — for healthcare data interoperability
- **Aadhaar / ABHA** — for patient identity (with consent framework)

Any production deployment would require compliance with the **Digital Personal
Data Protection Act**, medical device regulations, and approval from relevant
health authorities. The prototype makes no claim of such compliance or integration.

---

## Security Notes (Prototype Level)

- Passwords are hashed with SHA-256 (production would use bcrypt/argon2)
- Role-based access control limits what each role can see and do
- No real patient data is used — all data is fictional
- Form inputs are validated
- No database credentials are exposed

---

## License

Built for Smart India Hackathon 2026 prototype demonstration.
