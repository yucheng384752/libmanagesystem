# 使用 Python 3.12 的 Alpine Linux 基礎映像
FROM python:3.12-slim

# 設定容器內的工作目錄
WORKDIR /app

# 複製 requirment.txt 到工作目錄
# 注意：這裡修正了檔名拼寫錯誤
COPY requirments.txt .

# 升級 pip
RUN pip install --upgrade pip


# 安裝 opencv-python 依賴
RUN apt-get update && \
    apt-get install -y gcc g++ libgl1 libglib2.0-0 libzbar0 libzbar-dev && \
    rm -rf /var/lib/apt/lists/*


# 安裝 requirment.txt 中列出的 Python 函式庫
# --no-cache-dir 減少映像檔大小
RUN pip install --no-cache-dir -r requirments.txt

# 複製所有專案程式碼到容器內的工作目錄
COPY . .

# 執行 Django 資料庫遷移
# 注意：這裡修正了 'py' 為 'python'
RUN python manage.py migrate

# 收集靜態檔案
RUN python manage.py collectstatic --noinput

# 暴露應用程式監聽的端口
EXPOSE 8000

# 容器啟動時執行的命令，使用 Gunicorn 運行 Django 應用
# 'libmanagesystem.wsgi:application' 應該是你的 Django 專案名和 WSGI 應用程式的路徑
CMD ["gunicorn", "libmanagesystem.wsgi:application", "--bind", "0.0.0.0:8000"]
