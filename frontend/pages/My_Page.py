import streamlit as st

from sidebar import sidebar

st.write("# Detection History")

if st.session_state["authentication_status"] == None:
    st.error("You need to login to view your detection history")
else:
    st.success("We're still working on it")

sidebar()