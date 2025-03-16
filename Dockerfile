# 1️⃣ 使用 Python 3.10-slim 作为基础镜像
FROM python:3.10-slim

# 2️⃣ 设置工作目录
WORKDIR /app

# 3️⃣ 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    lsb-release \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ 安装 Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ 复制整个项目
COPY . .

# 6️⃣ 更新 pip 并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7️⃣ 设置 Matplotlib 配置目录为 /tmp
ENV MPLCONFIGDIR=/tmp

# 8️⃣ 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV SQLALCHEMY_DATABASE_URI=sqlite:///:memory:

# 9️⃣ 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "API exists: ${API:+true}"

# 🔟 暴露端口
EXPOSE 7860

# 1️⃣1️⃣ 直接启动应用，不再使用 start.sh
CMD ["python", "app.py"]
