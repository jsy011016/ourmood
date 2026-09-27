// app/layering/page.js
'use client';
import { useState } from 'react';

export default function LayeringPage() {
  const [personImg, setPersonImg] = useState(null);
  const [garments, setGarments] = useState([]);  // 여러 의상
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      if (type === 'person') {
        setPersonImg(reader.result);
      } else {
        // 의상 추가
        setGarments([...garments, reader.result]);
      }
    };
    reader.readAsDataURL(file);
  };

  const removeGarment = (index) => {
    setGarments(garments.filter((_, i) => i !== index));
  };

  const handleLayering = async () => {
    if (!personImg || garments.length === 0) {
      alert('사람 이미지와 최소 1개 의상을 선택해주세요!');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/tryon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'layering',
          person: personImg,
          garments: garments
        })
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.result);
        console.log('레이어 정보:', data.layers);
      } else {
        alert('에러: ' + data.error);
      }
    } catch (error) {
      alert('에러 발생: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">
          🎨 레이어링 가상 피팅
        </h1>

        {/* 사람 이미지 */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">1. 사람 이미지</h2>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'person')}
            className="mb-4"
          />
          {personImg && (
            <img src={personImg} alt="Person" className="w-64 rounded" />
          )}
        </div>

        {/* 의상 추가 */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">
            2. 의상 추가 ({garments.length}개)
          </h2>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'garment')}
            className="mb-4"
          />

          <div className="grid grid-cols-4 gap-4">
            {garments.map((garment, idx) => (
              <div key={idx} className="relative">
                <img src={garment} alt={`Garment ${idx+1}`} className="w-full rounded" />
                <button
                  onClick={() => removeGarment(idx)}
                  className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded"
                >
                  ✕
                </button>
                <div className="text-center mt-2">의상 {idx+1}</div>
              </div>
            ))}
          </div>

          <p className="text-sm text-gray-500 mt-4">
            💡 AI가 자동으로 순서를 정합니다 (하의 → 상의 → 아우터)
          </p>
        </div>

        {/* 실행 버튼 */}
        <div className="text-center mb-8">
          <button
            onClick={handleLayering}
            disabled={loading}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? `처리 중... (${garments.length}개 레이어)` : '레이어링 착용 실행!'}
          </button>
        </div>

        {/* 결과 */}
        {result && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-semibold mb-4 text-center">✅ 결과</h2>
            <img src={result} alt="Result" className="w-full max-w-2xl mx-auto rounded" />
          </div>
        )}
      </div>
    </div>
  );
}