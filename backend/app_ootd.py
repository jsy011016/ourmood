# backend/app_ootd.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from ootd_wrapper import get_ootd_model
import os
import io
import uuid
from PIL import Image

app = FastAPI(title="OOTDiffusion Virtual Try-On API")

ootd_model = None


@app.on_event("startup")
async def startup_event():
    global ootd_model
    print("🚀 OOTDiffusion 서버 시작...")
    ootd_model = get_ootd_model()


@app.get("/upload-form")
async def upload_form():
    # 같은 HTML 폼 (이전과 동일)
    pass


@app.post("/try-on")
async def real_virtual_try_on(
        person_image: UploadFile = File(...),
        garment_image: UploadFile = File(...)
):
    """실제 OOTDiffusion 가상피팅"""
    if not ootd_model or not ootd_model.model_loaded:
        raise HTTPException(status_code=503, detail="OOTDiffusion 모델이 로드되지 않았습니다.")

    try:
        # 파일 저장
        session_id = uuid.uuid4().hex[:8]
        person_path = f"uploads/person_{session_id}.jpg"
        garment_path = f"uploads/garment_{session_id}.jpg"

        with open(person_path, "wb") as f:
            f.write(await person_image.read())
        with open(garment_path, "wb") as f:
            f.write(await garment_image.read())

        # 실제 OOTDiffusion 가상피팅
        result_image = ootd_model.generate_tryon(person_path, garment_path)

        if result_image is None:
            raise HTTPException(status_code=500, detail="가상피팅 처리 실패")

        # 결과 반환
        img_io = io.BytesIO()
        result_image.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)

        os.remove(person_path)
        os.remove(garment_path)

        return StreamingResponse(img_io, media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)  # 포트 8001 사용