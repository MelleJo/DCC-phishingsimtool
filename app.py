import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import logging
import hashlib
import uuid

# Configureer logging
logging.basicConfig(filename='phishing_generator.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Stel pagina-configuratie in
st.set_page_config(page_title="Interne Phishing Simulatie E-mail Generator", layout="wide")

# Aangepaste CSS (hetzelfde als voorheen)
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Importeer configuratie
from config import get_anthropic_api_key, MAX_TOKENS, TEMPERATURE, MODEL_NAME

# Initialiseer ChatAnthropic
@st.cache_resource
def get_chat_anthropic():
    try:
        return ChatAnthropic(
            model=MODEL_NAME,
            anthropic_api_key=get_anthropic_api_key(),
            max_tokens_to_sample=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het initialiseren van ChatAnthropic: {str(e)}")
        return None

chat = get_chat_anthropic()

if chat is None:
    st.stop()

# Definieer het promptsjabloon
PROMPT_TEMPLATE = """
U hebt de taak om een phishing-simulatie-e-mail te maken op basis van een gegeven context en moeilijkheidsgraad. Uw doel is om een realistisch en educatief voorbeeld van een phishing-poging te produceren dat kan worden gebruikt voor trainingsdoeleinden.
Lees eerst zorgvuldig de volgende context en moeilijkheidsgraad:
<context>
{CONTEXT}
</context>
<difficulty>{DIFFICULTY}</difficulty>
Maak nu een phishing-simulatie-e-mail op basis van deze informatie. Volg deze stappen:
1. Analyseer de context en overweeg veelvoorkomende phishing-tactieken die geschikt zouden zijn voor het gegeven moeilijkheidsniveau.
2. Ontwikkel een aannemelijk scenario voor de phishing-poging dat aansluit bij de context.
3. Maak de e-mailcomponenten, waarbij u ervoor zorgt dat ze het gekozen scenario en moeilijkheidsniveau weerspiegelen.
Geef uw output in het volgende formaat:
<phishing_simulation>
<subject>
[Schrijf hier de onderwerpregel van de e-mail]
</subject>
<sender>
[Geef een fictieve naam en e-mailadres voor de afzender]
</sender>
<email_body>
[Schrijf hier de volledige tekst van de e-mail in het Nederlands]
</email_body>
<phishing_indicators>
[Noem minstens 3 phishing-indicatoren die in de e-mail aanwezig zijn]
</phishing_indicators>
<explanation>
[Geef een korte uitleg voor elke indicator, waarbij u beschrijft waarom deze verdacht is]
</explanation>
</phishing_simulation>
Richtlijnen voor het maken van een realistische phishing-simulatie:
1. Zorg ervoor dat de e-mail volledig in het Nederlands is geschreven.
2. Verwerk veelvoorkomende phishing-tactieken die passen bij het opgegeven moeilijkheidsniveau.
3. Maak de inhoud van de e-mail relevant voor de gegeven context.
4. Gebruik taal en opmaak die legitieme e-mails nabootsen, maar bevat subtiele waarschuwingssignalen.
5. Gebruik geen echte namen, e-mailadressen of identificeerbare informatie in de gegenereerde inhoud.
6. Pas de verfijning van de phishing-poging aan op basis van het moeilijkheidsniveau (bijvoorbeeld meer voor de hand liggende indicatoren voor eenvoudigere niveaus, meer subtiele voor moeilijkere niveaus).
"""

# Functie om e-mail te genereren
def generate_email(context, difficulty):
    try:
        messages = [
            HumanMessage(content=PROMPT_TEMPLATE.format(context=context, difficulty=difficulty))
        ]
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het genereren van de e-mail: {str(e)}")
        logging.error(f"Fout bij het genereren van e-mail: {str(e)}")
        return None

# Anonimisatiefunctie
def anonymize_input(input_text):
    return hashlib.sha256(input_text.encode()).hexdigest()[:10]

# Genereer unieke sessie-ID
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Streamlit-app
st.title("Interne Phishing Simulatie E-mail Generator")

# Gebruikersinvoer
context = st.text_area("Voer de context in voor de phishing e-mail (bijv. bedrijfsspecifieke informatie, industrie, actuele gebeurtenissen):", height=150)
difficulty = st.selectbox("Selecteer het moeilijkheidsniveau:", ["Makkelijk", "Gemiddeld", "Moeilijk"])

if st.button("Genereer Phishing E-mail"):
    if context:
        with st.spinner("Phishing e-mail wordt gegenereerd..."):
            # Anonimiseer invoer voor logging
            anon_context = anonymize_input(context)
            
            # Log geanonimiseerd gebruik
            logging.info(f"Sessie ID: {st.session_state['session_id']}, Context: {anon_context}, Moeilijkheidsgraad: {difficulty}")
            
            result = generate_email(context, difficulty)
            
            if result:
                # Parseer en toon resultaten
                sections = result.split("\n\n")
                subject = next((s for s in sections if s.startswith("Onderwerpregel:")), "").replace("Onderwerpregel:", "").strip()
                sender = next((s for s in sections if s.startswith("Afzender:")), "").replace("Afzender:", "").strip()
                body = next((s for s in sections if not s.startswith(("Onderwerpregel:", "Afzender:", "Phishing-indicatoren:", "Uitleg:"))), "")
                indicators = next((s for s in sections if s.startswith("Phishing-indicatoren:")), "").split("\n")[1:]
                explanation = next((s for s in sections if s.startswith("Uitleg:")), "").split("\n")[1:]
                
                st.subheader("Gegenereerde Phishing E-mail")
                st.text(f"Van: {sender}")
                st.text(f"Onderwerp: {subject}")
                st.text_area("E-mailtekst:", value=body, height=200)
                
                st.subheader("Phishing-indicatoren")
                for indicator in indicators:
                    st.markdown(f"- {indicator}")
                
                st.subheader("Uitleg")
                for point in explanation:
                    st.markdown(f"- {point}")
    else:
        st.warning("Voer alstublieft de context in voor de phishing e-mail.")

# Voeg een voettekst toe
st.markdown("---")
st.markdown("Interne tool voor Uw Cyberbeveiligingsbedrijf | Aangedreven door Claude 3.5 Sonnet")