import streamlit as st

def get_anthropic_api_key():
    return st.secrets["ANTHROPIC_API_KEY"]

MAX_TOKENS = 1000
TEMPERATURE = 0.7
MODEL_NAME = "claude-3-5-sonnet-20240620"