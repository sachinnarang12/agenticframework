"""
Example 5: Clinical Decision Support — Healthcare
==================================================

Pattern: Sequential pipeline with healthcare domain agents
Agents:  NotesAnalyst → DiagnosticAgent → RiskAssessor → TreatmentPlanner → CareSummaryWriter

Takes patient notes and produces a structured clinical decision support report
through five specialist agents that build on each other's analysis.

This demonstrates:
  - Domain-specific system prompts for healthcare
  - Risk flagging layer before treatment recommendations
  - Patient-friendly final summary

Run:
    python examples/05_healthcare.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

PATIENT_NOTES = """
Patient: Male, 58 years old
Chief Complaint: Chest tightness and shortness of breath on exertion for 3 weeks
History: Hypertension (10 years), Type 2 Diabetes (5 years), BMI 31
Medications: Metformin 1000mg BD, Amlodipine 5mg OD, Aspirin 81mg OD
Family History: Father had MI at 62, mother has T2DM
Vitals: BP 148/92, HR 88, SpO2 97%, Temp 36.8C
Recent Labs: HbA1c 8.2%, LDL 4.1 mmol/L, HDL 0.9 mmol/L, Creatinine 105 umol/L
ECG: Sinus rhythm, no ST changes at rest
Lifestyle: Sedentary desk job, ex-smoker (quit 8 years ago), occasional alcohol
Symptoms: No chest pain at rest, no palpitations, mild ankle swelling
"""


def build_agents(client: anthropic.Anthropic) -> dict[str, Agent]:
    return {
        "NotesAnalyst": Agent(
            name="NotesAnalyst",
            system_prompt=(
                "You are a clinical data analyst. Given patient notes, extract and organise:\n"
                "  • Demographics and chief complaint\n"
                "  • Relevant medical history and current medications\n"
                "  • Vital signs and recent investigations\n"
                "  • Key risk factors (cardiovascular, metabolic, lifestyle)\n"
                "  • Red flag symptoms if any\n"
                "Use structured bullet points. Be precise with numbers and units."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "DiagnosticAgent": Agent(
            name="DiagnosticAgent",
            system_prompt=(
                "You are an experienced physician. Given structured patient data, "
                "produce a differential diagnosis ranked by likelihood:\n"
                "  • List top 3-5 diagnoses with brief rationale\n"
                "  • Identify which diagnosis is most likely and why\n"
                "  • List investigations needed to confirm or exclude each\n"
                "Be evidence-based and specific."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "RiskAssessor": Agent(
            name="RiskAssessor",
            system_prompt=(
                "You are a clinical risk assessment specialist. Given patient data and "
                "differential diagnoses, assess:\n"
                "  • Immediate safety concerns (requiring urgent action)\n"
                "  • Cardiovascular risk score (SCORE2 or Framingham factors)\n"
                "  • Drug interaction or contraindication risks\n"
                "  • Monitoring requirements\n"
                "Flag each risk as LOW / MEDIUM / HIGH / URGENT."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "TreatmentPlanner": Agent(
            name="TreatmentPlanner",
            system_prompt=(
                "You are a clinical pharmacist and treatment planning specialist. "
                "Given diagnosis and risk assessment, recommend:\n"
                "  • Immediate management steps\n"
                "  • Medication adjustments (with rationale)\n"
                "  • Lifestyle interventions\n"
                "  • Referrals needed\n"
                "  • Follow-up timeline\n"
                "Base recommendations on current clinical guidelines."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "CareSummaryWriter": Agent(
            name="CareSummaryWriter",
            system_prompt=(
                "You are a patient communication specialist. Write a clear, empathetic "
                "care plan summary structured as:\n"
                "  1. What We Found\n"
                "  2. What This Means For You\n"
                "  3. Your Treatment Plan\n"
                "  4. Important Warning Signs (when to seek urgent help)\n"
                "  5. Your Next Steps\n"
                "Use plain English. Avoid jargon. Be reassuring but honest."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
    }


def run_healthcare_analysis(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents.values():
        orch.register(agent)

    print("\n" + "=" * 60)
    print("CLINICAL DECISION SUPPORT PIPELINE")
    print("=" * 60)

    print("\n[Step 1/5] Notes Analyst — extracting structured data")
    structured_data = orch.send(
        to="NotesAnalyst",
        message=f"Extract and organise all clinical data from these patient notes:\n\n{PATIENT_NOTES}",
        from_name="User",
    )

    print("\n[Step 2/5] Diagnostic Agent — differential diagnosis")
    differential = orch.send(
        to="DiagnosticAgent",
        message=f"Generate a differential diagnosis based on:\n\n{structured_data}",
        from_name="NotesAnalyst",
    )

    print("\n[Step 3/5] Risk Assessor — flagging risks")
    risk_report = orch.send(
        to="RiskAssessor",
        message=(
            f"Assess clinical risks for this patient.\n\n"
            f"PATIENT DATA:\n{structured_data}\n\n"
            f"DIFFERENTIAL DIAGNOSIS:\n{differential}"
        ),
        from_name="DiagnosticAgent",
    )

    print("\n[Step 4/5] Treatment Planner — management plan")
    treatment_plan = orch.send(
        to="TreatmentPlanner",
        message=(
            f"Develop a treatment and management plan.\n\n"
            f"DIAGNOSIS:\n{differential}\n\n"
            f"RISK ASSESSMENT:\n{risk_report}"
        ),
        from_name="RiskAssessor",
    )

    print("\n[Step 5/5] Care Summary Writer — patient-friendly summary")
    care_summary = orch.send(
        to="CareSummaryWriter",
        message=(
            f"Write a patient-friendly care plan summary.\n\n"
            f"CLINICAL FINDINGS:\n{structured_data}\n\n"
            f"DIAGNOSIS:\n{differential}\n\n"
            f"RISKS:\n{risk_report}\n\n"
            f"TREATMENT PLAN:\n{treatment_plan}"
        ),
        from_name="TreatmentPlanner",
    )

    output_path = "clinical_care_summary.txt"
    with open(output_path, "w") as f:
        f.write("CLINICAL DECISION SUPPORT REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write("DIFFERENTIAL DIAGNOSIS:\n")
        f.write(differential + "\n\n")
        f.write("RISK ASSESSMENT:\n")
        f.write(risk_report + "\n\n")
        f.write("TREATMENT PLAN:\n")
        f.write(treatment_plan + "\n\n")
        f.write("PATIENT CARE SUMMARY:\n")
        f.write(care_summary)
    print(f"\n[Saved] Clinical report → {output_path}")

    print("\n" + "=" * 60)
    print("CLINICAL ANALYSIS COMPLETE")
    print("=" * 60)
    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_healthcare_analysis(client)
