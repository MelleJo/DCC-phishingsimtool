import streamlit as st
import streamlit_antd_components as sac
from business_categories import get_categories, get_business_types, add_business_type
from ai_modules import generate_context_questions, conduct_research, generate_email_ideas, generate_full_email
from config import get_config, update_config, reset_to_defaults
from logger import log_step, log_error, save_session_to_file


# Set page configuration
st.set_page_config(page_title="Phishing Simulation Email Generator", layout="wide")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

def main():
    st.title("Phishing Simulation Email Generator")

    # Display progress
    st.progress((st.session_state.step - 1) / 6)
    st.write(f"Step {st.session_state.step} of 7")

    if st.session_state.step == 1:
        step_1_select_business()
    elif st.session_state.step == 2:
        step_2_select_email_type()
    elif st.session_state.step == 3:
        step_3_answer_questions()
    elif st.session_state.step == 4:
        step_4_review_research()
    elif st.session_state.step == 5:
        step_5_select_email_ideas()
    elif st.session_state.step == 6:
        step_6_generate_full_emails()
    elif st.session_state.step == 7:
        step_7_display_results()

def step_1_select_business():
    st.header("Step 1: Select Business Category and Type")
    categories = get_categories()
    selected_category = st.selectbox("Select a business category", categories)
    
    if selected_category:
        business_types = get_business_types(selected_category)
        selected_business = st.selectbox("Select a business type", business_types)
        
        if selected_business:
            st.session_state.business_type = selected_business
            if st.button("Next"):
                log_step("Business selected", selected_business)
                st.session_state.step = 2
                st.rerun()

def step_2_select_email_type():
    st.header("Step 2: Select Email Type")
    st.write(f"Selected business type: {st.session_state.business_type}")
    
    email_type = st.radio(
        "Select the type of email",
        ["Internal", "External"],
        format_func=lambda x: f"{x} - {'Email from a colleague or manager' if x == 'Internal' else 'Email from a customer, government, IT provider, etc.'}"
    )
    
    if st.button("Next"):
        st.session_state.email_type = email_type
        log_step("Email type selected", email_type)
        st.session_state.step = 3
        st.rerun()

def step_3_answer_questions():
    st.header("Step 3: Answer Context Questions")
    st.write(f"Selected business type: {st.session_state.business_type}")
    st.write(f"Selected email type: {st.session_state.email_type}")
    
    if 'context_questions' not in st.session_state:
        with st.spinner("Generating context questions..."):
            st.session_state.context_questions = generate_context_questions(
                st.session_state.business_type,
                st.session_state.email_type
            )
    
    if 'context_answers' not in st.session_state:
        st.session_state.context_answers = {}

    for i, q in enumerate(st.session_state.context_questions):
        key = f"context_question_{i}"
        st.session_state.context_answers[q] = st.text_input(label=q, key=key)
    
    if st.button("Next", key="context_next_button"):
        if all(st.session_state.context_answers.values()):
            log_step("Context questions answered")
            st.session_state.step = 4
            st.experimental_rerun()
        else:
            st.error("Please answer all questions before proceeding.")

def step_4_review_research():
    st.header("Step 4: Review Research Results")
    st.write(f"Selected business type: {st.session_state.business_type}")
    st.write(f"Selected email type: {st.session_state.email_type}")
    
    if 'research_results' not in st.session_state:
        with st.spinner("Conducting research..."):
            research_query = f"{st.session_state.business_type} {' '.join(st.session_state.context_answers.values())}"
            st.session_state.research_results = conduct_research(research_query)
    
    for result in st.session_state.research_results:
        st.write(result)
    
    if st.button("Next"):
        log_step("Research reviewed")
        st.session_state.step = 5
        st.rerun()

def step_5_select_email_ideas():
    st.header("Step 5: Select Email Ideas")
    st.write(f"Selected business type: {st.session_state.business_type}")
    st.write(f"Selected email type: {st.session_state.email_type}")
    
    if 'email_ideas' not in st.session_state:
        with st.spinner("Generating email ideas..."):
            st.session_state.email_ideas = generate_email_ideas(
                st.session_state.business_type,
                st.session_state.email_type,
                st.session_state.context_answers,
                st.session_state.research_results
            )
    
    st.session_state.selected_ideas = []
    for i, idea in enumerate(st.session_state.email_ideas):
        if st.checkbox(f"Idea {i+1}", key=f"idea_{i}"):
            st.session_state.selected_ideas.append(idea)
        st.text_area(f"Idea {i+1}", value=idea, height=100, key=f"idea_text_{i}")
    
    if st.button("Generate Emails") and len(st.session_state.selected_ideas) > 0:
        log_step("Email ideas selected", st.session_state.selected_ideas)
        st.session_state.step = 6
        st.rerun()

def step_6_generate_full_emails():
    st.header("Step 6: Generate Full Emails")
    st.write(f"Selected business type: {st.session_state.business_type}")
    st.write(f"Selected email type: {st.session_state.email_type}")
    
    if 'generated_emails' not in st.session_state:
        with st.spinner("Generating full emails..."):
            st.session_state.generated_emails = []
            for idea in st.session_state.selected_ideas:
                email = generate_full_email(
                    st.session_state.business_type,
                    st.session_state.email_type,
                    st.session_state.context_answers,
                    st.session_state.research_results,
                    idea
                )
                st.session_state.generated_emails.append(email)
    
    if st.button("View Results"):
        log_step("Emails generated")
        st.session_state.step = 7
        st.rerun()

def step_7_display_results():
    st.header("Step 7: View Generated Emails")
    for i, email in enumerate(st.session_state.generated_emails):
        with st.expander(f"Email {i+1}", expanded=True):
            display_email(email, i)
    
    if st.button("Start Over"):
        reset_session()
        st.rerun()

def display_email(email, index):
    # Extract email components (subject, sender, body, indicators, explanation)
    # Display each component
    # Add a download button for the email
    pass  # Implement this function based on your email structure

def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 1
    reset_to_defaults()
    log_step("Session reset")

if __name__ == "__main__":
    main()