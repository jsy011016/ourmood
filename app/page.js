import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="text-center text-white">
        <h1 className="text-6xl font-bold mb-4">👔 가상 피팅 시스템</h1>
        <p className="text-xl mb-8">AI 기반 의상 착용 시뮬레이션</p>
        <Link href="/fitting" className="bg-white text-blue-600 px-8 py-4 rounded-lg text-xl font-semibold hover:bg-gray-100">
          시작하기 →
        </Link>
      </div>
    </div>
  );
}