import streamlit as st
import streamlit_antd_components as sac
from business_categories import get_categories, get_business_types, add_business_type

def display_business_categories():
    st.subheader("Selecteer een bedrijfscategorie")
    
    try:
        categories = get_categories()
        if not categories:
            st.error("Geen bedrijfscategorieën gevonden. Controleer de business_categories.py file.")
            return None
        
        selected_category = sac.buttons(
            items=[sac.ButtonsItem(label=cat) for cat in categories],
            format_func="title",
            key="category_buttons"
        )
        
        if selected_category:
            st.subheader("Selecteer een bedrijfstype")
            business_types = get_business_types(selected_category)
            if not business_types:
                st.warning(f"Geen bedrijfstypes gevonden voor de categorie '{selected_category}'.")
            else:
                selected_business = sac.buttons(
                    items=[sac.ButtonsItem(label=bt) for bt in business_types],
                    format_func="title",
                    key="business_type_buttons"
                )
                if selected_business:
                    return selected_business
    
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het laden van de bedrijfscategorieën: {str(e)}")
        return None
    
    # Option to add a new business type
    with st.expander("Voeg een nieuw bedrijfstype toe"):
        new_category = st.selectbox("Selecteer een categorie", categories, key="new_category_select")
        new_business_type = st.text_input("Voer het nieuwe bedrijfstype in", key="new_business_type_input")
        if st.button("Toevoegen", key="add_business_type_button") and new_business_type:
            try:
                add_business_type(new_category, new_business_type)
                st.success(f"Bedrijfstype '{new_business_type}' toegevoegd aan categorie '{new_category}'")
                st.rerun()
            except Exception as e:
                st.error(f"Fout bij het toevoegen van het nieuwe bedrijfstype: {str(e)}")

    return None

def display_internal_external_selection():
    st.subheader("Selecteer het type e-mail")
    return st.radio(
        "E-mail type",
        ["Intern", "Extern"],
        format_func=lambda x: f"{x} - {'E-mail van een collega of leidinggevende' if x == 'Intern' else 'E-mail van een klant, overheid, IT-provider, etc.'}",
        key="internal_external_radio"
    )

def display_context_questions(questions):
    st.subheader("Beantwoord de volgende vragen")
    answers = {}
    for i, q in enumerate(questions):
        answers[q] = st.text_input(q, key=f"context_question_{i}")
    return answers

def display_research_results(research_results):
    st.subheader("Onderzoeksresultaten")
    for category, results in research_results.items():
        with st.expander(f"{category} Informatie"):
            for item in results:
                st.write(f"- {item}")

def display_progress_bar(current_step, total_steps):
    progress = (current_step - 1) / (total_steps - 1)
    st.progress(progress)
    st.write(f"Stap {current_step} van {total_steps}")

def display_email_ideas(ideas):
    st.subheader("Selecteer 1-3 e-mailideeën")
    selected_ideas = []
    for i, idea in enumerate(ideas, 1):
        if st.checkbox(f"Idee {i}", key=f"idea_checkbox_{i}"):
            selected_ideas.append(idea)
        st.text_area(f"Idee {i}", value=idea, height=150, key=f"idea_text_{i}")
    return selected_ideas

def display_generated_emails(emails):
    for i, email in enumerate(emails, 1):
        with st.expander(f"Gegenereerde E-mail {i}", expanded=True):
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
                subject = email[subject_start:subject_end] if subject_start > 8 and subject_end != -1 else "Geen onderwerp"
                sender = email[sender_start:sender_end] if sender_start > 7 and sender_end != -1 else "Onbekende afzender"
                body = email[body_start:body_end] if body_start > 5 and body_end != -1 else "Geen inhoud"
                indicators = email[indicators_start:indicators_end].split('\n') if indicators_start > 11 and indicators_end != -1 else []
                explanation = email[explanation_start:explanation_end] if explanation_start > 12 and explanation_end != -1 else "Geen uitleg beschikbaar"

                st.markdown(f"**Onderwerp:** {subject}")
                st.markdown(f"**Afzender:** {sender}")
                st.text_area("E-mailinhoud:", value=body, height=200, key=f"email_body_{i}")
                
                st.subheader("Phishing-indicatoren:")
                for indicator in indicators:
                    if indicator.strip():
                        st.markdown(f"- {indicator.strip()}")
                
                st.subheader("Uitleg:")
                st.write(explanation)

                if st.button(f"Download E-mail {i}", key=f"download_email_{i}"):
                    email_content = f"Onderwerp: {subject}\nAfzender: {sender}\n\n{body}\n\nPhishing-indicatoren:\n"
                    email_content += '\n'.join(indicators)
                    email_content += f"\n\nUitleg:\n{explanation}"
                    st.download_button(
                        label=f"Download E-mail {i} als tekstbestand",
                        data=email_content,
                        file_name=f"phishing_email_{i}.txt",
                        mime="text/plain",
                        key=f"download_button_{i}"
                    )
            except Exception as e:
                st.error(f"Er is een fout opgetreden bij het weergeven van e-mail {i}: {str(e)}")