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

### API Key Configuration

This application uses the DeepSeek API for AI chat functionality. You need to:

1. Create an account on [DeepSeek Platform](https://platform.deepseek.com/)
2. Generate an API key
3. Add the API key to the API variable in your .env file

**Important Note:** Do not hardcode the API key in your code, and do not commit the .env file containing your real API key to version control systems. 