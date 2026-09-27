# test_layering.py
response = requests.post(
    "http://localhost:5000/api/layering-tryon",
    json={
        "person": person_b64,
        "garments": [
            {"image": tshirt_b64, "filename": "tshirt.jpg"},
            {"image": jacket_b64, "filename": "jacket.jpg"},
            {"image": pants_b64, "filename": "pants.jpg"}
        ]
    }
)

result = response.json()
print("레이어 순서:", [l['class'] for l in result['layers']])