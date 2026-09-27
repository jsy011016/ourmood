import torch
import os
import time
from PIL import Image
from diffusers.image_processor import VaeImageProcessor
from model.pipeline import CatVTONPipeline
from model.cloth_masker import AutoMasker
from huggingface_hub import snapshot_download

# 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
weight_dtype = torch.float16 if device == "cuda" else torch.float32

print(f"사용 디바이스: {device}")
print("=" * 50)

# 파이프라인 로딩
print("모델 로딩 중...")
repo_path = snapshot_download(repo_id="zhengchong/CatVTON")

pipeline = CatVTONPipeline(
    base_ckpt="booksforcharlie/stable-diffusion-inpainting",
    attn_ckpt=repo_path,
    attn_ckpt_version="mix",
    weight_dtype=weight_dtype,
    device=device,
    skip_safety_check=True
)

automasker = AutoMasker(
    densepose_ckpt=os.path.join(repo_path, "DensePose"),
    schp_ckpt=os.path.join(repo_path, "SCHP"),
    device=device,
)

mask_processor = VaeImageProcessor(
    vae_scale_factor=8,
    do_normalize=False,
    do_binarize=True,
    do_convert_grayscale=True
)

print("모델 로딩 완료!")
print("=" * 50)

# 테스트 이미지 경로 (직접 지정)
person_path = r"D:\virtual-fitting-new\CatVTON\input_person.jpg"
top_cloth_path = r"D:\virtual-fitting-new\CatVTON\input_cloth.jpg"
skirt_path = r"D:\virtual-fitting-new\CatVTON\skirt.jpg"

# 결과 저장 폴더
output_dir = "test_results"
os.makedirs(output_dir, exist_ok=True)


def run_single_test(person_img, cloth_img, test_name, garment_type="upper"):
    """단일 피팅 테스트"""
    start_time = time.time()

    # 크기 조정
    person_img = person_img.resize((768, 1024))
    cloth_img = cloth_img.resize((768, 1024))

    # 마스크 생성
    print(f"  마스크 생성 중 ({garment_type})...")
    mask = automasker(person_img, garment_type)['mask']
    mask = mask_processor.blur(mask, blur_factor=9)

    # 피팅 실행
    print(f"  피팅 실행 중...")
    result = pipeline(
        image=person_img,
        condition_image=cloth_img,
        mask=mask,
        num_inference_steps=50,
        guidance_scale=2.5,
    )[0]

    elapsed_time = time.time() - start_time
    print(f"  완료! (소요 시간: {elapsed_time:.2f}초)")

    return result, elapsed_time


# 이미지 로드
print("\n이미지 로딩 중...")
person_img = Image.open(person_path).convert('RGB')
top_cloth_img = Image.open(top_cloth_path).convert('RGB')
skirt_img = Image.open(skirt_path).convert('RGB')
print("이미지 로딩 완료!")

# 테스트 1: 상의만 피팅
print("\n[테스트 1] 상의 단일 피팅")
print("-" * 50)

result_top, time_top = run_single_test(person_img, top_cloth_img, "top_only", "upper")
result_top.save(os.path.join(output_dir, "test1_top_only.jpg"))
print(f"저장 완료: {output_dir}/test1_top_only.jpg")

# 테스트 2: 스커트만 피팅
print("\n[테스트 2] 스커트 단일 피팅")
print("-" * 50)

result_skirt, time_skirt = run_single_test(person_img, skirt_img, "skirt_only", "lower")
result_skirt.save(os.path.join(output_dir, "test2_skirt_only.jpg"))
print(f"저장 완료: {output_dir}/test2_skirt_only.jpg")

# 테스트 3: 다중 순차 피팅 (상의 → 스커트)
print("\n[테스트 3] 다중 순차 피팅 (상의 → 스커트)")
print("-" * 50)

person_img = Image.open(person_path).convert('RGB')

print("1단계: 상의 피팅")
result_step1, time1 = run_single_test(person_img, top_cloth_img, "multi_step1", "upper")
result_step1.save(os.path.join(output_dir, "test3_step1_top.jpg"))

print("2단계: 스커트 피팅")
result_step2, time2 = run_single_test(result_step1, skirt_img, "multi_step2", "lower")
result_step2.save(os.path.join(output_dir, "test3_step2_skirt.jpg"))

print(f"\n총 소요 시간: {time1 + time2:.2f}초")
print(f"저장 완료: {output_dir}/test3_step*.jpg")

# 테스트 4: 역순 피팅 (스커트 → 상의)
print("\n[테스트 4] 역순 피팅 (스커트 → 상의)")
print("-" * 50)

person_img = Image.open(person_path).convert('RGB')

print("1단계: 스커트 피팅")
result_step1_rev, time1_rev = run_single_test(person_img, skirt_img, "reverse_step1", "lower")
result_step1_rev.save(os.path.join(output_dir, "test4_step1_skirt.jpg"))

print("2단계: 상의 피팅")
result_step2_rev, time2_rev = run_single_test(result_step1_rev, top_cloth_img, "reverse_step2", "upper")
result_step2_rev.save(os.path.join(output_dir, "test4_step2_top.jpg"))

print(f"\n총 소요 시간: {time1_rev + time2_rev:.2f}초")
print(f"저장 완료: {output_dir}/test4_step*.jpg")

# 최종 통계
print("\n" + "=" * 50)
print("성능 통계 요약:")
print(f"  상의 단일 피팅: {time_top:.2f}초")
print(f"  스커트 단일 피팅: {time_skirt:.2f}초")
print(f"  다중 피팅 (상의→스커트): {time1 + time2:.2f}초")
print(f"  다중 피팅 (스커트→상의): {time1_rev + time2_rev:.2f}초")
print("=" * 50)

print(f"\n모든 결과가 '{output_dir}' 폴더에 저장되었습니다!")
print("\n생성된 파일:")
print("  - test1_top_only.jpg (상의만)")
print("  - test2_skirt_only.jpg (스커트만)")
print("  - test3_step1_top.jpg, test3_step2_skirt.jpg (상의→스커트)")
print("  - test4_step1_skirt.jpg, test4_step2_top.jpg (스커트→상의)")