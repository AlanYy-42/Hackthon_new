# 1️⃣ 使用 Python 3.10-slim 作为基础镜像
FROM python:3.10-slim

# 2️⃣ 设置工作目录
WORKDIR /app

# 3️⃣ 复制整个项目
COPY . .

# 4️⃣ 更新 pip 并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5️⃣ 打印已安装的关键依赖（避免 grep 失败）
RUN python -c "import flask, numpy, pandas, sklearn, sqlalchemy, flask_sqlalchemy, flask_cors, requests, bs4, matplotlib; print('✅ All required packages installed successfully')"

# 6️⃣ 创建数据库目录
RUN mkdir -p instance

# 7️⃣ 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
# API密钥将从 Hugging Face Spaces 的 Secret 中自动获取

# 8️⃣ 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "API exists: ${API:+true}"

# 9️⃣ 暴露端口
EXPOSE 7860

# 🔟 启动应用（先初始化数据库，再启动 Flask）
CMD ["sh", "-c", "python seed_db.py && exec python app.py"]
