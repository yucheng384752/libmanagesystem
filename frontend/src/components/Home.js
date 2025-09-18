import React from 'react';

const Home = ({ setCurrentPage }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-8">圖書館首頁</h1>
      <div className="space-y-4">
        <button
          onClick={() => setCurrentPage('login')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          登入
        </button>
        <button
          onClick={() => setCurrentPage('user_home')}
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          借還書紀錄
        </button>
        <button
          onClick={() => setCurrentPage('book_list')}
          className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
        >
          館藏查詢
        </button>
      </div>
      <footer className="mt-12 text-center text-gray-600">
        <p>建工圖書館：807618高雄市三民區建工路415號 電話:07-3814526 分機:13101</p>
        <p>第一圖書館：824005高雄市燕巢區大學路1號 電話:07-6011000 分機:31591、31599</p>
      </footer>
    </div>
  );
};

export default Home;