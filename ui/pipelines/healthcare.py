"""Healthcare: Clinical Decision Support pipeline."""
import streamlit as st
from ui.helpers import run_agent

SAMPLE_NOTES = """Patient: Male, 58. Chief complaint: chest tightness on exertion x3 weeks.
History: Hypertension 10yr, T2DM 5yr, BMI 31. Meds: Metformin, Amlodipine, Aspirin.
Family: Father MI at 62. Vitals: BP 148/92, HR 88, SpO2 97%.
Labs: HbA1c 8.2%, LDL 4.1, HDL 0.9. ECG: sinus rhythm, no ST changes.
Lifestyle: sedentary, ex-smoker (8yr), mild ankle swelling."""


def render(client):
    st.subheader("🏥 Clinical Decision Support — Healthcare")
    st.caption("Paste patient notes. Five agents produce a structured clinical report and patient summary.")

    col1, col2 = st.columns([2, 1])
    with col1:
        notes = st.text_area("Patient notes", value=SAMPLE_NOTES, height=200)
    with col2:
        st.markdown("**Pipeline:**\n1. 📋 Notes Analyst\n2. 🩺 Diagnostic Agent\n"
                    "3. ⚠️ Risk Assessor\n4. 💊 Treatment Planner\n5. 🤝 Care Summary")

    if st.button("▶  Analyse", type="primary", use_container_width=True):
        if not notes.strip():
            st.error("Please enter patient notes.")
            st.stop()
        st.divider()

        h1: list = []
        with st.expander("📋 Step 1 — Notes Analyst", expanded=True):
            structured = run_agent(client, "Notes Analyst", "📋",
                "You are a clinical data analyst. Extract demographics, history, medications, "
                "vitals, investigations, and key risk factors. Use structured bullet points.",
                f"Extract and organise all clinical data:\n\n{notes}", h1)

        h2: list = []
        with st.expander("🩺 Step 2 — Differential Diagnosis", expanded=True):
            differential = run_agent(client, "Diagnostic Agent", "🩺",
                "You are an experienced physician. Produce differential diagnosis ranked by "
                "likelihood. List top 3-5 with rationale and investigations needed.",
                f"Generate differential diagnosis:\n\n{structured}", h2)

        h3: list = []
        with st.expander("⚠️ Step 3 — Risk Assessment", expanded=True):
            risks = run_agent(client, "Risk Assessor", "⚠️",
                "You are a clinical risk specialist. Assess immediate safety concerns, "
                "cardiovascular risk, drug interactions. Flag each: LOW/MEDIUM/HIGH/URGENT.",
                f"Assess clinical risks.\nPATIENT DATA:\n{structured}\nDIAGNOSIS:\n{differential}", h3)

        h4: list = []
        with st.expander("💊 Step 4 — Treatment Plan", expanded=True):
            treatment = run_agent(client, "Treatment Planner", "💊",
                "You are a clinical pharmacist. Recommend immediate management, medication "
                "adjustments, lifestyle interventions, referrals, and follow-up timeline.",
                f"Develop treatment plan.\nDIAGNOSIS:\n{differential}\nRISKS:\n{risks}", h4)

        h5: list = []
        with st.expander("🤝 Step 5 — Patient Care Summary", expanded=True):
            summary = run_agent(client, "Care Summary Writer", "🤝",
                "Write a plain-English patient care summary: 1.What We Found 2.What This Means "
                "3.Your Treatment Plan 4.Warning Signs 5.Next Steps. No jargon.",
                f"Write patient summary.\nFINDINGS:\n{structured}\nDIAGNOSIS:\n{differential}\n"
                f"RISKS:\n{risks}\nTREATMENT:\n{treatment}", h5)

        st.success("✅ Clinical report complete!")
        st.download_button("⬇️ Download Report", data=summary,
            file_name="clinical_care_summary.txt", mime="text/plain")
