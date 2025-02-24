import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from sqlalchemy import text

def signup():
    st.markdown(
        """
        ### 👇 Experience the Power of Deepfake Detection
        """
    )
    
    name = st.text_input("Name", placeholder="Enter your name")
    user_id = st.text_input("User ID", placeholder="Enter your ID")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    email = st.text_input("Email", placeholder="Enter your email")

    if "signup_success" not in st.session_state:
        st.session_state["signup_success"] = False  

    if st.button("Welcome ❤️"):
        if not (name and user_id and email and password):
            st.error("Please fill out all fields 😢")
        elif user_id in st.session_state["config"]["credentials"]["usernames"]:
            st.error("User ID already exists 😢")
        else:
            # Hash
            hashed_password = stauth.Hasher.hash(password)

            try:
                with open("config.yaml", "r") as file:
                    config = yaml.load(file, Loader=SafeLoader)
            except FileNotFoundError:
                # if config.yaml file does not exist, create a new one
                config = {
                    "credentials": {
                        "usernames": {}
                    },
                    "cookie": {
                        "expiry_days": 30,
                        "key": "signature_key_for_fakemarker",
                        "name": "cookie_name+for_fakemarker",
                    }
                }

            # Add new user to config.yaml
            config["credentials"]["userID"][user_id] = {
                "name": name,
                "password": hashed_password,
                "email": email,
                "logged_in": False  
            }

            # Update config.yaml
            with open("config.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

            st.session_state["signup_success"] = True  

    if st.session_state["signup_success"]:
        st.success("Thank you for signing up 😀")
        
        # DB로 사용자 정보 전송
        conn = st.connection('mysql', type='sql')
        with conn.session as s:
            query = text(f"INSERT INTO Users (user_id, user_name, email, password) VALUES ('{user_id}', '{name}', '{email}', '{hashed_password}');")
            s.execute(query)
            s.commit()