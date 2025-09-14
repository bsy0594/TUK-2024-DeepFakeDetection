import time
import json
import os
import streamlit as st

def main_result(placeholder):
    time.sleep(4)
    placeholder.empty()

    # 프레임에 대한 확률로 딥페이크 판단
    P_result_path = "../../DF_임시데이터/yes_df/yes_df_P.json"
    with open(P_result_path, "r") as f:
        P_result = json.load(f)

    high_prob_frames = []
    max_prob_frame = None
    max_probability = 0

    # 확률이 0.5 이상인 프레임이 있는 경우 딥페이크로 판단
    for frame, prob in P_result.items():
        probability = prob["probability"]
        if probability > 0.5:
            high_prob_frames.append((frame, probability))
            if probability > max_probability:
                max_probability = probability
                max_prob_frame = frame

    st.session_state.high_prob_frames = high_prob_frames

    # 확률이 가장 높은 프레임을 메인으로 출력
    if len(high_prob_frames) > 0:
        st.markdown("### ⚠️ Deepfake is detected ⚠️")

        frames_path = "../../DF_임시데이터/yes_df/yes_df_frames"
        max_prob_frame_path = os.path.join(frames_path, max_prob_frame)

        if os.path.exists(max_prob_frame_path):
            st.image(max_prob_frame_path, use_container_width=True)
        else:
            st.error("Error loading the frame image.")

    else:
        st.markdown("#### No Deepfake Detected 🎉")

    # 결과 자세히 보러가기 버튼
    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    def click_button():
        st.session_state.clicked = True

    st.button("View results in detail", on_click=click_button)

# 자세한 결과 출력
def detail_result(placeholder):
    placeholder.empty()

    high_prob_frames = st.session_state.high_prob_frames

    # 확률이 높은 프레임들 출력
    st.markdown("### ⚠️ Deepfake is detected ⚠️")
    frame_path = "../../DF_임시데이터/yes_df/yes_df_frames"

    frame_index = st.slider("Select Frame", 0, len(high_prob_frames) - 1, 0)
    selected_frame, selected_probability = high_prob_frames[frame_index]
    frame_img_path = os.path.join(frame_path, selected_frame)

    # gradcam 방식으로 프레임들 출력
    gradcam_toggle = st.checkbox("Show Grad-CAM")

    if gradcam_toggle:
        gradcam_img_path = os.path.join(frame_path, f"gradcam_{selected_frame}")
        if os.path.exists(gradcam_img_path):
            st.image(frame_img_path, caption=f"Frame: {selected_frame} (Probability: {selected_probability:.2f})")
        else:
            st.error("Grad-CAM image not found.")
    else:
        st.image(frame_img_path, caption=f"'{selected_frame}' is suspected to be deepfake with {selected_probability*100:.2f}%")
