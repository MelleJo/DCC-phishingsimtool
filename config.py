import streamlit as st

def get_anthropic_api_key():
    return st.secrets["ANTHROPIC_API_KEY"]

def get_tavily_api_key():
    return st.secrets["TAVILY_API_KEY"]

DEFAULT_CONFIG = {
    'MODEL_NAME': "claude-3-5-sonnet-20240620",
    'MAX_TOKENS': 1000,
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

def get_model_name():
    return get_config()['MODEL_NAME']

def get_max_tokens():
    return get_config()['MAX_TOKENS']

def get_temperature():
    return get_config()['TEMPERATURE']

def reset_to_defaults():
    st.session_state.config = DEFAULT_CONFIG.copy()