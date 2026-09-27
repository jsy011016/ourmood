# server_old.py - 미묘한 차이 버전 (어깨/목 부분만 부정확)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch
import base64
import io
import os
import numpy as np
from PIL import Image
from diffusers.image_processor import VaeImageProcessor
from huggingface_hub import snapshot_download

# CatVTON imports
from model.pipeline import CatVTONPipeline
from model.cloth_masker import AutoMasker

app = Flask(__name__)
CORS(app)

# 전역 변수
pipeline = None
automasker = None
mask_processor = None


def load_pipeline():
    """서버 시작 시 모델 로드"""
    global pipeline, automasker, mask_processor

    print("⚠️ CatVTON 파이프라인 로딩 중 (기본 버전)...")
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

    print("⚠️ 파이프라인 로드 완료 (기본 버전)!")


def base64_to_image(base64_str):
    """Base64 문자열을 PIL Image로 변환"""
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]

    img_data = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_data)).convert('RGB')
    return img


def image_to_base64(image):
    """PIL Image를 Base64 문자열로 변환"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


def run_inference(person_img, cloth_img, garment_type="upper"):
    """
    ⚠️ 기본 가상 피팅 (미묘한 차이)

    차이점:
    - SCHP 파싱 맵 사용 안 함 (AutoMasker의 기본 mask만)
    - 어깨/목 영역 정확도 낮음
    - 얼굴 보호 없음

    지원하는 garment_type:
    - "upper": 상의 (셔츠, 티셔츠, 블라우스 등)
    - "lower": 하의 (바지, 치마 등)
    - "overall": 원피스, 드레스
    """
    person_img = person_img.resize((768, 1024))
    cloth_img = cloth_img.resize((768, 1024))

    # garment_type 유효성 검사
    valid_types = ["upper", "lower", "overall"]
    if garment_type not in valid_types:
        print(f"⚠️ 잘못된 garment_type: {garment_type}, 기본값 'upper' 사용")
        garment_type = "upper"

    print(f"⚠️ 기본 마스크 생성 중... (타입: {garment_type})")

    # ⚠️ AutoMasker 사용하지만 SCHP 파싱 맵은 안 씀
    mask_result = automasker(person_img, garment_type)

    # ❌ 단순히 mask만 가져옴 (SCHP 파싱 결과 무시)
    mask = mask_result['mask']

    # ✅ lower 타입일 때 상의 영역 보호 (허리 위쪽 제거)
    if garment_type == "lower":
        mask_array = np.array(mask)
        height, width = mask_array.shape

        # 상위 45%는 마스킹 제거 (허리 기준)
        upper_limit = int(height * 0.45)
        mask_array[:upper_limit, :] = 0

        mask = Image.fromarray(mask_array)
        print(f"✅ 하의 착용: 상의 영역 보호 (상위 45% 제거)")

    # ❌ 얼굴 보호 없음 (상단 30% 제거 안 함)
    # ❌ 어깨 영역 추가 없음

    # 기본 블러
    mask = mask_processor.blur(mask, blur_factor=9)

    # 마스크 저장
    mask_filename = f"mask_old_{garment_type}.png"
    mask.save(mask_filename)
    print(f"마스크 저장: {mask_filename}")

    print(f"⚠️ 가상 착용 처리 중 (기본 버전, {garment_type})...")

    result = pipeline(
        image=person_img,
        condition_image=cloth_img,
        mask=mask,
        num_inference_steps=50,  # 같은 값 유지
        guidance_scale=2.5,  # 같은 값 유지
    )

    if isinstance(result, list):
        final_result = result[0] if len(result) > 0 else None
    else:
        final_result = result

    if isinstance(final_result, np.ndarray):
        final_result = Image.fromarray(final_result)

    return final_result


@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok (BASIC VERSION)',
        'model_loaded': pipeline is not None,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'supported_types': ['upper', 'lower', 'overall'],
        'schp_parsing': 'NOT USED',
        'shoulder_mask': 'NOT USED',
        'face_protection': 'NOT USED'
    })


@app.route('/virtual-fitting', methods=['POST'])
def virtual_fitting():
    """FormData 방식 가상 피팅 (기본 버전)"""
    try:
        print("\n" + "=" * 50)
        print("📥 가상 피팅 요청 받음 (⚠️ 기본 버전)")

        # 1. 사용자 이미지
        if 'person_image' not in request.files:
            return jsonify({'error': 'No person_image'}), 400

        person_file = request.files['person_image']
        person_img = Image.open(person_file.stream).convert('RGB')
        print(f"✅ 사용자 이미지: {person_file.filename}, {person_img.size}")

        # 2. 옷 이미지 경로
        cloth_image_path = request.form.get('cloth_image_path')
        print(f"📁 옷 이미지 경로: {cloth_image_path}")

        # 3. 옷 타입 (upper, lower, overall)
        cloth_type = request.form.get('cloth_type', 'upper')
        valid_types = ['upper', 'lower', 'overall']

        if cloth_type not in valid_types:
            print(f"⚠️ 잘못된 cloth_type: {cloth_type}, 기본값 'upper' 사용")
            cloth_type = 'upper'

        print(f"👗 옷 타입: {cloth_type}")

        # 4. 옷 이미지 로드
        if cloth_image_path.startswith('http'):
            import requests
            response = requests.get(cloth_image_path, timeout=10)
            cloth_img = Image.open(io.BytesIO(response.content)).convert('RGB')
        elif cloth_image_path.startswith('/uploads'):
            local_path = cloth_image_path.replace('/uploads/products/', 'uploads/products/')
            if not os.path.exists(local_path):
                return jsonify({'error': f'File not found: {local_path}'}), 404
            cloth_img = Image.open(local_path).convert('RGB')
        else:
            return jsonify({'error': 'Invalid cloth_image_path'}), 400

        print(f"✅ 옷 이미지 로드: {cloth_img.size}")

        # 5. ⚠️ 기본 버전 가상 피팅
        print(f"⚠️ 가상 피팅 시작... (기본 버전, {cloth_type})")
        result = run_inference(person_img, cloth_img, cloth_type)
        print(f"⚠️ 가상 피팅 완료 (기본 버전, {cloth_type})!")

        if result is None:
            return jsonify({'error': '결과 생성 실패'}), 500

        # 6. 결과 반환
        img_io = io.BytesIO()
        result.save(img_io, 'PNG')
        img_io.seek(0)

        print("📤 결과 이미지 전송")
        print("=" * 50 + "\n")

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        print(f"❌ 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/single-tryon', methods=['POST'])
def single_tryon():
    """단일 의상 피팅 (기본 버전)"""
    try:
        data = request.json
        print("단일 피팅 요청 받음 (기본 버전)")

        person_img = base64_to_image(data['person'])
        cloth_img = base64_to_image(data['cloth'])
        garment_type = data.get('garment_type', 'upper')

        # garment_type 유효성 검사
        valid_types = ['upper', 'lower', 'overall']
        if garment_type not in valid_types:
            print(f"⚠️ 잘못된 garment_type: {garment_type}, 기본값 'upper' 사용")
            garment_type = 'upper'

        result = run_inference(person_img, cloth_img, garment_type)

        if result is None:
            return jsonify({'success': False, 'error': '결과 생성 실패'}), 500

        result_base64 = image_to_base64(result)
        print(f"단일 피팅 완료 (기본 버전, {garment_type})!")

        return jsonify({
            'success': True,
            'result': result_base64,
            'garment_type': garment_type
        })

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    load_pipeline()

    print("\n" + "=" * 50)
    print("⚠️ Flask 서버 시작! (기본 버전)")
    print("📍 주소: http://localhost:5002")
    print("")
    print("지원하는 의상 타입:")
    print("  👕 upper: 상의 (셔츠, 티셔츠, 블라우스 등)")
    print("  👖 lower: 하의 (바지, 치마 등)")
    print("  👗 overall: 원피스, 드레스")
    print("")
    print("기본 방식 (Before):")
    print("  ⚠️ AutoMasker의 기본 mask만 사용")
    print("  ⚠️ SCHP 파싱 맵 미활용")
    print("  ⚠️ 어깨/목 영역 부정확")
    print("  ⚠️ 얼굴 보호 없음")
    print("")
    print("개선 방식 (After)과 차이:")
    print("  ✅ SCHP 파싱 맵으로 정확한 영역 인식")
    print("  ✅ 타원형 어깨 마스크 추가")
    print("  ✅ 얼굴 영역 보호 (상단 30%)")
    print("=" * 50 + "\n")

    app.run(
        host='0.0.0.0',
        port=5002,
        debug=False
    )