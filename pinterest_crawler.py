# pinterest_crawler.py

from pinterest_downloader import pinterest
import os

BOARDS = {
    'balletcore': [
        'balletcore aesthetic',
        'ballet fashion',
        'pink tutu outfit'
    ],
    'angelcore': [
        'angelcore aesthetic',
        'white angel dress',
        'ethereal fashion'
    ],
    'y2k': [
        'y2k aesthetic',
        'y2k fashion 2000s',
        'neon y2k'
    ],
    'darkacademia': [
        'dark academia aesthetic',
        'dark academia fashion',
        'vintage academic'
    ]
}

for core, searches in BOARDS.items():
    save_dir = f'dataset/raw/{core}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"\n📸 {core.upper()} 수집...")

    for search in searches:
        print(f"  🔍 '{search}'...")

        try:
            pinterest.download(
                search=search,
                output_dir=save_dir,
                limit=50
            )
            print(f"    ✅ 완료!")
        except Exception as e:
            print(f"    ❌ 실패: {str(e)}")

print("\n🎉 전체 완료!")