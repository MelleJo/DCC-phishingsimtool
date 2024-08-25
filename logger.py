import logging
import streamlit as st
from datetime import datetime

def setup_logger():
    logger = logging.getLogger("PhishingSimulatorApp")
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler("phishing_simulator.log")
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

def log_step(step_name, details=None):
    log_message = f"Step completed: {step_name}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)

def log_error(error_message):
    logger.error(f"Error occurred: {error_message}")

def save_session_to_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{timestamp}.txt"
    
    with open(filename, "w") as f:
        for key, value in st.session_state.items():
            f.write(f"{key}: {value}\n")
    
    logger.info(f"Session saved to file: {filename}")
    return filename