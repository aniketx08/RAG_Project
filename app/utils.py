import streamlit as st

def log_message(message, streamlit_output=True):
    print(message)
    if streamlit_output:
        st.write(f"`{message}`")


