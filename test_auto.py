# test_auto.py
response = requests.post(
    "http://localhost:5000/api/single-tryon",
    json={
        "person": person_b64,
        "cloth": cloth_b64,
        "cloth_filename": "jacket.jpg"  # 선택
    }
)

result = response.json()
print("분류:", result['classification']['class'])