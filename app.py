import streamlit as st

# Set page configuration - this must be the first Streamlit command
st.set_page_config(page_title="DCC Phishing Simulatie Tool", layout="wide")

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

def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 1

def main():
    init_session_state()

    st.title("DCC Phishing Simulatie Tool")

    # Sidebar
    with st.sidebar:
        st.write(f"Current Step: {st.session_state.step}/{TOTAL_STEPS}")
        if st.button("Reset Application"):
            st.session_state.clear()
            st.session_state.step = 1
            st.rerun()

    display_progress_bar(st.session_state.step, TOTAL_STEPS)

    if st.session_state.step == 1:
        st.subheader("Step 1: Select Business Type")
        business_type = display_business_categories()
        if business_type:
            st.session_state.business_type = business_type
            log_step("Business Type Selection", business_type)
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.subheader("Step 2: Select Email Type")
        st.info(f"Selected business type: {st.session_state.business_type}")
        internal_external = display_internal_external_selection()
        if internal_external:
            st.session_state.internal_external = internal_external
            log_step("Internal/External Selection", internal_external)
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        st.subheader("Step 3: Answer Context Questions")
        st.info(f"Selected business type: {st.session_state.business_type}")
        st.info(f"Selected email type: {st.session_state.internal_external}")
        
        if 'context_questions' not in st.session_state:
            with st.spinner("Generating context questions..."):
                st.session_state.context_questions = generate_context_questions(
                    st.session_state.business_type,
                    st.session_state.internal_external
                )
        
        if not st.session_state.context_questions:
            st.error("Unable to generate context questions. Please try again or proceed without questions.")
            if st.button("Proceed without questions"):
                st.session_state.context_answers = {}
                st.session_state.step = 4
                st.rerun()
        else:
            context_answers = display_context_questions(st.session_state.context_questions)
            if st.button("Start Research"):
                st.session_state.context_answers = context_answers
                log_step("Context Questions", context_answers)
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:
        st.subheader("Step 4: Research Results")
        st.info(f"Selected business type: {st.session_state.business_type}")
        st.info(f"Selected email type: {st.session_state.internal_external}")
        
        if 'research_results' not in st.session_state:
            with st.spinner("Conducting research..."):
                research_query = f"{st.session_state.business_type} {' '.join(st.session_state.context_answers.values())}"
                st.session_state.research_results = conduct_research(research_query)
        
        display_research_results({"Research Results": st.session_state.research_results})
        
        if st.button("Generate Email Ideas"):
            log_step("Research Conducted")
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        st.subheader("Step 5: Select Email Ideas")
        st.info(f"Selected business type: {st.session_state.business_type}")
        st.info(f"Selected email type: {st.session_state.internal_external}")
        
        if 'email_ideas' not in st.session_state:
            with st.spinner("Generating email ideas..."):
                st.session_state.email_ideas = generate_email_ideas(
                    st.session_state.business_type,
                    st.session_state.internal_external,
                    st.session_state.context_answers,
                    st.session_state.research_results
                )
        
        selected_ideas = display_email_ideas(st.session_state.email_ideas)
        
        if len(selected_ideas) > 0 and len(selected_ideas) <= 3:
            if st.button("Generate Full Emails"):
                st.session_state.selected_ideas = selected_ideas
                log_step("Email Ideas Selected", selected_ideas)
                st.session_state.step = 6
                st.rerun()
        else:
            st.warning("Please select 1-3 email ideas to proceed.")

    elif st.session_state.step == 6:
        st.subheader("Step 6: Generated Phishing Simulation Emails")
        st.info(f"Selected business type: {st.session_state.business_type}")
        st.info(f"Selected email type: {st.session_state.internal_external}")
        
        if 'generated_emails' not in st.session_state:
            with st.spinner("Generating full emails..."):
                st.session_state.generated_emails = [
                    generate_full_email(
                        st.session_state.business_type,
                        st.session_state.internal_external,
                        st.session_state.context_answers,
                        st.session_state.research_results,
                        idea
                    ) for idea in st.session_state.selected_ideas
                ]
        
        display_generated_emails(st.session_state.generated_emails)
        
        if st.button("Save Session and Finish"):
            session_file = save_session_to_file()
            log_step("Session Completed and Saved", session_file)
            st.success(f"Phishing simulation emails have been generated and the session has been saved to {session_file}!")

    if st.button("Start Over"):
        st.session_state.clear()
        st.session_state.step = 1
        st.rerun()

if __name__ == "__main__":
    main()