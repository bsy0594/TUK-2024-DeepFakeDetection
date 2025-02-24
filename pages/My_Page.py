import streamlit as st

from sidebar import sidebar

st.write("# 탐지 기록 확인")

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from Detections;', ttl=600) # 10 minutes for cache.

# Print results.
for row in df.itertuples():
    st.write(f"{row.user_id} has a document {row.document_path}:")

st.write("1. 로그인한 사용자의 기록을 DB에서 가져오기")
st.write("2-a. 선택한 날짜 별로 기록 보여주기")
st.write("2-b. 기록 별로 영상이 저장된 경로를 통해 영상 보여주기")
st.write("2-c. 문서를 생성했다면 문서가 저장된 경로를 통해 문서를 저장받을 수 있도록 하기")
st.write("3. 쿼리로 기록 삭제하기 기능 추가하기")

sidebar()