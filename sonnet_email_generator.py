import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Initialize ChatAnthropic for Sonnet
@st.cache_resource
def get_sonnet_chat():
    return ChatAnthropic(
        model="claude-3-sonnet-20240229",
        anthropic_api_key=st.secrets["ANTHROPIC_API_KEY"],
        max_tokens_to_sample=4000,
        temperature=0.7,
    )

sonnet_chat = get_sonnet_chat()

def generate_full_emails(business_type, internal_external, context_answers, research_results, selected_ideas):
    prompt = f"""
    Je bent een expert in het maken van realistische phishing-simulatie e-mails. Maak volledige e-mails gebaseerd op de volgende informatie en ideeën:

    Bedrijfstype: {business_type}
    E-mailtype: {internal_external}

    Context:
    {' '.join([f"{q}: {a}" for q, a in context_answers.items()])}

    Onderzoeksresultaten:
    {' '.join([f"{cat}: {', '.join(items)}" for cat, items in research_results.items()])}

    Geselecteerde ideeën:
    {' '.join(selected_ideas)}

    Voor elke e-mail, geef de volgende onderdelen:
    1. Onderwerp
    2. Afzender (naam en e-mailadres)
    3. Volledige inhoud van de e-mail
    4. Lijst van phishing-indicatoren in de e-mail
    5. Uitleg waarom deze indicatoren verdacht zijn

    Maak de e-mails zo realistisch mogelijk, maar zorg ervoor dat er geen echte namen, e-mailadressen of identificeerbare informatie worden gebruikt. De e-mails moeten in het Nederlands zijn.

    Geef de e-mails in het volgende format:

    <email>
    <subject>Onderwerp hier</subject>
    <sender>Naam <emailadres@voorbeeld.com></sender>
    <body>
    Volledige e-mailinhoud hier...
    </body>
    <indicators>
    - Indicator 1
    - Indicator 2
    - Indicator 3
    </indicators>
    <explanation>
    Uitleg van de indicatoren hier...
    </explanation>
    </email>

    Genereer een e-mail voor elk geselecteerd idee.
    """
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = sonnet_chat.invoke(messages)
        emails = response.content.strip().split("<email>")
        return [email.strip() for email in emails if email.strip()]
    except Exception as e:
        st.error(f"Fout bij het genereren van volledige e-mails: {str(e)}")
        return []