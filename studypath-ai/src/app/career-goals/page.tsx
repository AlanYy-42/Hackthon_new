'use client'

import React, { useState } from 'react'
import { Card, Title, ProgressBar, Button, TextInput } from '@tremor/react'
import { motion } from 'framer-motion'

export default function CareerGoals() {
  const [jobTitles, setJobTitles] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showRoadmap, setShowRoadmap] = useState(false)
  
  // Example career path data
  const careerPath = [
    {
      phase: "Undergraduate Studies",
      progress: 75,
      milestones: [
        "Complete core courses",
        "Participate in research projects",
        "Gain internship experience",
      ]
    },
    {
      phase: "Graduate School Application",
      progress: 30,
      milestones: [
        "Prepare for GRE exam",
        "Write research proposal",
        "Contact potential advisors",
      ]
    },
    {
      phase: "Career Development",
      progress: 10,
      milestones: [
        "Build professional network",
        "Attend industry conferences",
        "Obtain certifications",
      ]
    }
  ]

  // Example learning roadmap for Machine Learning Engineer
  const mleRoadmap = [
    {
      month: "March 2025",
      skills: [
        "Learn Python & NumPy (LinkedIn Learning)",
        "Start \"Machine Learning Foundations\" (Coursera)",
        "Implement a Linear Regression model (Kaggle project)"
      ]
    },
    {
      month: "April 2025",
      skills: [
        "Learn TensorFlow/PyTorch (Udacity)",
        "Work on a Neural Network from scratch",
        "Participate in a Kaggle competition"
      ]
    },
    {
      month: "May 2025",
      skills: [
        "Study MLOps & Model Deployment (AWS, GCP)",
        "Deploy a Flask-based ML API on AWS",
        "Join an AI-focused hackathon"
      ]
    }
  ]

  // Example learning roadmap for Data Scientist
  const dsRoadmap = [
    {
      month: "March 2025",
      skills: [
        "Learn Python & Pandas (DataCamp)",
        "Start \"Data Science Specialization\" (Coursera)",
        "Practice data cleaning and visualization (Tableau)"
      ]
    },
    {
      month: "April 2025",
      skills: [
        "Learn statistical analysis (edX)",
        "Work on exploratory data analysis projects",
        "Participate in a data visualization challenge"
      ]
    },
    {
      month: "May 2025",
      skills: [
        "Study Big Data technologies (Hadoop, Spark)",
        "Build a data pipeline with Apache Airflow",
        "Join a data science hackathon"
      ]
    }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call to Gemini for learning roadmap
    setTimeout(() => {
      setShowRoadmap(true)
      setIsLoading(false)
    }, 2000)
  }

  // Determine which roadmap to show based on job titles
  const getLearningRoadmap = () => {
    if (jobTitles.toLowerCase().includes('machine learning') || 
        jobTitles.toLowerCase().includes('ml engineer')) {
      return mleRoadmap
    } else if (jobTitles.toLowerCase().includes('data scientist')) {
      return dsRoadmap
    } else {
      // Default to ML Engineer roadmap
      return mleRoadmap
    }
  }

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Career Goal Planning</Title>

      {!showRoadmap ? (
        <Card className="mt-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Gemini Career Planning Assistant</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-blue-900 mb-2">
                Please enter the job titles you prefer
              </label>
              <TextInput
                placeholder="e.g., Machine Learning Engineer, Data Scientist"
                value={jobTitles}
                onChange={(e) => setJobTitles(e.target.value)}
                required
              />
            </div>
            
            <Button 
              type="submit" 
              color="blue" 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? "Analyzing career path..." : "Generate Learning Roadmap"}
            </Button>
          </form>
        </Card>
      ) : (
        <>
          <div className="mt-6">
            <Card>
              <div className="flex justify-between items-center">
                <Title>Monthly Learning Roadmap</Title>
                <Button 
                  color="blue" 
                  variant="light"
                  onClick={() => setShowRoadmap(false)}
                >
                  Start Over
                </Button>
              </div>
              
              <div className="mt-6 space-y-8">
                {getLearningRoadmap().map((month, index) => (
                  <motion.div
                    key={month.month}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.2 }}
                    className="p-4 border border-blue-100 rounded-lg bg-blue-50"
                  >
                    <h3 className="text-lg font-semibold text-blue-900 mb-3">🔹 {month.month}</h3>
                    <ul className="space-y-2">
                      {month.skills.map((skill, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="inline-block w-4 h-4 mt-1 mr-2 bg-blue-500 rounded-full"></span>
                          <span className="text-blue-800">{skill}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                ))}
              </div>
            </Card>
          </div>

          <div className="mt-8">
            <Card>
              <Title>Development Path</Title>
              <div className="mt-6 space-y-6">
                {careerPath.map((path, index) => (
                  <motion.div
                    key={path.phase}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.2 }}
                  >
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-medium text-blue-900">{path.phase}</h3>
                        <ProgressBar value={path.progress} color="blue" className="mt-2" />
                        <p className="text-sm text-blue-600 mt-1">
                          Completion: {path.progress}%
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-blue-900 mb-2">Milestones</h4>
                        <ul className="space-y-2">
                          {path.milestones.map((milestone, idx) => (
                            <li
                              key={idx}
                              className="flex items-center text-sm text-blue-700"
                            >
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
                              {milestone}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </Card>
          </div>

          <div className="mt-8">
            <Card>
              <Title>Recommended Resources</Title>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    title: "LinkedIn Learning",
                    description: "Professional skills online courses",
                    type: "Online Learning",
                  },
                  {
                    title: "Industry Workshops",
                    description: "Network with industry professionals",
                    type: "Offline Events",
                  },
                  {
                    title: "Professional Certifications",
                    description: "Enhance career competitiveness",
                    type: "Career Development",
                  },
                  {
                    title: "Mentorship Program",
                    description: "One-on-one career guidance",
                    type: "Personal Growth",
                  },
                ].map((resource) => (
                  <div
                    key={resource.title}
                    className="p-4 bg-blue-50 rounded-lg"
                  >
                    <h3 className="font-medium text-blue-900">{resource.title}</h3>
                    <p className="text-sm text-blue-700 mt-1">{resource.description}</p>
                    <span className="inline-block mt-2 px-2 py-1 text-xs text-white bg-blue-600 rounded-full">
                      {resource.type}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </main>
  )
} 