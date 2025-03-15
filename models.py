from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between courses and prerequisites
course_prerequisites = db.Table('course_prerequisites',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('prerequisite_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.Float)  # Estimated difficulty (1-5)
    avg_study_hours = db.Column(db.Float)   # Average weekly study hours
    
    # Many-to-many relationship with itself for prerequisites
    prerequisites = db.relationship(
        'Course', secondary=course_prerequisites,
        primaryjoin=(course_prerequisites.c.course_id == id),
        secondaryjoin=(course_prerequisites.c.prerequisite_id == id),
        backref=db.backref('required_for', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'credits': self.credits,
            'difficulty_level': self.difficulty_level,
            'avg_study_hours': self.avg_study_hours,
            'prerequisites': [p.code for p in self.prerequisites]
        }

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    major = db.Column(db.String(100))
    gpa = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with enrollments
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'major': self.major,
            'gpa': self.gpa,
            'created_at': self.created_at.isoformat()
        }

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)  # e.g., "Fall 2023"
    grade = db.Column(db.String(2))  # e.g., "A", "B+", etc.
    status = db.Column(db.String(20), default="planned")  # planned, in-progress, completed
    
    # Relationship with course
    course = db.relationship('Course', backref='enrollments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'course_code': self.course.code,
            'semester': self.semester,
            'grade': self.grade,
            'status': self.status
        } 