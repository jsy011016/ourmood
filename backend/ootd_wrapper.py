import sys
import os

sys.path.append('../OOTDiffusion')

import torch
from PIL import Image
import numpy as np
from pathlib import Path


class OOTDiffusionWrapper:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        try:
            # OOTDiffusion 모델 로드
            from run.run_ootd import OOTDiffusionPipeline

            self.pipe = OOTDiffusionPipeline(
                model_path="../OOTDiffusion/checkpoints/ootd/ootd_hd",
                device=self.device
            )

            print("✅ OOTDiffusion 모델 로드 완료!")
            self.model_loaded = True

        except Exception as e:
            print(f"❌ OOTDiffusion 로드 실패: {e}")
            self.model_loaded = False

    def generate_tryon(self, person_image_path, garment_image_path):
        """실제 OOTDiffusion 가상피팅"""
        if not self.model_loaded:
            print("❌ 모델이 로드되지 않았습니다.")
            return None

        try:
            print("🎨 OOTDiffusion 가상피팅 시작...")

            # 이미지 로드
            person_img = Image.open(person_image_path).convert("RGB")
            garment_img = Image.open(garment_image_path).convert("RGB")

            # OOTDiffusion 추론
            result = self.pipe(
                model_img=person_img,
                cloth_img=garment_img,
                scale=2.0,
                sample=4,
                num_inference_steps=20
            )

            print("✅ OOTDiffusion 가상피팅 완료!")
            return result

        except Exception as e:
            print(f"❌ OOTDiffusion 처리 중 오류: {e}")
            return None


# 전역 인스턴스
ootd_model = None


def get_ootd_model():
    global ootd_model
    if ootd_model is None:
        ootd_model = OOTDiffusionWrapper()
    return ootd_model