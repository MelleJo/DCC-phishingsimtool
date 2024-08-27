import autogen
import streamlit as st
from tavily import TavilyClient
import os

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize Tavily client
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# Configuration for the AI agents
#config_list = [
    {
        "model": "claude-3-5-sonnet-20240620",
        "api_key": st.secrets["ANTHROPIC_API_KEY"],
        "api_type": "anthropic",
    }
]

# Assistant configurations
assistant_config = {
    "name": "Phishing Email Assistant",
    "system_message": "You are an AI assistant specialized in creating phishing simulation emails. Your goal is to create realistic and educational examples for cybersecurity training.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

researcher_config = {
    "name": "Research Assistant",
    "system_message": "You are a research assistant specialized in finding relevant information for creating phishing simulation emails.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

email_writer_config = {
    "name": "Email Writer",
    "system_message": "You are an AI specialized in writing realistic phishing emails based on given information and ideas.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

# Create agent instances
assistant = autogen.AssistantAgent(**assistant_config)
researcher = autogen.AssistantAgent(**researcher_config)
email_writer = autogen.AssistantAgent(**email_writer_config)

# Create a UserProxyAgent to manage the conversation
user_proxy = autogen.UserProxyAgent(
    name="Human",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "coding"},
    llm_config={"config_list": config_list},
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

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
    
    user_proxy.initiate_chat(assistant, message=prompt)
    response = assistant.last_message()["content"]
    
    try:
        questions = response.strip().split('\n')
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        st.error(f"Error in processing context questions: {str(e)}")
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
    
    user_proxy.initiate_chat(assistant, message=prompt)
    response = assistant.last_message()["content"]
    
    try:
        return response.strip().split("\n\n")
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
    
    user_proxy.initiate_chat(email_writer, message=prompt)
    response = email_writer.last_message()["content"]
    
    try:
        return response.strip().split("<email>")[1:]  # Remove the first empty split
    except Exception as e:
        st.error(f"Error in generating full emails: {str(e)}")
        return []