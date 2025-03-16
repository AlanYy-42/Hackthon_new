import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pickle
import os
import random
import sqlite3
import json

class CourseRecommender:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'models', 'course_recommender.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler.pkl')
        self.data_path = os.path.join(os.path.dirname(__file__), 'models', 'training_data.pkl')
        self.courses_path = os.path.join(os.path.dirname(__file__), 'models', 'courses.pkl')
        self.prereqs_path = os.path.join(os.path.dirname(__file__), 'models', 'prerequisites.pkl')
        
        # 使用与 app.py 相同的数据库路径
        basedir = os.path.abspath(os.path.dirname(__file__))
        self.db_path = os.path.join(basedir, "instance", "studypath.db")
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # 尝试从数据库加载训练数据
        if self._load_training_data_from_db():
            print("Successfully loaded training data from database")
            # 如果模型文件不存在，则训练模型
            if not (os.path.exists(self.model_path) and os.path.exists(self.scaler_path)):
                self.train_model()
        # 如果数据库中没有训练数据，则生成合成数据并训练模型
        else:
            print("No training data found in database, generating synthetic data")
            # Generate synthetic data and train a model
            self.generate_synthetic_data()
            self.train_model()
            # 将训练数据保存到数据库
            self.save_training_data_to_db()
    
    def _load_training_data_from_db(self):
        """从SQLite数据库加载训练数据"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 检查数据库是否存在
            if not os.path.exists(self.db_path):
                return False
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            
            # 检查是否存在训练数据表
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_training_data'")
            if not cursor.fetchone():
                conn.close()
                return False
            
            # 加载训练数据
            self.training_data = pd.read_sql("SELECT * FROM ml_training_data", conn)
            
            # 加载课程数据
            cursor.execute("SELECT * FROM ml_courses")
            courses_data = cursor.fetchall()
            if not courses_data:
                conn.close()
                return False
            
            # 重建课程字典
            self.courses = {}
            for row in courses_data:
                major, course_type, course_code = row
                if major not in self.courses:
                    self.courses[major] = {"core": [], "electives": [], "related": []}
                self.courses[major][course_type].append(course_code)
            
            # 加载先修课程关系
            cursor.execute("SELECT * FROM ml_prerequisites")
            prereqs_data = cursor.fetchall()
            
            # 重建先修课程字典
            self.prerequisites = {}
            for row in prereqs_data:
                course, prereq = row
                if course not in self.prerequisites:
                    self.prerequisites[course] = []
                self.prerequisites[course].append(prereq)
            
            conn.close()
            
            # 将数据保存为pickle文件以便快速访问
            pickle.dump(self.training_data, open(self.data_path, 'wb'))
            pickle.dump(self.courses, open(self.courses_path, 'wb'))
            pickle.dump(self.prerequisites, open(self.prereqs_path, 'wb'))
            
            return True
        except Exception as e:
            print(f"Error loading training data from database: {str(e)}")
            return False
    
    def save_training_data_to_db(self):
        """将训练数据保存到SQLite数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建训练数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_training_data (
                student_id INTEGER,
                major TEXT,
                semester INTEGER,
                gpa REAL,
                num_completed_courses INTEGER,
                completed_courses TEXT,
                next_courses TEXT
            )
            ''')
            
            # 创建课程表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_courses (
                major TEXT,
                course_type TEXT,
                course_code TEXT,
                PRIMARY KEY (major, course_type, course_code)
            )
            ''')
            
            # 创建先修课程关系表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_prerequisites (
                course TEXT,
                prerequisite TEXT,
                PRIMARY KEY (course, prerequisite)
            )
            ''')
            
            # 清空现有数据
            cursor.execute("DELETE FROM ml_training_data")
            cursor.execute("DELETE FROM ml_courses")
            cursor.execute("DELETE FROM ml_prerequisites")
            
            # 保存训练数据
            for _, row in self.training_data.iterrows():
                cursor.execute(
                    "INSERT INTO ml_training_data VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        row['student_id'],
                        row['major'],
                        row['semester'],
                        row['gpa'],
                        row['num_completed_courses'],
                        json.dumps(row['completed_courses']),
                        json.dumps(row['next_courses'])
                    )
                )
            
            # 保存课程数据
            for major, courses in self.courses.items():
                for course_type, course_list in courses.items():
                    for course in course_list:
                        cursor.execute(
                            "INSERT INTO ml_courses VALUES (?, ?, ?)",
                            (major, course_type, course)
                        )
            
            # 保存先修课程关系
            for course, prereqs in self.prerequisites.items():
                for prereq in prereqs:
                    cursor.execute(
                        "INSERT INTO ml_prerequisites VALUES (?, ?)",
                        (course, prereq)
                    )
            
            # 提交更改
            conn.commit()
            conn.close()
            
            print("Training data saved to database successfully")
            return True
        except Exception as e:
            print(f"Error saving training data to database: {str(e)}")
            return False
    
    def generate_synthetic_data(self):
        """Generate synthetic student data and course information for training"""
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
        num_students = 500
        student_data = []
        
        for i in range(num_students):
            # Randomly select a major
            major = random.choice(majors)
            
            # Randomly select semester (1-8)
            semester = random.randint(1, 8)
            
            # Randomly select GPA (2.0-4.0)
            gpa = round(random.uniform(2.0, 4.0), 2)
            
            # 根据先修课程关系确定已完成的课程
            completed_courses = self._generate_completed_courses(major, semester)
            
            # Create feature vector
            student_record = {
                "student_id": i,
                "major": major,
                "semester": semester,
                "gpa": gpa,
                "completed_courses": completed_courses,
                "num_completed_courses": len(completed_courses)
            }
            
            # 根据先修课程关系确定下一步可以学习的课程
            next_courses = self._get_next_courses(completed_courses, major)
            student_record["next_courses"] = next_courses[:3]  # Top 3 recommended courses
            
            student_data.append(student_record)
        
        self.training_data = pd.DataFrame(student_data)
        
        # Save the synthetic data and course catalog
        pickle.dump(self.training_data, open(self.data_path, 'wb'))
        pickle.dump(self.courses, open(self.courses_path, 'wb'))
        pickle.dump(self.prerequisites, open(self.prereqs_path, 'wb'))
    
    def _generate_completed_courses(self, major, semester):
        """根据学期和先修课程关系生成已完成的课程列表"""
        completed_courses = []
        
        # 获取该专业的所有课程
        all_courses = (self.courses[major]["core"] + 
                      self.courses[major]["electives"] + 
                      self.courses[major]["related"])
        
        # 按照先修课程关系排序课程
        sorted_courses = self._sort_courses_by_prerequisites(all_courses)
        
        # 根据学期确定已完成的课程数量（每学期平均完成3门课程）
        num_completed = min(semester * 3, len(sorted_courses))
        
        # 选择前N门课程作为已完成课程
        completed_courses = sorted_courses[:num_completed]
        
        return completed_courses
    
    def _sort_courses_by_prerequisites(self, courses):
        """根据先修课程关系对课程进行拓扑排序"""
        # 创建课程依赖图
        graph = {course: self.prerequisites.get(course, []) for course in courses}
        
        # 拓扑排序
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(node):
            if node in temp_visited:
                # 检测到循环依赖，跳过
                return
            if node in visited:
                return
            
            temp_visited.add(node)
            
            for prereq in graph.get(node, []):
                if prereq in courses:  # 只考虑列表中的课程
                    dfs(prereq)
            
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        # 对每个课程进行DFS
        for course in courses:
            if course not in visited:
                dfs(course)
        
        # 反转结果，使得先修课程在前
        return result[::-1]
    
    def _get_next_courses(self, completed_courses, major):
        """根据已完成的课程和先修课程关系，获取下一步可以学习的课程"""
        next_courses = []
        
        # 获取该专业的所有课程
        all_courses = (self.courses[major]["core"] + 
                      self.courses[major]["electives"] + 
                      self.courses[major]["related"])
        
        # 检查每门课程是否可以学习（已满足先修要求且尚未学习）
        for course in all_courses:
            if course not in completed_courses:
                prereqs = self.prerequisites.get(course, [])
                if all(prereq in completed_courses for prereq in prereqs):
                    next_courses.append(course)
        
        # 优先推荐核心课程
        core_next = [c for c in next_courses if c in self.courses[major]["core"]]
        elective_next = [c for c in next_courses if c in self.courses[major]["electives"]]
        related_next = [c for c in next_courses if c in self.courses[major]["related"]]
        
        # 按优先级排序
        prioritized_next = core_next + elective_next + related_next
        
        return prioritized_next[:5]  # 返回最多5门课程
    
    def train_model(self):
        """Train a KNN model on the synthetic data"""
        # Extract features for training
        X = self.training_data[['major', 'semester', 'gpa', 'num_completed_courses']]
        
        # 为了将已完成的课程作为特征，我们需要创建一个课程-学生矩阵
        # 首先获取所有可能的课程
        all_possible_courses = set()
        for major in self.courses:
            all_possible_courses.update(self.courses[major]["core"])
            all_possible_courses.update(self.courses[major]["electives"])
            all_possible_courses.update(self.courses[major]["related"])
        
        # 为每个学生创建一个课程完成向量
        course_completion = pd.DataFrame(0, index=self.training_data.index, 
                                        columns=sorted(list(all_possible_courses)))
        
        # 填充课程完成矩阵
        for idx, row in self.training_data.iterrows():
            for course in row['completed_courses']:
                if course in course_completion.columns:
                    course_completion.loc[idx, course] = 1
        
        # 创建一个预处理器，处理分类特征和数值特征
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), ['major']),
                ('num', StandardScaler(), ['semester', 'gpa', 'num_completed_courses'])
            ])
        
        # 预处理基本特征
        X_basic_processed = preprocessor.fit_transform(X)
        
        # 将课程完成矩阵与基本特征合并
        X_course_processed = course_completion.values
        
        # 合并所有特征
        X_processed = np.hstack((X_basic_processed, X_course_processed))
        
        # 创建并训练KNN模型
        knn = NearestNeighbors(n_neighbors=5, algorithm='auto')
        self.model = knn.fit(X_processed)
        
        # 保存预处理器和模型
        self.preprocessor = preprocessor
        pickle.dump(self.model, open(self.model_path, 'wb'))
        pickle.dump(self.preprocessor, open(self.scaler_path, 'wb'))
        
        # 可视化学生数据（可选）
        self._visualize_student_data(X_processed)
    
    def _visualize_student_data(self, X_processed, method='tsne'):
        """使用TSNE或PCA可视化学生数据"""
        try:
            # 降维到2D
            if method == 'tsne':
                X_embedded = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(X_processed)
                title = "Student Data Visualization (t-SNE)"
            else:  # PCA
                X_embedded = PCA(n_components=2, random_state=42).fit_transform(X_processed)
                title = "Student Data Visualization (PCA)"
            
            # 创建图表
            plt.figure(figsize=(10, 8))
            
            # 为不同专业使用不同颜色
            majors = self.training_data['major'].unique()
            colors = plt.cm.rainbow(np.linspace(0, 1, len(majors)))
            
            for i, major in enumerate(majors):
                # 获取该专业的学生索引
                indices = self.training_data[self.training_data['major'] == major].index
                
                # 绘制该专业的学生
                plt.scatter(
                    X_embedded[indices, 0], 
                    X_embedded[indices, 1],
                    c=[colors[i]],
                    label=major,
                    alpha=0.7
                )
            
            plt.title(title)
            plt.legend()
            
            # 保存图表
            vis_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            os.makedirs(vis_dir, exist_ok=True)
            plt.savefig(os.path.join(vis_dir, f'student_data_{method}.png'))
            plt.close()
            
            print(f"Visualization saved to {vis_dir}/student_data_{method}.png")
        except Exception as e:
            print(f"Visualization failed: {str(e)}")
    
    def recommend_courses(self, student_data):
        """
        Recommend courses based on student data using KNN
        
        Args:
            student_data: Dictionary containing student information
                - major: Student's major
                - semester: Current semester
                - completed_courses: List of completed course codes
                - gpa: Current GPA
        
        Returns:
            List of recommended course codes
        """
        major = student_data.get('major', 'CS')  # Default to CS if not provided
        semester = student_data.get('semester', 1)  # Default to 1st semester if not provided
        completed_courses = student_data.get('completed_courses', [])
        gpa = student_data.get('gpa', 3.0)  # Default to 3.0 if not provided
        
        # 创建学生特征向量
        student_features = pd.DataFrame({
            'major': [major],
            'semester': [semester],
            'gpa': [gpa],
            'num_completed_courses': [len(completed_courses)]
        })
        
        # 预处理基本特征
        student_basic_processed = self.preprocessor.transform(student_features)
        
        # 创建课程完成向量
        all_possible_courses = set()
        for m in self.courses:
            all_possible_courses.update(self.courses[m]["core"])
            all_possible_courses.update(self.courses[m]["electives"])
            all_possible_courses.update(self.courses[m]["related"])
        
        course_completion = np.zeros(len(all_possible_courses))
        for i, course in enumerate(sorted(list(all_possible_courses))):
            if course in completed_courses:
                course_completion[i] = 1
        
        # 合并所有特征
        student_processed = np.hstack((student_basic_processed, course_completion.reshape(1, -1)))
        
        # 找到相似的学生
        distances, indices = self.model.kneighbors(student_processed)
        
        # 从相似学生中获取课程推荐
        final_recommendations = []
        seen_courses = set()  # 用于去重
        
        for idx in indices[0]:
            similar_student = self.training_data.iloc[idx]
            next_courses = similar_student['next_courses']
            
            for course in next_courses:
                # 检查课程是否已完成、是否已在推荐列表中、是否满足先修要求
                if (course not in completed_courses and 
                    course not in seen_courses and 
                    self._check_prerequisites_met(course, completed_courses)):
                    seen_courses.add(course)
                    final_recommendations.append(course)
            
            # 只推荐最多5门课
            if len(final_recommendations) >= 5:
                break
        
        # 如果从相似学生中没有获得足够的推荐，使用基于规则的方法补充
        if len(final_recommendations) < 5:
            # 获取下一步可以学习的课程
            rule_based_recommendations = self._get_next_courses(completed_courses, major)
            
            # 添加尚未推荐的课程
            for course in rule_based_recommendations:
                if course not in completed_courses and course not in seen_courses:
                    seen_courses.add(course)
                    final_recommendations.append(course)
                    
                    # 只推荐最多5门课
                    if len(final_recommendations) >= 5:
                        break
        
        return final_recommendations[:5]  # 确保最多返回5门课程
    
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
        elif course_num.startswith('4'):
            level = "Special Topics in"
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