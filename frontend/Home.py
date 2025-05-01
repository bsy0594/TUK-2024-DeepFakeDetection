import streamlit as st

from sidebar import sidebar
from signup import signup
import result_UI
import result_server
import os

st.set_page_config(page_title="Fake Marker", page_icon="😎")

sidebar()

placeholder = st.empty()

if "clicked" in st.session_state and st.session_state.clicked:
    # result_UI.detail_result(placeholder)
    result_server.detail_result(placeholder)
else:
    with placeholder.container():
        st.markdown("# Welcome to Fake Marker 👋")
        
        # Select model
        st.markdown(
            """
            #####
            ##### 1. Model Selection
            - CNN-based Model: It has **fast detection speed** but may lead to lower accuracy.
            - Transformer-based Model: This model can lead to **better detection accuracy** but the detection speed is slow.
            """
        )
        
        option = st.selectbox(
            "Choose one of the following models:",
            ("1. CNN-based Model", "2. Transformer-based Model"),
            index=None,
            placeholder="Select a Model...",
        )

        # 모델 이름 매핑
        model_names = {
            "1. CNN-based Model": "CNN-based Model",
            "2. Transformer-based Model": "Transformer-based Model"
        }
        model_name = model_names.get(option, option)
        st.session_state.model_name = model_name

        # File Upload
        st.markdown("""######""")
        st.markdown(
            """
            ##### 2. File Upload
            -  **Supported formats**: mp4, mov, avi, mpeg4
            - **Note**: The maximum file size is 200MB.
            """
        )

        uploaded_file = st.file_uploader("Upload your video to scan", type=["mp4", "mov", "avi"])
        st.markdown("######")        
        st.session_state.uploaded_file = uploaded_file

        button = st.button("Scan 🚀", key="Scan")

    if button:
        if not option:
            st.error("Please select a model before starting!")
        elif not uploaded_file:
            st.error("Please upload video file before starting!")
        else:
            # Loading message
            with st.spinner("Uploading and processing your video... "):
                # result_UI.main_result(placeholder)
                result_server.main_result(placeholder, uploaded_file, model_name)
