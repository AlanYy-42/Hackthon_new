from flask import Flask, jsonify, request, render_template
import os
from dotenv import load_dotenv
from models import db, Course, Student, Enrollment
from ml_service import recommender

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///studypath.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

# API routes for courses
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict())

# API routes for students
@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())

@app.route('/api/students/<int:student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    return jsonify([enrollment.to_dict() for enrollment in enrollments])

# Course recommendation endpoint
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Get student data
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400
    
    # Get student from database
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Get completed courses
    completed_enrollments = Enrollment.query.filter_by(
        student_id=student_id, 
        status="completed"
    ).all()
    completed_courses = [e.course.code for e in completed_enrollments]
    
    # Prepare data for recommendation
    student_data = {
        'major': student.major,
        'completed_courses': completed_courses,
        'gpa': student.gpa
    }
    
    # Get recommendations
    recommendations = recommender.recommend_courses(student_data)
    
    # Get full course details for recommendations
    recommended_courses = Course.query.filter(Course.code.in_(recommendations)).all()
    
    return jsonify([course.to_dict() for course in recommended_courses])

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # 获取端口，Hugging Face Space使用7860端口
    port = int(os.environ.get('PORT', 7860))
    # 设置host为0.0.0.0，允许外部访问
    app.run(host='0.0.0.0', port=port, debug=False)
