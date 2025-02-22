import streamlit as st

from sidebar import sidebar
import result_UI
import result_server

st.set_page_config(page_title="Fake Marker", page_icon="😎")
st.write("# Welcome to Fake Marker 👋")

sidebar()

placeholder = st.empty()

if "clicked" in st.session_state and st.session_state.clicked:
    # result_UI.detail_result(placeholder)
    result_server.detail_result(placeholder)
else:
    with placeholder.container():
        # Select model
        option = st.selectbox(
            "Choose one of the following models:",
            ("1. CNN-based Model", "2. Transformer-based Model"),
            index=None,
            placeholder="Select a Model...",
        )

        st.markdown("""######""")

        # File Upload
        uploaded_file = st.file_uploader(
            "Upload your video or with image", type=["mp4", "mov", "avi"]
        )

        button = st.button("Start 🚀", key="start")

    if button:
        if not option:
            st.error("Please select a model before starting!")
        elif not uploaded_file:
            st.error("Please upload at least one file before starting!")
        else:
            # Loading message
            with st.spinner("Uploading and processing your video... "):
                # result_UI.main_result(placeholder)
                result_server.main_result(placeholder, uploaded_file, option)
