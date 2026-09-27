# test3.py
from PIL import Image
import requests
import base64
import io


def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# 이미지 로드
person = Image.open("input_person.jpg")
cloth = Image.open("input_cloth.jpg")

person_b64 = "data:image/png;base64," + image_to_base64(person)
cloth_b64 = "data:image/png;base64," + image_to_base64(cloth)

print("API 호출 중...")

# API 호출
response = requests.post(
    "http://localhost:5000/api/single-tryon",
    json={
        "person": person_b64,
        "cloth": cloth_b64
    }
)

# 결과 확인
result = response.json()
print(f"Success: {result['success']}")

# ===== 여기 추가! =====
if result['success']:
    print("✅ 결과 저장 중...")
    # Base64 디코딩
    result_data = result['result'].split(',')[1]
    result_bytes = base64.b64decode(result_data)

    # 이미지로 변환 및 저장
    result_img = Image.open(io.BytesIO(result_bytes))
    result_img.save("test_result.jpg")

    print("✅ 저장 완료: test_result.jpg")
    print("확인: explorer test_result.jpg")
else:
    print(f"❌ 에러: {result.get('error')}")