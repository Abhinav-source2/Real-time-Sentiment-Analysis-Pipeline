<p align="center">
  <img src="https://img.icons8.com/color/96/000000/speech-bubble.png" width="80" alt="logo" />
</p>

<h1 align="center">Real-Time Sentiment Analysis Pipeline 💬📊</h1>

<p align="center">
  A fully scalable pipeline to collect, process, analyze, and visualize public sentiment from social media platforms like Reddit and Twitter.
</p>

<p align="center">
  <img src="https://img.shields.io/github/languages/top/Abhinav-source2/Real-time-Sentiment-Analysis-Pipeline?style=flat-square" />
  <img src="https://img.shields.io/github/last-commit/Abhinav-source2/Real-time-Sentiment-Analysis-Pipeline?style=flat-square" />
  <img src="https://img.shields.io/badge/PowerBI-Dashboard-yellow?style=flat-square&logo=powerbi" />
  <img src="https://img.shields.io/badge/HuggingFace-NLP-orange?style=flat-square&logo=huggingface" />
</p>

---

## 📌 Overview

This project implements a **real-time sentiment analysis pipeline** for social media. It automatically:
- Scrapes posts from Twitter and Reddit using APIs
- Preprocesses and cleans text
- Classifies sentiment (positive, neutral, negative)
- Displays trends through live dashboards

The pipeline can be used for **brand monitoring**, **public opinion analysis**, and **crisis response**.

---

## ⚙️ Tech Stack

| Layer              | Tools & Libraries |
|--------------------|------------------|
| 🧠 NLP              | Hugging Face 🤗, NLTK, TextBlob |
| 💾 Storage (optional) | PostgreSQL / MongoDB |
| 🔄 Backend Processing | Python, Pandas, Transformers |
| 📈 Visualization    | Tableau / Power BI |
| 🔌 APIs             | Reddit API (PRAW), Twitter API |
| 🧪 Testing           | Pre-saved data + real-time validation |

---

## 🚀 Features

- ✅ Real-time scraping from Reddit & Twitter
- ✅ Sentiment classification using NLP models
- ✅ Dashboard with visual trends and charts
- ✅ Easy to scale and modify
- ✅ Clean modular codebase
- ✅ Exportable reports and visualizations

---

## 🔄 Pipeline Architecture

```mermaid
graph TD
  A[API Data Ingestion] --> B[Text Cleaning & Preprocessing]
  B --> C[Sentiment Analysis Model]
  C --> D[Store Results in DB (optional)]
  D --> E[Dashboard Visualization]
  C --> E
