import streamlit as st
import streamlit_antd_components as sac
from config import get_config, update_config, reset_to_defaults, DEFAULT_CONFIG
import html

def render_main_page():
    tab = sac.tabs([
        sac.TabsItem(label='Generator', icon='robot'),
        sac.TabsItem(label='Instellingen', icon='gear')
    ])

    if tab == 'Generator':
        context = st.text_area("Voer de context in voor de phishing e-mail (bijv. bedrijfsspecifieke informatie, industrie, actuele gebeurtenissen):", height=150)
        difficulty = st.selectbox("Selecteer het moeilijkheidsniveau:", ["Makkelijk", "Gemiddeld", "Moeilijk"])

        sac.steps([
            sac.StepsItem(title='Input', description='Voer de context en het moeilijkheidsniveau in', icon='pencil'),
            sac.StepsItem(title='Generatie', description='De AI genereert een phishing simulatie e-mail', icon='gear'),
            sac.StepsItem(title='Resultaat', description='Bekijk de gegenereerde e-mail en phishing-indicatoren', icon='check')
        ])

        return context, difficulty
    elif tab == 'Instellingen':
        render_settings()
        return None, None

def display_generated_email(result, debug_info):
    if not result:
        st.error("Er is geen e-mail gegenereerd om weer te geven.")
        return

    try:
        sections = result.split("\n\n")
        subject = next((s for s in sections if s.startswith("Onderwerpregel:")), "").replace("Onderwerpregel:", "").strip()
        sender = next((s for s in sections if s.startswith("Afzender:")), "").replace("Afzender:", "").strip()
        body = next((s for s in sections if not s.startswith(("Onderwerpregel:", "Afzender:", "Phishing-indicatoren:", "Uitleg:"))), "")
        indicators = next((s for s in sections if s.startswith("Phishing-indicatoren:")), "").split("\n")[1:]
        explanation = next((s for s in sections if s.startswith("Uitleg:")), "").split("\n")[1:]

        # Escape the sender information
        sender_name, sender_email = sender.split(" ", 1) if " " in sender else (sender, "")
        sender_email = sender_email.strip("<>")

        st.markdown("""
        <style>
        .email-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            background-color: #f9f9f9;
            font-family: Arial, sans-serif;
        }
        .email-header {
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .email-subject {
            font-size: 18px;
            font-weight: bold;
        }
        .email-sender {
            color: #666;
            margin-top: 5px;
        }
        .email-body {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="email-container">
            <div class="email-header">
                <div class="email-subject">{html.escape(subject)}</div>
                <div class="email-sender">Van: {html.escape(sender_name)} &lt;{html.escape(sender_email)}&gt;</div>
            </div>
            <div class="email-body">
                {html.escape(body).replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Phishing-indicatoren")
        for indicator in indicators:
            st.markdown(f"- {indicator}")

        st.subheader("Uitleg")
        for point in explanation:
            st.markdown(f"- {point}")

        # Expandable debug field
        with st.expander("Debug Informatie"):
            st.subheader("Claude 3.5 Sonnet Request")
            st.json(debug_info['sonnet_request'])
            st.subheader("Claude 3.5 Sonnet Response")
            st.json(debug_info['sonnet_response'])
            st.subheader("Tavily Search Requests")
            for i, request in enumerate(debug_info['tavily_requests'], 1):
                st.write(f"Request {i}:")
                st.json(request)
            st.subheader("Tavily Search Responses")
            for i, response in enumerate(debug_info['tavily_responses'], 1):
                st.write(f"Response {i}:")
                st.json(response)

    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het weergeven van de e-mail: {str(e)}")
        st.write("Ruwe e-mail inhoud:")
        st.write(result)

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