'use client'

import React, { useState } from 'react'
import { Card, Title, BarChart, DonutChart, Button, TextInput } from '@tremor/react'

export default function CoursePlanning() {
  const [programUrl, setProgramUrl] = useState('')
  const [careerPath, setCareerPath] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [courseRecommendations, setCourseRecommendations] = useState<any[]>([])
  const [showRecommendations, setShowRecommendations] = useState(false)

  // Example data for charts
  const courseData = [
    {
      semester: "Spring 2024",
      credits: 15,
      courses: 5,
      completed: 3,
    },
    {
      semester: "Fall 2024",
      credits: 18,
      courses: 6,
      completed: 0,
    },
    {
      semester: "Spring 2025",
      credits: 12,
      courses: 4,
      completed: 0,
    },
  ]

  const courseDistribution = [
    {
      name: "Required Courses",
      value: 45,
    },
    {
      name: "Elective Courses",
      value: 30,
    },
    {
      name: "Practical Courses",
      value: 15,
    },
  ]

  // Example course recommendations for Machine Learning Engineer path
  const mleCourses = [
    {
      semester: "Fall 2025",
      name: "Data Structures & Algorithms",
      code: "CS201",
      credits: 4,
    },
    {
      semester: "Spring 2026",
      name: "Introduction to Machine Learning",
      code: "AI301",
      credits: 3,
    },
    {
      semester: "Fall 2026",
      name: "Deep Learning & Neural Networks",
      code: "AI450",
      credits: 4,
    },
    {
      semester: "Spring 2027",
      name: "Capstone Project in AI",
      code: "AI499",
      credits: 6,
    },
  ]

  // Example course recommendations for Software Developer path
  const sdCourses = [
    {
      semester: "Fall 2025",
      name: "Data Structures & Algorithms",
      code: "CS201",
      credits: 4,
    },
    {
      semester: "Spring 2026",
      name: "Software Engineering",
      code: "SE301",
      credits: 3,
    },
    {
      semester: "Fall 2026",
      name: "Web Development",
      code: "WD401",
      credits: 4,
    },
    {
      semester: "Spring 2027",
      name: "Software Development Capstone",
      code: "SE499",
      credits: 6,
    },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call to Gemini for course recommendations
    setTimeout(() => {
      // Choose recommendations based on career path
      if (careerPath.toLowerCase().includes('machine learning')) {
        setCourseRecommendations(mleCourses)
      } else if (careerPath.toLowerCase().includes('software')) {
        setCourseRecommendations(sdCourses)
      } else {
        // Default to ML path if no match
        setCourseRecommendations(mleCourses)
      }
      
      setShowRecommendations(true)
      setIsLoading(false)
    }, 2000)
  }

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <Title>Course Planning</Title>
      
      {!showRecommendations ? (
        <Card className="mt-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Gemini Course Planning Assistant</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-blue-900 mb-2">
                Please provide your program information (URL)
              </label>
              <TextInput
                placeholder="Enter university program URL"
                value={programUrl}
                onChange={(e) => setProgramUrl(e.target.value)}
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-blue-900 mb-2">
                Please provide your preferred career path
              </label>
              <TextInput
                placeholder="e.g., Machine Learning Engineer, Software Developer"
                value={careerPath}
                onChange={(e) => setCareerPath(e.target.value)}
                required
              />
            </div>
            
            <Button 
              type="submit" 
              color="blue" 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? "Analyzing courses..." : "Generate Course Plan"}
            </Button>
          </form>
        </Card>
      ) : (
        <>
          <div className="mt-6">
            <Card>
              <div className="flex justify-between items-center">
                <Title>Recommended Course Timeline</Title>
                <Button 
                  color="blue" 
                  variant="light"
                  onClick={() => setShowRecommendations(false)}
                >
                  Start Over
                </Button>
              </div>
              
              <div className="mt-6 space-y-8">
                {courseRecommendations.map((course, index) => (
                  <div key={index} className="relative">
                    {index < courseRecommendations.length - 1 && (
                      <div className="absolute left-4 top-14 bottom-0 w-0.5 bg-blue-200"></div>
                    )}
                    <div className="flex items-start">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                        {index + 1}
                      </div>
                      <div className="ml-4">
                        <h3 className="text-lg font-semibold text-blue-900">{course.semester}</h3>
                        <div className="mt-2 p-4 bg-blue-50 rounded-lg">
                          <h4 className="font-medium text-blue-900">{course.name}</h4>
                          <p className="text-sm text-blue-700">
                            Course Code: {course.code} | Credits: {course.credits}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div className="mt-6">
            <Card>
              <Title>Semester Credit Distribution</Title>
              <BarChart
                className="mt-6"
                data={courseData}
                index="semester"
                categories={["credits"]}
                colors={["blue"]}
                valueFormatter={(number: number) => `${number} credits`}
                yAxisWidth={48}
              />
            </Card>
          </div>

          <div className="mt-6">
            <Card>
              <Title>Course Type Distribution</Title>
              <DonutChart
                className="mt-6"
                data={courseDistribution}
                category="value"
                index="name"
                colors={["blue", "cyan", "indigo"]}
                valueFormatter={(number: number) => `${number} credits`}
              />
            </Card>
          </div>
        </>
      )}
    </main>
  )
} 