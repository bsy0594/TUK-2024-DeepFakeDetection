import streamlit as st

def howToUse():
    st.markdown(
        """
        ### 🔎 How to use Fake Marker 
        ##### 1. File Upload
        - You can upload videos and images. Images are optional.
        - By uploading images, the model can undergo additional training, which may improve its performance.
        ##### 2. Personal Data Collection
        - Uploaded images and videos may contain personal data.
        - By uploading these files to our web service, you are deemed to have consented to the collection of your personal data.
        #####
        """
    )

    if st.button("Start 🚀"):
        st.switch_page("pages/Detection.py")