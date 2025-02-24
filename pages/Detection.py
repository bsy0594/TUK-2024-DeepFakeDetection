import streamlit as st
import requests

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
uploaded_file = st.file_uploader(
    "Upload your video or with image", type=["mp4", "mov", "avi"], accept_multiple_files=True
)

# FastAPI server URL
FASTAPI_URL = "http://localhost:8000/upload"

if st.button("Start 🚀"):
    if not option:
        st.error("Please select a model before starting!")
    elif not uploaded_file: 
        st.error("Please upload at least one file before starting!")
    else:
        file = {
                "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
            }
        model = {"model": option}  # 선택한 모델 정보 전송

        # FastAPI 서버로 POST 요청
        response = requests.post(FASTAPI_URL, files=file, data=model, timeout=30)

        # 결과 출력
        if response.status_code == 200:
            result = response.json()
            st.success(f"File '{uploaded_file.name}' processed successfully!")
            
            # 특정 프레임 번호의 확률 값 가져오기
            frame_number = "1"  
            frame_probability = next((frame[frame_number] for frame in result["frames"] if frame_number in frame), None)
            st.write(f"Frame {frame_number} Probability: {frame_probability}")
        else:
            st.error(f"Error uploading '{uploaded_file.name}' (Status Code: {response.status_code})")