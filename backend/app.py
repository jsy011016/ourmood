# backend/app.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
import os
import io
import uuid
from PIL import Image

# 개선된 VTON 모델 import
from improved_vton import get_improved_vton_model

app = FastAPI(title="Real Virtual Try-On API", version="2.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 폴더 생성
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# 전역 변수
vton_model = None


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 초기화"""
    global vton_model
    print("🚀 개선된 Virtual Try-On 서버 시작...")
    vton_model = get_improved_vton_model()

    if vton_model.model_loaded:
        print("✅ 개선된 VTON 모델 초기화 완료!")
    else:
        print("⚠️ VTON 모델 초기화 실패")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Improved Virtual Try-On API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "AI Segmentation",
            "Background Removal",
            "Smart Blending",
            "Realistic Effects"
        ],
        "endpoints": {
            "upload_form": "/upload-form",
            "try_on": "/try-on",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    model_status = "loaded" if vton_model and vton_model.model_loaded else "failed"
    return {
        "status": "healthy",
        "model_status": model_status,
        "message": "Improved Virtual Try-On API is running"
    }


@app.get("/upload-form")
async def upload_form():
    """개선된 HTML 업로드 폼"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>개선된 Virtual Try-On</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                max-width: 900px; 
                margin: 30px auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 { 
                text-align: center; 
                color: #333; 
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .features {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            .features h3 {
                margin-top: 0;
                color: #495057;
            }
            .features-list {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 10px;
            }
            .feature-item {
                background: #e9ecef;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                color: #495057;
            }
            .upload-section { 
                margin: 25px 0; 
                padding: 25px; 
                border: 3px dashed #ddd; 
                border-radius: 15px; 
                background: #f9f9f9;
                transition: all 0.3s ease;
            }
            .upload-section:hover {
                border-color: #4CAF50;
                background: #f0f8f0;
            }
            .upload-section h3 { 
                color: #333; 
                margin-top: 0;
                font-size: 1.3em;
            }
            .upload-section p {
                color: #666;
                margin: 10px 0;
            }
            input[type="file"] { 
                margin: 15px 0; 
                padding: 10px;
                width: 100%;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button { 
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white; 
                padding: 18px 40px; 
                border: none; 
                border-radius: 10px; 
                cursor: pointer; 
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                margin-top: 20px;
                transition: all 0.3s ease;
            }
            button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .result { 
                margin-top: 30px; 
                text-align: center;
            }
            #loading { 
                display: none; 
                color: #666; 
                text-align: center;
                font-size: 18px;
                margin: 20px 0;
            }
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result img {
                max-width: 100%; 
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                margin-top: 20px;
            }
            .error {
                background: #ffe6e6;
                color: #d32f2f;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .success {
                background: #e8f5e8;
                color: #2e7d32;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 개선된 Virtual Try-On</h1>
            <p class="subtitle">AI 세그멘테이션 기반 가상 피팅 체험</p>

            <div class="features">
                <h3>✨ 개선된 기능들</h3>
                <div class="features-list">
                    <span class="feature-item">🤖 AI 세그멘테이션</span>
                    <span class="feature-item">🧹 자동 배경 제거</span>
                    <span class="feature-item">🎨 스마트 블렌딩</span>
                    <span class="feature-item">✨ 현실적 효과</span>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-section">
                    <h3>👤 사람 이미지</h3>
                    <p>전신이 나온 정면 사진을 업로드하세요 (JPG, PNG, 최대 10MB)</p>
                    <input type="file" id="personImage" name="person_image" accept=".jpg,.jpeg,.png" required>
                    <small style="color: #888;">권장: 512x768 이상, 단순한 배경, 정면 포즈</small>
                </div>

                <div class="upload-section">
                    <h3>👕 옷 이미지</h3>
                    <p>입혀보고 싶은 옷 이미지를 업로드하세요 (JPG, PNG, 최대 10MB)</p>
                    <input type="file" id="garmentImage" name="garment_image" accept=".jpg,.jpeg,.png" required>
                    <small style="color: #888;">권장: 흰 배경, 펼쳐진 상태, 상의류</small>
                </div>

                <button type="submit" id="submitBtn">🚀 개선된 가상 피팅 시작!</button>
            </form>

            <div id="loading">
                <div class="spinner"></div>
                AI 처리 중입니다... 세그멘테이션과 스마트 블렌딩을 수행하고 있습니다.
            </div>

            <div class="result" id="result"></div>
        </div>

        <script>
            document.getElementById('uploadForm').onsubmit = async function(e) {
                e.preventDefault();

                const formData = new FormData();
                const personImage = document.getElementById('personImage').files[0];
                const garmentImage = document.getElementById('garmentImage').files[0];
                const submitBtn = document.getElementById('submitBtn');

                if (!personImage || !garmentImage) {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">❌ 두 이미지를 모두 선택해주세요!</div>';
                    return;
                }

                // 파일 크기 체크 (10MB)
                if (personImage.size > 10*1024*1024 || garmentImage.size > 10*1024*1024) {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">❌ 파일 크기는 10MB 이하여야 합니다!</div>';
                    return;
                }

                formData.append('person_image', personImage);
                formData.append('garment_image', garmentImage);

                // UI 상태 변경
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').innerHTML = '';
                submitBtn.disabled = true;
                submitBtn.textContent = '🎨 AI 처리 중...';

                try {
                    const response = await fetch('/try-on', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        const imageUrl = URL.createObjectURL(blob);
                        document.getElementById('result').innerHTML = 
                            '<div class="success">✅ 개선된 가상 피팅 완료!</div>' +
                            '<p>AI 세그멘테이션과 스마트 블렌딩이 적용되었습니다.</p>' +
                            '<img src="' + imageUrl + '" alt="Improved Virtual Try-On Result">' +
                            '<br><br><a href="' + imageUrl + '" download="improved_tryon_result.jpg" style="color: #4CAF50; text-decoration: none; font-weight: bold;">📥 결과 이미지 다운로드</a>';
                    } else {
                        const errorText = await response.text();
                        document.getElementById('result').innerHTML = 
                            '<div class="error">❌ 처리 중 오류가 발생했습니다:<br>' + errorText + '</div>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">❌ 네트워크 오류: ' + error.message + '</div>';
                }

                // UI 상태 복원
                document.getElementById('loading').style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 개선된 가상 피팅 시작!';
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/try-on")
async def improved_virtual_try_on(
        person_image: UploadFile = File(..., description="사람 전신 사진"),
        garment_image: UploadFile = File(..., description="옷 이미지")
):
    """개선된 가상피팅 API"""
    if not vton_model:
        raise HTTPException(
            status_code=503,
            detail="개선된 가상피팅 모델이 초기화되지 않았습니다."
        )

    try:
        # 파일 확장자 검증
        allowed_extensions = {".jpg", ".jpeg", ".png"}
        person_ext = os.path.splitext(person_image.filename)[1].lower()
        garment_ext = os.path.splitext(garment_image.filename)[1].lower()

        if person_ext not in allowed_extensions or garment_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="지원되는 파일 형식: JPG, PNG만 가능합니다."
            )

        # 고유 ID 생성
        session_id = uuid.uuid4().hex[:8]
        person_filename = f"person_{session_id}.jpg"
        garment_filename = f"garment_{session_id}.jpg"

        person_path = os.path.join("uploads", person_filename)
        garment_path = os.path.join("uploads", garment_filename)

        print(f"📁 파일 저장 중... (세션 ID: {session_id})")

        # 이미지 저장
        with open(person_path, "wb") as f:
            content = await person_image.read()
            f.write(content)

        with open(garment_path, "wb") as f:
            content = await garment_image.read()
            f.write(content)

        print(f"✅ 파일 저장 완료: {person_filename}, {garment_filename}")

        # 이미지 유효성 검사
        try:
            person_img = Image.open(person_path)
            garment_img = Image.open(garment_path)

            print(f"📏 이미지 크기 - 사람: {person_img.size}, 옷: {garment_img.size}")

        except Exception as img_error:
            raise HTTPException(
                status_code=400,
                detail=f"이미지 파일이 손상되었거나 올바르지 않습니다: {str(img_error)}"
            )

        # 개선된 가상피팅 수행
        print("🎨 개선된 가상피팅 처리 시작...")
        result_image = vton_model.generate_tryon(person_path, garment_path)

        if result_image is None:
            raise HTTPException(
                status_code=500,
                detail="개선된 가상피팅 처리 중 오류가 발생했습니다."
            )

        print("✅ 개선된 가상피팅 처리 완료!")

        # 결과 이미지를 바이트 스트림으로 변환
        img_io = io.BytesIO()
        result_image.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)

        # 임시 파일 정리
        try:
            os.remove(person_path)
            os.remove(garment_path)
            print("🧹 임시 파일 정리 완료")
        except Exception as cleanup_error:
            print(f"⚠️ 임시 파일 정리 실패: {cleanup_error}")

        # 결과 반환
        return StreamingResponse(
            img_io,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename=improved_tryon_{session_id}.jpg",
                "X-Session-ID": session_id,
                "X-Processing-Type": "AI-Segmentation-Enhanced"
            }
        )

    except HTTPException:
        # HTTP 예외는 그대로 전달
        raise
    except Exception as e:
        print(f"❌ 처리 중 예상치 못한 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 개선된 Virtual Try-On 서버 시작...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )