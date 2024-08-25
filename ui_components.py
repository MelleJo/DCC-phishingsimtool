import streamlit as st
from streamlit_antd.tabs import st_antd_tabs
from streamlit_antd.cards import Action, Item, st_antd_cards
from streamlit_antd.steps import Item as StepItem, st_antd_steps

def render_main_page():
    tab_event = st_antd_tabs([{"Label": "Generator"}, {"Label": "Instructies"}], key="main_tabs")

    if tab_event["payload"]["Label"] == "Generator":
        context = st.text_area("Voer de context in voor de phishing e-mail (bijv. bedrijfsspecifieke informatie, industrie, actuele gebeurtenissen):", height=150)
        difficulty = st.selectbox("Selecteer het moeilijkheidsniveau:", ["Makkelijk", "Gemiddeld", "Moeilijk"])

        # Display steps of the process
        steps = [
            StepItem("Input", "Voer de context en het moeilijkheidsniveau in"),
            StepItem("Generatie", "De AI genereert een phishing simulatie e-mail"),
            StepItem("Resultaat", "Bekijk de gegenereerde e-mail en phishing-indicatoren")
        ]
        st_antd_steps(steps, current=1, direction="horizontal")

        return context, difficulty
    elif tab_event["payload"]["Label"] == "Instructies":
        st.write("Hier kunt u instructies toevoegen over hoe de phishing simulatie e-mail generator te gebruiken.")
        return None, None

def display_generated_email(result):
    sections = result.split("\n\n")
    subject = next((s for s in sections if s.startswith("Onderwerpregel:")), "").replace("Onderwerpregel:", "").strip()
    sender = next((s for s in sections if s.startswith("Afzender:")), "").replace("Afzender:", "").strip()
    body = next((s for s in sections if not s.startswith(("Onderwerpregel:", "Afzender:", "Phishing-indicatoren:", "Uitleg:"))), "")
    indicators = next((s for s in sections if s.startswith("Phishing-indicatoren:")), "").split("\n")[1:]
    explanation = next((s for s in sections if s.startswith("Uitleg:")), "").split("\n")[1:]

    # Display generated email in a Card
    email_card = Item(
        id="generated_email",
        title=f"Onderwerp: {subject}",
        description=f"Van: {sender}\n\n{body}",
        actions=[Action("copy", "CopyOutlined")]
    )
    st_antd_cards([email_card])

    # Display phishing indicators and explanation
    st.subheader("Phishing-indicatoren")
    for indicator in indicators:
        st.markdown(f"- {indicator}")

    st.subheader("Uitleg")
    for point in explanation:
        st.markdown(f"- {point}")

def render_debug_info(api_key, model_name, max_tokens, temperature):
    st.subheader("Debug Informatie")
    st.write("API Key (gemaskeerd):", "*" * len(api_key))
    st.write("Model Naam:", model_name)
    st.write("Max Tokens:", max_tokens)
    st.write("Temperature:", temperature)