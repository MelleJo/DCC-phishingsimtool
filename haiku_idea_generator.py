import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Initialize ChatAnthropic for Haiku
@st.cache_resource
def get_haiku_chat():
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        anthropic_api_key=st.secrets["ANTHROPIC_API_KEY"],
        max_tokens_to_sample=2000,
        temperature=0.7,
    )

haiku_chat = get_haiku_chat()

def generate_email_ideas(business_type, internal_external, context_answers, research_results):
    prompt = f"""
    Je bent een expert in het maken van phishing-simulaties. Genereer 6 verschillende ideeën voor phishing e-mails gebaseerd op de volgende informatie:

    Bedrijfstype: {business_type}
    E-mailtype: {internal_external}

    Context:
    {' '.join([f"{q}: {a}" for q, a in context_answers.items()])}

    Onderzoeksresultaten:
    {' '.join([f"{cat}: {', '.join(items)}" for cat, items in research_results.items()])}

    Voor elk idee, geef een korte beschrijving van:
    1. Het onderwerp van de e-mail
    2. De vermeende afzender
    3. De belangrijkste phishing-tactiek die wordt gebruikt
    4. Hoe het relevant is voor het bedrijfstype en de context

    Geef alleen de 6 ideeën, geen extra tekst. Nummer ze van 1 tot 6.
    """
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = haiku_chat.invoke(messages)
        ideas = response.content.strip().split("\n\n")
        return [idea.strip() for idea in ideas if idea.strip()]
    except Exception as e:
        st.error(f"Fout bij het genereren van e-mailideeën: {str(e)}")
        return []