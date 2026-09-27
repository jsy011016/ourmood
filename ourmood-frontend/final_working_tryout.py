# final_working_tryout.py 수정
import torch
import os
from PIL import Image
from diffusers.image_processor import VaeImageProcessor
from model.pipeline import CatVTONPipeline
from model.cloth_masker import AutoMasker
from huggingface_hub import snapshot_download

# 파이프라인 로딩
device = "cuda" if torch.cuda.is_available() else "cpu"
weight_dtype = torch.float16 if device == "cuda" else torch.float32

repo_path = snapshot_download(repo_id="zhengchong/CatVTON")

pipeline = CatVTONPipeline(
    base_ckpt="booksforcharlie/stable-diffusion-inpainting",
    attn_ckpt=repo_path,
    attn_ckpt_version="mix",
    weight_dtype=weight_dtype,
    device=device,
    skip_safety_check=True
)

# AutoMasker 로딩 (중요!)
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

# 이미지 로드
person_dir = r"D:\virtual-fitting-new\CatVTON\resource\demo\example\person\women"
cloth_dir = r"D:\virtual-fitting-new\CatVTON\resource\demo\example\cloth"

person_files = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
cloth_files = [f for f in os.listdir(cloth_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

person_path = os.path.join(person_dir, person_files[0])
cloth_path = os.path.join(cloth_dir, cloth_files[0])

person_img = Image.open(person_path).convert('RGB').resize((768, 1024))
cloth_img = Image.open(cloth_path).convert('RGB').resize((768, 1024))

# AutoMasker로 정확한 마스크 생성
print("마스크 생성 중...")
mask = automasker(person_img, "upper")['mask']  # "upper" = 상의
mask = mask_processor.blur(mask, blur_factor=9)
mask.save("generated_mask.png")
print("마스크 생성 완료")

# 가상 착용 실행
print("처리 중...")
result = pipeline(
    image=person_img,
    condition_image=cloth_img,
    mask=mask,
    num_inference_steps=50,
    guidance_scale=2.5,
)[0]

result.save("virtual_tryout_result.jpg")
person_img.save("input_person.jpg")
cloth_img.save("input_cloth.jpg")
print("완료!")