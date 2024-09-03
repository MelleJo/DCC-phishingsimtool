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

    elif session_manager.get_step() == 4:
        st.subheader("Step 4: Research Results")
        st.info(f"Selected business type: {session_manager.get_value('business_type')}")
        st.info(f"Selected email type: {session_manager.get_value('internal_external')}")
        
        if not session_manager.get_value('research_results'):
            with st.spinner("Conducting research..."):
                research_query = f"{session_manager.get_value('business_type')} {' '.join(session_manager.get_value('context_answers', {}).values())}"
                research_results = conduct_research(research_query)
            session_manager.set_value('research_results', research_results)
        
        display_research_results({"Research Results": session_manager.get_value('research_results')})
        
        if st.button("Generate Email Ideas"):
            log_step("Research Conducted")
            session_manager.increment_step()
            st.rerun()

    elif session_manager.get_step() == 5:
        st.subheader("Step 5: Select Email Ideas")
        st.info(f"Selected business type: {session_manager.get_value('business_type')}")
        st.info(f"Selected email type: {session_manager.get_value('internal_external')}")
        
        if not session_manager.get_value('email_ideas'):
            with st.spinner("Generating email ideas..."):
                email_ideas = generate_email_ideas(
                    session_manager.get_value('business_type'),
                    session_manager.get_value('internal_external'),
                    session_manager.get_value('context_answers'),
                    session_manager.get_value('research_results')
                )
            session_manager.set_value('email_ideas', email_ideas)
        
        selected_ideas = display_email_ideas(session_manager.get_value('email_ideas'))
        
        if len(selected_ideas) > 0 and len(selected_ideas) <= 3:
            if st.button("Generate Full Emails"):
                session_manager.set_value('selected_ideas', selected_ideas)
                log_step("Email Ideas Selected", selected_ideas)
                session_manager.increment_step()
                st.rerun()
        else:
            st.warning("Please select 1-3 email ideas to proceed.")

    elif session_manager.get_step() == 6:
        st.subheader("Step 6: Generated Phishing Simulation Emails")
        st.info(f"Selected business type: {session_manager.get_value('business_type')}")
        st.info(f"Selected email type: {session_manager.get_value('internal_external')}")
        
        if not session_manager.get_value('generated_emails'):
            with st.spinner("Generating full emails..."):
                generated_emails = [
                    generate_full_email(
                        session_manager.get_value('business_type'),
                        session_manager.get_value('internal_external'),
                        session_manager.get_value('context_answers'),
                        session_manager.get_value('research_results'),
                        idea
                    ) for idea in session_manager.get_value('selected_ideas')
                ]
            session_manager.set_value('generated_emails', generated_emails)
        
        display_generated_emails(session_manager.get_value('generated_emails'))
        
        if st.button("Save Session and Finish"):
            session_file = save_session_to_file()
            log_step("Session Completed and Saved", session_file)
            st.success(f"Phishing simulation emails have been generated and the session has been saved to {session_file}!")

    if st.button("Start Over"):
        session_manager.reset_session()
        st.rerun()

if __name__ == "__main__":
    main()