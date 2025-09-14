# src/utils/grouping.py

from pathlib import Path
from typing import List

def get_video_ids_from_paths(frame_paths: List[str]) -> List[str]:
    """
    이미지 경로 리스트에서 각 이미지의 부모 폴더명(=video ID)을 뽑아 반환.
    ex) "/.../Deepfakes/000_003/000_003_00000.jpg" -> "000_003"
    """
    return [Path(p).parent.name for p in frame_paths]
