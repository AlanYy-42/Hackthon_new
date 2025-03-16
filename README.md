---
title: StudyPath AI
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.9"
app_file: app.py
pinned: false
---

# StudyPath AI

An intelligent academic planning assistant powered by Edge AI technology, providing personalized learning planning services for university students and hackathon organizers.

## Features

- Smart Course Planning
  - AI-powered personalized course recommendations
  - Automatic course load balancing
  - Prerequisites analysis

- Career Goal Integration
  - Learning path visualization
  - Career development planning
  - Resource recommendations

- Data Visualization
  - Learning progress tracking
  - Course distribution analysis
  - Grade prediction

## Tech Stack

- Backend: Flask
- Database: SQLite
- AI Model: Google Generative AI
- Frontend: TailwindCSS + Chart.js

## Deployment Guide

1. Environment Requirements:
   - Python 3.9+
   - SQLite3

2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Environment Variables:
   Create a `.env` file and set the following variables:
   ```
   DATABASE_URI=sqlite:///studypath.db
   FLASK_APP=app.py
   FLASK_ENV=production
   API=your_deepseek_api_key
   ```

4. Initialize Database:
   ```bash
   python seed_db.py
   ```

5. Start Application:
   ```bash
   python app.py
   ```

## API Documentation

### Course Related

- GET `/api/courses` - Get all courses
- POST `/api/recommendations` - Get course recommendations

### Student Related

- GET `/api/student/<student_id>/progress` - Get learning progress

### Other Endpoints

- POST `/api/chat` - AI Assistant chat
- POST `/api/feedback` - Submit feedback

## Contributing

1. Fork this repository
2. Create a feature branch
3. Submit changes
4. Create a Pull Request

## License

MIT License 

### API密钥配置

本应用使用DeepSeek API进行AI聊天功能。你需要：

1. 在[DeepSeek Platform](https://platform.deepseek.com/)创建一个账户
2. 生成API密钥
3. 将API密钥添加到.env文件中的API变量

**重要提示：** 不要在代码中硬编码API密钥，也不要将包含真实API密钥的.env文件提交到版本控制系统。 