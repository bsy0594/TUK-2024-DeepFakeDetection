import streamlit as st

def howToUse():
    st.markdown(
        """
        ### 🔎 How to use Fake Marker 
        ##### 1. File Upload
        - You can upload videos and images. Images are optional.
        - By uploading images, the model can undergo additional training, which may improve its performance.
        ##### 2. Model Selection
        - CNN-based Model: It has **fast detection speed** but may lead to lower accuracy.
        - Transformer-based Model: This model can lead to **better detection accuracy** but the detection speed is slow.
        #####
        """
    )

    if st.button("Start 🚀"):
        st.switch_page("pages/Detection.py")