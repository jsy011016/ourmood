# predict.py

import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import requests
from io import BytesIO
import json

# 모델 로드
with open('class_indices.json', 'r') as f:
    class_to_idx = json.load(f)
    idx_to_class = {v: k for k, v in class_to_idx.items()}

model = models.mobilenet_v2()
model.classifier[1] = torch.nn.Linear(1280, 4)
model.load_state_dict(torch.load('best_model.pth', map_location='cpu'))
model.eval()

# 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def predict_from_url(image_url):
    """URL에서 이미지 받아서 코어 예측"""
    try:
        # URL에서 이미지 다운로드
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert('RGB')

        # 전처리
        image_tensor = transform(image).unsqueeze(0)

        # 예측
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            confidence, predicted = torch.max(probabilities, 0)

        predicted_class = idx_to_class[predicted.item()]
        confidence_pct = confidence.item() * 100

        probs_dict = {
            idx_to_class[i]: probabilities[i].item() * 100
            for i in range(len(idx_to_class))
        }

        return predicted_class, confidence_pct, probs_dict

    except Exception as e:
        print(f"❌ 예측 실패: {str(e)}")
        return None, None, None


def predict_from_file(image_path):
    """로컬 파일에서 예측"""
    try:
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            confidence, predicted = torch.max(probabilities, 0)

        predicted_class = idx_to_class[predicted.item()]
        confidence_pct = confidence.item() * 100

        probs_dict = {
            idx_to_class[i]: probabilities[i].item() * 100
            for i in range(len(idx_to_class))
        }

        return predicted_class, confidence_pct, probs_dict

    except Exception as e:
        print(f"❌ 예측 실패: {str(e)}")
        return None, None, None


# 테스트
if __name__ == '__main__':
    # URL 테스트
    test_url = "https://image.msscdn.net/images/goods_img/..."
    predicted, conf, probs = predict_from_url(test_url)

    if predicted:
        print(f"\n예측 결과: {predicted}")
        print(f"신뢰도: {conf:.2f}%")
        print("\n각 클래스 확률:")
        for cls, prob in probs.items():
            print(f"  {cls}: {prob:.2f}%")