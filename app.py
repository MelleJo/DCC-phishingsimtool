import streamlit as st

# Set page configuration - this must be the first Streamlit command
st.set_page_config(page_title="DCC Phishing Simulatie Tool", layout="wide")

from session_manager import session_manager
from ui_components import (
    display_business_categories, 
    display_internal_external_selection, 
    display_context_questions,
    display_research_results,
    display_email_ideas,
    display_generated_emails,
    display_progress_bar
)
from autogen_agents import (
    generate_context_questions,
    conduct_research,
    generate_email_ideas,
    generate_full_email
)
from logger import log_step, log_error, save_session_to_file

TOTAL_STEPS = 6

def main():
    st.title("DCC Phishing Simulatie Tool")

    # Debug information
    st.sidebar.text("Debug Info:")
    st.sidebar.text(f"Current step: {session_manager.get_step()}")
    st.sidebar.text(f"Session state keys: {list(st.session_state.keys())}")

    # Sidebar
    with st.sidebar:
        st.write(f"Current Step: {session_manager.get_step()}/{TOTAL_STEPS}")
        if st.button("Reset Application"):
            session_manager.reset_session()
            st.rerun()

    display_progress_bar(session_manager.get_step(), TOTAL_STEPS)

    if session_manager.get_step() == 1:
        st.subheader("Step 1: Select Business Type")
        business_type = display_business_categories()
        if business_type:
            session_manager.set_value('business_type', business_type)
            log_step("Business Type Selection", business_type)
            session_manager.increment_step()
            st.rerun()

    elif session_manager.get_step() == 2:
        st.subheader("Step 2: Select Email Type")
        st.info(f"Selected business type: {session_manager.get_value('business_type')}")
        internal_external = display_internal_external_selection()
        if internal_external:
            session_manager.set_value('internal_external', internal_external)
            log_step("Internal/External Selection", internal_external)
            session_manager.increment_step()
            st.rerun()

    elif session_manager.get_step() == 3:
        st.subheader("Step 3: Answer Context Questions")
        st.info(f"Selected business type: {session_manager.get_value('business_type')}")
        st.info(f"Selected email type: {session_manager.get_value('internal_external')}")
        
        if not session_manager.get_value('context_questions'):
            with st.spinner("Generating context questions..."):
                context_questions = generate_context_questions(
                    session_manager.get_value('business_type'),
                    session_manager.get_value('internal_external')
                )
            session_manager.set_value('context_questions', context_questions)
        
        if not session_manager.get_value('context_questions'):
            st.error("Unable to generate context questions. Please try again or proceed without questions.")
            if st.button("Proceed without questions"):
                session_manager.set_value('context_answers', {})
                session_manager.increment_step()
                st.rerun()
        else:
            context_answers = display_context_questions(session_manager.get_value('context_questions'))
            if st.button("Start Research"):
                session_manager.set_value('context_answers', context_answers)
                log_step("Context Questions", context_answers)
                session_manager.increment_step()
                st.rerun()

    # ... [Continue with the rest of the steps, using session_manager methods] ...

    if st.button("Start Over"):
        session_manager.reset_session()
        st.rerun()

if __name__ == "__main__":
    main()