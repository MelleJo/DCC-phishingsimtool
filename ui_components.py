import streamlit as st
from streamlit_antd.tabs import st_antd_tabs
from streamlit_antd.cards import Action, Item, st_antd_cards
from streamlit_antd.steps import Item as StepItem, st_antd_steps
from streamlit_antd.form import st_antd_form
from config import get_config, update_config

def render_main_page():
    tabs = [{"Label": "Generator"}, {"Label": "Instellingen"}]
    tab_event = st_antd_tabs(tabs, key="main_tabs")
    
    active_tab = "Generator"
    if tab_event and isinstance(tab_event, dict) and "payload" in tab_event:
        active_tab = tab_event["payload"].get("Label", "Generator")

    if active_tab == "Generator":
        context = st.text_area("Voer de context in voor de phishing e-mail (bijv. bedrijfsspecifieke informatie, industrie, actuele gebeurtenissen):", height=150)
        difficulty = st.selectbox("Selecteer het moeilijkheidsniveau:", ["Makkelijk", "Gemiddeld", "Moeilijk"])

        steps = [
            StepItem("Input", "Voer de context en het moeilijkheidsniveau in"),
            StepItem("Generatie", "De AI genereert een phishing simulatie e-mail"),
            StepItem("Resultaat", "Bekijk de gegenereerde e-mail en phishing-indicatoren")
        ]
        st_antd_steps(steps, current=1, direction="horizontal")

        return context, difficulty
    elif active_tab == "Instellingen":
        render_settings()
        return None, None

def display_generated_email(result):
    if not result:
        st.error("Er is geen e-mail gegenereerd om weer te geven.")
        return

    sections = result.split("\n\n")
    subject = next((s for s in sections if s.startswith("Onderwerpregel:")), "").replace("Onderwerpregel:", "").strip()
    sender = next((s for s in sections if s.startswith("Afzender:")), "").replace("Afzender:", "").strip()
    body = next((s for s in sections if not s.startswith(("Onderwerpregel:", "Afzender:", "Phishing-indicatoren:", "Uitleg:"))), "")
    indicators = next((s for s in sections if s.startswith("Phishing-indicatoren:")), "").split("\n")[1:]
    explanation = next((s for s in sections if s.startswith("Uitleg:")), "").split("\n")[1:]

    email_card = Item(
        id="generated_email",
        title=f"Onderwerp: {subject}",
        description=f"Van: {sender}\n\n{body}",
        actions=[Action("copy", "CopyOutlined")]
    )
    st_antd_cards([email_card])

    st.subheader("Phishing-indicatoren")
    for indicator in indicators:
        st.markdown(f"- {indicator}")

    st.subheader("Uitleg")
    for point in explanation:
        st.markdown(f"- {point}")

def render_settings():
    config = get_config()
    with st_antd_form("settings_form"):
        st.subheader("AI Model Instellingen")
        model_name = st.text_input("Model Naam", value=config['MODEL_NAME'])
        max_tokens = st.number_input("Max Tokens", value=config['MAX_TOKENS'], min_value=1, max_value=10000)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=config['TEMPERATURE'], step=0.1)
        
        if st.form_submit_button("Instellingen Opslaan"):
            update_config({
                'MODEL_NAME': model_name,
                'MAX_TOKENS': max_tokens,
                'TEMPERATURE': temperature
            })
            st.success("Instellingen zijn opgeslagen!")

def render_debug_info(api_key, model_name, max_tokens, temperature):
    st.subheader("Debug Informatie")
    st.write("API Key (gemaskeerd):", "*" * len(api_key))
    st.write("Model Naam:", model_name)
    st.write("Max Tokens:", max_tokens)
    st.write("Temperature:", temperature)