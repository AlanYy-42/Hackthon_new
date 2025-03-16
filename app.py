from flask import Flask, jsonify, request, render_template
import os
from dotenv import load_dotenv
from models import db, Course, Student, Enrollment
from ml_service import recommender
from deepseek_service import chat_service

# Load environment variables at the start
load_dotenv()

# Print environment variables (without actual values) for debugging
print("Environment variables loaded:")
print("GOOGLE_API_KEY exists:", "GOOGLE_API_KEY" in os.environ)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///instance/studypath.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/courses')
def get_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    completed_enrollments = Enrollment.query.filter_by(
        student_id=student_id, 
        status="completed"
    ).all()
    completed_courses = [e.course.code for e in completed_enrollments]
    
    student_data = {
        'major': student.major,
        'completed_courses': completed_courses,
        'gpa': student.gpa
    }
    
    recommendations = recommender.recommend_courses(student_data)
    recommended_courses = Course.query.filter(Course.code.in_(recommendations)).all()
    
    return jsonify([course.to_dict() for course in recommended_courses])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    message = data['message']
    response = chat_service.send_message(message)
    
    if response is None:
        return jsonify({"error": "Failed to get response from API"}), 500
    
    return jsonify({"response": response})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Logic for saving feedback to database can be added here
    return jsonify({"message": "Thank you for your feedback!"})

@app.route('/api/student/<int:student_id>/progress')
def get_student_progress(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    
    total_credits = sum(e.course.credits for e in enrollments)
    completed_credits = sum(e.course.credits for e in enrollments if e.status == "completed")
    
    return jsonify({
        "total_credits": total_credits,
        "completed_credits": completed_credits,
        "completion_percentage": (completed_credits / total_credits * 100) if total_credits > 0 else 0
    })

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # Get port, Hugging Face Space uses port 7860
    port = int(os.environ.get('PORT', 7860))
    # Set host to 0.0.0.0 to allow external access
    app.run(host='0.0.0.0', port=port, debug=False)
