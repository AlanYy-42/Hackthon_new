import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import os
import random
import io

class CourseRecommender:
    def __init__(self):
        # 完全使用内存存储
        self.model = None
        self.preprocessor = None
        self.training_data = None
        self.courses = None
        self.prerequisites = None
        
        # 不再使用文件路径
        print("Generating synthetic data in memory")
        self.generate_synthetic_data()
        self.train_model()
        
    def generate_synthetic_data(self):
        """生成合成训练数据"""
        # Define course catalog
        majors = ["CS", "MATH", "ENG", "BIO", "PHYS", "CHEM", "ECON", "PSYCH"]
        
        # Generate courses for each major
        self.courses = {}
        self.prerequisites = {}  # 添加先修课程关系
        
        for major in majors:
            # Core courses for the major (sequential courses with prerequisites)
            core_courses = [f"{major}{101+i*100}" for i in range(5)]
            
            # Elective courses for the major
            elective_courses = [f"{major}E{201+i*50}" for i in range(8)]
            
            # Related courses from other majors
            related_majors = random.sample([m for m in majors if m != major], 3)
            related_courses = []
            for related_major in related_majors:
                related_courses.extend([f"{related_major}{101+i*100}" for i in range(2)])
            
            # Combine all courses for this major
            self.courses[major] = {
                "core": core_courses,
                "electives": elective_courses,
                "related": related_courses
            }
            
            # 设置先修课程关系
            # 核心课程的先修关系（每门课程依赖前一门）
            for i in range(1, len(core_courses)):
                self.prerequisites[core_courses[i]] = [core_courses[i-1]]
            
            # 选修课程的先修关系（依赖至少一门核心课程）
            for i, elective in enumerate(elective_courses):
                # 前半部分选修课依赖第一门核心课程
                if i < len(elective_courses) // 2:
                    self.prerequisites[elective] = [core_courses[0]]
                # 后半部分选修课依赖第二门核心课程
                else:
                    self.prerequisites[elective] = [core_courses[1]]
            
            # 相关课程没有先修要求
            for related in related_courses:
                self.prerequisites[related] = []
        
        # Generate synthetic student data
        num_students = 1000
        self.training_data = []
        
        for i in range(num_students):
            # Randomly select a major
            major = random.choice(majors)
            
            # Randomly select semester (1-8)
            semester = random.randint(1, 8)
            
            # Randomly select GPA (2.0-4.0)
            gpa = round(random.uniform(2.0, 4.0), 2)
            
            # Select completed courses based on semester
            all_courses = self.courses[major]["core"] + self.courses[major]["electives"] + self.courses[major]["related"]
            
            # The higher the semester, the more courses completed
            num_completed = min(len(all_courses), int(semester * 1.5))
            
            # Ensure prerequisites are respected
            completed_courses = []
            available_courses = [c for c in all_courses if not self.prerequisites.get(c, [])]  # Start with courses that have no prerequisites
            
            while len(completed_courses) < num_completed and available_courses:
                # Select a random available course
                course = random.choice(available_courses)
                completed_courses.append(course)
                available_courses.remove(course)
                
                # Add new available courses based on prerequisites
                for c in all_courses:
                    if c not in completed_courses and c not in available_courses:
                        prereqs = self.prerequisites.get(c, [])
                        if all(p in completed_courses for p in prereqs):
                            available_courses.append(c)
            
            # Generate grades for completed courses (higher GPA = higher grades)
            grades = {}
            for course in completed_courses:
                # Base grade on student's GPA with some randomness
                mean_grade = max(60, min(100, 60 + (gpa - 2.0) * 20))  # Map GPA 2.0-4.0 to grade 60-100
                grade = max(60, min(100, int(random.gauss(mean_grade, 10))))  # Add normal distribution noise
                grades[course] = grade
            
            # Add to training data
            self.training_data.append({
                "student_id": i + 1,
                "major": major,
                "semester": semester,
                "gpa": gpa,
                "completed_courses": completed_courses,
                "grades": grades
            })
    
    def train_model(self):
        """训练推荐模型"""
        # Extract features from training data
        X = []
        y = []
        
        for student in self.training_data:
            # Create features
            features = [
                student["semester"],
                student["gpa"],
                len(student["completed_courses"]),
                # Average grade
                sum(student["grades"].values()) / len(student["grades"]) if student["grades"] else 0
            ]
            
            # One-hot encode major
            major_feature = [0] * 8  # Assuming 8 majors
            major_idx = ["CS", "MATH", "ENG", "BIO", "PHYS", "CHEM", "ECON", "PSYCH"].index(student["major"])
            major_feature[major_idx] = 1
            
            # Combine all features
            X.append(features + major_feature)
            
            # Target is the next course they took (last one in their list)
            if student["completed_courses"]:
                y.append(student["completed_courses"][-1])
            else:
                y.append("")
        
        # Create preprocessor
        self.preprocessor = StandardScaler()
        X_scaled = self.preprocessor.fit_transform(X)
        
        # Train nearest neighbors model
        self.model = NearestNeighbors(n_neighbors=10, algorithm='ball_tree')
        self.model.fit(X_scaled)
    
    def visualize_student_data(self):
        """Visualize the synthetic student data"""
        try:
            # Extract features from training data
            X = []
            majors = []
            
            for student in self.training_data:
                # Create features
                features = [
                    student["semester"],
                    student["gpa"],
                    len(student["completed_courses"]),
                    # Average grade
                    sum(student["grades"].values()) / len(student["grades"]) if student["grades"] else 0
                ]
                
                X.append(features)
                majors.append(student["major"])
            
            # Convert to numpy array
            X = np.array(X)
            
            # Apply t-SNE to reduce dimensions for visualization
            X_embedded = TSNE(n_components=2, random_state=42).fit_transform(X)
            
            # Create a figure
            plt.figure(figsize=(10, 8))
            
            # Define colors for different majors
            unique_majors = list(set(majors))
            colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_majors)))
            
            # Plot each major with a different color
            for i, major in enumerate(unique_majors):
                indices = [j for j, m in enumerate(majors) if m == major]
                plt.scatter(
                    X_embedded[indices, 0],
                    X_embedded[indices, 1],
                    c=[colors[i]],
                    label=major,
                    alpha=0.7
                )
            
            plt.title("t-SNE Visualization of Student Data")
            plt.legend()
            plt.tight_layout()
            
            # 使用内存缓冲区而不是文件
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            
            return buf
        except Exception as e:
            print(f"Error generating visualization: {str(e)}")
            return None
    
    def get_recommendations(self, student_id=None, major=None, completed_courses=[], student_data=None):
        """Get course recommendations for a student"""
        if student_id and student_id in [s["student_id"] for s in self.training_data]:
            # Get recommendations for an existing student
            student = next(s for s in self.training_data if s["student_id"] == student_id)
            
            # Extract student features
            features = [
                student["semester"],
                student["gpa"],
                len(student["completed_courses"]),
                sum(student["grades"].values()) / len(student["grades"]) if student["grades"] else 0
            ]
            
            # One-hot encode major
            major_feature = [0] * 8  # Assuming 8 majors
            major_idx = ["CS", "MATH", "ENG", "BIO", "PHYS", "CHEM", "ECON", "PSYCH"].index(student["major"])
            major_feature[major_idx] = 1
            
            # Combine all features
            X = [features + major_feature]
            
            # Scale features
            X_scaled = self.preprocessor.transform(X)
            
            # Find nearest neighbors
            distances, indices = self.model.kneighbors(X_scaled)
            
            # Get recommendations based on what similar students took
            recommendations = []
            seen_courses = set(student["completed_courses"])
            
            for idx in indices[0]:
                similar_student = self.training_data[idx]
                for course in similar_student["completed_courses"]:
                    if course not in seen_courses:
                        seen_courses.add(course)
                        recommendations.append(course)
            
            return recommendations[:5]  # Return top 5 recommendations
        
        elif major:
            # Generate recommendations for a new student with a specific major
            if not completed_courses:
                # If no courses completed, recommend first core course
                return self.courses[major]["core"][:1]
            
            # Get all courses for this major
            all_courses = self.courses[major]["core"] + self.courses[major]["electives"] + self.courses[major]["related"]
            
            # Find courses that haven't been taken yet but prerequisites are met
            available_courses = []
            for course in all_courses:
                if course not in completed_courses:
                    prereqs = self.prerequisites.get(course, [])
                    if all(p in completed_courses for p in prereqs):
                        available_courses.append(course)
            
            # Sort by course number (core courses first)
            available_courses.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
            
            return available_courses[:5]  # Return top 5 recommendations
        
        else:
            # Default recommendations (CS major)
            return self.courses["CS"]["core"][:5]
    
    def _get_next_courses(self, completed_courses, major):
        """使用规则方法获取下一步可学习的课程"""
        all_courses = self.courses[major]["core"] + self.courses[major]["electives"] + self.courses[major]["related"]
        
        # 找出所有尚未完成但先修课程要求已满足的课程
        available_courses = []
        for course in all_courses:
            if course not in completed_courses:
                prereqs = self.prerequisites.get(course, [])
                if all(p in completed_courses for p in prereqs):
                    available_courses.append(course)
        
        # 按课程编号排序（核心课程优先）
        available_courses.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 999)
        
        return available_courses
    
    def recommend_courses(self, student_data=None, num_recommendations=5):
        """推荐课程给学生"""
        # 从student_data中提取信息
        if student_data is None:
            return []
        
        major = student_data.get('major', '')
        completed_courses = student_data.get('completed_courses', [])
        
        # 如果没有完成任何课程，推荐该专业的第一门核心课程
        if not completed_courses and major:
            # 确保major存在于self.courses中
            if major in self.courses:
                return self.courses[major]["core"][:num_recommendations]
            else:
                # 如果专业不存在，返回CS专业的核心课程
                return self.courses["CS"]["core"][:num_recommendations]
        
        # 获取下一步可以学习的课程
        available_courses = self._get_next_courses(completed_courses, major)
        
        # 如果没有可用课程，返回一些通用课程
        if not available_courses:
            # 返回一些通用的AI/ML课程
            return ["CS101", "CS201", "MATH101", "AI101", "ML101"][:num_recommendations]
        
        return available_courses[:num_recommendations]  # 确保最多返回指定数量的课程
    
    def _check_prerequisites_met(self, course, completed_courses):
        """检查是否满足课程的先修要求"""
        prereqs = self.prerequisites.get(course, [])
        return all(prereq in completed_courses for prereq in prereqs)
    
    def get_course_details(self, course_code):
        """Get details for a specific course"""
        # This would typically come from a database
        # For now, we'll generate some dummy details
        
        if not course_code:
            return None
        
        # Extract major from course code
        major_code = ''.join([c for c in course_code if c.isalpha()])
        course_num = ''.join([c for c in course_code if c.isdigit()])
        
        # Generate course name based on number
        if course_num.startswith('1'):
            level = "Introduction to"
        elif course_num.startswith('2'):
            level = "Fundamentals of"
        elif course_num.startswith('3'):
            level = "Advanced"
        else:
            level = "Topics in"
        
        # Map major codes to full names
        major_names = {
            "CS": "Computer Science",
            "MATH": "Mathematics",
            "ENG": "English",
            "BIO": "Biology",
            "PHYS": "Physics",
            "CHEM": "Chemistry",
            "ECON": "Economics",
            "PSYCH": "Psychology",
            "CSE": "Computer Science and Engineering"
        }
        
        major_name = major_names.get(major_code, major_code)
        
        # Generate credits (3-4)
        credits = random.choice([3, 4])
        
        # Generate a description
        descriptions = [
            f"This course covers the {level.lower()} principles and concepts in {major_name}.",
            f"An {level.lower()} course exploring key topics in {major_name}.",
            f"Students will learn {level.lower()} techniques and methodologies in {major_name}.",
            f"A comprehensive study of {level.lower()} {major_name} concepts and applications."
        ]
        
        # 获取先修课程
        prerequisites = self.prerequisites.get(course_code, [])
        
        return {
            "code": course_code,
            "name": f"{level} {major_name}",
            "credits": credits,
            "description": random.choice(descriptions),
            "prerequisites": prerequisites
        }

# Create a singleton instance
recommender = CourseRecommender() 