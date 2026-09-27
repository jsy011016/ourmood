# garment_classifier_cnn.py

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image


class GarmentCNN:
    def __init__(self, model_path='garment_cnn.pth'):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 5개 클래스 분류
        self.model = models.efficientnet_b0(pretrained=True)
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.model.classifier[1].in_features, 5)
        )

        # 학습된 모델 로드
        if torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path))
        else:
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))

        self.model = self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        # 클래스 정의
        self.classes = {
            0: 'top',  # 상의 (티셔츠, 셔츠)
            1: 'outer',  # 아우터 (재킷, 코트)
            2: 'bottom',  # 하의 (바지, 치마)
            3: 'dress',  # 원피스
            4: 'accessory'  # 악세서리 (나중에)
        }

        # CatVTON 타입 매핑
        self.catvton_mapping = {
            'top': 'upper',
            'outer': 'upper',
            'bottom': 'lower',
            'dress': 'overall',
            'accessory': 'upper'
        }

        # 레이어 순서 (낮을수록 먼저)
        self.layer_order = {
            'bottom': 1,  # 하의 먼저
            'dress': 1,  # 원피스도 먼저
            'top': 2,  # 상의
            'outer': 3,  # 아우터 마지막
            'accessory': 4  # 악세서리 맨 마지막
        }

    def classify(self, cloth_img):
        """의상 타입 분류"""
        img_tensor = self.transform(cloth_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(img_tensor)
            probs = torch.softmax(output, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred].item()

        garment_class = self.classes[pred]
        catvton_type = self.catvton_mapping[garment_class]
        layer = self.layer_order[garment_class]

        return {
            'class': garment_class,  # top, outer, bottom, dress
            'catvton_type': catvton_type,  # upper, lower, overall
            'layer': layer,  # 1, 2, 3
            'confidence': confidence
        }