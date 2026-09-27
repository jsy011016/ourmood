"""
CatVTON 퀄리티 개선 유틸리티
- 이미지 전처리 (노이즈 제거, 대비 향상)
- 마스크 정확도 개선
- 후처리 (색상 보정, 경계선 블렌딩)
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2


class QualityImprover:
    """가상 피팅 품질 개선"""

    @staticmethod
    def preprocess_person_image(image):
        """
        사람 이미지 전처리
        - 조명 정규화
        - 선명도 향상
        - 노이즈 제거
        """
        # PIL -> numpy
        img_array = np.array(image)

        # 1. 조명 정규화 (CLAHE)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        lab = cv2.merge([l, a, b])
        img_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # 2. 가벼운 노이즈 제거
        img_array = cv2.fastNlMeansDenoisingColored(img_array, None, 5, 5, 7, 21)

        # 3. 선명도 향상
        image = Image.fromarray(img_array)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)

        return image

    @staticmethod
    def preprocess_garment_image(image):
        """
        의상 이미지 전처리
        - 배경 제거 개선
        - 색상 선명도 향상
        - 주름 감소
        """
        # PIL -> numpy
        img_array = np.array(image)

        # 1. 대비 향상
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        lab = cv2.merge([l, a, b])
        img_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # 2. 색상 선명도
        image = Image.fromarray(img_array)

        # 채도 증가
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)

        # 선명도 증가
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)

        return image

    @staticmethod
    def improve_mask(mask, person_img, garment_type):
        """
        마스크 정확도 개선
        - 형태학적 연산으로 노이즈 제거
        - 경계선 스무딩
        - 영역별 정밀 조정
        """
        mask_array = np.array(mask)
        person_array = np.array(person_img)

        # 1. 형태학적 연산 (작은 구멍 제거)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_CLOSE, kernel)
        mask_array = cv2.morphologyEx(mask_array, cv2.MORPH_OPEN, kernel)

        # 2. 의상 타입별 영역 정밀 조정
        height, width = mask_array.shape

        if garment_type == "upper":
            # 상의: 상단 30%, 하단 20% 제거
            mask_array[:int(height * 0.30), :] = 0
            mask_array[int(height * 0.80):, :] = 0

            # 팔 영역 보정 (양 옆 20% 유지)
            side_margin = int(width * 0.15)
            mask_array[:, :side_margin] = 0
            mask_array[:, width - side_margin:] = 0

        elif garment_type == "lower":
            # 하의: 상단 50%, 하단 10% 제거
            mask_array[:int(height * 0.50), :] = 0
            mask_array[int(height * 0.90):, :] = 0

            # 다리 영역 중심 집중
            center_width = int(width * 0.7)
            margin = (width - center_width) // 2
            for y in range(height):
                if y < height * 0.65:
                    mask_array[y, :margin] = 0
                    mask_array[y, width - margin:] = 0

        elif garment_type == "overall":
            # 원피스: 상단 20%, 하단 5% 제거
            mask_array[:int(height * 0.20), :] = 0
            mask_array[int(height * 0.95):, :] = 0

        # 3. 가우시안 블러로 경계선 스무딩
        mask_array = cv2.GaussianBlur(mask_array, (11, 11), 0)

        # 4. 피부색 기반 추가 마스킹 (선택적)
        # YCrCb 색공간에서 피부색 감지
        ycrcb = cv2.cvtColor(person_array, cv2.COLOR_RGB2YCrCb)

        # 피부색 범위
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

        # 피부 영역은 마스크에서 제외 (약하게)
        skin_mask = cv2.GaussianBlur(skin_mask, (15, 15), 0)
        skin_weight = skin_mask.astype(float) / 255.0
        mask_array = mask_array * (1.0 - skin_weight * 0.3)
        mask_array = mask_array.astype(np.uint8)

        return Image.fromarray(mask_array, mode='L')

    @staticmethod
    def postprocess_result(result_img, original_person, cloth_img):
        """
        결과 이미지 후처리
        - 색상 보정
        - 경계선 블렌딩
        - 전체적인 자연스러움 향상
        """
        result_array = np.array(result_img)
        original_array = np.array(original_person.resize(result_img.size))
        cloth_array = np.array(cloth_img.resize(result_img.size))

        # 1. 색온도 매칭 (의상 색상을 결과에 더 반영)
        # LAB 색공간에서 색상 채널 조정
        result_lab = cv2.cvtColor(result_array, cv2.COLOR_RGB2LAB)
        cloth_lab = cv2.cvtColor(cloth_array, cv2.COLOR_RGB2LAB)

        # A, B 채널 (색상) 보정
        result_lab[:, :, 1] = (result_lab[:, :, 1] * 0.7 + cloth_lab[:, :, 1] * 0.3).astype(np.uint8)
        result_lab[:, :, 2] = (result_lab[:, :, 2] * 0.7 + cloth_lab[:, :, 2] * 0.3).astype(np.uint8)

        result_array = cv2.cvtColor(result_lab, cv2.COLOR_LAB2RGB)

        # 2. 디테일 복원 (언샤프 마스크)
        gaussian = cv2.GaussianBlur(result_array, (0, 0), 2.0)
        result_array = cv2.addWeighted(result_array, 1.5, gaussian, -0.5, 0)

        # 3. 전체적인 대비 향상
        lab = cv2.cvtColor(result_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        lab = cv2.merge([l, a, b])
        result_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # 4. 노이즈 감소 (약하게)
        result_array = cv2.fastNlMeansDenoisingColored(result_array, None, 3, 3, 7, 21)

        return Image.fromarray(result_array)

    @staticmethod
    def blend_edges(result_img, original_person, mask, blend_radius=20):
        """
        마스크 경계선 부드럽게 블렌딩
        """
        result_array = np.array(result_img).astype(float)
        original_array = np.array(original_person.resize(result_img.size)).astype(float)
        mask_array = np.array(mask.resize(result_img.size)).astype(float) / 255.0

        # 경계선 영역 찾기
        mask_blur = cv2.GaussianBlur(mask_array, (blend_radius * 2 + 1, blend_radius * 2 + 1), 0)

        # 알파 블렌딩
        for c in range(3):
            result_array[:, :, c] = (
                    result_array[:, :, c] * mask_blur +
                    original_array[:, :, c] * (1 - mask_blur)
            )

        result_array = np.clip(result_array, 0, 255).astype(np.uint8)
        return Image.fromarray(result_array)

    @staticmethod
    def enhance_texture(image, strength=1.2):
        """
        텍스처 디테일 향상
        """
        img_array = np.array(image).astype(float)

        # 고주파 성분 추출
        low_freq = cv2.GaussianBlur(img_array, (0, 0), 3)
        high_freq = img_array - low_freq

        # 고주파 성분 강화
        enhanced = img_array + high_freq * (strength - 1.0)
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)

        return Image.fromarray(enhanced)

    @staticmethod
    def color_correction(result_img, reference_img):
        """
        색상 보정 (reference 이미지 기준)
        """
        result_array = np.array(result_img)
        ref_array = np.array(reference_img.resize(result_img.size))

        # LAB 색공간 변환
        result_lab = cv2.cvtColor(result_array, cv2.COLOR_RGB2LAB).astype(float)
        ref_lab = cv2.cvtColor(ref_array, cv2.COLOR_RGB2LAB).astype(float)

        # 각 채널의 평균과 표준편차 맞추기
        for i in range(3):
            result_mean = np.mean(result_lab[:, :, i])
            result_std = np.std(result_lab[:, :, i])

            ref_mean = np.mean(ref_lab[:, :, i])
            ref_std = np.std(ref_lab[:, :, i])

            # 표준편차와 평균 조정
            if result_std > 0:
                result_lab[:, :, i] = (result_lab[:, :, i] - result_mean) * (ref_std / result_std) + ref_mean

        result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
        result_array = cv2.cvtColor(result_lab, cv2.COLOR_LAB2RGB)

        return Image.fromarray(result_array)


class MaskRefiner:
    """마스크 정밀 조정 전문 클래스"""

    @staticmethod
    def refine_upper_mask(mask, person_img):
        """상의 마스크 정밀 조정"""
        mask_array = np.array(mask)
        height, width = mask_array.shape

        # 목 영역 제거 (상단 25%)
        neck_height = int(height * 0.25)
        mask_array[:neck_height, :] = 0

        # 허리 아래 제거 (하단 30%)
        waist_height = int(height * 0.70)
        mask_array[waist_height:, :] = 0

        # 팔 영역 다듬기
        # 중심에서 멀어질수록 감소
        center_x = width // 2
        for y in range(height):
            for x in range(width):
                if mask_array[y, x] > 0:
                    distance_from_center = abs(x - center_x)
                    if distance_from_center > width * 0.35:
                        # 멀리 있으면 감소
                        mask_array[y, x] = int(mask_array[y, x] * 0.5)

        return Image.fromarray(mask_array, mode='L')

    @staticmethod
    def refine_lower_mask(mask, person_img):
        """하의 마스크 정밀 조정"""
        mask_array = np.array(mask)
        height, width = mask_array.shape

        # 상체 제거 (상단 45%)
        upper_height = int(height * 0.45)
        mask_array[:upper_height, :] = 0

        # 발목 아래 제거 (하단 8%)
        ankle_height = int(height * 0.92)
        mask_array[ankle_height:, :] = 0

        # 다리 형태로 좁아지도록
        center_x = width // 2
        for y in range(upper_height, height):
            # 아래로 갈수록 좁아짐
            progress = (y - upper_height) / (height - upper_height)
            max_width = int(width * (0.6 - progress * 0.2))

            left_bound = center_x - max_width // 2
            right_bound = center_x + max_width // 2

            mask_array[y, :left_bound] = 0
            mask_array[y, right_bound:] = 0

        return Image.fromarray(mask_array, mode='L')

    @staticmethod
    def refine_dress_mask(mask, person_img):
        """원피스 마스크 정밀 조정"""
        mask_array = np.array(mask)
        height, width = mask_array.shape

        # 목 영역 제거
        neck_height = int(height * 0.22)
        mask_array[:neck_height, :] = 0

        # 발목 아래 제거
        ankle_height = int(height * 0.93)
        mask_array[ankle_height:, :] = 0

        # 원피스 실루엣 (위는 넓고 아래로 좁아짐 or 넓어짐)
        center_x = width // 2

        # 상체 부분 (넓음)
        upper_end = int(height * 0.5)
        for y in range(neck_height, upper_end):
            max_width = int(width * 0.7)
            left_bound = center_x - max_width // 2
            right_bound = center_x + max_width // 2
            mask_array[y, :left_bound] = 0
            mask_array[y, right_bound:] = 0

        # 하체 부분 (약간 좁아짐)
        for y in range(upper_end, ankle_height):
            max_width = int(width * 0.65)
            left_bound = center_x - max_width // 2
            right_bound = center_x + max_width // 2
            mask_array[y, :left_bound] = 0
            mask_array[y, right_bound:] = 0

        return Image.fromarray(mask_array, mode='L')


# 사용 예시
if __name__ == '__main__':
    print("🎨 Quality Improver 유틸리티")
    print("\n주요 기능:")
    print("1. preprocess_person_image() - 사람 이미지 전처리")
    print("2. preprocess_garment_image() - 의상 이미지 전처리")
    print("3. improve_mask() - 마스크 정확도 개선")
    print("4. postprocess_result() - 결과 후처리")
    print("5. blend_edges() - 경계선 블렌딩")
    print("\nserver.py에 통합하여 사용하세요!")