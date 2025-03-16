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
RUN mkdir -p /app/models /app/instance /tmp/mpl_config /app/visualizations && \
    chmod -R 755 /app/models /app/instance /tmp/mpl_config /app/visualizations && \
    touch /app/instance/studypath.db && chmod 666 /app/instance/studypath.db

# 6️⃣ 设置 Matplotlib 缓存路径，避免权限问题
ENV MPLCONFIGDIR=/tmp/mpl_config

# 7️⃣ 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV SQLALCHEMY_DATABASE_URI=sqlite:////app/instance/studypath.db

# 8️⃣ 打印环境变量状态（不显示值）
RUN echo "Checking environment variables:" && \
    echo "API exists: ${API:+true}"

# 9️⃣ 暴露端口
EXPOSE 7860

# 🔟 创建一个启动脚本
RUN echo '#!/bin/bash\n\
# 确保数据库目录存在并有正确权限\n\
mkdir -p /app/instance\n\
chmod -R 777 /app/instance\n\
touch /app/instance/studypath.db\n\
chmod 666 /app/instance/studypath.db\n\
\n\
# 初始化数据库\n\
python seed_db.py\n\
\n\
# 启动应用\n\
exec python app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 🔟🔟 启动命令
CMD ["/app/start.sh"]
