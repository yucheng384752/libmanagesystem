import React, { useState, useContext } from 'react';
// 假設有一個 AuthContext 來管理用戶登入狀態
import { AuthContext } from '../App';

const Login = ({ setCurrentPage }) => {
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const { loginUser } = useContext(AuthContext); // 從 context 獲取登入函數

  const handleSubmit = async (action) => {
    if (!account || !password) {
      setMessage('請輸入帳號與密碼');
      setMessageType('error');
      return;
    }

    try {
      const response = await fetch('/api/login/', { // 調用後端API
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: account, password: password, action: action }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setMessageType('success');
        loginUser(data.user_id, data.username); // 更新全局用戶狀態
        setCurrentPage('user_home'); // 導航到用戶主頁
      } else {
        setMessage(data.message || '登入失敗');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('網路錯誤，請稍後再試。');
      setMessageType('error');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">登入</h1>
      {message && <div className={`p-2 mb-4 ${messageType === 'error' ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>{message}</div>}
      <form className="bg-white p-6 rounded shadow-md w-80" onSubmit={(e) => e.preventDefault()}>
        <label className="block text-gray-700 text-sm font-bold mb-2">帳號</label>
        <input
          type="text"
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mb-4"
          value={account}
          onChange={(e) => setAccount(e.target.value)}
          required
        />
        <label className="block text-gray-700 text-sm font-bold mb-2">密碼</label>
        <input
          type="password"
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mb-6"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button
          type="button"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full mb-3"
          onClick={() => handleSubmit('login')}
        >
          登入
        </button>
        <button
          type="button"
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
          onClick={() => handleSubmit('register')}
        >
          註冊
        </button>
      </form>
      <p className="mt-4">還沒有帳號嗎？<button onClick={() => setCurrentPage('register')} className="text-blue-500 hover:underline">註冊新帳號</button></p>
    </div>
  );
};

export default Login;