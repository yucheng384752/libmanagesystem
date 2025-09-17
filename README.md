# libraryManageSystem

![homepage](https://github.com/user-attachments/assets/17979578-f4db-4e28-9938-f89dd81ca497)

## 安裝方式

### 1. 後端 (Django)

- 進入 `backend` 資料夾
- 安裝 Python 套件 (建議使用 Python 3.12)
```sh
pip install --upgrade pip
pip install -r 
```

- 執行料庫遷移
```
python  migrate
```

- 啟動Django server
```
python  runserver
```

### 2. 前端(React)

- 進入`frontend`資料夾
- 安裝 Node.js 套件(建議 Node.js 22.x)
```
npm install
```
- 開發模式啟動 React 前端
```
npm start
```
- 建置生產環境靜態檔案
```
npm run build
```

### 3. Docker 一鍵佈署

- 需安裝 Docker & docker-compose
- 在專案根目錄執行
```
docker-compose up --build
```

## 版本要求

- Python：3.12
- Django：5.2.3
- Node.js：22.x
- React：19.1.0
- 其他依賴請參考 backend/requirments.txt 與 frontend/package.json

## 操作說明

> 使用者端
1. 註冊新帳號、登入、修改密碼
2. 查詢館藏書籍
3. 借閱與歸還書籍
4. 查看個人借閱紀錄

> 管理者端
1. 新增、編輯、刪除書籍
2. 管理書籍狀態（可借閱、已損壞、維修中、遺失）

> 前端操作
- 進入首頁可選擇登入、查詢書籍、查看借閱紀錄
- 登入後可進行借閱、歸還、個人資料修改等操作
- 管理員登入後可新增/編輯/刪除書籍

> API端點
- `/api/login/`：登入
- `/api/register/`：註冊
- `/api/books/`：查詢書籍列表
- `/api/books/create/`：新增書籍（管理員）
- `/api/books/update/<book_id>/`：編輯書籍（管理員）
- `/api/books/delete/<book_id>/`：刪除書籍（管理員）
- `/api/books/borrow/<book_id>/`：借閱書籍
- `/api/books/return/<record_id>`/：歸還書籍
- `/api/user/update_profile/`：修改密碼

## 其他
- 支援 Docker 部署，靜態檔案由 Nginx 提供
