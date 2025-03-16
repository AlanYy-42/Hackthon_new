'use client'

import React, { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('')
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // 处理搜索逻辑
    console.log('Search query:', searchQuery)
  }
  
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      {/* Hero Section */}
      <div className="w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">
              Redefine Your Learning Path with AI
            </h1>
            <p className="text-lg leading-8 text-blue-100 mb-8">
              StudyPath.AI leverages cutting-edge Edge AI technology to provide intelligent academic planning tools for university students and hackathon organizers.
            </p>
            
            {/* 添加搜索表单 */}
            <form onSubmit={handleSearch} className="max-w-md mx-auto mb-8">
              <div className="flex items-center border-2 border-white rounded-lg overflow-hidden">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for courses or career paths..."
                  className="w-full px-4 py-2 text-gray-800 focus:outline-none"
                />
                <button
                  type="submit"
                  className="bg-white text-blue-600 px-6 py-2 font-medium hover:bg-blue-50"
                >
                  Search
                </button>
              </div>
            </form>
            
            <div className="flex justify-center gap-4">
              <Link
                href="/course-planning"
                className="rounded-md bg-white px-6 py-3 text-base font-semibold text-blue-600 shadow-sm hover:bg-blue-50"
              >
                Start Planning
              </Link>
              <Link
                href="/career-goals"
                className="rounded-md bg-blue-500 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-400"
              >
                Explore Career Goals
              </Link>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="w-full bg-white py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="rounded-lg bg-blue-50 p-6"
            >
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Smart Course Planning</h3>
              <p className="text-blue-700">
                AI-powered personalized course recommendations to help you create the optimal learning path.
              </p>
            </motion.div>

            {/* Feature 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="rounded-lg bg-blue-50 p-6"
            >
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Career Integration</h3>
              <p className="text-blue-700">
                Seamlessly align your academic planning with career development goals.
              </p>
            </motion.div>

            {/* Feature 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="rounded-lg bg-blue-50 p-6"
            >
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Data Visualization</h3>
              <p className="text-blue-700">
                Intuitive charts and graphs to track your progress and achievements.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </main>
  )
} 