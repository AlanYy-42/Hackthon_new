FROM python:3.10-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 更新pip并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # 验证关键依赖是否安装成功
    pip list | grep flask && \
    pip list | grep python-dotenv && \
    pip list | grep numpy && \
    pip list | grep pandas && \
    pip list | grep scikit-learn && \
    pip list | grep sqlalchemy && \
    pip list | grep flask-sqlalchemy && \
    pip list | grep flask-cors && \
    pip list | grep requests && \
    pip list | grep beautifulsoup4 && \
    pip list | grep matplotlib && \
    pip list | grep google-generativeai

# 创建数据库目录
RUN mkdir -p instance

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
# API密钥将从Hugging Face Spaces的Secret中自动获取

# 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "API exists: ${API:+true}"

# 验证Python包安装
RUN python -c "import flask, numpy, pandas, sklearn, sqlalchemy, flask_sqlalchemy, flask_cors, requests, bs4, matplotlib; print('All required packages imported successfully')"

# 暴露端口
EXPOSE 7860

# 启动应用（先初始化数据库，然后启动应用）
CMD ["sh", "-c", "python seed_db.py && python app.py"] 