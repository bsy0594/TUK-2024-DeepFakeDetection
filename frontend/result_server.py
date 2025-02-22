import streamlit as st
import requests
import json
import os
from urllib.parse import urljoin

def main_result(placeholder, uploaded_file, option):
    placeholder.empty()

    # 서버로 파일 및 옵션 전송
    FASTAPI_URL = "http://localhost:8000"
    detection_post_endpoint = "/video/"
    api_url = urljoin(FASTAPI_URL, detection_post_endpoint)

    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    data = {"model": option}
    response = requests.post(api_url, files=files, data=data, timeout=60)

    if response.status_code == 200:
        # 서버 응답 저장
        data = response.json()

        frame_index = []
        image_url = []
        prediction = []

        for image in data["images"]:
            frame_index.append(image["frame_index"])
            image_url.append(image["image_url"])
            prediction.append(image["prediction"])

        # 확률이 0.5 이상인 프레임이 있는 경우 딥페이크로 판단
        high_prob_frames = []
        max_prob_frame = None
        max_probability = 0

        for index, prob in enumerate(prediction):
            if prob > 0.5:
                high_prob_frames.append((image_url[index], prob))
                if prob > max_probability:
                    max_probability = prob
                    max_prob_frame = image_url[index]

        st.session_state.high_prob_frames = high_prob_frames

        # 확률이 가장 높은 프레임을 메인으로 출력
        if len(high_prob_frames) > 0:
            st.markdown("### ⚠️ Deepfake is detected ⚠️")
            frame_url = urljoin(FASTAPI_URL, max_prob_frame)
            st.image(frame_url, use_container_width=True)
            st.write(high_prob_frames)
        else:
            st.markdown("#### No Deepfake Detected 🎉")

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

    # 확률이 높은 프레임들 출력
    st.markdown("### ⚠️ Deepfake is detected ⚠️")
    FASTAPI_URL = "http://localhost:8000"

    frame_index = st.slider("Select Frame", 0, len(high_prob_frames) - 1, 0)
    frame, prob = high_prob_frames[frame_index]
    frame_url = urljoin(FASTAPI_URL, frame)

    # gradcam 방식으로 프레임들 출력
    gradcam_toggle = st.checkbox("Show Grad-CAM")

    if gradcam_toggle:
        gradcam_img_path = os.path.join(frame_url, f"gradcam_{frame}")
        if os.path.exists(gradcam_img_path):
            st.image(frame_url, caption=f"Frame: {frame} (Probability: {prob:.2f})")
        else:
            st.error("Grad-CAM image not found.")
    else:
        st.image(frame_url, caption=f"'{frame}' is suspected to be deepfake with {prob*100:.2f}%")