import streamlit as st
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
    generate_full_emails
)
from logger import log_step, log_error, save_session_to_file

# Set page configuration
st.set_page_config(page_title="DCC Phishing Simulatie Tool", layout="wide")

TOTAL_STEPS = 6

def main():
    st.title("DCC Phishing Simulatie Tool")

    # Initialize step if not already set
    if 'step' not in st.session_state:
        st.session_state.step = 1

    display_progress_bar(st.session_state.step, TOTAL_STEPS)

    # Step 1: Business Type Selection
    if st.session_state.step == 1:
        st.session_state.business_type = display_business_categories()
        if st.session_state.business_type and st.button("Next Step"):
            log_step("Business Type Selection", st.session_state.business_type)
            st.session_state.step = 2
            st.rerun()

    # Step 2: Internal/External Selection
    elif st.session_state.step == 2:
        st.write(f"Selected business type: {st.session_state.business_type}")
        st.session_state.internal_external = display_internal_external_selection()
        if st.session_state.internal_external and st.button("Next Step"):
            log_step("Internal/External Selection", st.session_state.internal_external)
            st.session_state.step = 3
            st.rerun()

    # Step 3: Generate and Display Context Questions
    elif st.session_state.step == 3:
        st.write(f"Selected business type: {st.session_state.business_type}")
        st.write(f"Selected email type: {st.session_state.internal_external}")
        
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
            st.session_state.context_answers = display_context_questions(st.session_state.context_questions)
        
        if st.button("Start Research", key="start_research_button"):
            log_step("Context Questions", st.session_state.context_answers)
            st.session_state.step = 4
            st.rerun()

    # Step 4: Conduct Research and Display Results
    elif st.session_state.step == 4:
        st.write(f"Selected business type: {st.session_state.business_type}")
        st.write(f"Selected email type: {st.session_state.internal_external}")
        
        if 'research_results' not in st.session_state:
            with st.spinner("Conducting research..."):
                research_query = f"{st.session_state.business_type} {' '.join(st.session_state.context_answers.values())}"
                st.session_state.research_results = conduct_research(research_query)
        
        display_research_results({"Research Results": st.session_state.research_results})
        
        if st.button("Next Step", key="next_step_button"):
            log_step("Research Conducted")
            st.session_state.step = 5
            st.rerun()

    # Step 5: Generate and Display Email Ideas
    elif st.session_state.step == 5:
        st.write(f"Selected business type: {st.session_state.business_type}")
        st.write(f"Selected email type: {st.session_state.internal_external}")
        
        if 'email_ideas' not in st.session_state:
            with st.spinner("Generating email ideas..."):
                st.session_state.email_ideas = generate_email_ideas(
                    st.session_state.business_type,
                    st.session_state.internal_external,
                    st.session_state.context_answers,
                    st.session_state.research_results
                )
        
        st.session_state.selected_ideas = display_email_ideas(st.session_state.email_ideas)
        
        if len(st.session_state.selected_ideas) > 0 and len(st.session_state.selected_ideas) <= 3:
            if st.button("Generate Full Emails", key="generate_full_emails_button"):
                log_step("Email Ideas Selected", st.session_state.selected_ideas)
                st.session_state.step = 6
                st.rerun()
        else:
            st.warning("Select 1-3 email ideas to proceed.")

    # Step 6: Generate and Display Full Emails
    elif st.session_state.step == 6:
        st.write(f"Selected business type: {st.session_state.business_type}")
        st.write(f"Selected email type: {st.session_state.internal_external}")
        
        if 'generated_emails' not in st.session_state:
            with st.spinner("Generating full emails..."):
                st.session_state.generated_emails = generate_full_emails(
                    st.session_state.business_type,
                    st.session_state.internal_external,
                    st.session_state.context_answers,
                    st.session_state.research_results,
                    st.session_state.selected_ideas
                )
        
        display_generated_emails(st.session_state.generated_emails)
        
        if st.button("Save Session and Finish", key="finish_button"):
            session_file = save_session_to_file()
            log_step("Session Completed and Saved", session_file)
            st.success(f"Phishing simulation emails generated and session saved to {session_file}!")

    # Reset button
    if st.button("Start Over", key="reset_button"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = 1
        log_step("Session Reset")
        st.rerun()

if __name__ == "__main__":
    main()