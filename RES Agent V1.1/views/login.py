import streamlit as st

def show_login_page():
    st.container()
    st.title("🔒 RES Agent Login")
    st.markdown("Please sign in to access the HDB Market Analytics Dashboard.")
    
    # Simple centered login card layout
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            # Replace these with your preferred admin credentials
            if username == "aaa" and password == "aaa":
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun() # Refresh the app to switch views
            else:
                st.error("Invalid username or password. Please try again.")