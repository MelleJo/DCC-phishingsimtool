import streamlit as st
from langchain.llms import Anthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import get_anthropic_api_key, MAX_TOKENS, TEMPERATURE, MODEL_NAME

# Set page configuration
st.set_page_config(page_title="Phishing Simulation Email Generator", layout="wide")

# Custom CSS for a sleek design
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
    input_variables=["context", "difficulty"],
    template="""
    Create a phishing simulation email based on the following context: {context}
    
    The email should be at a {difficulty} difficulty level.
    
    Please provide the following:
    1. Subject line
    2. Sender name and email address
    3. Full email body
    4. List of phishing indicators in the email
    5. Explanation of why these indicators are suspicious
    
    Ensure the email is realistic and incorporates common phishing tactics appropriate for the specified difficulty level.
    """
)

# Create the LangChain
email_chain = LLMChain(llm=llm, prompt=prompt_template)

# Streamlit app
st.title("Phishing Simulation Email Generator")

# User inputs
context = st.text_area("Enter the context for the phishing email (e.g., company name, industry, current events):", height=100)
difficulty = st.selectbox("Select the difficulty level:", ["Easy", "Medium", "Hard"])

if st.button("Generate Phishing Email"):
    if context:
        with st.spinner("Generating phishing email..."):
            result = email_chain.run(context=context, difficulty=difficulty)
            
            # Parse the result
            sections = result.split("\n\n")
            subject = sections[0].replace("Subject line: ", "")
            sender = sections[1].replace("Sender: ", "")
            body = sections[2]
            indicators = sections[3].split("\n")[1:]
            explanation = sections[4].split("\n")[1:]
            
            # Display the results
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
        st.warning("Please provide context for the phishing email.")

# Add a footer
st.markdown("---")
st.markdown("Created by Your Cybersecurity Business | Powered by Claude 3.5 Sonnet")