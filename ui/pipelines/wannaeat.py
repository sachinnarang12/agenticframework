"""
FlavorSavers — Catering Proposal Generator
=======================================
Chef enters their details + customer inquiry.
Four agents produce a ready-to-send professional catering proposal.
"""
import streamlit as st
from ui.helpers import run_agent

SAMPLE_INQUIRY = """Hi, I'm looking for catering for my wife's 40th birthday dinner.
We'll have 18 guests at our home in West London this Saturday evening.
Looking for something special — Mediterranean or Middle Eastern style.
Two guests are vegetarian, one is gluten-free.
Budget is around £900 total. Would love canapes on arrival too.
Can you send me a proposal?"""


def render(client):
    st.subheader("🍽️ Catering Proposal Generator")
    st.caption("Paste a customer inquiry. Four agents produce a ready-to-send professional proposal in minutes.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**About You (the Chef)**")
        chef_name = st.text_input("Your name", value="Layla Hassan")
        cuisine = st.text_input("Your cuisine style", value="Lebanese & Mediterranean home cooking")
        signature_dishes = st.text_area("Your signature dishes (optional)",
            placeholder="e.g. Slow-roasted lamb shoulder, mezze platters, homemade baklava...",
            height=80)
        experience = st.text_input("Years of experience / background (optional)",
            placeholder="e.g. 12 years, trained in Beirut, specialise in family feasts")

    with col2:
        st.markdown("**Customer's Inquiry**")
        inquiry = st.text_area("Paste the customer message here",
            value=SAMPLE_INQUIRY, height=220)

    st.markdown("**Pipeline:** `📋 Event Analyst` → `🍴 Menu Planner` → `💷 Pricing Agent` → `✉️ Proposal Writer`")

    if st.button("▶  Generate Proposal", type="primary", use_container_width=True):
        if not inquiry.strip():
            st.error("Please paste the customer inquiry.")
            st.stop()
        if not chef_name.strip():
            st.error("Please enter the chef name.")
            st.stop()

        chef_context = (
            f"Chef: {chef_name}\n"
            f"Cuisine: {cuisine}\n"
            f"Signature dishes: {signature_dishes or 'Not specified'}\n"
            f"Background: {experience or 'Not specified'}"
        )

        st.divider()

        h1: list = []
        with st.expander("📋 Step 1 — Event Analyst", expanded=True):
            event_brief = run_agent(client, "Event Analyst", "📋",
                "You are an experienced events coordinator. From a customer inquiry extract:\n"
                "  • Guest count\n"
                "  • Occasion / event type\n"
                "  • Date, time, location type (home/venue)\n"
                "  • Dietary requirements (vegetarian, vegan, allergies)\n"
                "  • Budget (total and per-head estimate)\n"
                "  • Service style preferences (seated, grazing, canapes, etc)\n"
                "  • Any special requests or tone (formal, relaxed, surprise, etc)\n"
                "Be precise. Flag anything unclear as [NEEDS CLARIFICATION].",
                f"Extract the event brief from this customer inquiry:\n\n{inquiry}",
                h1)

        h2: list = []
        with st.expander("🍴 Step 2 — Menu Planner", expanded=True):
            menu = run_agent(client, "Menu Planner", "🍴",
                "You are a creative chef and menu designer. Design a menu that:\n"
                "  • Matches the chef's cuisine style and signature dishes\n"
                "  • Suits the occasion and guest count\n"
                "  • Accommodates all dietary requirements\n"
                "  • Fits within the budget\n"
                "Structure: Canapes (if requested) / Starter / Main / Sides / Dessert\n"
                "For each dish: name, brief description (1 sentence), dietary labels (V/VG/GF)\n"
                "Also note: service style recommendation and any equipment/setup needs.",
                f"Design a menu for this event.\n\nCHEF:\n{chef_context}\n\nEVENT BRIEF:\n{event_brief}",
                h2)

        h3: list = []
        with st.expander("💷 Step 3 — Pricing Agent", expanded=True):
            pricing = run_agent(client, "Pricing Agent", "💷",
                "You are a catering business advisor. Produce a clear pricing breakdown:\n"
                "  • Per-head food cost\n"
                "  • Service / chef fee\n"
                "  • Travel/setup if applicable\n"
                "  • Total price\n"
                "  • Deposit required (recommend 30-50%) and when due\n"
                "  • Balance payment timeline\n"
                "  • Cancellation policy (recommend 50% within 7 days, 100% within 48hrs)\n"
                "  • What's included vs excluded (e.g. crockery, serving staff)\n"
                "Stay within or slightly above the customer's stated budget. "
                "If budget is too low for the brief, note this diplomatically.",
                f"Produce pricing for this catering booking.\n\nEVENT BRIEF:\n{event_brief}\n\nMENU:\n{menu}",
                h3)

        h4: list = []
        with st.expander("✉️ Step 4 — Catering Proposal (Ready to Send)", expanded=True):
            proposal = run_agent(client, "Proposal Writer", "✉️",
                "You are a professional catering business owner writing a proposal to a client. "
                "Write a warm, confident, ready-to-send proposal structured as:\n\n"
                "  Subject: Catering Proposal — [Occasion] for [Guest Count] Guests\n\n"
                "  1. Personal opening (excited to help with their event, 2 sentences)\n"
                "  2. About Me (brief, warm, 2-3 sentences referencing chef background)\n"
                "  3. Your Event (confirm key details back to them)\n"
                "  4. Proposed Menu (formatted clearly with sections)\n"
                "  5. Investment (clean pricing table)\n"
                "  6. What's Included\n"
                "  7. Next Steps (how to confirm, deposit details)\n"
                "  8. Warm closing with contact details placeholder\n\n"
                "Tone: professional but personal. This is home cooking with heart — not a corporate caterer. "
                "Make the client feel excited and confident about booking.",
                f"Write the catering proposal.\n\nCHEF:\n{chef_context}\n\n"
                f"EVENT:\n{event_brief}\n\nMENU:\n{menu}\n\nPRICING:\n{pricing}",
                h4)

        st.success("✅ Proposal ready to send!")
        st.download_button(
            "⬇️ Download Proposal as .txt",
            data=proposal,
            file_name=f"catering_proposal_{chef_name.replace(' ','_').lower()}.txt",
            mime="text/plain"
        )

        st.info("💡 **Tip for your pitch:** Show FlavorSavers that this tool reduces chef response time "
                "from hours to 2 minutes — and a faster response rate directly increases booking conversion.")
