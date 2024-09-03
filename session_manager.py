import streamlit as st

class SessionManager:
    def __init__(self):
        self.initialize_session()

    def initialize_session(self):
        if 'step' not in st.session_state:
            st.session_state.step = 1

    def reset_session(self):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self.initialize_session()

    def get_step(self):
        return st.session_state.step

    def set_step(self, step):
        st.session_state.step = step

    def set_value(self, key, value):
        st.session_state[key] = value

    def get_value(self, key, default=None):
        return st.session_state.get(key, default)

    def increment_step(self):
        st.session_state.step += 1

session_manager = SessionManager()