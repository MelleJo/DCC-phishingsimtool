import streamlit as st
from langchain.llms import Anthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import get_anthropic_api_key, MAX_TOKENS, TEMPERATURE, MODEL_NAME
import hashlib
import uuid
import logging

# Configure logging
logging.basicConfig(filename='phishing_generator.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Set page configuration
st.set_page_config(page_title="Internal Phishing Simulation Email Generator", layout="wide")

# Custom CSS (same as before)
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

# Initialize Anthropic LLM
@st.cache_resource
def get_llm():
    return Anthropic(
        model=MODEL_NAME,
        anthropic_api_key=get_anthropic_api_key(),
        max_tokens_to_sample=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

llm = get_llm()

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "difficulty", "client"],
    template="""
    Create a phishing simulation email based on the following context: {context}
    
    The email should be at a {difficulty} difficulty level.
    This is for a phishing simulation for client: {client}
    
    Please provide the following:
    1. Subject line
    2. Sender name and email address
    3. Full email body
    4. List of phishing indicators in the email
    5. Explanation of why these indicators are suspicious
    
    Ensure the email is realistic and incorporates common phishing tactics appropriate for the specified difficulty level.
    Do not include any real names, email addresses, or identifiable information in the generated content.
    """
)

# Create the LangChain
email_chain = LLMChain(llm=llm, prompt=prompt_template)

# Anonymization function
def anonymize_input(input_text):
    return hashlib.sha256(input_text.encode()).hexdigest()[:10]

# Generate unique session ID
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Streamlit app
st.title("Internal Phishing Simulation Email Generator")

# User inputs
client_name = st.text_input("Enter the client company name:")
context = st.text_area("Enter the context for the phishing email (e.g., company specifics, industry, current events):", height=100)
difficulty = st.selectbox("Select the difficulty level:", ["Easy", "Medium", "Hard"])

if st.button("Generate Phishing Email"):
    if context and client_name:
        with st.spinner("Generating phishing email..."):
            # Anonymize inputs for logging
            anon_context = anonymize_input(context)
            anon_client = anonymize_input(client_name)
            
            # Log anonymized usage
            logging.info(f"Session ID: {st.session_state['session_id']}, Client: {anon_client}, Context: {anon_context}, Difficulty: {difficulty}")
            
            result = email_chain.run(context=context, difficulty=difficulty, client=client_name)
            
            # Parse and display results
            sections = result.split("\n\n")
            subject = sections[0].replace("Subject line: ", "")
            sender = sections[1].replace("Sender: ", "")
            body = sections[2]
            indicators = sections[3].split("\n")[1:]
            explanation = sections[4].split("\n")[1:]
            
            st.subheader("Generated Phishing Email")
            st.text(f"From: {sender}")
            st.text(f"Subject: {subject}")
            st.text_area("Email Body:", value=body, height=200)
            
            st.subheader("Phishing Indicators")
            for indicator in indicators:
                st.markdown(f"- {indicator}")
            
            st.subheader("Explanation")
            for point in explanation:
                st.markdown(f"- {point}")
    else:
        st.warning("Please provide both client name and context for the phishing email.")

# Add a footer
st.markdown("---")
st.markdown("Internal tool for Your Cybersecurity Business | Powered by Claude 3.5 Sonnet")