# StudyPath AI

您的个人学术导航器 - 利用边缘AI智能革新学术规划

## 项目概述

StudyPath AI通过利用Snapdragon的NPU创建一个强大的、以隐私为先的平台，为个性化学术指导提供支持。我们的解决方案解决了当今大学生在课程选择、学术表现优化和职业对齐方面面临的关键挑战。

## 功能

- 智能课程规划系统
- 个人学习分析
- 职业整合模块

## 使用方法

1. 在"学生ID"字段中输入学生ID（示例数据中有1、2、3三个学生ID）
2. 点击"获取推荐"按钮获取课程推荐
3. 点击"查看日程"按钮查看当前课程安排

## 示例数据

种子脚本创建了：
- 10门跨计算机科学、数学和英语的课程
- 3名不同专业的学生
- 具有各种状态的课程注册

## API端点

- `/api/health` - 健康检查端点
- `/api/courses` - 获取所有课程
- `/api/courses/<course_id>` - 获取特定课程
- `/api/students/<student_id>` - 获取特定学生
- `/api/students/<student_id>/courses` - 获取学生的课程
- `/api/recommendations` - 获取课程推荐（POST）

## 下一步计划

1. 实现NPU集成的ML模型
2. 添加更复杂的推荐算法
3. 开发学习分析模块
4. 创建职业整合功能
5. 使用React Native或Flutter增强UI 