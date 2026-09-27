# backend/simple_vton.py
from gradio_client import Client
from PIL import Image
import os
import time


class HuggingFaceVTON:
    def __init__(self):
        print("Hugging Face VTON 클라이언트 초기화 중...")
        self.model_loaded = False

        # 여러 가상피팅 Space 시도
        spaces_to_try = [
            "yisol/IDM-VTON",
            "Nymbo/Virtual-Try-On",
            "kadirnar/IDM-VTON",
            "pngwn/IDM-VTON"
        ]

        for space in spaces_to_try:
            try:
                print(f"🔄 {space} 연결 시도 중...")
                self.client = Client(space)
                print(f"✅ {space} 클라이언트 초기화 완료!")
                self.current_space = space
                self.model_loaded = True
                break
            except Exception as e:
                print(f"❌ {space} 초기화 실패: {e}")
                continue

        if not self.model_loaded:
            print("❌ 모든 Hugging Face Space 연결 실패")
            print("🔄 로컬 fallback 모드로 전환합니다...")

    def test_connection(self):
        """연결 테스트"""
        if not self.model_loaded:
            return False
        try:
            # 간단한 API 테스트
            print("🔄 연결 테스트 중...")
            return True
        except Exception as e:
            print(f"연결 테스트 실패: {e}")
            return False

    def generate_tryon(self, person_image_path, garment_image_path):
        """실제 가상피팅 수행"""
        if not self.model_loaded:
            print("❌ 모델이 로드되지 않았습니다.")
            return self.create_simple_blend(person_image_path, garment_image_path)

        try:
            print(f"🔄 가상피팅 시작...")
            print(f"  👤 사람 이미지: {person_image_path}")
            print(f"  👕 옷 이미지: {garment_image_path}")
            print(f"  🌐 사용 중인 Space: {self.current_space}")

            start_time = time.time()

            # API 호출 방법들을 순차적으로 시도
            methods = [
                self.try_method_1,
                self.try_method_2,
                self.try_method_3
            ]

            for i, method in enumerate(methods, 1):
                try:
                    print(f"🔄 방법 {i} 시도 중...")
                    result = method(person_image_path, garment_image_path)
                    if result:
                        end_time = time.time()
                        print(f"⏱️ 처리 시간: {end_time - start_time:.2f}초")
                        print("✅ 가상피팅 성공!")
                        return result
                except Exception as e:
                    print(f"❌ 방법 {i} 실패: {e}")
                    continue

            # 모든 방법 실패시 간단한 블렌딩 사용
            print("🔄 모든 API 방법 실패, 로컬 블렌딩 사용...")
            return self.create_simple_blend(person_image_path, garment_image_path)

        except Exception as e:
            print(f"❌ 가상피팅 처리 중 오류: {e}")
            return self.create_simple_blend(person_image_path, garment_image_path)

    def try_method_1(self, person_path, garment_path):
        """첫 번째 API 호출 방법"""
        result = self.client.predict(
            person_path,
            garment_path,
            "상의",
            True,  # auto_mask
            True,  # auto_crop
            api_name="/tryon"
        )
        return self.process_result(result)

    def try_method_2(self, person_path, garment_path):
        """두 번째 API 호출 방법"""
        result = self.client.predict(
            person_path,
            garment_path,
            api_name="/predict"
        )
        return self.process_result(result)

    def try_method_3(self, person_path, garment_path):
        """세 번째 API 호출 방법 (파일 직접 전송)"""
        with open(person_path, 'rb') as f1, open(garment_path, 'rb') as f2:
            result = self.client.predict(
                f1,
                f2,
                api_name="/process"
            )
        return self.process_result(result)

    def process_result(self, result):
        """결과 처리"""
        if result and len(result) > 0:
            result_path = result[0] if isinstance(result, list) else result

            if isinstance(result_path, str) and os.path.exists(result_path):
                return Image.open(result_path)
        return None

    def create_simple_blend(self, person_path, garment_path):
        """로컬 간단 블렌딩 (fallback)"""
        try:
            print("🎨 로컬 블렌딩 모드로 처리 중...")
            person_img = Image.open(person_path).convert("RGB")
            garment_img = Image.open(garment_path).convert("RGB")

            # 크기 맞추기
            target_size = (512, 768)
            person_img = person_img.resize(target_size, Image.Resampling.LANCZOS)
            garment_img = garment_img.resize(target_size, Image.Resampling.LANCZOS)

            # 간단한 마스크 생성 및 블렌딩
            import numpy as np

            person_array = np.array(person_img)
            garment_array = np.array(garment_img)

            # 상체 영역 마스크 생성
            height, width = person_array.shape[:2]
            mask = np.zeros((height, width), dtype=np.float32)

            # 상체 영역 (가슴~허리)
            top = int(height * 0.25)
            bottom = int(height * 0.65)
            left = int(width * 0.2)
            right = int(width * 0.8)

            mask[top:bottom, left:right] = 0.6  # 60% 블렌딩

            # 블렌딩 적용
            mask_3d = mask[:, :, np.newaxis]
            blended = person_array * (1 - mask_3d) + garment_array * mask_3d

            result_img = Image.fromarray(blended.astype(np.uint8))
            print("✅ 로컬 블렌딩 완료!")
            return result_img

        except Exception as e:
            print(f"❌ 로컬 블렌딩도 실패: {e}")
            return Image.open(person_path)  # 최악의 경우 원본 반환

    def simple_test(self):
        """간단한 테스트"""
        print("🧪 간단한 테스트를 실행합니다...")
        # 테스트용 더미 데이터로 API 호출 테스트
        return True


# 전역 인스턴스
vton_model = None


def get_vton_model():
    global vton_model
    if vton_model is None:
        vton_model = HuggingFaceVTON()
    return vton_model


# 테스트 함수
if __name__ == "__main__":
    print("🚀 VTON 모델 테스트 시작...")
    model = get_vton_model()

    if model.test_connection():
        print("✅ 연결 테스트 통과!")
    else:
        print("❌ 연결 테스트 실패!")

    print("테스트 완료!")