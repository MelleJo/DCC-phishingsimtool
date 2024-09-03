import streamlit as st
import streamlit_antd_components as sac
from business_categories import get_categories, get_business_types, add_business_type

def display_business_categories():
    st.subheader("Select a business category")
    
    try:
        categories = get_categories()
        if not categories:
            st.error("No business categories found. Check the business_categories.py file.")
            return None
        
        selected_category = sac.buttons(
            items=[sac.ButtonsItem(label=cat) for cat in categories],
            format_func="title",
            key="category_buttons"
        )
        
        if selected_category:
            st.subheader("Select a business type")
            business_types = get_business_types(selected_category)
            if not business_types:
                st.warning(f"No business types found for the category '{selected_category}'.")
            else:
                selected_business = sac.buttons(
                    items=[sac.ButtonsItem(label=bt) for bt in business_types],
                    format_func="title",
                    key="business_type_buttons"
                )
                if selected_business:
                    return selected_business
    
    except Exception as e:
        st.error(f"An error occurred while loading business categories: {str(e)}")
        return None
    
    # Option to add a new business type
    with st.expander("Add a new business type"):
        new_category = st.selectbox("Select a category", categories, key="new_category_select")
        new_business_type = st.text_input("Enter the new business type", key="new_business_type_input")
        if st.button("Add", key="add_business_type_button") and new_business_type:
            try:
                add_business_type(new_category, new_business_type)
                st.success(f"Business type '{new_business_type}' added to category '{new_category}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding the new business type: {str(e)}")

    return None

def display_internal_external_selection():
    st.subheader("Select the type of email")
    return st.radio(
        "Email type",
        ["Internal", "External"],
        format_func=lambda x: f"{x} - {'Email from a colleague or manager' if x == 'Internal' else 'Email from a customer, government, IT provider, etc.'}",
        key="internal_external_radio"
    )

def display_context_questions(questions):
    st.subheader("Answer the following questions")
    answers = {}
    for i, q in enumerate(questions):
        answers[q] = st.text_input(q, key=f"context_question_{i}")
    return answers

def display_research_results(research_results):
    st.subheader("Research Results")
    for category, results in research_results.items():
        with st.expander(f"{category} Information"):
            for item in results:
                st.write(f"- {item}")

def display_progress_bar(current_step, total_steps):
    progress = (current_step - 1) / (total_steps - 1)
    st.progress(progress)
    st.write(f"Step {current_step} of {total_steps}")

def display_email_ideas(ideas):
    st.subheader("Select 1-3 email ideas")
    selected_ideas = []
    for i, idea in enumerate(ideas, 1):
        if st.checkbox(f"Idea {i}", key=f"idea_checkbox_{i}"):
            selected_ideas.append(idea)
        st.text_area(f"Idea {i}", value=idea, height=150, key=f"idea_text_{i}")
    return selected_ideas

def display_generated_emails(emails):
    for i, email in enumerate(emails, 1):
        with st.expander(f"Generated Email {i}", expanded=True):
            try:
                # Find the indices of the tags
                subject_start = email.find('<subject>') + 9
                subject_end = email.find('</subject>')
                sender_start = email.find('<sender>') + 8
                sender_end = email.find('</sender>')
                body_start = email.find('<body>') + 6
                body_end = email.find('</body>')
                indicators_start = email.find('<indicators>') + 12
                indicators_end = email.find('</indicators>')
                explanation_start = email.find('<explanation>') + 13
                explanation_end = email.find('</explanation>')

                # Extract the content
                subject = email[subject_start:subject_end] if subject_start > 8 and subject_end != -1 else "No subject"
                sender = email[sender_start:sender_end] if sender_start > 7 and sender_end != -1 else "Unknown sender"
                body = email[body_start:body_end] if body_start > 5 and body_end != -1 else "No content"
                indicators = email[indicators_start:indicators_end].split('\n') if indicators_start > 11 and indicators_end != -1 else []
                explanation = email[explanation_start:explanation_end] if explanation_start > 12 and explanation_end != -1 else "No explanation available"

                st.markdown(f"**Subject:** {subject}")
                st.markdown(f"**Sender:** {sender}")
                st.text_area("Email content:", value=body, height=200, key=f"email_body_{i}")
                
                st.subheader("Phishing indicators:")
                for indicator in indicators:
                    if indicator.strip():
                        st.markdown(f"- {indicator.strip()}")
                
                st.subheader("Explanation:")
                st.write(explanation)

                if st.button(f"Download Email {i}", key=f"download_email_{i}"):
                    email_content = f"Subject: {subject}\nSender: {sender}\n\n{body}\n\nPhishing indicators:\n"
                    email_content += '\n'.join(indicators)
                    email_content += f"\n\nExplanation:\n{explanation}"
                    st.download_button(
                        label=f"Download Email {i} as text file",
                        data=email_content,
                        file_name=f"phishing_email_{i}.txt",
                        mime="text/plain",
                        key=f"download_button_{i}"
                    )
            except Exception as e:
                st.error(f"An error occurred while displaying email {i}: {str(e)}")