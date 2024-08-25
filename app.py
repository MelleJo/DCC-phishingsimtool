import streamlit as st
from ui_components import render_main_page, render_debug_info, display_generated_email
from email_generator import generate_phishing_email
from config import get_anthropic_api_key, MAX_TOKENS, TEMPERATURE, MODEL_NAME
import logging
import uuid

# Configure logging
logging.basicConfig(filename='phishing_generator.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Set page configuration
st.set_page_config(page_title="DCC Phishing Simulatie Tool", layout="wide")

# Generate unique session ID
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

def main():
    st.title("DCC Phishing Simulatie Tool")

    context, difficulty = render_main_page()

    if context is not None and difficulty is not None:
        if st.button("Genereer Phishing E-mail"):
            if context:
                with st.spinner("Phishing e-mail wordt gegenereerd..."):
                    result = generate_phishing_email(context, difficulty)
                    if result:
                        st.session_state['generated_email'] = result
                        display_generated_email(result)
                    else:
                        st.error("Er is geen resultaat ontvangen van de API.")
            else:
                st.warning("Voer alstublieft de context in voor de phishing e-mail.")

    # Display debug information
    render_debug_info(get_anthropic_api_key(), MODEL_NAME, MAX_TOKENS, TEMPERATURE)

if __name__ == "__main__":
    main()