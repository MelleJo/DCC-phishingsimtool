from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import get_anthropic_api_key, get_config, get_tavily_api_key
from tavily import TavilyClient
import streamlit as st

# Initialize AI models and clients
config = get_config()
chat_model = ChatAnthropic(
    anthropic_api_key=get_anthropic_api_key(),
    model_name=config['MODEL_NAME'],
    max_tokens_to_sample=config['MAX_TOKENS'],
    temperature=config['TEMPERATURE']
)
tavily_client = TavilyClient(api_key=get_tavily_api_key())

def generate_context_questions(business_type, email_type):
    prompt = PromptTemplate(
        input_variables=["business_type", "email_type"],
        template="Generate 5 relevant questions to gather context for creating a phishing simulation email for a {business_type}. The email will be {email_type} (from a colleague/boss if internal, or from a client/vendor/etc. if external). Questions should help in creating a realistic scenario."
    )
    chain = LLMChain(llm=chat_model, prompt=prompt)
    result = chain.run(business_type=business_type, email_type=email_type)
    return result.strip().split("\n")

def conduct_research(query):
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return [result['content'] for result in response['results']]
    except Exception as e:
        st.error(f"Error in Tavily search: {str(e)}")
        return []

def generate_email_ideas(business_type, email_type, context_answers, research_results):
    prompt = PromptTemplate(
        input_variables=["business_type", "email_type", "context", "research"],
        template="Create 6 different ideas for phishing emails based on the following information:\nBusiness Type: {business_type}\nEmail Type: {email_type}\nContext: {context}\nResearch Results: {research}\n\nFor each idea, provide:\n1. Email subject\n2. Sender description\n3. Main phishing tactic\n4. Relevance to the business type and context"
    )
    chain = LLMChain(llm=chat_model, prompt=prompt)
    result = chain.run(business_type=business_type, email_type=email_type, context=str(context_answers), research=str(research_results))
    return result.strip().split("\n\n")

def generate_full_email(business_type, email_type, context_answers, research_results, idea):
    prompt = PromptTemplate(
        input_variables=["business_type", "email_type", "context", "research", "idea"],
        template="Create a full phishing simulation email based on the following information:\nBusiness Type: {business_type}\nEmail Type: {email_type}\nContext: {context}\nResearch Results: {research}\nSelected Idea: {idea}\n\nProvide the following:\n1. Subject line\n2. Sender (name and email address)\n3. Full email body\n4. List of phishing indicators\n5. Explanation of why these indicators are suspicious"
    )
    chain = LLMChain(llm=chat_model, prompt=prompt)
    result = chain.run(business_type=business_type, email_type=email_type, context=str(context_answers), research=str(research_results), idea=idea)
    return result.strip()