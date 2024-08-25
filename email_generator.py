import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from config import get_anthropic_api_key, get_model_name, get_max_tokens, get_temperature
import logging
from search_agent import get_authentic_info

# Initialize ChatAnthropic
@st.cache_resource
def get_chat_anthropic():
    try:
        return ChatAnthropic(
            model=get_model_name(),
            anthropic_api_key=get_anthropic_api_key(),
            max_tokens_to_sample=get_max_tokens(),
            temperature=get_temperature(),
        )
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het initialiseren van ChatAnthropic: {str(e)}")
        return None

chat = get_chat_anthropic()

# Define the prompt template
PROMPT_TEMPLATE = """
U hebt de taak om een phishing-simulatie-e-mail te maken op basis van een gegeven context en moeilijkheidsgraad. Uw doel is om een realistisch en educatief voorbeeld van een phishing-poging te produceren dat kan worden gebruikt voor trainingsdoeleinden.
Lees eerst zorgvuldig de volgende context en moeilijkheidsgraad:
<context>
{context}
</context>
<difficulty>{difficulty}</difficulty>

Gebruik de volgende authentieke informatie in uw e-mail:
<authentic_info>
Website: {website}
E-mail: {email}
Persoon: {person}
</authentic_info>

Maak nu een phishing-simulatie-e-mail op basis van deze informatie. Volg deze stappen:
1. Analyseer de context en overweeg veelvoorkomende phishing-tactieken die geschikt zouden zijn voor het gegeven moeilijkheidsniveau.
2. Ontwikkel een aannemelijk scenario voor de phishing-poging dat aansluit bij de context en de authentieke informatie gebruikt.
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
5. Gebruik de verstrekte authentieke informatie om de e-mail geloofwaardiger te maken.
6. Pas de verfijning van de phishing-poging aan op basis van het moeilijkheidsniveau (bijvoorbeeld meer voor de hand liggende indicatoren voor eenvoudigere niveaus, meer subtiele voor moeilijkere niveaus).
"""

def generate_phishing_email(context, difficulty):
    try:
        # Get authentic information
        website = get_authentic_info(context, 'website')
        email = get_authentic_info(context, 'email')
        person = get_authentic_info(context, 'person')

        messages = [
            HumanMessage(content=PROMPT_TEMPLATE.format(
                context=context, 
                difficulty=difficulty,
                website=website,
                email=email,
                person=person
            ))
        ]
        st.write("Debug - Sending request to API")  # Debug output
        response = chat.invoke(messages)
        st.write("Debug - Raw API Response:", response.content)  # Debug output
        return response.content
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het genereren van de e-mail: {str(e)}")
        logging.error(f"Fout bij het genereren van e-mail: {str(e)}")
        st.write("Debug - Exception details:", str(e))  # Debug output
        return None