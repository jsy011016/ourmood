# backend/improved_vton.py
import torch
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import cv2
import os


class ImprovedVTON:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        try:
            # 사람 세그멘테이션 모델 로드
            from transformers import pipeline
            self.segmentation_pipeline = pipeline(
                "image-segmentation",
                model="mattmdjaga/segformer_b2_clothes",
                device=0 if self.device == "cuda" else -1
            )
            self.segmentation_loaded = True
            print("✅ 세그멘테이션 모델 로드 완료!")
        except Exception as e:
            print(f"⚠️ 세그멘테이션 모델 로드 실패: {e}")
            self.segmentation_loaded = False

        self.model_loaded = True

    def segment_person(self, image):
        """사람 이미지에서 옷 영역 세그멘테이션"""
        try:
            if not self.segmentation_loaded:
                return self.create_simple_mask(image)

            # Segformer로 옷 영역 감지
            segments = self.segmentation_pipeline(image)

            # 상의 영역 마스크 생성
            mask = np.zeros((image.size[1], image.size[0]), dtype=np.uint8)

            for segment in segments:
                label = segment['label'].lower()
                if any(cloth_type in label for cloth_type in ['shirt', 'top', 'upper', 'dress']):
                    segment_mask = np.array(segment['mask'])
                    mask = np.logical_or(mask, segment_mask)

            return Image.fromarray(mask.astype(np.uint8) * 255, mode='L')

        except Exception as e:
            print(f"세그멘테이션 실패, 단순 마스크 사용: {e}")
            return self.create_simple_mask(image)

    def create_simple_mask(self, image):
        """간단한 상체 마스크 생성"""
        width, height = image.size
        mask = Image.new('L', (width, height), 0)

        draw = ImageDraw.Draw(mask)

        # 상체 영역 (가슴~허리)
        left = int(width * 0.2)
        right = int(width * 0.8)
        top = int(height * 0.25)
        bottom = int(height * 0.65)

        # 타원형 마스크
        draw.ellipse([left, top, right, bottom], fill=255)

        return mask

    def remove_garment_background(self, garment_img):
        """옷 이미지 배경 제거"""
        try:
            # OpenCV로 배경 제거
            img_array = np.array(garment_img)

            # 흰색 배경 제거
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 마스크 적용
            result = img_array.copy()
            result[mask == 0] = [255, 255, 255]  # 배경을 흰색으로

            return Image.fromarray(result)

        except Exception as e:
            print(f"배경 제거 실패: {e}")
            return garment_img

    def enhance_garment_fit(self, person_img, garment_img, mask):
        """옷을 사람 체형에 맞게 조정"""
        try:
            # 마스크 영역의 평균 색상 추출
            person_array = np.array(person_img)
            mask_array = np.array(mask) / 255.0

            # 사람 피부톤 추출 (마스크 외부 영역)
            skin_mask = 1 - mask_array
            if skin_mask.sum() > 0:
                skin_color = person_array[skin_mask > 0.5].mean(axis=0)
            else:
                skin_color = [200, 180, 160]  # 기본 피부톤

            # 옷 이미지 조정
            garment_array = np.array(garment_img)

            # 조명 조정 (사람 이미지의 조명에 맞춤)
            person_brightness = person_array.mean()
            garment_brightness = garment_array.mean()

            if abs(person_brightness - garment_brightness) > 20:
                brightness_ratio = person_brightness / garment_brightness
                garment_array = np.clip(garment_array * brightness_ratio, 0, 255)

            return Image.fromarray(garment_array.astype(np.uint8))

        except Exception as e:
            print(f"옷 피팅 조정 실패: {e}")
            return garment_img

    def create_smooth_blend(self, person_img, garment_img, mask):
        """부드러운 블렌딩"""
        try:
            person_array = np.array(person_img)
            garment_array = np.array(garment_img)
            mask_array = np.array(mask) / 255.0

            # 가우시안 블러로 마스크 부드럽게
            mask_blurred = cv2.GaussianBlur(mask_array, (21, 21), 0)
            mask_3d = mask_blurred[:, :, np.newaxis]

            # 그라디언트 블렌딩
            blended = person_array * (1 - mask_3d) + garment_array * mask_3d

            # 경계면 스무딩
            boundary_mask = cv2.Canny((mask_array * 255).astype(np.uint8), 50, 150)
            boundary_kernel = np.ones((5, 5), np.uint8)
            boundary_mask = cv2.dilate(boundary_mask, boundary_kernel, iterations=1)

            # 경계 영역에 추가 블러 적용
            boundary_coords = np.where(boundary_mask > 0)
            if len(boundary_coords[0]) > 0:
                blurred_result = cv2.GaussianBlur(blended.astype(np.uint8), (5, 5), 0)
                blended[boundary_coords] = blurred_result[boundary_coords]

            return Image.fromarray(blended.astype(np.uint8))

        except Exception as e:
            print(f"블렌딩 실패: {e}")
            return person_img

    def add_realistic_effects(self, result_img):
        """현실적인 효과 추가"""
        try:
            # 약간의 선명도 증가
            enhancer = ImageEnhance.Sharpness(result_img)
            result_img = enhancer.enhance(1.1)

            # 대비 조정
            enhancer = ImageEnhance.Contrast(result_img)
            result_img = enhancer.enhance(1.05)

            # 색상 포화도 조정
            enhancer = ImageEnhance.Color(result_img)
            result_img = enhancer.enhance(1.02)

            return result_img

        except Exception as e:
            print(f"효과 추가 실패: {e}")
            return result_img

    def generate_tryon(self, person_image_path, garment_image_path):
        """개선된 가상피팅 생성"""
        try:
            print("🎨 개선된 가상피팅 시작...")

            # 이미지 로드 및 크기 조정
            person_img = Image.open(person_image_path).convert("RGB")
            garment_img = Image.open(garment_image_path).convert("RGB")

            target_size = (512, 768)
            person_img = person_img.resize(target_size, Image.Resampling.LANCZOS)
            garment_img = garment_img.resize(target_size, Image.Resampling.LANCZOS)

            print("📐 이미지 크기 조정 완료")

            # 1. 사람 이미지에서 옷 영역 세그멘테이션
            print("🔍 옷 영역 세그멘테이션 중...")
            mask = self.segment_person(person_img)

            # 2. 옷 이미지 배경 제거
            print("🧹 옷 배경 제거 중...")
            garment_img = self.remove_garment_background(garment_img)

            # 3. 옷을 사람 체형에 맞게 조정
            print("👔 옷 피팅 조정 중...")
            garment_img = self.enhance_garment_fit(person_img, garment_img, mask)

            # 4. 부드러운 블렌딩
            print("🎨 이미지 블렌딩 중...")
            result_img = self.create_smooth_blend(person_img, garment_img, mask)

            # 5. 현실적인 효과 추가
            print("✨ 마무리 효과 추가 중...")
            result_img = self.add_realistic_effects(result_img)

            print("✅ 개선된 가상피팅 완료!")
            return result_img

        except Exception as e:
            print(f"❌ 가상피팅 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None


# 전역 인스턴스
improved_vton_model = None


def get_improved_vton_model():
    global improved_vton_model
    if improved_vton_model is None:
        print("ImprovedVTON 모델 초기화 중...")
        improved_vton_model = ImprovedVTON()
    return improved_vton_model


# 테스트 함수
if __name__ == "__main__":
    print("🧪 ImprovedVTON 테스트 시작...")
    model = get_improved_vton_model()
    print("테스트 완료!")