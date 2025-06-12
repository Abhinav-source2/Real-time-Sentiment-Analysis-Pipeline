<p align="center">
  <img src="https://img.icons8.com/color/96/000000/speech-bubble.png" width="80" alt="logo" />
</p>

<h1 align="center">Real-Time Sentiment Analysis Pipeline 💬📊</h1>

<p align="center">
  A production-ready pipeline that scrapes Reddit and YouTube comments, classifies sentiment using NLP models, and visualizes results in Power BI — all orchestrated through Apache Airflow.
</p>

<p align="center">
  <img src="https://img.shields.io/github/languages/top/Abhinav-source2/Real-time-Sentiment-Analysis-Pipeline?style=flat-square" />
  <img src="https://img.shields.io/github/last-commit/Abhinav-source2/Real-time-Sentiment-Analysis-Pipeline?style=flat-square" />
  <img src="https://img.shields.io/badge/Airflow-Orchestration-blue?style=flat-square&logo=apacheairflow" />
  <img src="https://img.shields.io/badge/PowerBI-Dashboard-yellow?style=flat-square&logo=powerbi" />
  <img src="https://img.shields.io/badge/HuggingFace-NLP-orange?style=flat-square&logo=huggingface" />
</p>

---

## 📌 Overview

This project implements a **real-time sentiment analysis pipeline** for public social media content using:

- Apache Airflow for end-to-end orchestration
- Python-based NLP pipelines
- Hugging Face models for sentiment classification
- Power BI for trend visualization

It's modular, scalable, and deployable for any organization interested in public sentiment monitoring.

---

## ⚙️ Tech Stack

| Layer              | Tools & Libraries |
|--------------------|------------------|
| 🧠 NLP              | Hugging Face 🤗, NLTK, TextBlob |
| 🔄 Orchestration    | Apache Airflow |
| 📊 Visualization    | Power BI |
| 🔌 APIs             | Reddit API (PRAW), YouTube Comments |
| 🧹 Preprocessing     | Pandas, Regex, Custom Python Scripts |
| 🧪 Testing           | Sample datasets + DAG validation |

---

## 🚀 Features

- ✅ Real-time scraping from Reddit and YouTube
- ✅ Sentiment classification using Hugging Face transformers
- ✅ Apache Airflow DAG for complete automation
- ✅ Power BI dashboard for visualization
- ✅ Modular, clean, production-grade pipeline

---

## 🔄 Pipeline Architecture

```mermaid
graph TD
  A[API Data Ingestion] --> B[Text Cleaning & Preprocessing]
  B --> C[Sentiment Analysis Model]
  C --> D[Store to DB / CSV]
  C --> E[Dashboard Visualization]
  D --> E
