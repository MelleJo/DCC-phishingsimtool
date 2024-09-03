import autogen
import streamlit as st
from tavily import TavilyClient
from config import get_anthropic_api_key, get_tavily_api_key, get_model_name, get_max_tokens, get_temperature
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Initialize Tavily client
tavily_client = TavilyClient(api_key=get_tavily_api_key())

# Initialize ChatAnthropic for Haiku
@st.cache_resource
def get_haiku_chat():
    return ChatAnthropic(
        model="claude-3-haiku-20240307",
        anthropic_api_key=get_anthropic_api_key(),
        max_tokens_to_sample=1000,
        temperature=0.7,
    )

haiku_chat = get_haiku_chat()

# Initialize ChatAnthropic for main tasks
@st.cache_resource
def get_main_chat():
    return ChatAnthropic(
        model=get_model_name(),
        anthropic_api_key=get_anthropic_api_key(),
        max_tokens_to_sample=get_max_tokens(),
        temperature=get_temperature(),
    )

main_chat = get_main_chat()

def generate_context_questions(business_type, email_type):
    prompt = f"""Generate 5 relevant questions to gather context for creating a phishing simulation email for a {business_type}. 
    The email will be {email_type} (from a colleague/boss if internal, or from a client/vendor/etc. if external).
    Questions should help in creating a realistic scenario. Only provide the questions, no additional text."""
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = haiku_chat.invoke(messages)
        questions = response.content.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        st.error(f"Error in generating context questions: {str(e)}")
        return []

@st.cache_data
def conduct_research(query):
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return [result['content'] for result in response['results']]
    except Exception as e:
        st.error(f"Error in Tavily search: {str(e)}")
        return []

def generate_email_ideas(business_type, email_type, context_answers, research_results):
    prompt = f"""Create 6 different ideas for phishing emails based on the following information:
    Business Type: {business_type}
    Email Type: {email_type}
    Context: {context_answers}
    Research Results: {research_results}
    
    For each idea, provide:
    1. Email subject
    2. Sender description
    3. Main phishing tactic
    4. Relevance to the business type and context
    
    Number the ideas from 1 to 6. Provide only the ideas, no additional text."""
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = main_chat.invoke(messages)
        ideas = response.content.strip().split("\n\n")
        return [idea.strip() for idea in ideas if idea.strip()]
    except Exception as e:
        st.error(f"Error in generating email ideas: {str(e)}")
        return []

def generate_full_email(business_type, email_type, context_answers, research_results, selected_idea):
    prompt = f"""Create a full phishing simulation email based on the following information:
    Business Type: {business_type}
    Email Type: {email_type}
    Context: {context_answers}
    Research Results: {research_results}
    Selected Idea: {selected_idea}
    
    Provide the following:
    1. Subject line
    2. Sender (name and email address)
    3. Full email body
    4. List of phishing indicators
    5. Explanation of why these indicators are suspicious
    
    Use the following format:
    <email>
    <subject>Subject line here</subject>
    <sender>Name <email@example.com></sender>
    <body>
    Full email content here...
    </body>
    <indicators>
    - Indicator 1
    - Indicator 2
    - Indicator 3
    </indicators>
    <explanation>
    Explanation of indicators here...
    </explanation>
    </email>
    """
    
    messages = [HumanMessage(content=prompt)]
    
    try:
        response = main_chat.invoke(messages)
        return response.content.strip()
    except Exception as e:
        st.error(f"Error in generating full email: {str(e)}")
        return None