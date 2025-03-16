from app import app, db
from models import Course, Student, Enrollment
import random

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        # 先删除所有表，然后重新创建
        db.drop_all()
        db.create_all()
        
        print("Creating fresh database tables...")
        
        # Create courses
        courses = [
            # Computer Science courses
            Course(code="CS101", name="Introduction to Programming", description="Basic programming concepts using Python", 
                  credits=3, difficulty_level=2.5, avg_study_hours=6),
            Course(code="CS201", name="Data Structures", description="Fundamental data structures and algorithms", 
                  credits=4, difficulty_level=3.5, avg_study_hours=8),
            Course(code="CS301", name="Database Systems", description="Database design and SQL", 
                  credits=3, difficulty_level=3.0, avg_study_hours=7),
            Course(code="CS401", name="Artificial Intelligence", description="Introduction to AI concepts and algorithms", 
                  credits=4, difficulty_level=4.0, avg_study_hours=10),
            
            # Math courses
            Course(code="MATH101", name="Calculus I", description="Limits, derivatives, and integrals", 
                  credits=4, difficulty_level=3.0, avg_study_hours=8),
            Course(code="MATH201", name="Linear Algebra", description="Vector spaces, matrices, and linear transformations", 
                  credits=3, difficulty_level=3.5, avg_study_hours=7),
            Course(code="STAT101", name="Introduction to Statistics", description="Basic statistical concepts and methods", 
                  credits=3, difficulty_level=2.5, avg_study_hours=6),
            
            # English courses
            Course(code="ENG101", name="Composition", description="Academic writing and rhetoric", 
                  credits=3, difficulty_level=2.0, avg_study_hours=5),
            Course(code="ENG201", name="Technical Writing", description="Writing for technical and professional contexts", 
                  credits=3, difficulty_level=2.5, avg_study_hours=5),
            Course(code="LIT101", name="Introduction to Literature", description="Analysis of literary texts", 
                  credits=3, difficulty_level=2.0, avg_study_hours=4),
        ]
        
        # Add courses to database
        for course in courses:
            db.session.add(course)
        
        # 提交课程以获取ID
        db.session.commit()
        
        # Set up prerequisites (确保不会添加自引用的先修课程关系)
        def add_prerequisite(course, prerequisite):
            if course.id != prerequisite.id:  # 确保课程不能是自己的前置课程
                course.prerequisites.append(prerequisite)
            else:
                print(f"Warning: Attempted to add {course.code} as its own prerequisite. Skipped.")
        
        add_prerequisite(courses[1], courses[0])  # CS201 requires CS101
        add_prerequisite(courses[2], courses[0])  # CS301 requires CS101
        add_prerequisite(courses[3], courses[1])  # CS401 requires CS201
        add_prerequisite(courses[5], courses[4])  # MATH201 requires MATH101
        
        # Create students
        students = [
            Student(username="alice", email="alice@example.com", major="CS", gpa=3.8),
            Student(username="bob", email="bob@example.com", major="MATH", gpa=3.5),
            Student(username="charlie", email="charlie@example.com", major="ENG", gpa=3.9),
        ]
        
        # Add students to database
        for student in students:
            db.session.add(student)
        
        # 提交学生以获取ID
        db.session.commit()
        
        # Create enrollments
        enrollments = [
            # Alice's enrollments
            Enrollment(student_id=1, course_id=1, semester="Fall 2022", grade="A", status="completed"),
            Enrollment(student_id=1, course_id=2, semester="Spring 2023", grade="B+", status="completed"),
            Enrollment(student_id=1, course_id=5, semester="Fall 2022", grade="A-", status="completed"),
            Enrollment(student_id=1, course_id=3, semester="Fall 2023", status="in-progress"),
            
            # Bob's enrollments
            Enrollment(student_id=2, course_id=5, semester="Fall 2022", grade="A", status="completed"),
            Enrollment(student_id=2, course_id=6, semester="Spring 2023", grade="A-", status="completed"),
            Enrollment(student_id=2, course_id=7, semester="Fall 2023", status="in-progress"),
            
            # Charlie's enrollments
            Enrollment(student_id=3, course_id=8, semester="Fall 2022", grade="A", status="completed"),
            Enrollment(student_id=3, course_id=9, semester="Spring 2023", grade="A", status="completed"),
            Enrollment(student_id=3, course_id=10, semester="Fall 2023", status="in-progress"),
        ]
        
        # Add enrollments to database
        for enrollment in enrollments:
            db.session.add(enrollment)
        
        # Commit changes
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 