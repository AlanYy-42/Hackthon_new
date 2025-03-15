import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import os

class CourseRecommender:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'models', 'course_recommender.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler.pkl')
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Load model and scaler if they exist, otherwise create dummy ones
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = pickle.load(open(self.model_path, 'rb'))
            self.scaler = pickle.load(open(self.scaler_path, 'rb'))
        else:
            # For demo purposes, we'll create a dummy model
            self.create_dummy_model()
    
    def create_dummy_model(self):
        """Create a simple dummy model for demonstration purposes"""
        # This is just a placeholder - in a real app, you'd train a proper model
        self.scaler = StandardScaler()
        # Save the dummy model and scaler
        pickle.dump(self.scaler, open(self.scaler_path, 'wb'))
        # We'll use a simple dictionary as our "model" for now
        self.model = {
            "CS": ["CS101", "CS201", "CS301"],
            "MATH": ["MATH101", "MATH201", "STAT101"],
            "ENG": ["ENG101", "ENG201", "LIT101"]
        }
        pickle.dump(self.model, open(self.model_path, 'wb'))
    
    def recommend_courses(self, student_data):
        """
        Recommend courses based on student data
        
        Args:
            student_data: Dictionary containing student information
                - major: Student's major
                - completed_courses: List of completed course codes
                - gpa: Current GPA
        
        Returns:
            List of recommended course codes
        """
        # This is a simplified recommendation logic
        # In a real app, you'd use a trained ML model
        
        major = student_data.get('major', '')
        completed_courses = student_data.get('completed_courses', [])
        
        # Get courses for the student's major
        recommended = self.model.get(major, [])
        
        # Filter out courses the student has already completed
        recommended = [course for course in recommended if course not in completed_courses]
        
        return recommended[:5]  # Return top 5 recommendations

# Create a singleton instance
recommender = CourseRecommender() 