import streamlit as st

class SessionManager:
    def __init__(self):
        self.initialize_session()

    def initialize_session(self):
        if 'initialized' not in st.session_state:
            st.session_state.clear()
            st.session_state.initialized = True
        if 'step' not in st.session_state:
            st.session_state.step = 1

    def reset_session(self):
        for key in list(st.session_state.keys()):
            if key != 'initialized':
                del st.session_state[key]
        st.session_state.step = 1

    def get_step(self):
        if 'step' not in st.session_state:
            st.session_state.step = 1
        return st.session_state.step

    def set_step(self, step):
        st.session_state.step = step

    def set_value(self, key, value):
        st.session_state[key] = value

    def get_value(self, key, default=None):
        return st.session_state.get(key, default)

    def increment_step(self):
        if 'step' not in st.session_state:
            st.session_state.step = 1
        else:
            st.session_state.step += 1

session_manager = SessionManager()