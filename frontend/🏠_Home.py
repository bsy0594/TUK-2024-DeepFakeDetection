import streamlit as st

from sidebar import sidebar
from signup import signup
from howToUse import howToUse

st.set_page_config(page_title="Fake Marker", page_icon=":sunglasses:")
st.write("# Welcome to Fake Marker 👋")

# Video for usage example
video_file = open("boynextdoor_ifIsayILOVEYOU.mp4", "rb")
video_bytes = video_file.read()
st.video(video_bytes, start_time=45, autoplay=True, muted=True)

sidebar()

if st.session_state["authentication_status"] == None:
    signup()
else:
    howToUse()
