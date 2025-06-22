# deepfake-ml

## Requirements

- **Python** 3.10.13

## Setup

1. **Create & activate** a new environment  
   # conda
    ```bash
   conda create -n dfml python=3.10.13 -y
   conda activate dfml
   ```

   # or with venv
    ```bash
   python3.10 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

2. **Install dependencies** 
    ```bash
    pip install -r requirements.txt
    ```

3. **Install .pth***
    구글 드라이브 링크를 올려둘테니, 복사해서 다운로드
    ```bash
    https://drive.google.com/file/d/1I1t9quDe4kRtvPulbmba1QFOHYyDB8fT/view?usp=drive_link
    ```
    다운로드 후, 
    deepfake_ml/deepfake-adapter/outputs/checkpoints/ffpp_c23/
    안에 넣어서 예측 진행.

4. 중요 사항
    
    XAI가 구현이 완료가 되었으나, 기존 사진 크기를 유지하여 처리하는 것은 시간이 오래 걸림...
    그래서 기존의 220x220 크기를 유지하면서 진행을 하였음...

5. 서버 구현시 사용하면 되는 코드

    deepfake-adapter/scripts 안에 있는 inference.py와 xai_inference.py 코드 두 가지만 실행하면 됨.
    - inference.py 실행하면 각 프레임 단위로 자르고 확률 출력.
    - xai_inference.py 실행하면 각 프레임 단위로 xai 이미지 제작