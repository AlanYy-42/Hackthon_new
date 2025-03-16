FROM python:3.9-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 更新pip并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip list | grep google-generativeai

# 创建数据库目录
RUN mkdir -p instance

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

# 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "GOOGLE_API_KEY exists: ${GOOGLE_API_KEY:+true}"

# 验证Python包安装
RUN python -c "import google.generativeai; print('Google AI package version:', google.generativeai.__version__)"

# 初始化数据库
RUN python seed_db.py

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "app.py"] 