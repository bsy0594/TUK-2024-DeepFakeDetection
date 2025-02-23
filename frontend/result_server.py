import os
from urllib.parse import urljoin
import streamlit as st
import requests
import json
import plotly.express as px
import pandas as pd
from datetime import datetime
from PIL import Image
from io import BytesIO

def main_result(placeholder, uploaded_file, model_name):
    placeholder.empty()

    # 서버로 파일 및 옵션 전송
    FASTAPI_URL = "http://218.48.124.18:8000"
    detection_post_endpoint = "/video/"
    api_url = urljoin(FASTAPI_URL, detection_post_endpoint)

    files = {"file": uploaded_file.getvalue()}
    data = {"model": model_name}
    response = requests.post(api_url, files=files, data=data, timeout=60)

    if response.status_code == 200:
        # 서버 응답 저장
        data = response.json()
        
        frame_index = []
        original_image = []
        gradcam_image = []
        prediction = []

        for image in data["images"]:
            frame_index.append(image["frame_index"])
            original_image.append(image["original_image"])
            gradcam_image.append(image["gradcam_image"])
            prediction.append(image["prediction"])

        # 확률이 0.5 이상인 프레임이 있는 경우 딥페이크로 판단
        high_prob_frames = []
        max_prob_frame = None
        max_probability = 0

        for index, prob in enumerate(prediction):
            if prob > 0.5:
                high_prob_frames.append((original_image[index], gradcam_image[index],prob))
                if prob > max_probability:
                    max_probability = prob
                    max_prob_frame = original_image[index]

        st.session_state.high_prob_frames = high_prob_frames
        st.session_state.prediction = prediction
        st.session_state.frame_index = frame_index

        # 확률이 가장 높은 프레임을 메인으로 출력
        if len(high_prob_frames) > 0:
            st.markdown("# ⚠️ Deepfake is detected ⚠️")
            frame_url = urljoin(FASTAPI_URL, max_prob_frame)
            response = requests.get(frame_url)

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, use_container_width=True)
            else:
                st.error("Image not found")

            # st.image(frame_url, use_container_width=True)
        else:
            st.markdown("# No Deepfake Detected 🎉")

        # 결과 자세히 보러가기 버튼
        if "clicked" not in st.session_state:
            st.session_state.clicked = False

        def click_button():
            st.session_state.clicked = True

        st.button("View results in detail", on_click=click_button)

    else:
        st.error(f"Error: {response.status_code}")

# 자세한 결과 출력
def detail_result(placeholder):
    placeholder.empty()

    high_prob_frames = st.session_state.high_prob_frames
    probabilities = st.session_state.prediction
    frame_indices = st.session_state.frame_index
    uploaded_file = st.session_state.uploaded_file
    model_name = st.session_state.model_name

    st.markdown("# ⚠️ Deepfake is detected ⚠️")

    # 영상, 모델, 시간 정보 출력
    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown(f"**Name:** {uploaded_file.name}")  
        st.markdown(f"**Size:** {uploaded_file.size / 1048576:.2f} MB")

    with col2:
        st.markdown(f"**Model:** {model_name}")
        st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 확률이 높은 프레임들 출력
    st.markdown(
        """
        ######
        ### High Probability Frames
        """
    )
    FASTAPI_URL = "http://218.48.124.18:8000"

    frame_index = st.slider("Select Frame", 0, len(high_prob_frames) - 1, 0)
    original_image, gradcam_image, prob = high_prob_frames[frame_index]
    original_image_url = urljoin(FASTAPI_URL, original_image)
    gradcam_image_url = urljoin(FASTAPI_URL, gradcam_image)

    # gradcam 방식으로 프레임들 출력
    gradcam_toggle = st.checkbox("Show Grad-CAM")

    if gradcam_toggle:
        frame_name = os.path.basename(gradcam_image_url)
        st.image(gradcam_image_url, caption=f"'{frame_name}' is suspected to be deepfake with {prob*100:.2f}%")
    else:
        frame_name = os.path.basename(original_image_url)
        st.image(original_image_url, caption=f"'{frame_name}' is suspected to be deepfake with {prob*100:.2f}%")

    # 프레임 별 확률에 대한 그래프
    st.markdown("### ")
    st.markdown("### Deepfake Probability per Frame")

    df = pd.DataFrame({
        "Frame": frame_indices,
        "Probability": probabilities
    })

    fig = px.line(df, x="Frame", y="Probability")
    fig.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(fig, use_container_width=True)
