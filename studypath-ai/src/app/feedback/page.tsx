'use client'

import React from 'react'
import { Card, Title, Button, TextInput, Textarea } from '@tremor/react'

export default function Feedback() {
  return (
    <main className="p-4 md:p-10 mx-auto max-w-3xl">
      <Title>Feedback</Title>
      
      <Card className="mt-6">
        <form className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-blue-900">
              Name
            </label>
            <TextInput
              id="name"
              placeholder="Enter your name"
              className="mt-1"
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
            />
          </div>

          <div>
            <label htmlFor="category" className="block text-sm font-medium text-blue-900">
              Feedback Type
            </label>
            <select
              id="category"
              className="mt-1 block w-full rounded-md border-blue-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
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
            />
          </div>

          <div className="flex items-center">
            <input
              id="terms"
              type="checkbox"
              className="h-4 w-4 rounded border-blue-300 text-blue-600 focus:ring-blue-500"
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
            >
              Submit Feedback
            </Button>
          </div>
        </form>
      </Card>

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