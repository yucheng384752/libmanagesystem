# 第一階段：建構 React 應用
FROM node:22-alpine AS build

WORKDIR /app

# 複製 package.json 和 package-lock.json（如果有）
COPY package.json ./
COPY package-lock.json ./

RUN npm install

# 複製所有原始碼
COPY . .

# 建立靜態檔案
RUN npm run build

# 第二階段：用 Nginx 服務靜態檔案
FROM nginx:alpine

# 複製 build 出來的檔案到 Nginx 預設目錄
COPY --from=build /app/build /usr/share/nginx/html

# 如有自訂 nginx.conf 可取消註解並調整路徑
# COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]