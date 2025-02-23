import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Login
def sidebar():
    with open("./frontend/config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Create authentication object
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )
    st.session_state["authenticator"] = authenticator
    st.session_state["config"] = config

    def logout_callback(_):
        st.session_state["authentication_status"] = None
        st.session_state["login_user"] = None
        st.cache_data.clear()
        authenticator.cookie_controller.delete_cookie()
        st.rerun()

    # Render login widget
    try:
        authenticator.login(
            location="sidebar",
            fields={
                "Form name": "🔑 Unlock Your Access",
                "Username": "User ID",
                "Password": "Password",
                "Login": "Login",
            },
        )
    except Exception as e:
        st.sidebar.error(e)
        # logout_callback(None)
        return

    if st.session_state["authentication_status"] is False:
        st.sidebar.error("Login Failed 😢")
        return
    elif st.session_state["authentication_status"] is None:
        return
    
    username = st.session_state["username"]  # username value filled by login widget
    st.sidebar.write(f"### 🆔 **{username}**")
    authenticator.logout(location="sidebar", callback=logout_callback)