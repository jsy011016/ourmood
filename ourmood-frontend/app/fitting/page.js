'use client';
import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

function FittingContent() {
  const searchParams = useSearchParams();
  const [userImage, setUserImage] = useState(null);
  const [userImagePreview, setUserImagePreview] = useState(null);
  const [selectedClothes, setSelectedClothes] = useState([]);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  useEffect(() => {
    const clothesParam = searchParams.get('clothes');
    const clothParam = searchParams.get('cloth');
    
    if (clothesParam) {
      const ids = clothesParam.split(',').map(id => parseInt(id));
      fetchClothes(ids);
    } else if (clothParam) {
      fetchClothes([parseInt(clothParam)]);
    }
  }, [searchParams]);

  const fetchClothes = async (ids) => {
    try {
      const response = await fetch('http://localhost:5001/api/products');
      const data = await response.json();
      
      if (data.success) {
        const filtered = data.products.filter(p => ids.includes(p.id));
        setSelectedClothes(filtered);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleUserImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUserImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setUserImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const startFitting = async (cloth) => {
    if (!userImage) {
      alert('사용자 사진을 먼저 업로드해주세요!');
      return;
    }

    setLoading(true);
    setStep(3);

    try {
      const formData = new FormData();
      formData.append('person_image', userImage);
      
      const clothImagePath = cloth.image_url.startsWith('http') 
        ? cloth.image_url 
        : `http://localhost:5001${cloth.image_url}`;
      
      formData.append('cloth_image_path', clothImagePath);
      
      // 상품 타입 매핑
      let clothType = 'upper';
      if (cloth.type === 'bottoms') {
        clothType = 'lower';
      } else if (cloth.type === 'dress') {
        clothType = 'dresses';
      }
      
      formData.append('cloth_type', clothType);

      console.log('📤 요청:', {
        person_image: userImage.name,
        cloth_image_path: clothImagePath,
        cloth_type: clothType,
        cloth_name: cloth.name
      });

      const response = await fetch('http://localhost:5002/virtual-fitting', {
        method: 'POST',
        body: formData
      });

      console.log('📥 응답:', response.status);

      if (response.ok) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        setResultImage(imageUrl);
      } else {
        const errorText = await response.text();
        console.error('❌ 에러:', errorText);
        alert(`가상 피팅 실패!\n${errorText}`);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      alert(`가상 피팅 중 오류: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setUserImage(null);
    setUserImagePreview(null);
    setResultImage(null);
    setStep(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-100 to-blue-100">
      <header className="bg-white/80 backdrop-blur-lg shadow-lg sticky top-0 z-50 border-b border-purple-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-600 hover:text-gray-800 transition-colors">
                <span className="text-2xl">←</span>
              </Link>
              <h1 className="text-2xl md:text-3xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                🎨 AI 가상 피팅
              </h1>
            </div>
            
            <div className="flex items-center gap-3">
              <Link 
                href="/favorites"
                className="bg-white border-2 border-purple-300 text-purple-700 px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:bg-purple-50 transition-all"
              >
                ❤️ 찜 목록
              </Link>
              <Link 
                href="/"
                className="bg-gray-200 text-gray-700 px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:bg-gray-300 transition-all"
              >
                홈으로
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 진행 단계 */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-4">
            <div className={`flex items-center gap-3 px-6 py-3 rounded-full font-bold transition-all ${
              step >= 1 ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' : 'bg-white text-gray-400'
            }`}>
              <span className="text-2xl">📸</span>
              <span>사진 업로드</span>
            </div>
            
            <div className={`w-12 h-1 rounded-full ${step >= 2 ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-gray-300'}`} />
            
            <div className={`flex items-center gap-3 px-6 py-3 rounded-full font-bold transition-all ${
              step >= 2 ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' : 'bg-white text-gray-400'
            }`}>
              <span className="text-2xl">👗</span>
              <span>옷 선택</span>
            </div>
            
            <div className={`w-12 h-1 rounded-full ${step >= 3 ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-gray-300'}`} />
            
            <div className={`flex items-center gap-3 px-6 py-3 rounded-full font-bold transition-all ${
              step >= 3 ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' : 'bg-white text-gray-400'
            }`}>
              <span className="text-2xl">✨</span>
              <span>결과 확인</span>
            </div>
          </div>
        </div>

        {/* Step 1: 사용자 이미지 업로드 */}
        {step === 1 && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-purple-100">
              <h2 className="text-3xl font-black text-center text-gray-800 mb-4">
                📸 사진을 업로드하세요
              </h2>
              <p className="text-center text-gray-600 mb-8 font-medium">
                전신 사진을 업로드하면 더 정확한 가상 피팅이 가능해요
              </p>

              {!userImagePreview ? (
                <label className="block cursor-pointer">
                  <div className="border-4 border-dashed border-purple-300 rounded-3xl p-16 text-center hover:border-purple-500 hover:bg-purple-50 transition-all">
                    <div className="text-8xl mb-4">📷</div>
                    <p className="text-xl font-bold text-gray-700 mb-2">
                      클릭하여 사진 선택
                    </p>
                    <p className="text-gray-500">
                      JPG, PNG 형식 지원
                    </p>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleUserImageUpload}
                    className="hidden"
                  />
                </label>
              ) : (
                <div className="space-y-6">
                  <div className="relative rounded-3xl overflow-hidden shadow-xl">
                    <img
                      src={userImagePreview}
                      alt="User"
                      className="w-full h-96 object-cover"
                    />
                  </div>
                  
                  <div className="flex gap-4">
                    <button
                      onClick={() => {
                        setUserImage(null);
                        setUserImagePreview(null);
                      }}
                      className="flex-1 bg-gray-200 text-gray-700 py-4 rounded-2xl font-bold hover:bg-gray-300 transition-all"
                    >
                      다시 선택
                    </button>
                    <button
                      onClick={() => setStep(2)}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-2xl font-bold hover:shadow-2xl transition-all transform hover:scale-105"
                    >
                      다음 단계 →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: 옷 선택 */}
        {step === 2 && (
          <div>
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-purple-100 mb-8">
              <h2 className="text-3xl font-black text-gray-800 mb-2">
                👗 입어볼 옷을 선택하세요
              </h2>
              <p className="text-gray-600 font-medium">
                {selectedClothes.length}개의 옷이 준비되어 있어요
              </p>
            </div>

            {selectedClothes.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {selectedClothes.map(cloth => (
                  <div
                    key={cloth.id}
                    className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2"
                  >
                    <div className="relative aspect-square overflow-hidden bg-gray-100">
                      <img
                        src={`http://localhost:5001${cloth.image_url}`}
                        alt={cloth.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    
                    <div className="p-5">
                      <h3 className="font-bold text-gray-800 mb-2 truncate">
                        {cloth.name}
                      </h3>
                      <p className="text-lg font-black text-gray-900 mb-3">
                        {cloth.price}
                      </p>
                      <button
                        onClick={() => startFitting(cloth)}
                        className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-xl font-bold hover:shadow-xl transition-all"
                      >
                        이 옷으로 피팅하기
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 bg-white/80 rounded-2xl">
                <p className="text-8xl mb-6">👗</p>
                <p className="text-2xl font-bold text-gray-800 mb-3">선택된 옷이 없습니다</p>
                <p className="text-gray-500 mb-6">찜 목록에서 옷을 선택해주세요</p>
                <Link
                  href="/favorites"
                  className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full font-bold hover:shadow-2xl transition-all transform hover:scale-105"
                >
                  찜 목록으로 가기
                </Link>
              </div>
            )}

            <div className="mt-8 text-center">
              <button
                onClick={() => setStep(1)}
                className="bg-gray-200 text-gray-700 px-8 py-4 rounded-full font-bold hover:bg-gray-300 transition-all"
              >
                ← 이전 단계
              </button>
            </div>
          </div>
        )}

        {/* Step 3: 결과 */}
        {step === 3 && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-purple-100">
              <h2 className="text-3xl font-black text-center text-gray-800 mb-8">
                ✨ 가상 피팅 결과
              </h2>

              {loading ? (
                <div className="text-center py-20">
                  <div className="inline-block animate-spin rounded-full h-20 w-20 border-4 border-purple-500 border-t-transparent mb-4"></div>
                  <p className="text-xl font-bold text-gray-700">AI가 옷을 입혀주는 중...</p>
                  <p className="text-gray-500 mt-2">잠시만 기다려주세요</p>
                </div>
              ) : resultImage ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-center font-bold text-gray-700 mb-3">원본</p>
                      <img
                        src={userImagePreview}
                        alt="Original"
                        className="w-full rounded-2xl shadow-xl"
                      />
                    </div>
                    <div>
                      <p className="text-center font-bold text-gray-700 mb-3">피팅 결과</p>
                      <img
                        src={resultImage}
                        alt="Result"
                        className="w-full rounded-2xl shadow-xl"
                      />
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <button
                      onClick={reset}
                      className="flex-1 bg-gray-200 text-gray-700 py-4 rounded-2xl font-bold hover:bg-gray-300 transition-all"
                    >
                      다시 시작
                    </button>
                    <a
                      href={resultImage}
                      download="fitting-result.png"
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-2xl font-bold hover:shadow-2xl transition-all text-center"
                    >
                      💾 결과 저장하기
                    </a>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ⭐ 중요: default export!
export default function FittingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
      </div>
    }>
      <FittingContent />
    </Suspense>
  );
}