FROM python:3.9-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据库目录
RUN mkdir -p instance

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HF_DEEPSEEK_API_KEY=${HF_DEEPSEEK_API_KEY}

# 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "HF_DEEPSEEK_API_KEY exists: ${HF_DEEPSEEK_API_KEY:+true}"

# 初始化数据库
RUN python seed_db.py

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "app.py"] 