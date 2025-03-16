FROM python:3.9-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据库目录
RUN mkdir -p instance

# 初始化数据库
RUN python seed_db.py

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "app.py"] 