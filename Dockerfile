# 1️⃣ 使用 Python 3.10-slim 作为基础镜像
FROM python:3.10-slim

# 2️⃣ 设置工作目录
WORKDIR /app

# 3️⃣ 复制整个项目
COPY . .

# 4️⃣ 更新 pip 并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5️⃣ 创建必要目录并赋予权限
RUN mkdir -p /app/models && chmod -R 777 /app/models && \
    mkdir -p /app/instance && chmod -R 777 /app/instance && \
    mkdir -p /tmp/mpl_config && chmod -R 777 /tmp/mpl_config

# 6️⃣ 设置 Matplotlib 缓存路径，避免权限问题
ENV MPLCONFIGDIR=/tmp/mpl_config

# 7️⃣ 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 8️⃣ 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "API exists: ${API:+true}"

# 9️⃣ 暴露端口
EXPOSE 7860

# 🔟 启动应用（先初始化数据库，再启动 Flask）
CMD ["sh", "-c", "python seed_db.py && exec python app.py"]
