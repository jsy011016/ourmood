# final_working_tryout.py
import torch
import os
import numpy as np
from PIL import Image
from model.pipeline import CatVTONPipeline
from PIL import ImageDraw


def create_simple_mask(person_img):
    width, height = person_img.size
    mask = np.zeros((height, width), dtype=np.uint8)  # 전부 검은색으로 시작

    # 상의 부분만 흰색으로 (교체할 영역)
    start_h = int(height * 0.30)
    end_h = int(height * 0.50)
    start_w = int(width * 0.28)
    end_w = int(width * 0.72)

    mask[start_h:end_h, start_w:end_w] = 255  # 0이 아니라 255
    return Image.fromarray(mask, mode='L')


# 1. 파이프라인 로딩 (안전 필터 비활성화)
print("CatVTON 파이프라인 로딩 중...")
device = "cuda" if torch.cuda.is_available() else "cpu"
weight_dtype = torch.float16 if device == "cuda" else torch.float32

pipeline = CatVTONPipeline(
    base_ckpt="booksforcharlie/stable-diffusion-inpainting",
    attn_ckpt="zhengchong/CatVTON",
    attn_ckpt_version="mix",
    weight_dtype=weight_dtype,
    device=device,
    use_tf32=True,
    skip_safety_check=True  # 안전 필터 비활성화
)

# 2. 이미지 경로 설정
#person_dir = r"D:\virtual-fitting-new\CatVTON\resource\demo\example\person\women"
#cloth_dir = r"D:\virtual-fitting-new\CatVTON\resource\demo\example\cloth"

# 2. 이미지 경로 설정
person_dir = r"D:\virtual-fitting-new\CatVTON\t1"
cloth_dir = r"D:\virtual-fitting-new\CatVTON\t2"

# 3. 이미지 파일 찾기
person_files = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
cloth_files = [f for f in os.listdir(cloth_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print(f"사람 이미지: {len(person_files)}개")
print(f"의상 이미지: {len(cloth_files)}개")

if person_files and cloth_files:
    # 4. 첫 번째 이미지들로 테스트
    person_path = os.path.join(person_dir, person_files[0])
    cloth_path = os.path.join(cloth_dir, cloth_files[0])

    print(f"테스트 이미지: {person_files[0]} + {cloth_files[0]}")

    # 5. 이미지 로드 및 크기 조정
    person_img = Image.open(person_path).convert('RGB')
    cloth_img = Image.open(cloth_path).convert('RGB')

    # 표준 크기로 조정 (512x768 권장)
    person_img = person_img.resize((512, 768))
    cloth_img = cloth_img.resize((512, 768))

    # 6. 마스크 생성
    mask_img = create_simple_mask(person_img)
    mask_img.save("generated_mask.png")
    print("마스크 이미지 생성 완료")

    print("가상 착용 처리 중... (몇 분 걸릴 수 있습니다)")

    try:
        # 7. 실제 가상 착용 실행
        result = pipeline(
            image=person_img,  # 사람 이미지
            condition_image=cloth_img,  # 의상 이미지
            mask=mask_img,  # 마스크 이미지
            num_inference_steps=50,  # 빠른 처리를 위해 단계 수 줄임
            guidance_scale=7.5,
            height=768,
            width=512
        )

        # 8. 결과 처리 (리스트인지 이미지인지 확인)
        if isinstance(result, list):
            if len(result) > 0:
                final_result = result[0]  # 첫 번째 결과 사용
                print(f"결과 타입: {type(final_result)}")
            else:
                print("결과 리스트가 비어있습니다.")
                final_result = None
        else:
            final_result = result

        if final_result is not None:
            if hasattr(final_result, 'save'):
                final_result.save("virtual_tryout_result1.jpg")
                print("성공! 결과가 virtual_tryout_result.jpg1로 저장되었습니다!")
            else:
                # PIL Image로 변환 시도
                if isinstance(final_result, np.ndarray):
                    final_result = Image.fromarray(final_result)
                    final_result.save("virtual_tryout_result.jpg")
                    print("numpy 배열을 이미지로 변환하여 저장했습니다!")
                else:
                    print(f"알 수 없는 결과 타입: {type(final_result)}")

        # 9. 입력 이미지들도 저장
        person_img.save("input_person.jpg")
        cloth_img.save("input_cloth.jpg")
        print("입력 이미지들도 저장했습니다.")

    except Exception as e:
        print(f"가상 착용 처리 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()

else:
    print("이미지를 찾을 수 없습니다.")