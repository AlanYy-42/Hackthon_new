'use client'

import React, { useState } from 'react'
import { Card, Title, Button, TextInput, Textarea } from '@tremor/react'

export default function Feedback() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [category, setCategory] = useState('Feature Suggestion')
  const [message, setMessage] = useState('')
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate API call
    setTimeout(() => {
      console.log('Feedback submitted:', { name, email, category, message, agreeTerms })
      setIsSubmitting(false)
      setIsSubmitted(true)
      
      // Reset form
      setName('')
      setEmail('')
      setCategory('Feature Suggestion')
      setMessage('')
      setAgreeTerms(false)
    }, 1500)
  }

  return (
    <main className="p-4 md:p-10 mx-auto max-w-3xl">
      <Title>Feedback</Title>
      
      {isSubmitted ? (
        <Card className="mt-6 p-6 text-center">
          <div className="text-green-600 text-5xl mb-4">✓</div>
          <h2 className="text-xl font-semibold text-blue-900 mb-2">Thank You for Your Feedback!</h2>
          <p className="text-blue-700 mb-6">Your input is valuable to us and helps improve StudyPath.AI.</p>
          <Button 
            color="blue" 
            onClick={() => setIsSubmitted(false)}
          >
            Submit Another Feedback
          </Button>
        </Card>
      ) : (
        <Card className="mt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-blue-900">
                Name
              </label>
              <TextInput
                id="name"
                placeholder="Enter your name"
                className="mt-1"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-blue-900">
                Email
              </label>
              <TextInput
                id="email"
                type="email"
                placeholder="Enter your email address"
                className="mt-1"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-medium text-blue-900">
                Feedback Type
              </label>
              <select
                id="category"
                className="mt-1 block w-full rounded-md border-blue-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option>Feature Suggestion</option>
                <option>Bug Report</option>
                <option>User Experience</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="message" className="block text-sm font-medium text-blue-900">
                Message
              </label>
              <Textarea
                id="message"
                placeholder="Please describe your feedback or suggestions in detail..."
                rows={6}
                className="mt-1"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
              />
            </div>

            <div className="flex items-center">
              <input
                id="terms"
                type="checkbox"
                className="h-4 w-4 rounded border-blue-300 text-blue-600 focus:ring-blue-500"
                checked={agreeTerms}
                onChange={(e) => setAgreeTerms(e.target.checked)}
                required
              />
              <label htmlFor="terms" className="ml-2 block text-sm text-blue-700">
                I agree to use this feedback to improve the service
              </label>
            </div>

            <div>
              <Button
                type="submit"
                className="w-full"
                color="blue"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit Feedback"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="mt-6">
        <Title>Frequently Asked Questions</Title>
        <div className="mt-4 space-y-4">
          {[
            {
              question: "How do I start using StudyPath.AI?",
              answer: "After registering an account, enter your learning goals and current course information, and the system will generate a personalized learning plan for you."
            },
            {
              question: "How are course recommendations generated?",
              answer: "We use advanced AI algorithms to recommend the most suitable courses based on your learning history, interests, and career goals."
            },
            {
              question: "How can I update my learning plan?",
              answer: "You can update your goals and preferences in your profile at any time, and the system will adjust recommendations in real-time."
            }
          ].map((item, index) => (
            <div key={index} className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900">{item.question}</h3>
              <p className="mt-2 text-sm text-blue-700">{item.answer}</p>
            </div>
          ))}
        </div>
      </Card>
    </main>
  )
} 