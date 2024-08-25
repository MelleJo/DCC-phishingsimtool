import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Initialize ChatAnthropic for Haiku
@st.cache_resource
def get_haiku_chat():
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        anthropic_api_key=st.secrets["ANTHROPIC_API_KEY"],
        max_tokens_to_sample=1000,
        temperature=0.7,
    )

haiku_chat = get_haiku_chat()

def generate_context_questions(business_type, internal_external):
    prompt = f"""
    Je bent een cybersecurity-expert die een phishing-simulatie voorbereidt voor een {business_type}. 
    De e-mail zal {internal_external.lower()} zijn. 
    Genereer 5 relevante vragen die helpen bij het opbouwen van de context voor een realistische phishing e-mail.
    De vragen moeten specifiek zijn voor het type bedrijf en het soort e-mail (intern/extern).
    Geef alleen de vragen, geen extra tekst.
    """
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = haiku_chat.invoke(messages)
        questions = response.content.strip().split("\n")
        return [q.strip("1234567890-. ") for q in questions if q.strip()]
    except Exception as e:
        st.error(f"Fout bij het genereren van contextvragen: {str(e)}")
        return []