import streamlit as st

# Anthropic API key from Streamlit secrets
def get_anthropic_api_key():
    return st.secrets["ANTHROPIC_API_KEY"]

# Other configuration variables
MAX_TOKENS = 1000
TEMPERATURE = 0.7
MODEL_NAME = "claude-3-sonnet-20240229"