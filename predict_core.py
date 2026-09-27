# predict_core.py

import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import json
import io

# 전역 변수
fashion_model = None
idx_to_class = None
transform = None


def load_model():
    """모델 로드 (서버 시작 시 1번만 실행)"""
    global fashion_model, idx_to_class, transform

    print("🤖 CNN 모델 로딩 중...")

    # 클래스 인덱스 로드
    with open('class_indices.json', 'r') as f:
        class_to_idx = json.load(f)
        idx_to_class = {v: k for k, v in class_to_idx.items()}

    # 모델 로드
    fashion_model = models.mobilenet_v2()
    fashion_model.classifier[1] = torch.nn.Linear(1280, 4)
    fashion_model.load_state_dict(torch.load('best_model.pth', map_location='cpu'))
    fashion_model.eval()

    # 전처리
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print("✅ CNN 모델 로드 완료!")
    print(f"📂 Classes: {list(idx_to_class.values())}\n")


def predict_from_pil(image):
    """PIL Image로부터 코어 예측"""
    if fashion_model is None:
        raise Exception("Model not loaded! Call load_model() first.")

    # RGB 변환
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # 전처리
    image_tensor = transform(image).unsqueeze(0)

    # 예측
    with torch.no_grad():
        outputs = fashion_model(image_tensor)
        probabilities = F.softmax(outputs, dim=1)[0]
        confidence, predicted = torch.max(probabilities, 0)

    predicted_class = idx_to_class[predicted.item()]
    confidence_pct = confidence.item() * 100

    # 각 클래스별 확률
    probs_dict = {
        idx_to_class[i]: probabilities[i].item() * 100
        for i in range(len(idx_to_class))
    }

    return predicted_class, confidence_pct, probs_dict


def predict_from_bytes(image_bytes):
    """이미지 바이트로부터 예측"""
    image = Image.open(io.BytesIO(image_bytes))
    return predict_from_pil(image)


def predict_from_file(image_path):
    """파일 경로로부터 예측"""
    image = Image.open(image_path)
    return predict_from_pil(image)


# 테스트
if __name__ == '__main__':
    load_model()

    # 테스트 이미지로 예측
    test_image = 'test.jpg'  # 테스트 이미지 경로

    if os.path.exists(test_image):
        predicted, conf, probs = predict_from_file(test_image)

        print(f"예측 결과: {predicted}")
        print(f"신뢰도: {conf:.2f}%")
        print("\n각 클래스별 확률:")
        for cls, prob in probs.items():
            print(f"  {cls}: {prob:.2f}%")