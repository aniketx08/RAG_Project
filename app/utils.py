def log_message(message, streamlit_output=False):
    print(message)
    if streamlit_output:
        try:
            import streamlit as st
            st.write(f"`{message}`")
        except Exception:
            # Fallback: just print if Streamlit isn't available
            print(f"[Streamlit skipped] {message}")
