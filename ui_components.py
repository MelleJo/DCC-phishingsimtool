import streamlit as st
import streamlit_antd_components as sac
from config import get_config, update_config, reset_to_defaults, DEFAULT_CONFIG

def render_main_page():
    with sac.tabs([
        sac.TabsItem(label='Generator', icon='robot'),
        sac.TabsItem(label='Instellingen', icon='gear')
    ]):
        if sac.tabs_selected() == 'Generator':
            context = st.text_area("Voer de context in voor de phishing e-mail (bijv. bedrijfsspecifieke informatie, industrie, actuele gebeurtenissen):", height=150)
            difficulty = st.selectbox("Selecteer het moeilijkheidsniveau:", ["Makkelijk", "Gemiddeld", "Moeilijk"])

            sac.steps([
                sac.StepsItem(title='Input', description='Voer de context en het moeilijkheidsniveau in', icon='pencil'),
                sac.StepsItem(title='Generatie', description='De AI genereert een phishing simulatie e-mail', icon='gear'),
                sac.StepsItem(title='Resultaat', description='Bekijk de gegenereerde e-mail en phishing-indicatoren', icon='check')
            ], active=1)

            return context, difficulty
        elif sac.tabs_selected() == 'Instellingen':
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

    sac.card(
        title=f"Onderwerp: {subject}",
        content=[
            sac.text(f"Van: {sender}"),
            sac.divider(),
            sac.text(body)
        ],
        actions=[
            sac.CardAction(label='Kopiëren', icon='copy')
        ]
    )

    st.subheader("Phishing-indicatoren")
    for indicator in indicators:
        st.markdown(f"- {indicator}")

    st.subheader("Uitleg")
    for point in explanation:
        st.markdown(f"- {point}")

def render_settings():
    config = get_config()
    with st.form("settings_form"):
        st.subheader("AI Model Instellingen")
        model_name = st.text_input("Model Naam", value=config['MODEL_NAME'])
        max_tokens = st.number_input("Max Tokens", value=config['MAX_TOKENS'], min_value=1, max_value=10000)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=config['TEMPERATURE'], step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Instellingen Opslaan"):
                update_config({
                    'MODEL_NAME': model_name,
                    'MAX_TOKENS': max_tokens,
                    'TEMPERATURE': temperature
                })
                st.success("Instellingen zijn opgeslagen!")
        
        with col2:
            if st.form_submit_button("Reset naar Standaardinstellingen"):
                reset_to_defaults()
                st.success("Instellingen zijn gereset naar standaardwaarden!")

    st.subheader("Huidige Instellingen")
    st.json(get_config())

    st.subheader("Standaardinstellingen")
    st.json(DEFAULT_CONFIG)

def render_debug_info(api_key, model_name, max_tokens, temperature):
    st.subheader("Debug Informatie")
    st.write("API Key (gemaskeerd):", "*" * len(api_key))
    st.write("Model Naam:", model_name)
    st.write("Max Tokens:", max_tokens)
    st.write("Temperature:", temperature)