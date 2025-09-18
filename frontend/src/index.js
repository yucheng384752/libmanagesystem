import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));

// 將 App 組件渲染到 HTML 頁面中 id 為 'root' 的元素裡
root.render(
  <React.StrictMode>
    {/* React.StrictMode 是一個工具，用於在開發模式下檢查應用程式中的潛在問題 */}
    <App /> {/* 渲染您的主要應用程式組件 */}
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
