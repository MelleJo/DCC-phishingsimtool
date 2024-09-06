import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

def get_anthropic_api_key():
    return os.getenv("ANTHROPIC_API_KEY") or st.secrets["ANTHROPIC_API_KEY"]

def get_tavily_api_key():
    return os.getenv("TAVILY_API_KEY") or st.secrets["TAVILY_API_KEY"]

DEFAULT_CONFIG = {
    'MODEL_NAME': "claude-3-opus-20240229",
    'MAX_TOKENS': 4000,
    'TEMPERATURE': 0.7
}

def get_config():
    if 'config' not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG.copy()
    return st.session_state.config

def update_config(new_config):
    config = get_config()
    config.update(new_config)
    st.session_state.config = config

def reset_to_defaults():
    st.session_state.config = DEFAULT_CONFIG.copy()