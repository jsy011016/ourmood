# train_cnn.py

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import json
import time

# 🔹 추가: 깨진 이미지도 강제로 로드하도록 설정
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# 🔥 데이터 경로
DATA_DIR = r"D:\virtual-fitting-new\CatVTON\fashion_dataset_core"
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "val")

# 설정
BATCH_SIZE = 32
LEARNING_RATE = 0.001
NUM_EPOCHS = 30
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"🖥️  Device: {DEVICE}")
print(f"📂 Train dir: {TRAIN_DIR}")
print(f"📂 Val dir  : {VAL_DIR}")

# 데이터 전처리
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# 데이터 로딩
train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transform)
val_dataset = datasets.ImageFolder(VAL_DIR, transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

print(f"📊 Train: {len(train_dataset)}, Val: {len(val_dataset)}")
print(f"📂 Classes: {train_dataset.classes}")

# 모델 (MobileNetV2)
model = models.mobilenet_v2(weights="IMAGENET1K_V1")
model.classifier[1] = nn.Linear(1280, 4)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)


def train_epoch(model, loader):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return running_loss / len(loader), 100. * correct / total


def validate(model, loader):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    return running_loss / len(loader), 100. * correct / total


print("\n" + "=" * 60)
print("🚀 학습 시작!")
print("=" * 60 + "\n")

best_acc = 0

for epoch in range(NUM_EPOCHS):
    start = time.time()

    train_loss, train_acc = train_epoch(model, train_loader)
    val_loss, val_acc = validate(model, val_loader)

    elapsed = time.time() - start

    print(f'Epoch {epoch + 1}/{NUM_EPOCHS} ({elapsed:.1f}s)')
    print(f'  Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%')
    print(f'  Val  Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%')

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), 'best_model.pth')
        print(f'  ✅ Best model saved! ({val_acc:.2f}%)\n')

print(f'\n🎉 학습 완료! Best Val Acc: {best_acc:.2f}%')

with open('class_indices.json', 'w') as f:
    json.dump(train_dataset.class_to_idx, f)

print("✅ class_indices.json 저장 완료!")
