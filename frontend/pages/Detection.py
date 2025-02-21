import streamlit as st

from sidebar import sidebar

st.set_page_config(page_title="Fake Marker", page_icon="😎")
st.write("# Welcome to Fake Marker 👋")

sidebar()

st.markdown(
    """
    ### 🔎 Choose a Model
    ##### 1. CNN-based Model
    - It has **fast detection speed** but may lead to lower accuracy.

    ##### 2. Transformer-based Model
    - This model can lead to **better detection accuracy** but the detection speed is slow.
    """
)

# Select model
option = st.selectbox(
    "",
    ("1. CNN-based Model", "2. Transformer-based Model"),
    index=None,
    placeholder="Select a Model...",
)

st.markdown(
    """
    ### 
    ### 📂 File Upload
    """
)

# File Upload
uploaded_files = st.file_uploader(
    "Upload your video or with image", accept_multiple_files=True
)

if st.button("Start 🚀"):
    if not option:
        st.error("Please select a model before starting!")
    elif not uploaded_files: 
        st.error("Please upload at least one file before starting!")
    else:
        st.write("서버로 모델 선택 정보 및 파일 전송")
        st.write("로딩창 제작해야 함")