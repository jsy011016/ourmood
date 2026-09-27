# server.py
from flask import Flask, request, jsonify
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

    print("CatVTON 파이프라인 로딩 중...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    weight_dtype = torch.float16 if device == "cuda" else torch.float32

    # 모델 다운로드
    repo_path = snapshot_download(repo_id="zhengchong/CatVTON")

    # 파이프라인 로드
    pipeline = CatVTONPipeline(
        base_ckpt="booksforcharlie/stable-diffusion-inpainting",
        attn_ckpt=repo_path,
        attn_ckpt_version="mix",
        weight_dtype=weight_dtype,
        device=device,
        skip_safety_check=True
    )

    # AutoMasker 로드 (중요!)
    automasker = AutoMasker(
        densepose_ckpt=os.path.join(repo_path, "DensePose"),
        schp_ckpt=os.path.join(repo_path, "SCHP"),
        device=device,
    )

    # Mask Processor
    mask_processor = VaeImageProcessor(
        vae_scale_factor=8,
        do_normalize=False,
        do_binarize=True,
        do_convert_grayscale=True
    )

    print("파이프라인 로드 완료!")


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


def run_inference(person_img, cloth_img):
    """실제 가상 피팅 실행"""
    # 표준 크기로 조정
    person_img = person_img.resize((768, 1024))
    cloth_img = cloth_img.resize((768, 1024))

    print("AutoMasker로 마스크 생성 중...")
    # AutoMasker로 정확한 마스크 생성
    mask = automasker(person_img, "upper")['mask']
    mask = mask_processor.blur(mask, blur_factor=9)

    print("가상 착용 처리 중...")

    # 파이프라인 실행
    result = pipeline(
        image=person_img,
        condition_image=cloth_img,
        mask=mask,
        num_inference_steps=50,
        guidance_scale=2.5,
    )[0]

    return result


@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'model_loaded': pipeline is not None,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu'
    })


@app.route('/api/single-tryon', methods=['POST'])
def single_tryon():
    """단일 의상 피팅"""
    try:
        data = request.json

        print("단일 피팅 요청 받음")

        # Base64 → PIL Image
        person_img = base64_to_image(data['person'])
        cloth_img = base64_to_image(data['cloth'])

        # 추론 실행
        result = run_inference(person_img, cloth_img)

        # PIL Image → Base64
        result_base64 = image_to_base64(result)

        print("단일 피팅 완료!")

        return jsonify({
            'success': True,
            'result': result_base64
        })

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/multi-tryon', methods=['POST'])
def multi_tryon():
    """다중 의상 순차 피팅"""
    try:
        data = request.json

        print("다중 피팅 요청 받음")

        person_img = base64_to_image(data['person'])
        result = person_img

        # 1. 하의 피팅
        if data.get('bottom'):
            print("하의 피팅 중...")
            bottom_img = base64_to_image(data['bottom'])
            result = run_inference(result, bottom_img)

        # 2. 상의 피팅
        if data.get('top'):
            print("상의 피팅 중...")
            top_img = base64_to_image(data['top'])
            result = run_inference(result, top_img)

        # 3. 아우터 피팅
        if data.get('outer'):
            print("아우터 피팅 중...")
            outer_img = base64_to_image(data['outer'])
            result = run_inference(result, outer_img)

        # 결과 변환
        result_base64 = image_to_base64(result)

        print("다중 피팅 완료!")

        return jsonify({
            'success': True,
            'result': result_base64
        })

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 서버 시작 전 모델 로드
    load_pipeline()

    print("\n" + "=" * 50)
    print("Flask 서버 시작!")
    print("주소: http://localhost:5000")
    print("=" * 50 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )