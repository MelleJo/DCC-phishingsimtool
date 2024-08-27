import streamlit as st
from tavily import TavilyClient
import os
from anthropic import Anthropic

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize Tavily client
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# Initialize Anthropic client
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def conduct_research(query):
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return [result['content'] for result in response['results']]
    except Exception as e:
        st.error(f"Error in Tavily search: {str(e)}")
        return []

def generate_context_questions(business_type, email_type):
    prompt = f"""Generate 5 relevant questions to gather context for creating a phishing simulation email for a {business_type}. 
    The email will be {email_type} (from a colleague/boss if internal, or from a client/vendor/etc. if external).
    Questions should help in creating a realistic scenario. Only provide the questions, no additional text."""
    
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content = response.content
        if isinstance(content, str):
            questions = content.strip().split('\n')
            return [q.strip() for q in questions if q.strip()]
        elif isinstance(content, list):
            return [q.strip() for q in content if isinstance(q, str) and q.strip()]
        else:
            raise ValueError(f"Unexpected response format: {type(content)}")
    except Exception as e:
        st.error(f"Error in generating context questions: {str(e)}")
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
    
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content.strip().split("\n\n")
    except Exception as e:
        st.error(f"Error in generating email ideas: {str(e)}")
        return []

def generate_full_emails(business_type, email_type, context_answers, research_results, selected_ideas):
    prompt = f"""Create full phishing simulation emails based on the following information:
    Business Type: {business_type}
    Email Type: {email_type}
    Context: {context_answers}
    Research Results: {research_results}
    Selected Ideas: {selected_ideas}
    
    For each email, provide:
    1. Subject line
    2. Sender (name and email address)
    3. Full email body
    4. List of phishing indicators
    5. Explanation of why these indicators are suspicious
    
    Make the emails realistic but ensure no real names or identifiable information is used. Emails should be in Dutch.
    Use the following format for each email:
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
    
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content.strip().split("<email>")[1:]  # Remove the first empty split
    except Exception as e:
        st.error(f"Error in generating full emails: {str(e)}")
        return []