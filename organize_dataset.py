import os
import shutil
from sklearn.model_selection import train_test_split
from PIL import Image

cores = ['balletcore', 'angelcore', 'y2k', 'darkacademia']

# 🔹 raw / train / val 기본 경로를 네 폴더 구조에 맞게 정의
BASE_DIR = r'D:\virtual-fitting-new\CatVTON\fashion_dataset_core'
RAW_BASE = os.path.join(BASE_DIR, 'raw')
TRAIN_BASE = os.path.join(BASE_DIR, 'train')
VAL_BASE = os.path.join(BASE_DIR, 'val')


def clean_and_split():
    """이미지 정리 & Train/Val 분할"""

    print("\n" + "=" * 60)
    print("🔧 데이터 정리 시작")
    print("=" * 60 + "\n")

    for core in cores:
        raw_dir = os.path.join(RAW_BASE, core)

        if not os.path.exists(raw_dir):
            print(f"❌ {core} 폴더 없음! ({raw_dir})")
            continue

        # 이미지 파일 필터링
        images = []
        removed = 0

        for f in os.listdir(raw_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                filepath = os.path.join(raw_dir, f)

                try:
                    img = Image.open(filepath)
                    img.verify()
                    img = Image.open(filepath)

                    # 최소 크기 체크
                    if img.size[0] >= 200 and img.size[1] >= 200:
                        images.append(f)
                    else:
                        os.remove(filepath)
                        removed += 1

                except Exception:
                    print(f"  ❌ 손상된 파일 제거: {f}")
                    os.remove(filepath)
                    removed += 1

        print(f"📁 {core}:")
        print(f"  유효 이미지: {len(images)}개")
        print(f"  제거된 파일: {removed}개")

        if len(images) == 0:
            print(f"  ⚠️  이미지가 없습니다!\n")
            continue

        # Train/Val split (80:20)
        train_imgs, val_imgs = train_test_split(
            images, test_size=0.2, random_state=42
        )

        # 🔹 Train / Val 경로도 BASE 기준으로
        train_dir = os.path.join(TRAIN_BASE, core)
        os.makedirs(train_dir, exist_ok=True)
        for img in train_imgs:
            shutil.copy(
                os.path.join(raw_dir, img),
                os.path.join(train_dir, img)
            )

        val_dir = os.path.join(VAL_BASE, core)
        os.makedirs(val_dir, exist_ok=True)
        for img in val_imgs:
            shutil.copy(
                os.path.join(raw_dir, img),
                os.path.join(val_dir, img)
            )

        print(f"  ✅ Train: {len(train_imgs)}개")
        print(f"  ✅ Val: {len(val_imgs)}개\n")

    print("=" * 60)
    print("✅ 데이터 정리 완료!")
    print("\n📊 최종 데이터셋:")
    print(f"  📁 {TRAIN_BASE}  (학습용)")
    print(f"  📁 {VAL_BASE}    (검증용)")

    # 통계
    total_train = 0
    total_val = 0
    for core in cores:
        train_dir = os.path.join(TRAIN_BASE, core)
        val_dir = os.path.join(VAL_BASE, core)

        train_count = len(os.listdir(train_dir)) if os.path.exists(train_dir) else 0
        val_count = len(os.listdir(val_dir)) if os.path.exists(val_dir) else 0

        total_train += train_count
        total_val += val_count

        print(f"\n  {core}:")
        print(f"    Train: {train_count}개")
        print(f"    Val: {val_count}개")

    print(f"\n  전체:")
    print(f"    Train: {total_train}개")
    print(f"    Val: {total_val}개")
    print("=" * 60)


if __name__ == '__main__':
    clean_and_split()
