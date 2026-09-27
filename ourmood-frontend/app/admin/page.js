'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

const CATEGORIES = {
  balletcore: { name: '발레코어', emoji: '🩰', color: 'from-pink-300 to-purple-200' },
  angelcore: { name: '엔젤코어', emoji: '👼', color: 'from-white to-blue-100' },
  y2k: { name: 'Y2K', emoji: '🌈', color: 'from-pink-500 to-purple-500' },
  darkacademia: { name: '다크 아카데미아', emoji: '📚', color: 'from-amber-800 to-stone-700' }
};

export default function AdminPage() {
  const [formData, setFormData] = useState({
    name: '',
    type: 'tops',
    price: '',
    description: '',
    purchase_url: '',
    image: null
  });
  
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [products, setProducts] = useState([]);

  // 상품 목록 불러오기
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/admin/products');
      const data = await response.json();
      if (data.success) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // 이미지 선택
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, image: file });
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // 폼 제출
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAiResult(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('image', formData.image);
      formDataToSend.append('name', formData.name);
      formDataToSend.append('type', formData.type);
      formDataToSend.append('price', formData.price);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('purchase_url', formData.purchase_url);

      const response = await fetch('http://localhost:5001/api/admin/upload-product', {
        method: 'POST',
        body: formDataToSend
      });

      const data = await response.json();

      if (data.success) {
        setAiResult(data.ai_classification);
        alert(`✅ 상품 등록 완료!\n🤖 AI 분류: ${data.ai_classification.predicted_class} (${data.ai_classification.confidence.toFixed(1)}%)`);
        
        // 폼 초기화
        setFormData({
          name: '',
          type: 'tops',
          price: '',
          description: '',
          purchase_url: '',
          image: null
        });
        setPreview(null);
        
        // 상품 목록 새로고침
        fetchProducts();
      } else {
        alert('❌ 등록 실패: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('❌ 업로드 중 오류 발생: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 상품 삭제
  const handleDelete = async (productId) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`http://localhost:5001/api/admin/products/${productId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      if (data.success) {
        alert('삭제되었습니다');
        fetchProducts();
      }
    } catch (error) {
      console.error('Error:', error);
      alert('삭제 실패');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* 헤더 */}
        <div className="bg-white rounded-xl p-8 shadow-md mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                🔐 관리자 페이지
              </h1>
              <p className="text-gray-600">
                🤖 AI가 자동으로 코어를 분류합니다
              </p>
            </div>
            <Link
              href="/"
              className="bg-gray-200 text-gray-700 px-6 py-3 rounded-full font-semibold hover:bg-gray-300 transition-all"
            >
              홈으로 돌아가기
            </Link>
          </div>

          {/* 통계 */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            {Object.entries(CATEGORIES).map(([key, cat]) => {
              const count = products.filter(p => p.category === key).length;
              return (
                <div key={key} className={`bg-gradient-to-r ${cat.color} p-4 rounded-lg text-white`}>
                  <p className="text-sm opacity-90">{cat.emoji} {cat.name}</p>
                  <p className="text-3xl font-bold mt-1">{count}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 왼쪽: 상품 등록 폼 */}
          <div className="bg-white rounded-xl p-8 shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">✨ 새 상품 등록</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* 이미지 업로드 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  상품 이미지 * (AI가 자동 분류)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-purple-500 transition-colors">
                  {preview ? (
                    <div className="relative">
                      <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-lg" />
                      <button
                        type="button"
                        onClick={() => {
                          setPreview(null);
                          setFormData({ ...formData, image: null });
                          setAiResult(null);
                        }}
                        className="mt-3 text-red-600 hover:text-red-700 font-semibold text-sm"
                      >
                        이미지 제거
                      </button>
                    </div>
                  ) : (
                    <div>
                      <p className="text-gray-500 mb-3">클릭하여 이미지 선택</p>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                        id="image-upload"
                        required
                      />
                      <label
                        htmlFor="image-upload"
                        className="bg-purple-600 text-white px-6 py-2 rounded-full font-semibold cursor-pointer hover:bg-purple-700 transition-colors inline-block"
                      >
                        이미지 선택
                      </label>
                    </div>
                  )}
                </div>
              </div>

              {/* 상품명 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  상품명 *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="예: 핑크 튜튜 스커트"
                  required
                />
              </div>

              {/* 타입 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  타입 *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="tops">상의</option>
                  <option value="bottoms">하의</option>
                  <option value="dress">원피스</option>
                </select>
              </div>

              {/* 가격 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  가격 *
                </label>
                <input
                  type="text"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="예: 45,000원"
                  required
                />
              </div>

              {/* 설명 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  상품 설명 (선택)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows="3"
                  placeholder="상품에 대한 간단한 설명"
                />
              </div>

              {/* 구매 링크 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  구매 링크 (선택)
                </label>
                <input
                  type="url"
                  value={formData.purchase_url}
                  onChange={(e) => setFormData({ ...formData, purchase_url: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="https://example.com/product/123"
                />
              </div>

              {/* 제출 버튼 */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-lg font-bold text-lg hover:shadow-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '🤖 AI 분류 중...' : '✨ 상품 등록 (AI 자동 분류)'}
              </button>
            </form>

            {/* AI 분류 결과 */}
            {aiResult && (
              <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  🤖 AI 자동 분류 결과
                </h3>
                
                <div className="bg-white p-4 rounded-lg mb-4">
                  <p className="text-gray-600 text-sm mb-2">분류 결과</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {CATEGORIES[aiResult.predicted_class]?.emoji} {CATEGORIES[aiResult.predicted_class]?.name}
                  </p>
                  <p className="text-gray-500 text-sm mt-1">
                    신뢰도: {aiResult.confidence.toFixed(1)}%
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold text-gray-700">각 코어별 확률:</p>
                  {Object.entries(aiResult.probabilities).map(([core, prob]) => (
                    <div key={core} className="flex items-center gap-3">
                      <div className="w-32 text-sm text-gray-600">
                        {CATEGORIES[core]?.emoji} {CATEGORIES[core]?.name}
                      </div>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-purple-600 h-2 rounded-full transition-all"
                          style={{ width: `${prob}%` }}
                        />
                      </div>
                      <div className="w-16 text-right text-sm font-semibold text-gray-700">
                        {prob.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 오른쪽: 상품 목록 */}
          <div className="bg-white rounded-xl p-8 shadow-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">📦 등록된 상품</h2>
              <p className="text-gray-500">{products.length}개</p>
            </div>

            <div className="space-y-4 max-h-[800px] overflow-y-auto">
              {products.map(product => (
                <div key={product.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex gap-4">
                    <img
                      src={`http://localhost:5001${product.image_url}`}
                      alt={product.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800">{product.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {CATEGORIES[product.category]?.emoji} {CATEGORIES[product.category]?.name} · {product.price}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        AI 신뢰도: {product.confidence?.toFixed(1)}%
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {product.type === 'tops' ? '상의' : product.type === 'bottoms' ? '하의' : '원피스'}
                        </span>
                        <span className="text-xs text-gray-500">
                          ❤️ {product.likes}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(product.id)}
                      className="text-red-600 hover:text-red-700 font-semibold text-sm h-fit"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              ))}

              {products.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <p className="text-4xl mb-2">📦</p>
                  <p>등록된 상품이 없습니다</p>
                  <p className="text-sm mt-2">왼쪽에서 첫 상품을 등록해보세요!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}